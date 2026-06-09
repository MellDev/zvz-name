from fastapi import APIRouter

from .auth import router as auth_router
from .guilds import router as guilds_router
from .players import router as players_router
from .events import router as events_router
from .checkins import router as checkins_router
from .dashboard import router as dashboard_router
from .weapons import router as weapons_router
from .mounts import router as mounts_router

router = APIRouter(prefix='/api')
router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(guilds_router, prefix='/guilds', tags=['guilds'])
router.include_router(players_router, prefix='/players', tags=['players'])
router.include_router(events_router, prefix='/events', tags=['events'])
router.include_router(checkins_router, prefix='/checkins', tags=['checkins'])
router.include_router(dashboard_router, prefix='/dashboard', tags=['dashboard'])
router.include_router(weapons_router, prefix='/weapons', tags=['weapons'])
router.include_router(mounts_router, prefix='/mounts', tags=['mounts'])
