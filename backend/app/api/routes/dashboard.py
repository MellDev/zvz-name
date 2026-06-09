from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import CheckIn, User, ZvZEvent
from app.schemas import DashboardStaffResponse, DashboardPlayerMetrics

router = APIRouter()

@router.get('/staff', response_model=DashboardStaffResponse)
def staff_dashboard(db: Session = Depends(get_db)):
    total_players = db.query(User).count()
    total_events = db.query(ZvZEvent).count()
    total_checkins = db.query(CheckIn).count()
    player_metrics = []

    players = db.query(
        User.id,
        User.albion_nick,
        func.sum(User.participations).label('total_participations'),
        func.avg(User.rating).label('rating'),
    ).group_by(User.id).all()

    for player in players:
        player_metrics.append(DashboardPlayerMetrics(
            total_participations=player.total_participations or 0,
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
