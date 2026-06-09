from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.discord_id == payload.discord_id).first()
    if existing:
        raise HTTPException(status_code=400, detail='Player already exists')

    player = User(**payload.model_dump())
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
def update_player(player_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    player = db.get(User, player_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player
