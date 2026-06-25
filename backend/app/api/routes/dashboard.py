from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import Counter

from app.deps import get_db
from app.models import Build, CheckIn, User, ZvZEvent
from app.schemas import DashboardAnalyticsResponse, DashboardBucket, DashboardStaffResponse, DashboardPlayerMetrics
from app.api.routes.checkins import serialize_checkin

router = APIRouter()

@router.get('/staff', response_model=DashboardStaffResponse)
def staff_dashboard(db: Session = Depends(get_db)):
    total_players = db.query(User).count()
    total_events = db.query(ZvZEvent).count()
    total_checkins = db.query(CheckIn).count()
    player_metrics = []

    players = db.query(User).all()

    for player in players:
        player_metrics.append(DashboardPlayerMetrics(
            total_participations=player.participations or 0,
            rating=float(player.rating or 0),
            top_weapons=[],
        ))

    return DashboardStaffResponse(
        total_players=total_players,
        total_events=total_events,
        total_checkins=total_checkins,
        player_metrics=player_metrics,
    )

@router.get('/player')
def player_dashboard():
    return {'detail': 'Player dashboard endpoint not implemented yet.'}

@router.get('/analytics', response_model=DashboardAnalyticsResponse)
def analytics_dashboard(
    event_id: int | None = None,
    player_id: int | None = None,
    content_type: str | None = None,
    build_id: int | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CheckIn).join(ZvZEvent).outerjoin(Build, CheckIn.build_id == Build.id)
    if event_id is not None:
        query = query.filter(CheckIn.event_id == event_id)
    if player_id is not None:
        query = query.filter(CheckIn.user_id == player_id)
    if content_type:
        query = query.filter(ZvZEvent.content_type.ilike(content_type))
    if build_id is not None:
        query = query.filter(CheckIn.build_id == build_id)
    if role:
        query = query.filter(Build.role.ilike(role))

    checkins = query.order_by(CheckIn.checkin_time.desc()).all()

    def buckets(values: list[str | None]) -> list[DashboardBucket]:
        counts = Counter(value or 'Nao informado' for value in values)
        return [DashboardBucket(label=label, total=total) for label, total in counts.most_common()]

    return DashboardAnalyticsResponse(
        total_participants=len({checkin.user_id for checkin in checkins}),
        by_build=buckets([checkin.build.name if checkin.build else checkin.weapon_selected for checkin in checkins]),
        by_role=buckets([checkin.build.role if checkin.build else None for checkin in checkins]),
        by_mount=buckets([checkin.mount_selected for checkin in checkins]),
        by_content_type=buckets([checkin.event.content_type if checkin.event else None for checkin in checkins]),
        top_builds=buckets([checkin.build.name if checkin.build else checkin.weapon_selected for checkin in checkins])[:5],
        checkins=[serialize_checkin(checkin) for checkin in checkins[:100]],
    )
