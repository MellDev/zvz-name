from typing import List
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import get_current_user, require_staff
from app.models import Build, BuildMount, CheckIn, EventBuild, PlayerBuildApproval, User, ZvZEvent
from app.schemas import (
    AvailableBuildsResponse,
    BuildCreate,
    BuildEventSlot,
    BuildEventSlotRead,
    BuildRead,
    BuildUpdate,
    PlayerBuildApprovalCreate,
    PlayerBuildApprovalRead,
)
from app.services.discord import publish_event_to_discord

router = APIRouter()

LEGACY_BUILD_CALLERS = {'GAKUIA', 'SOLUS', 'DELTA'}


def normalize_content_type(value: str | None) -> str:
    if not value:
        return ''
    without_accents = ''.join(
        char for char in unicodedata.normalize('NFD', value)
        if unicodedata.category(char) != 'Mn'
    )
    return without_accents.strip().lower()


def build_matches_event(build: Build, event: ZvZEvent) -> bool:
    build_type = normalize_content_type(build.build_type)
    event_type = normalize_content_type(event.content_type)
    dungeon_types = {'dg', 'dungeon', 'dungeons'}
    if build_type in dungeon_types and event_type in dungeon_types:
        return True
    return build_type == event_type


def is_staff_user(user: User) -> bool:
    return user.is_staff or user.role in {'staff', 'dev'}


def is_event_manager_user(user: User) -> bool:
    return is_staff_user(user) or user.is_leader or user.role in {'caller', 'leader'}


def caller_values(db: Session) -> set[str]:
    players = db.query(User).filter(User.active == True, User.role == 'caller').all()
    return LEGACY_BUILD_CALLERS | {player.albion_nick.strip().upper() for player in players if player.albion_nick.strip()}


def normalize_caller(value: str | None, db: Session) -> str | None:
    if not value:
        return None
    normalized = value.strip().upper()
    if normalized not in caller_values(db):
        raise HTTPException(status_code=422, detail='Caller must be a player tagged as caller')
    return normalized


def event_slot_reads(db: Session | None, build: Build) -> list[BuildEventSlotRead]:
    slots = []
    for link in build.event_links:
        taken = 0
        if db is not None:
            taken = db.query(CheckIn).filter(CheckIn.event_id == link.event_id, CheckIn.build_id == build.id).count()
        max_slots = max(link.max_slots or 1, 1)
        slots.append(
            BuildEventSlotRead(
                event_id=link.event_id,
                max_slots=max_slots,
                taken_slots=taken,
                remaining_slots=max(max_slots - taken, 0),
            )
        )
    return slots


def serialize_build(build: Build, db: Session | None = None) -> BuildRead:
    return BuildRead(
        id=build.id,
        guild_id=build.guild_id,
        name=build.name,
        build_type=build.build_type,
        role=build.role,
        weapon_name=build.weapon_name,
        weapon_item_id=build.weapon_item_id,
        weapon_icon_url=build.weapon_icon_url,
        weapon_skills=build.weapon_skills,
        offhand=build.offhand,
        offhand_item_id=build.offhand_item_id,
        offhand_icon_url=build.offhand_icon_url,
        helmet=build.helmet,
        helmet_item_id=build.helmet_item_id,
        helmet_icon_url=build.helmet_icon_url,
        helmet_skills=build.helmet_skills,
        chest=build.chest,
        chest_item_id=build.chest_item_id,
        chest_icon_url=build.chest_icon_url,
        chest_skills=build.chest_skills,
        boots=build.boots,
        boots_item_id=build.boots_item_id,
        boots_icon_url=build.boots_icon_url,
        boots_skills=build.boots_skills,
        cape=build.cape,
        food=build.food,
        potion=build.potion,
        recommended_mount=build.recommended_mount,
        required_level=build.required_level,
        description=build.description,
        active=build.active,
        created_at=build.created_at,
        updated_at=build.updated_at,
        allowed_mounts=[mount.mount_name for mount in build.mounts],
        event_ids=[link.event_id for link in build.event_links],
        event_slots=event_slot_reads(db, build),
    )


def normalize_event_slots(event_slots: list[BuildEventSlot], event_ids: list[int]) -> list[BuildEventSlot]:
    if event_slots:
        return [BuildEventSlot(event_id=slot.event_id, max_slots=max(slot.max_slots, 1)) for slot in event_slots]
    return [BuildEventSlot(event_id=event_id, max_slots=1) for event_id in event_ids]


