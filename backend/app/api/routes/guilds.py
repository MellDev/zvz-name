from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Guild
from app.schemas import GuildCreate, GuildRead

router = APIRouter()

@router.post('/', response_model=GuildRead, status_code=status.HTTP_201_CREATED)
def create_guild(payload: GuildCreate, db: Session = Depends(get_db)):
    if db.query(Guild).filter(Guild.name == payload.name).first():
        raise HTTPException(status_code=400, detail='Guild already exists')
    guild = Guild(**payload.model_dump())
    db.add(guild)
    db.commit()
    db.refresh(guild)
    return guild

@router.get('/', response_model=List[GuildRead])
def list_guilds(db: Session = Depends(get_db)):
    return db.query(Guild).all()

@router.get('/{guild_id}', response_model=GuildRead)
def get_guild(guild_id: int, db: Session = Depends(get_db)):
    guild = db.get(Guild, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail='Guild not found')
    return guild
