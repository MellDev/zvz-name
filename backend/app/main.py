from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.routes import router
from .core.config import settings
from .db.session import engine
from .db.base import Base
import logging
from sqlalchemy import inspect, text

app = FastAPI(
    title='ZvZ Name API',
    description='API para gerenciamento de guildas, jogadores, check-ins e eventos de ZvZ',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

def ensure_runtime_schema() -> None:
    inspector = inspect(engine)
    table_columns = {
        table: {column['name'] for column in inspector.get_columns(table)}
        for table in inspector.get_table_names()
    }
    dialect = engine.dialect.name

    def add_column(table: str, column: str, ddl: str) -> None:
        if column not in table_columns.get(table, set()):
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {ddl}'))

    string_type = 'VARCHAR(120)' if dialect != 'sqlite' else 'VARCHAR(120)'
    add_column('zvz_events', 'content_type', "content_type VARCHAR(80) NOT NULL DEFAULT 'ZvZ'")
    add_column('zvz_events', 'caller', 'caller VARCHAR(30)')
    add_column('zvz_events', 'mount_gallop_requirement', 'mount_gallop_requirement INTEGER NOT NULL DEFAULT 120')
    add_column('zvz_events', 'mount_requirement_note', 'mount_requirement_note TEXT')
    add_column('zvz_events', 'discord_channel_id', 'discord_channel_id VARCHAR(64)')
    add_column('zvz_events', 'discord_message_id', 'discord_message_id VARCHAR(64)')
    add_column('zvz_events', 'discord_message_url', 'discord_message_url VARCHAR(500)')
    add_column('zvz_events', 'discord_message_extra', 'discord_message_extra TEXT')
    add_column('zvz_events', 'discord_last_sync_at', 'discord_last_sync_at TIMESTAMP')
    add_column('users', 'active', 'active BOOLEAN NOT NULL DEFAULT TRUE')
    add_column('users', 'is_leader', 'is_leader BOOLEAN NOT NULL DEFAULT FALSE')
    add_column('checkins', 'build_id', 'build_id INTEGER')
    add_column('checkins', 'player_nick_snapshot', f'player_nick_snapshot {string_type}')
    add_column('builds', 'role', "role VARCHAR(50) NOT NULL DEFAULT 'DPS'")
    add_column('builds', 'weapon_skills', 'weapon_skills VARCHAR(250)')
    add_column('builds', 'offhand', f'offhand {string_type}')
    add_column('builds', 'offhand_item_id', f'offhand_item_id {string_type}')
    add_column('builds', 'offhand_icon_url', 'offhand_icon_url VARCHAR(500)')
    add_column('builds', 'helmet', f'helmet {string_type}')
    add_column('builds', 'helmet_item_id', f'helmet_item_id {string_type}')
    add_column('builds', 'helmet_icon_url', 'helmet_icon_url VARCHAR(500)')
    add_column('builds', 'helmet_skills', 'helmet_skills VARCHAR(250)')
    add_column('builds', 'chest', f'chest {string_type}')
    add_column('builds', 'chest_item_id', f'chest_item_id {string_type}')
    add_column('builds', 'chest_icon_url', 'chest_icon_url VARCHAR(500)')
    add_column('builds', 'chest_skills', 'chest_skills VARCHAR(250)')
    add_column('builds', 'boots', f'boots {string_type}')
    add_column('builds', 'boots_item_id', f'boots_item_id {string_type}')
    add_column('builds', 'boots_icon_url', 'boots_icon_url VARCHAR(500)')
    add_column('builds', 'boots_skills', 'boots_skills VARCHAR(250)')
    add_column('builds', 'cape', f'cape {string_type}')
    add_column('builds', 'food', f'food {string_type}')
    add_column('builds', 'potion', f'potion {string_type}')
    add_column('builds', 'recommended_mount', f'recommended_mount {string_type}')
    add_column('builds', 'required_level', 'required_level INTEGER')
    add_column('builds', 'updated_at', 'updated_at TIMESTAMP')
    add_column('event_builds', 'max_slots', 'max_slots INTEGER NOT NULL DEFAULT 1')
    add_column('player_build_approvals', 'caller', 'caller VARCHAR(30)')
    add_column('build_requests', 'weapon_power', 'weapon_power INTEGER')

    with engine.begin() as conn:
        if dialect == 'postgresql':
            conn.execute(text(
                'UPDATE checkins AS c SET player_nick_snapshot = u.albion_nick '
                'FROM users AS u WHERE c.user_id = u.id AND c.player_nick_snapshot IS NULL'
            ))
        else:
            conn.execute(text(
                'UPDATE checkins SET player_nick_snapshot = '
                '(SELECT users.albion_nick FROM users WHERE users.id = checkins.user_id) '
                'WHERE player_nick_snapshot IS NULL'
            ))
        conn.execute(text(
            "UPDATE users SET is_staff = TRUE, is_leader = TRUE, role = 'dev', active = TRUE "
            "WHERE lower(trim(albion_nick)) IN ('anderson mello', 'anderson') "
            "OR lower(trim(discord_name)) IN ('anderson mello', 'anderson')"
        ))

@app.on_event('startup')
def on_startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        ensure_runtime_schema()
    except Exception as e:
        logging.exception('Database initialization failed on startup; continuing without DB: %s', e)

@app.get('/')
def health_check() -> dict:
    return {'status': 'ok', 'service': 'zvz-name'}
