from sqlalchemy.exc import IntegrityError

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models import Guild, Mount, Weapon, User

DEFAULT_WEAPONS = [
    ('Shadowcaller', 'caster'),
    ('Realm Breaker', 'melee'),
    ('Permafrost', 'mage'),
    ('Great Hammer', 'melee'),
    ('Rift Hunter', 'caster'),
]

DEFAULT_MOUNTS = [
    'Frost Ram',
    'Direboar',
    'Spectral Bat',
    'Fiery Warhorse',
    'Swiftclaw',
]


def seed():
    session = SessionLocal()
    try:
        default_guild = Guild(name='Principal', discord_server_id=None, plan='free', active=True)
        session.add(default_guild)
        session.flush()

        admin = User(
            guild_id=default_guild.id,
            discord_id='admin',
            discord_name='admin',
            albion_nick='Admin',
            role='admin',
            is_staff=True,
            weapon_1_approved=True,
            weapon_2_approved=True,
            rating=10.0,
        )
        session.add(admin)

        for weapon_name, category in DEFAULT_WEAPONS:
            session.merge(Weapon(weapon_name=weapon_name, weapon_category=category, active=True))

        for mount_name in DEFAULT_MOUNTS:
            session.merge(Mount(mount_name=mount_name, active=True))

        session.commit()
        print('Seed completed successfully.')
    except IntegrityError:
        session.rollback()
        print('Seed data already exists or constraint issue encountered.')
    finally:
        session.close()


if __name__ == '__main__':
    seed()
