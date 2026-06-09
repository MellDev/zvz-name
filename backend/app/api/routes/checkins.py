from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import CheckIn, ZvZEvent, User
from app.schemas import CheckInCreate, CheckInRead

router = APIRouter()

@router.post('/', response_model=CheckInRead, status_code=status.HTTP_201_CREATED)
def create_checkin(payload: CheckInCreate, db: Session = Depends(get_db)):
    event = db.get(ZvZEvent, payload.event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    player = db.get(User, payload.user_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')

    existing = db.query(CheckIn).filter(CheckIn.event_id == payload.event_id, CheckIn.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail='Player already checked in for this event')

    checkin = CheckIn(**payload.model_dump())
    db.add(checkin)
    player.participations += 1
    db.commit()
    db.refresh(checkin)
    return checkin

@router.get('/', response_model=List[CheckInRead])
def list_checkins(db: Session = Depends(get_db)):
    return db.query(CheckIn).all()

@router.get('/event/{event_id}', response_model=List[CheckInRead])
def checkins_by_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    return db.query(CheckIn).filter(CheckIn.event_id == event_id).all()
