from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.deps import get_db
from app.models import User
from app.schemas import Token, UserRead

router = APIRouter()

@router.get('/discord')
def discord_oauth_redirect():
    return {'detail': 'Discord OAuth2 redirect will be implemented here.'}

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
