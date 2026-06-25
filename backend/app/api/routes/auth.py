from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.deps import get_db
from app.models import Guild, User
from app.schemas import DiscordCallbackResponse, DiscordLoginUrl, Token, UserRead

router = APIRouter()

DISCORD_AUTHORIZE_URL = 'https://discord.com/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
DISCORD_ME_URL = 'https://discord.com/api/users/@me'
DEV_NAMES = {'anderson mello', 'anderson'}


def require_discord_settings() -> None:
    if not settings.DISCORD_CLIENT_ID or not settings.DISCORD_CLIENT_SECRET or not settings.DISCORD_REDIRECT_URI:
        raise HTTPException(status_code=503, detail='Discord OAuth is not configured')


@router.get('/discord/login', response_model=DiscordLoginUrl)
def discord_login_url():
    require_discord_settings()
    params = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': settings.DISCORD_SCOPES,
        'prompt': 'consent',
    }
    return {'url': f'{DISCORD_AUTHORIZE_URL}?{urlencode(params)}'}


@router.get('/discord/callback')
async def discord_oauth_callback(
    code: str = Query(..., min_length=1),
    guild_id: int | None = None,
    response_mode: str = Query('redirect'),
    db: Session = Depends(get_db),
):
    require_discord_settings()

    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            DISCORD_TOKEN_URL,
            data={
                'client_id': settings.DISCORD_CLIENT_ID,
                'client_secret': settings.DISCORD_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.DISCORD_REDIRECT_URI,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        if token_response.status_code >= 400:
            raise HTTPException(status_code=401, detail='Discord token exchange failed')

        discord_token = token_response.json().get('access_token')
        me_response = await client.get(DISCORD_ME_URL, headers={'Authorization': f'Bearer {discord_token}'})
        if me_response.status_code >= 400:
            raise HTTPException(status_code=401, detail='Discord profile fetch failed')

    profile = me_response.json()
    discord_id = str(profile['id'])
    discord_name = profile.get('global_name') or profile.get('username') or discord_id
    target_guild_id = guild_id or settings.DISCORD_DEFAULT_GUILD_ID

    guild = db.get(Guild, target_guild_id)
    if not guild:
        guild = Guild(id=target_guild_id, name='Principal')
        db.add(guild)
        db.flush()

    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        user = db.query(User).filter(func.lower(func.trim(User.albion_nick)) == discord_name.strip().lower()).first()
    if user:
        user.discord_id = discord_id
        user.discord_name = discord_name
    else:
        user = User(
            guild_id=target_guild_id,
            discord_id=discord_id,
            discord_name=discord_name,
            albion_nick=discord_name,
            role='player',
            is_staff=False,
        )
        db.add(user)

    normalized_names = {discord_name.strip().lower(), user.albion_nick.strip().lower()}
    if normalized_names & DEV_NAMES:
        user.role = 'dev'
        user.is_staff = True
        user.is_leader = True
        user.active = True

    db.commit()
    db.refresh(user)
    access_token = create_access_token(subject=str(user.id))
    if response_mode == 'json':
        return DiscordCallbackResponse(access_token=access_token, token_type='bearer', user=user)

    frontend_callback = f'{settings.FRONTEND_URL.rstrip("/")}/auth/discord/callback'
    params = urlencode(
        {
            'token': access_token,
            'user_id': user.id,
            'nick': user.albion_nick,
            'discord_name': user.discord_name,
        }
    )
    return RedirectResponse(f'{frontend_callback}?{params}', status_code=status.HTTP_302_FOUND)

@router.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.discord_id == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = create_access_token(subject=str(user.id))
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.get('/me', response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
