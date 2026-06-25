from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import get_current_user, require_staff
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    data = payload.model_dump()
    data['albion_nick'] = data['albion_nick'].strip()
    data['discord_id'] = data.get('discord_id') or data['albion_nick'].strip().lower()
    data['discord_id'] = data['discord_id'].strip()
    data['discord_name'] = (data.get('discord_name') or data['albion_nick']).strip()

    existing = db.query(User).filter(
        (User.discord_id == data['discord_id']) |
        (func.lower(func.trim(User.albion_nick)) == data['albion_nick'].lower())
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail='Player already exists')

    player = User(**data)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.get('/', response_model=List[UserRead])
def list_players(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get('/{player_id}', response_model=UserRead)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(User, player_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    return player

@router.put('/{player_id}', response_model=UserRead)
def update_player(player_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    player = db.get(User, player_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')

    update_data = payload.model_dump(exclude_unset=True)
    staff_fields = {'role', 'is_staff', 'is_leader', 'active', 'rating', 'weapon_1_approved', 'weapon_2_approved'}
    is_staff = current_user.is_staff or current_user.role in {'staff', 'dev'}
    if current_user.id != player_id and not is_staff:
        raise HTTPException(status_code=403, detail='Staff access required')
    if not is_staff and any(field in update_data for field in staff_fields):
        raise HTTPException(status_code=403, detail='Staff access required')

    if 'albion_nick' in update_data and update_data['albion_nick']:
        update_data['albion_nick'] = update_data['albion_nick'].strip()
    for field, value in update_data.items():
        setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_player(payload: UserCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data['albion_nick'] = data['albion_nick'].strip()
    if not data['albion_nick']:
        raise HTTPException(status_code=400, detail='Nick Albion is required')

    existing = db.query(User).filter(
        User.guild_id == data['guild_id'],
        func.lower(func.trim(User.albion_nick)) == data['albion_nick'].lower(),
    ).first()
    if existing:
        if not existing.active:
            existing.active = True
            db.commit()
            db.refresh(existing)
        return existing

    data['discord_id'] = data.get('discord_id') or f"nick:{data['albion_nick'].strip().lower()}"
    data['discord_id'] = data['discord_id'].strip()
    data['discord_name'] = (data.get('discord_name') or data['albion_nick']).strip()
    data['role'] = 'player'
    data['is_staff'] = False
    data['is_leader'] = False

    player = User(**data)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.delete('/{player_id}', response_model=UserRead)
def deactivate_player(player_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    player = db.get(User, player_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    player.active = False
    db.commit()
    db.refresh(player)
    return player

@router.post('/{player_id}/reactivate', response_model=UserRead)
def reactivate_player(player_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    player = db.get(User, player_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    player.active = True
    db.commit()
    db.refresh(player)
    return player
