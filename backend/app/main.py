from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.routes import router
from .core.config import settings
from .db.session import engine
from .db.base import Base

app = FastAPI(
    title='ZvZ Name API',
    description='API para gerenciamento de guildas, jogadores, check-ins e eventos de ZvZ',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.BACKEND_CORS_ORIGINS == ['*'] else settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

@app.get('/')
def health_check() -> dict:
    return {'status': 'ok', 'service': 'zvz-name'}
