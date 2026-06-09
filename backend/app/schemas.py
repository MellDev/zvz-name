from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class GuildBase(BaseModel):
    name: str
    discord_server_id: Optional[str] = None
    plan: Optional[str] = 'free'
    active: bool = True

class GuildCreate(GuildBase):
    pass

class GuildRead(GuildBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    discord_id: str
    discord_name: str
    albion_nick: str
    main_weapon_1: Optional[str] = None
    main_weapon_2: Optional[str] = None

class UserCreate(UserBase):
    guild_id: int

class UserUpdate(BaseModel):
    albion_nick: Optional[str] = None
    main_weapon_1: Optional[str] = None
    main_weapon_2: Optional[str] = None

class UserRead(UserBase):
    id: int
    guild_id: int
    weapon_1_approved: bool
    weapon_2_approved: bool
    role: str
    is_staff: bool
    rating: int
    participations: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ZvZEventBase(BaseModel):
    title: str
    event_date: datetime
    status: str = 'draft'

class ZvZEventCreate(ZvZEventBase):
    guild_id: int
    created_by: Optional[int] = None

class ZvZEventRead(ZvZEventBase):
    id: int
    guild_id: int
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class CheckInCreate(BaseModel):
    guild_id: int
    event_id: int
    user_id: int
    weapon_selected: str
    mount_selected: str
    approved: bool = False
    notes: Optional[str] = None

class CheckInRead(CheckInCreate):
    id: int
    checkin_time: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenPayload(BaseModel):
    sub: str

class DashboardPlayerMetrics(BaseModel):
    total_participations: int
    rating: float
    top_weapons: List[str] = []

class DashboardStaffResponse(BaseModel):
    total_players: int
    total_events: int
    total_checkins: int
    player_metrics: List[DashboardPlayerMetrics] = []
