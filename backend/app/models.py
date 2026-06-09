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
    rating = Column(Float, default=7.0)
    participations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    guild = relationship('Guild', back_populates='users')
    checkins = relationship('CheckIn', back_populates='user')
    ratings = relationship('PlayerRating', back_populates='player')

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

class ZvZEvent(Base):
    __tablename__ = 'zvz_events'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    title = Column(String(180), nullable=False)
    event_date = Column(DateTime, nullable=False)
    status = Column(String(50), default='draft')
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guild = relationship('Guild', back_populates='events')
    checkins = relationship('CheckIn', back_populates='event')

class CheckIn(Base):
    __tablename__ = 'checkins'

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('zvz_events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    weapon_selected = Column(String(120), nullable=False)
    mount_selected = Column(String(120), nullable=False)
    checkin_time = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    user = relationship('User', back_populates='checkins')
    event = relationship('ZvZEvent', back_populates='checkins')

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
