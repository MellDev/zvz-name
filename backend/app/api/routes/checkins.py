from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import require_event_manager
from app.models import Build, CheckIn, EventBuild, PlayerBuildApproval, ZvZEvent, User
from app.api.routes.mounts import MOUNT_CATALOG
from app.schemas import CheckInCreate, CheckInRead, CheckInUpdate
from app.services.discord import publish_event_to_discord

router = APIRouter()

def serialize_checkin(checkin: CheckIn) -> CheckInRead:
    return CheckInRead(
        id=checkin.id,
        guild_id=checkin.guild_id,
        event_id=checkin.event_id,
        user_id=checkin.user_id,
        build_id=checkin.build_id,
        weapon_selected=checkin.weapon_selected,
        mount_selected=checkin.mount_selected,
        approved=checkin.approved,
        notes=checkin.notes,
        checkin_time=checkin.checkin_time,
        player_nick=checkin.player_nick_snapshot or (checkin.user.albion_nick if checkin.user else None),
        player_nick_snapshot=checkin.player_nick_snapshot,
        event_title=checkin.event.title if checkin.event else None,
        build_name=checkin.build.name if checkin.build else checkin.weapon_selected,
        build_role=checkin.build.role if checkin.build else None,
    )


def catalog_mount(mount_name: str) -> dict | None:
    normalized = mount_name.strip().lower()
    for mount in MOUNT_CATALOG:
        if mount['mount_name'].lower() == normalized or mount['display_name'].lower() == normalized:
            return mount
    return None


def sync_event_with_discord(event: ZvZEvent, db: Session) -> None:
    if event.status != 'draft':
        publish_event_to_discord(event, db=db)

@router.post('/', response_model=CheckInRead, status_code=status.HTTP_201_CREATED)
def create_checkin(payload: CheckInCreate, db: Session = Depends(get_db)):
    event = db.get(ZvZEvent, payload.event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    player = db.get(User, payload.user_id)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    if not player.active:
        raise HTTPException(status_code=403, detail='Player is inactive')

    existing = db.query(CheckIn).filter(CheckIn.event_id == payload.event_id, CheckIn.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail='Player already checked in for this event')

    build = db.get(Build, payload.build_id) if payload.build_id else (
        db.query(Build).filter(Build.name == payload.weapon_selected, Build.guild_id == payload.guild_id).first()
    )
    if not build:
        raise HTTPException(status_code=400, detail='A valid build is required')
    if not build.active:
        raise HTTPException(status_code=403, detail='Build is inactive')

    linked = db.query(EventBuild).filter(
        EventBuild.event_id == payload.event_id,
        EventBuild.build_id == build.id,
    ).first()
    approved = db.query(PlayerBuildApproval).filter(
        PlayerBuildApproval.player_id == payload.user_id,
        PlayerBuildApproval.build_id == build.id,
        PlayerBuildApproval.approved == True,
    ).first()
    if event.caller:
        approved = db.query(PlayerBuildApproval).filter(
            PlayerBuildApproval.player_id == payload.user_id,
            PlayerBuildApproval.build_id == build.id,
            PlayerBuildApproval.caller == event.caller,
            PlayerBuildApproval.approved == True,
        ).first()
    if not linked or not approved:
        raise HTTPException(status_code=403, detail='Build not approved for this player/event')

    taken_slots = db.query(CheckIn).filter(CheckIn.event_id == payload.event_id, CheckIn.build_id == build.id).count()
    if taken_slots >= max(linked.max_slots or 1, 1):
        raise HTTPException(status_code=409, detail='No slots left for this build in this event')

    mount = catalog_mount(payload.mount_selected)
    required_gallop = event.mount_gallop_requirement or 120
    if mount and (mount.get('gallop_speed_bonus') or 0) < required_gallop:
        raise HTTPException(status_code=403, detail=f'Mount must have {required_gallop}%+ gallop')

    data = payload.model_dump()
    data['build_id'] = build.id
    data['weapon_selected'] = build.name
    data['player_nick_snapshot'] = player.albion_nick
    checkin = CheckIn(**data)
    db.add(checkin)
    player.participations += 1
    db.flush()
    db.expire(event, ['checkins'])
    sync_event_with_discord(event, db)
    db.commit()
    db.refresh(checkin)
    return serialize_checkin(checkin)

@router.get('/', response_model=List[CheckInRead])
def list_checkins(
    event_id: int | None = None,
    player_id: int | None = None,
    content_type: str | None = None,
    build_id: int | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CheckIn)
    if event_id is not None:
        query = query.filter(CheckIn.event_id == event_id)
    if player_id is not None:
        query = query.filter(CheckIn.user_id == player_id)
    if build_id is not None:
        query = query.filter(CheckIn.build_id == build_id)
    if content_type:
        query = query.join(ZvZEvent).filter(ZvZEvent.content_type.ilike(content_type))
    if role:
        query = query.join(Build).filter(Build.role.ilike(role))
    return [serialize_checkin(checkin) for checkin in query.order_by(CheckIn.checkin_time.desc()).all()]

@router.get('/event/{event_id}', response_model=List[CheckInRead])
def checkins_by_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    return [serialize_checkin(checkin) for checkin in db.query(CheckIn).filter(CheckIn.event_id == event_id).all()]

@router.put('/{checkin_id}', response_model=CheckInRead)
def update_checkin(checkin_id: int, payload: CheckInUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    checkin = db.get(CheckIn, checkin_id)
    if not checkin:
        raise HTTPException(status_code=404, detail='Check-in not found')

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checkin, field, value)

    event = checkin.event
    db.flush()
    if event:
        db.expire(event, ['checkins'])
        sync_event_with_discord(event, db)
    db.commit()
    db.refresh(checkin)
    return serialize_checkin(checkin)

@router.delete('/{checkin_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(checkin_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_event_manager)):
    checkin = db.get(CheckIn, checkin_id)
    if not checkin:
        raise HTTPException(status_code=404, detail='Check-in not found')

    player = checkin.user
    event = checkin.event
    if player and player.participations > 0:
        player.participations -= 1
    db.delete(checkin)
    db.flush()
    if event:
        db.expire(event, ['checkins'])
        sync_event_with_discord(event, db)
    db.commit()
    return None
