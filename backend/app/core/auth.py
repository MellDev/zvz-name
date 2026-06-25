from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.deps import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token')
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token', auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get('sub'))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Inactive user')
    return user


def get_optional_current_user(token: Optional[str] = Depends(optional_oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_staff and current_user.role not in {'staff', 'dev'}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Staff access required')
    return current_user


def require_event_manager(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_staff and current_user.role not in {'caller', 'leader', 'staff', 'dev'} and not current_user.is_leader:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Event manager access required')
    return current_user


def require_leader(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_leader and not current_user.is_staff and current_user.role not in {'caller', 'leader', 'staff', 'dev'}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Leader access required')
    return current_user