def sync_build_links(
    db: Session,
    build: Build,
    allowed_mounts: list[str],
    event_slots: list[BuildEventSlot],
) -> set[int]:
    affected_event_ids = {link.event_id for link in build.event_links}
    db.query(BuildMount).filter(BuildMount.build_id == build.id).delete()
    for mount_name in allowed_mounts:
        if mount_name.strip():
            db.add(BuildMount(build_id=build.id, mount_name=mount_name.strip()))

    db.query(EventBuild).filter(EventBuild.build_id == build.id).delete()
    seen_event_ids = set()
    for slot in event_slots:
        if slot.event_id in seen_event_ids:
            continue
        seen_event_ids.add(slot.event_id)
        event = db.get(ZvZEvent, slot.event_id)
        if event:
            if not build_matches_event(build, event):
                raise HTTPException(
                    status_code=400,
                    detail=f'Build type {build.build_type} cannot be linked to event type {event.content_type}',
                )
            db.add(EventBuild(event_id=slot.event_id, build_id=build.id, max_slots=max(slot.max_slots, 1)))
            affected_event_ids.add(slot.event_id)

    return affected_event_ids


def sync_active_events_with_discord(db: Session, event_ids: set[int]) -> None:
    for event_id in event_ids:
        event = db.get(ZvZEvent, event_id)
        if event and event.status != 'draft':
            publish_event_to_discord(event, db=db)


