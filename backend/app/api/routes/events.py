from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import ZvZEvent
from app.schemas import ZvZEventCreate, ZvZEventRead

router = APIRouter()

@router.post('/', response_model=ZvZEventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: ZvZEventCreate, db: Session = Depends(get_db)):
    event = ZvZEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get('/', response_model=List[ZvZEventRead])
def list_events(db: Session = Depends(get_db)):
    return db.query(ZvZEvent).all()

@router.put('/{event_id}', response_model=ZvZEventRead)
def update_event(event_id: int, payload: ZvZEventCreate, db: Session = Depends(get_db)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    for field, value in payload.model_dump().items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event
