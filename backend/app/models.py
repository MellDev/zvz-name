from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db.base import Base

class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    discord_server_id = Column(String(64), nullable=True)
    plan = Column(String(50), default='free')
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship('User', back_populates='guild')
    events = relationship('ZvZEvent', back_populates='guild')

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    discord_id = Column(String(64), nullable=False, unique=True)
    discord_name = Column(String(120), nullable=False)
    albion_nick = Column(String(120), nullable=False)
    main_weapon_1 = Column(String(120), nullable=True)
    main_weapon_2 = Column(String(120), nullable=True)
    weapon_1_approved = Column(Boolean, default=False)
    weapon_2_approved = Column(Boolean, default=False)
    role = Column(String(50), default='player')
    is_staff = Column(Boolean, default=False)
    is_leader = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    rating = Column(Float, default=7.0)
    participations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    guild = relationship('Guild', back_populates='users')
    checkins = relationship('CheckIn', back_populates='user')
    ratings = relationship('PlayerRating', foreign_keys='PlayerRating.player_id', back_populates='player')
    build_approvals = relationship('PlayerBuildApproval', back_populates='player')
    build_requests = relationship('BuildRequest', foreign_keys='BuildRequest.player_id', back_populates='player')

class Weapon(Base):
    __tablename__ = 'weapons'

    id = Column(Integer, primary_key=True, index=True)
    weapon_name = Column(String(120), nullable=False, unique=True)
    weapon_category = Column(String(80), nullable=False)
    active = Column(Boolean, default=True)

class Mount(Base):
    __tablename__ = 'mounts'

    id = Column(Integer, primary_key=True, index=True)
    mount_name = Column(String(120), nullable=False, unique=True)
    active = Column(Boolean, default=True)

class Build(Base):
    __tablename__ = 'builds'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    name = Column(String(140), nullable=False)
    build_type = Column(String(80), nullable=False, default='CTA')
    role = Column(String(50), nullable=False, default='DPS')
    weapon_name = Column(String(120), nullable=False)
    weapon_item_id = Column(String(120), nullable=True)
    weapon_icon_url = Column(String(500), nullable=True)
    offhand = Column(String(120), nullable=True)
    offhand_item_id = Column(String(120), nullable=True)
    offhand_icon_url = Column(String(500), nullable=True)
    helmet = Column(String(120), nullable=True)
    helmet_item_id = Column(String(120), nullable=True)
    helmet_icon_url = Column(String(500), nullable=True)
    chest = Column(String(120), nullable=True)
    chest_item_id = Column(String(120), nullable=True)
    chest_icon_url = Column(String(500), nullable=True)
    boots = Column(String(120), nullable=True)
    boots_item_id = Column(String(120), nullable=True)
    boots_icon_url = Column(String(500), nullable=True)
    cape = Column(String(120), nullable=True)
    food = Column(String(120), nullable=True)
    potion = Column(String(120), nullable=True)
    recommended_mount = Column(String(120), nullable=True)
    required_level = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event_links = relationship('EventBuild', back_populates='build')
    player_approvals = relationship('PlayerBuildApproval', back_populates='build')
    mounts = relationship('BuildMount', back_populates='build', cascade='all, delete-orphan')

class BuildMount(Base):
    __tablename__ = 'build_mounts'

    id = Column(Integer, primary_key=True, index=True)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    mount_name = Column(String(120), nullable=False)

    build = relationship('Build', back_populates='mounts')

class EventBuild(Base):
    __tablename__ = 'event_builds'

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('zvz_events.id'), nullable=False)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    max_slots = Column(Integer, nullable=False, default=1)

    event = relationship('ZvZEvent', back_populates='build_links')
    build = relationship('Build', back_populates='event_links')

class PlayerBuildApproval(Base):
    __tablename__ = 'player_build_approvals'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    approved = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    player = relationship('User', back_populates='build_approvals')
    build = relationship('Build', back_populates='player_approvals')

class ZvZEvent(Base):
    __tablename__ = 'zvz_events'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    title = Column(String(180), nullable=False)
    content_type = Column(String(80), nullable=False, default='ZvZ')
    event_date = Column(DateTime, nullable=False)
    status = Column(String(50), default='draft')
    mount_gallop_requirement = Column(Integer, nullable=False, default=120)
    mount_requirement_note = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guild = relationship('Guild', back_populates='events')
    checkins = relationship('CheckIn', back_populates='event')
    build_links = relationship('EventBuild', back_populates='event')

class CheckIn(Base):
    __tablename__ = 'checkins'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('zvz_events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=True)
    weapon_selected = Column(String(120), nullable=False)
    mount_selected = Column(String(120), nullable=False)
    player_nick_snapshot = Column(String(120), nullable=True)
    checkin_time = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    user = relationship('User', back_populates='checkins')
    event = relationship('ZvZEvent', back_populates='checkins')
    build = relationship('Build')

class BuildRequest(Base):
    __tablename__ = 'build_requests'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('zvz_events.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)
    status = Column(String(30), nullable=False, default='pending')
    notes = Column(Text, nullable=True)
    weapon_power = Column(Integer, nullable=True)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship('ZvZEvent')
    player = relationship('User', foreign_keys=[player_id], back_populates='build_requests')
    leader = relationship('User', foreign_keys=[leader_id])
    build = relationship('Build')

class PlayerRating(Base):
    __tablename__ = 'player_ratings'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    player = relationship('User', foreign_keys=[player_id], back_populates='ratings')
