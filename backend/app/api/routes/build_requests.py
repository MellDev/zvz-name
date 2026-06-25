from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_optional_current_user, require_leader
from app.deps import get_db
from app.models import Build, BuildRequest, CheckIn, EventBuild, User, ZvZEvent
from app.schemas import BuildRequestCreate, BuildRequestRead, BuildRequestUpdate
from app.services.discord import publish_event_to_discord

router = APIRouter()


def is_dungeon_event(event: ZvZEvent) -> bool:
    return event.content_type.strip().lower() in {'dg', 'dungeon', 'dungeons'}


def serialize_request(request: BuildRequest) -> BuildRequestRead:
    return BuildRequestRead(
        id=request.id,
        guild_id=request.guild_id,
        event_id=request.event_id,
        player_id=request.player_id,
        build_id=request.build_id,
        status=request.status,
        notes=request.notes,
        weapon_power=request.weapon_power,
        leader_id=request.leader_id,
        created_at=request.created_at,
        decided_at=request.decided_at,
        event_title=request.event.title if request.event else None,
        event_created_by=request.event.created_by if request.event else None,
        player_nick=request.player.albion_nick if request.player else None,
        build_name=request.build.name if request.build else None,
        build_role=request.build.role if request.build else None,
        build_icon_url=request.build.weapon_icon_url if request.build else None,
    )


@router.post('/', response_model=BuildRequestRead, status_code=status.HTTP_201_CREATED)
def create_build_request(
    payload: BuildRequestCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    event = db.get(ZvZEvent, payload.event_id)
    build = db.get(Build, payload.build_id)
    if not event or not build:
        raise HTTPException(status_code=404, detail='Event or build not found')
    if not is_dungeon_event(event):
        raise HTTPException(status_code=400, detail='Build requests are only available for DG/Dungeon events')
    if not build.active:
        raise HTTPException(status_code=403, detail='Build is inactive')
    linked = db.query(EventBuild).filter(
        EventBuild.event_id == event.id,
        EventBuild.build_id == build.id,
    ).first()
    if not linked:
        raise HTTPException(status_code=403, detail='Build is not configured for this event')

    player = current_user
    if not player:
        player_nick = (payload.player_nick or '').strip()
        if not player_nick:
            raise HTTPException(status_code=400, detail='Informe o nick Albion para solicitar build')
        player = (
            db.query(User)
            .filter(User.guild_id == event.guild_id)
            .filter(User.albion_nick.ilike(player_nick))
            .first()
        )
        if not player:
            raise HTTPException(status_code=404, detail='Nick nao encontrado no cadastro')
    if not player.active:
        raise HTTPException(status_code=403, detail='Player is inactive')

    taken_slots = db.query(CheckIn).filter(CheckIn.event_id == event.id, CheckIn.build_id == build.id).count()
    if taken_slots >= max(linked.max_slots or 1, 1):
        raise HTTPException(status_code=409, detail='No slots left for this build in this event')

    existing_checkin = (
        db.query(CheckIn)
        .filter(CheckIn.event_id == event.id, CheckIn.user_id == player.id)
        .first()
    )
    if existing_checkin:
        raise HTTPException(status_code=400, detail='Player already checked in for this event')

    existing_request = (
        db.query(BuildRequest)
        .filter(
            BuildRequest.event_id == event.id,
            BuildRequest.player_id == player.id,
            BuildRequest.status == 'pending',
        )
        .first()
    )
    if existing_request:
        raise HTTPException(status_code=400, detail='Player already has a pending request for this event')

    request = BuildRequest(
        guild_id=event.guild_id,
        event_id=event.id,
        player_id=player.id,
        build_id=build.id,
        notes=payload.notes,
        weapon_power=payload.weapon_power,
        status='pending',
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return serialize_request(request)


@router.get('/', response_model=List[BuildRequestRead])
def list_build_requests(
    event_id: int | None = None,
    status_filter: str | None = None,
    mine: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(BuildRequest)
    if event_id is not None:
        query = query.filter(BuildRequest.event_id == event_id)
    if status_filter:
        query = query.filter(BuildRequest.status == status_filter)

    is_staff = current_user.is_staff or current_user.role in {'staff', 'dev'}
    can_lead = current_user.is_leader or current_user.role in {'caller', 'leader'}
    if mine:
        query = query.filter(BuildRequest.player_id == current_user.id)
    elif is_staff:
        pass
    elif can_lead:
        query = query.join(ZvZEvent).filter(ZvZEvent.created_by == current_user.id)
    else:
        query = query.filter(BuildRequest.player_id == current_user.id)

    return [serialize_request(request) for request in query.order_by(BuildRequest.created_at.desc()).all()]


@router.put('/{request_id}', response_model=BuildRequestRead)
def update_build_request(
    request_id: int,
    payload: BuildRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    request = db.get(BuildRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail='Build request not found')
    is_staff = current_user.is_staff or current_user.role in {'staff', 'dev'}
    is_event_leader = request.event and request.event.created_by == current_user.id
    is_caller = current_user.role == 'caller'
    if not is_staff and not is_event_leader and not is_caller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the event leader can decide this request')
    if request.status != 'pending':
        raise HTTPException(status_code=400, detail='Build request already decided')

    next_status = payload.status.strip().lower()
    if next_status not in {'approved', 'rejected'}:
        raise HTTPException(status_code=400, detail='Status must be approved or rejected')

    request.status = next_status
    request.notes = payload.notes if payload.notes is not None else request.notes
    request.weapon_power = payload.weapon_power if payload.weapon_power is not None else request.weapon_power
    request.leader_id = current_user.id
    request.decided_at = datetime.utcnow()

    if next_status == 'approved':
        linked = db.query(EventBuild).filter(
            EventBuild.event_id == request.event_id,
            EventBuild.build_id == request.build_id,
        ).first()
        if not linked:
            raise HTTPException(status_code=403, detail='Build is not configured for this event')
        taken_slots = db.query(CheckIn).filter(CheckIn.event_id == request.event_id, CheckIn.build_id == request.build_id).count()
        if taken_slots >= max(linked.max_slots or 1, 1):
            raise HTTPException(status_code=409, detail='No slots left for this build in this event')
        existing_checkin = (
            db.query(CheckIn)
            .filter(CheckIn.event_id == request.event_id, CheckIn.user_id == request.player_id)
            .first()
        )
        if not existing_checkin:
            checkin = CheckIn(
                guild_id=request.guild_id,
                event_id=request.event_id,
                user_id=request.player_id,
                build_id=request.build_id,
                weapon_selected=request.build.name if request.build else 'Build DG',
                mount_selected='Solicitacao DG',
                player_nick_snapshot=request.player.albion_nick if request.player else None,
                approved=True,
                notes=f'Aprovado por lider via solicitacao #{request.id}',
            )
            db.add(checkin)
            if request.player:
                request.player.participations += 1
            db.flush()
            if request.event and request.event.status != 'draft':
                db.expire(request.event, ['checkins'])
                publish_event_to_discord(request.event, db=db)

    db.commit()
    db.refresh(request)
    return serialize_request(request)
