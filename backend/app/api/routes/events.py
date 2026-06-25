from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_event_manager
from app.deps import get_db
from app.models import EventBuild, User, ZvZEvent
from app.schemas import DiscordEventPreview, ZvZEventCreate, ZvZEventDuplicate, ZvZEventRead, ZvZEventUpdate
from app.services.discord import _build_message_content, publish_event_to_discord

router = APIRouter()

LEGACY_BUILD_CALLERS = {'GAKUIA', 'SOLUS', 'DELTA'}
CALLER_REQUIRED_CONTENT_TYPES = {'zvz', 'cta', 'autorizacao de build', 'autorização de build'}


def _caller_values(db: Session) -> set[str]:
    players = db.query(User).filter(User.active == True, User.role == 'caller').all()
    return LEGACY_BUILD_CALLERS | {player.albion_nick.strip().upper() for player in players if player.albion_nick.strip()}


def _normalize_caller(value: str | None, db: Session) -> str | None:
    if not value:
        return None
    normalized = value.strip().upper()
    if normalized not in _caller_values(db):
        raise HTTPException(status_code=422, detail='Caller must be a player tagged as caller')
    return normalized


def _prepare_event_data(data: dict, db: Session) -> dict:
    content_type = str(data.get('content_type') or '').strip().lower()
    caller = _normalize_caller(data.get('caller'), db)
    if content_type in CALLER_REQUIRED_CONTENT_TYPES and caller is None:
        raise HTTPException(status_code=422, detail='Caller is required for ZvZ, CTA and build authorization events')
    data['caller'] = caller
    return data


def _sync_event_with_discord(event: ZvZEvent, db: Session) -> None:
    publish_event_to_discord(event, db=db)


@router.post('/', response_model=ZvZEventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: ZvZEventCreate, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    data = _prepare_event_data(payload.model_dump(), db)
    if data.get('created_by') is None:
        data['created_by'] = current_user.id
    event = ZvZEvent(**data)
    db.add(event)
    db.flush()
    _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event


@router.get('/', response_model=List[ZvZEventRead])
def list_events(db: Session = Depends(get_db)):
    return db.query(ZvZEvent).all()


@router.put('/{event_id}', response_model=ZvZEventRead)
def update_event(event_id: int, payload: ZvZEventUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    data = payload.model_dump(exclude_unset=True)
    preview = {
        'content_type': data.get('content_type', event.content_type),
        'caller': data.get('caller', event.caller),
    }
    prepared = _prepare_event_data(preview, db)
    if 'caller' in data or 'content_type' in data:
        data['caller'] = prepared['caller']
    for field, value in data.items():
        setattr(event, field, value)
    db.flush()
    if event.status != 'draft':
        _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event


@router.post('/{event_id}/duplicate', response_model=ZvZEventRead, status_code=status.HTTP_201_CREATED)
def duplicate_event(event_id: int, payload: ZvZEventDuplicate | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    source = db.get(ZvZEvent, event_id)
    if not source:
        raise HTTPException(status_code=404, detail='Event not found')

    payload = payload or ZvZEventDuplicate()
    event = ZvZEvent(
        guild_id=source.guild_id,
        title=payload.title or f'Copia de {source.title}',
        content_type=source.content_type,
        caller=source.caller,
        event_date=payload.event_date or source.event_date,
        status=payload.status or 'draft',
        mount_gallop_requirement=source.mount_gallop_requirement,
        mount_requirement_note=source.mount_requirement_note,
        created_by=current_user.id,
    )
    db.add(event)
    db.flush()

    for link in source.build_links:
        db.add(EventBuild(event_id=event.id, build_id=link.build_id, max_slots=max(link.max_slots or 1, 1)))

    db.flush()
    if event.status != 'draft':
        _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event


@router.post('/{event_id}/discord/publish', response_model=ZvZEventRead)
def publish_discord_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event


@router.get('/{event_id}/discord/preview', response_model=DiscordEventPreview)
def preview_discord_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    return DiscordEventPreview(
        event_id=event.id,
        content=_build_message_content(event),
        message_url=event.discord_message_url,
        last_sync_at=event.discord_last_sync_at,
    )


@router.post('/{event_id}/close', response_model=ZvZEventRead)
def close_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    event.status = 'closed'
    db.flush()
    _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event


@router.post('/{event_id}/reopen', response_model=ZvZEventRead)
def reopen_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    event.status = 'open'
    db.flush()
    _sync_event_with_discord(event, db)
    db.commit()
    db.refresh(event)
    return event