@router.post('/', response_model=BuildRead, status_code=status.HTTP_201_CREATED)
def create_build(payload: BuildCreate, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    build = Build(
        guild_id=payload.guild_id,
        name=payload.name,
        build_type=payload.build_type,
        role=payload.role,
        weapon_name=payload.weapon_name,
        weapon_item_id=payload.weapon_item_id,
        weapon_icon_url=payload.weapon_icon_url,
        weapon_skills=payload.weapon_skills,
        offhand=payload.offhand,
        offhand_item_id=payload.offhand_item_id,
        offhand_icon_url=payload.offhand_icon_url,
        helmet=payload.helmet,
        helmet_item_id=payload.helmet_item_id,
        helmet_icon_url=payload.helmet_icon_url,
        helmet_skills=payload.helmet_skills,
        chest=payload.chest,
        chest_item_id=payload.chest_item_id,
        chest_icon_url=payload.chest_icon_url,
        chest_skills=payload.chest_skills,
        boots=payload.boots,
        boots_item_id=payload.boots_item_id,
        boots_icon_url=payload.boots_icon_url,
        boots_skills=payload.boots_skills,
        cape=payload.cape,
        food=payload.food,
        potion=payload.potion,
        recommended_mount=payload.recommended_mount,
        required_level=payload.required_level,
        description=payload.description,
        active=payload.active,
    )
    db.add(build)
    db.flush()
    affected_event_ids = sync_build_links(
        db,
        build,
        payload.allowed_mounts,
        normalize_event_slots(payload.event_slots, payload.event_ids),
    )
    db.flush()
    sync_active_events_with_discord(db, affected_event_ids)
    db.commit()
    db.refresh(build)
    return serialize_build(build, db)


@router.get('/', response_model=List[BuildRead])
def list_builds(
    guild_id: int | None = None,
    event_id: int | None = None,
    content_type: str | None = None,
    role: str | None = None,
    active: bool | None = None,
    player_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Build)
    if guild_id is not None:
        query = query.filter(Build.guild_id == guild_id)
    if content_type:
        query = query.filter(Build.build_type.ilike(content_type))
    if role:
        query = query.filter(Build.role.ilike(role))
    if active is not None:
        query = query.filter(Build.active == active)
    if event_id is not None:
        query = query.join(EventBuild).filter(EventBuild.event_id == event_id)
    if player_id is not None:
        query = query.join(PlayerBuildApproval).filter(
            PlayerBuildApproval.player_id == player_id,
            PlayerBuildApproval.approved == True,
        )
    return [serialize_build(build, db) for build in query.order_by(Build.name).all()]


@router.put('/{build_id}', response_model=BuildRead)
def update_build(build_id: int, payload: BuildUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    build = db.get(Build, build_id)
    if not build:
        raise HTTPException(status_code=404, detail='Build not found')
    if not build.active:
        raise HTTPException(status_code=403, detail='Build is inactive')

    payload_data = payload.model_dump(exclude_unset=True)
    link_fields = {'allowed_mounts', 'event_ids', 'event_slots'}
    content_fields = set(payload_data) - link_fields
    if content_fields and not is_staff_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Staff access required')
    if not content_fields and not is_event_manager_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Event manager access required')

    update_data = payload.model_dump(exclude_unset=True, exclude=link_fields)
    for field, value in update_data.items():
        setattr(build, field, value)

    if payload.allowed_mounts is not None or payload.event_ids is not None or payload.event_slots is not None:
        current_event_slots = [
            BuildEventSlot(event_id=link.event_id, max_slots=link.max_slots or 1)
            for link in build.event_links
        ]
        affected_event_ids = sync_build_links(
            db,
            build,
            payload.allowed_mounts if payload.allowed_mounts is not None else [mount.mount_name for mount in build.mounts],
            normalize_event_slots(
                payload.event_slots if payload.event_slots is not None else current_event_slots,
                payload.event_ids if payload.event_ids is not None else [link.event_id for link in build.event_links],
            ),
        )
        db.flush()
        sync_active_events_with_discord(db, affected_event_ids)

    db.commit()
    db.refresh(build)
    return serialize_build(build, db)


@router.delete('/{build_id}', response_model=BuildRead)
def delete_build(build_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    build = db.get(Build, build_id)
    if not build:
        raise HTTPException(status_code=404, detail='Build not found')
    build.active = False
    db.commit()
    db.refresh(build)
    return serialize_build(build, db)


@router.post('/{build_id}/reactivate', response_model=BuildRead)
def reactivate_build(build_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    build = db.get(Build, build_id)
    if not build:
        raise HTTPException(status_code=404, detail='Build not found')
    build.active = True
    db.commit()
    db.refresh(build)
    return serialize_build(build, db)


@router.post('/approvals', response_model=PlayerBuildApprovalRead, status_code=status.HTTP_201_CREATED)
def approve_player_build(payload: PlayerBuildApprovalCreate, db: Session = Depends(get_db), current_user: User = Depends(require_staff)):
    player = db.get(User, payload.player_id)
    build = db.get(Build, payload.build_id)
    if not player or not build:
        raise HTTPException(status_code=404, detail='Player or build not found')
    if not player.active:
        raise HTTPException(status_code=403, detail='Player is inactive')

    caller = normalize_caller(payload.caller, db)
    approval = (
        db.query(PlayerBuildApproval)
        .filter(
            PlayerBuildApproval.player_id == payload.player_id,
            PlayerBuildApproval.build_id == payload.build_id,
            PlayerBuildApproval.caller == caller,
        )
        .first()
    )
    if approval:
        approval.approved = payload.approved
        approval.notes = payload.notes
        approval.caller = caller
    else:
        data = payload.model_dump()
        data['caller'] = caller
        approval = PlayerBuildApproval(**data)
        db.add(approval)

    db.commit()
    db.refresh(approval)
    return PlayerBuildApprovalRead(
        id=approval.id,
        guild_id=approval.guild_id,
        player_id=approval.player_id,
        build_id=approval.build_id,
        caller=approval.caller,
        approved=approval.approved,
        notes=approval.notes,
        build_name=build.name,
        player_nick=player.albion_nick,
    )


@router.get('/approvals', response_model=List[PlayerBuildApprovalRead])
def list_approvals(db: Session = Depends(get_db)):
    approvals = db.query(PlayerBuildApproval).all()
    return [
        PlayerBuildApprovalRead(
            id=approval.id,
            guild_id=approval.guild_id,
            player_id=approval.player_id,
            build_id=approval.build_id,
            caller=approval.caller,
            approved=approval.approved,
            notes=approval.notes,
            build_name=approval.build.name if approval.build else None,
            player_nick=approval.player.albion_nick if approval.player else None,
        )
        for approval in approvals
    ]


@router.get('/available', response_model=AvailableBuildsResponse)
def available_builds(
    nick: str = Query(..., min_length=1),
    event_id: int = Query(...),
    db: Session = Depends(get_db),
):
    normalized_nick = nick.strip().lower()
    player = db.query(User).filter(func.lower(func.trim(User.albion_nick)) == normalized_nick).first()
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    if not player.active:
        raise HTTPException(status_code=403, detail='Player is inactive')

    event = db.get(ZvZEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    open_event_links = []
    for link in event.build_links:
        if not link.build or not build_matches_event(link.build, event):
            continue
        taken = db.query(CheckIn).filter(CheckIn.event_id == event.id, CheckIn.build_id == link.build_id).count()
        if taken < max(link.max_slots or 1, 1):
            open_event_links.append(link)

    event_build_ids = [link.build_id for link in open_event_links]
    event_caller = normalize_caller(event.caller, db)
    approved_build_ids = []
    for approval in player.build_approvals:
        if not approval.approved or approval.build_id not in event_build_ids:
            continue
        if event_caller and approval.caller != event_caller:
            continue
        if not event_caller and approval.caller:
            continue
        approved_build_ids.append(approval.build_id)

    builds = (
        db.query(Build)
        .filter(
            Build.active == True,
            Build.id.in_(approved_build_ids),
        )
        .order_by(Build.name)
        .all()
        if approved_build_ids
        else []
    )

    return AvailableBuildsResponse(player=player, builds=[serialize_build(build, db) for build in builds])
