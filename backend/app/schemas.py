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
    discord_id: Optional[str] = None
    discord_name: Optional[str] = None
    albion_nick: str
    main_weapon_1: Optional[str] = None
    main_weapon_2: Optional[str] = None

class UserCreate(UserBase):
    guild_id: int
    active: bool = True

class UserUpdate(BaseModel):
    albion_nick: Optional[str] = None
    main_weapon_1: Optional[str] = None
    main_weapon_2: Optional[str] = None
    weapon_1_approved: Optional[bool] = None
    weapon_2_approved: Optional[bool] = None
    role: Optional[str] = None
    is_staff: Optional[bool] = None
    is_leader: Optional[bool] = None
    active: Optional[bool] = None
    rating: Optional[float] = None

class UserRead(UserBase):
    id: int
    guild_id: int
    weapon_1_approved: bool
    weapon_2_approved: bool
    role: str
    is_staff: bool
    is_leader: bool
    active: bool
    rating: float
    participations: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ZvZEventBase(BaseModel):
    title: str
    content_type: str = 'ZvZ'
    caller: Optional[str] = None
    event_date: datetime
    status: str = 'draft'
    mount_gallop_requirement: int = 120
    mount_requirement_note: Optional[str] = None
    discord_channel_id: Optional[str] = None
    discord_message_id: Optional[str] = None
    discord_message_url: Optional[str] = None
    discord_message_extra: Optional[str] = None
    discord_last_sync_at: Optional[datetime] = None

class ZvZEventCreate(ZvZEventBase):
    guild_id: int
    created_by: Optional[int] = None

class ZvZEventUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    caller: Optional[str] = None
    event_date: Optional[datetime] = None
    status: Optional[str] = None
    mount_gallop_requirement: Optional[int] = None
    mount_requirement_note: Optional[str] = None
    discord_channel_id: Optional[str] = None
    discord_message_id: Optional[str] = None
    discord_message_url: Optional[str] = None
    discord_message_extra: Optional[str] = None
    discord_last_sync_at: Optional[datetime] = None

class ZvZEventDuplicate(BaseModel):
    title: Optional[str] = None
    event_date: Optional[datetime] = None
    status: str = 'draft'

class ZvZEventRead(ZvZEventBase):
    id: int
    guild_id: int
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DiscordEventPreview(BaseModel):
    event_id: int
    content: str
    message_url: Optional[str] = None
    last_sync_at: Optional[datetime] = None

class CheckInCreate(BaseModel):
    guild_id: int
    event_id: int
    user_id: int
    build_id: Optional[int] = None
    weapon_selected: str
    mount_selected: str
    approved: bool = False
    notes: Optional[str] = None

class CheckInRead(CheckInCreate):
    id: int
    checkin_time: datetime
    player_nick: Optional[str] = None
    player_nick_snapshot: Optional[str] = None
    event_title: Optional[str] = None
    build_name: Optional[str] = None
    build_role: Optional[str] = None

    class Config:
        from_attributes = True

class CheckInUpdate(BaseModel):
    approved: Optional[bool] = None
    notes: Optional[str] = None

class BuildRequestCreate(BaseModel):
    event_id: int
    build_id: int
    player_nick: Optional[str] = None
    notes: Optional[str] = None
    weapon_power: Optional[int] = None

class BuildRequestUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    weapon_power: Optional[int] = None

class BuildRequestRead(BaseModel):
    id: int
    guild_id: int
    event_id: int
    player_id: int
    build_id: int
    status: str
    notes: Optional[str] = None
    weapon_power: Optional[int] = None
    leader_id: Optional[int] = None
    created_at: datetime
    decided_at: Optional[datetime] = None
    event_title: Optional[str] = None
    event_created_by: Optional[int] = None
    player_nick: Optional[str] = None
    build_name: Optional[str] = None
    build_role: Optional[str] = None
    build_icon_url: Optional[str] = None

    class Config:
        from_attributes = True

class BuildEventSlot(BaseModel):
    event_id: int
    max_slots: int = 1

class BuildEventSlotRead(BuildEventSlot):
    taken_slots: int = 0
    remaining_slots: int = 1

class BuildCreate(BaseModel):
    guild_id: int
    name: str
    build_type: str = 'CTA'
    role: str = 'DPS'
    weapon_name: str
    weapon_item_id: Optional[str] = None
    weapon_icon_url: Optional[str] = None
    weapon_skills: Optional[str] = None
    offhand: Optional[str] = None
    offhand_item_id: Optional[str] = None
    offhand_icon_url: Optional[str] = None
    helmet: Optional[str] = None
    helmet_item_id: Optional[str] = None
    helmet_icon_url: Optional[str] = None
    helmet_skills: Optional[str] = None
    chest: Optional[str] = None
    chest_item_id: Optional[str] = None
    chest_icon_url: Optional[str] = None
    chest_skills: Optional[str] = None
    boots: Optional[str] = None
    boots_item_id: Optional[str] = None
    boots_icon_url: Optional[str] = None
    boots_skills: Optional[str] = None
    cape: Optional[str] = None
    food: Optional[str] = None
    potion: Optional[str] = None
    recommended_mount: Optional[str] = None
    required_level: Optional[int] = None
    description: Optional[str] = None
    active: bool = True
    allowed_mounts: List[str] = []
    event_ids: List[int] = []
    event_slots: List[BuildEventSlot] = []

class BuildUpdate(BaseModel):
    name: Optional[str] = None
    build_type: Optional[str] = None
    role: Optional[str] = None
    weapon_name: Optional[str] = None
    weapon_item_id: Optional[str] = None
    weapon_icon_url: Optional[str] = None
    weapon_skills: Optional[str] = None
    offhand: Optional[str] = None
    offhand_item_id: Optional[str] = None
    offhand_icon_url: Optional[str] = None
    helmet: Optional[str] = None
    helmet_item_id: Optional[str] = None
    helmet_icon_url: Optional[str] = None
    helmet_skills: Optional[str] = None
    chest: Optional[str] = None
    chest_item_id: Optional[str] = None
    chest_icon_url: Optional[str] = None
    chest_skills: Optional[str] = None
    boots: Optional[str] = None
    boots_item_id: Optional[str] = None
    boots_icon_url: Optional[str] = None
    boots_skills: Optional[str] = None
    cape: Optional[str] = None
    food: Optional[str] = None
    potion: Optional[str] = None
    recommended_mount: Optional[str] = None
    required_level: Optional[int] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    allowed_mounts: Optional[List[str]] = None
    event_ids: Optional[List[int]] = None
    event_slots: Optional[List[BuildEventSlot]] = None

class BuildRead(BaseModel):
    id: int
    guild_id: int
    name: str
    build_type: str
    role: str
    weapon_name: str
    weapon_item_id: Optional[str]
    weapon_icon_url: Optional[str]
    weapon_skills: Optional[str]
    offhand: Optional[str]
    offhand_item_id: Optional[str]
    offhand_icon_url: Optional[str]
    helmet: Optional[str]
    helmet_item_id: Optional[str]
    helmet_icon_url: Optional[str]
    helmet_skills: Optional[str]
    chest: Optional[str]
    chest_item_id: Optional[str]
    chest_icon_url: Optional[str]
    chest_skills: Optional[str]
    boots: Optional[str]
    boots_item_id: Optional[str]
    boots_icon_url: Optional[str]
    boots_skills: Optional[str]
    cape: Optional[str]
    food: Optional[str]
    potion: Optional[str]
    recommended_mount: Optional[str]
    required_level: Optional[int]
    description: Optional[str]
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    allowed_mounts: List[str] = []
    event_ids: List[int] = []
    event_slots: List[BuildEventSlotRead] = []

class PlayerBuildApprovalCreate(BaseModel):
    guild_id: int
    player_id: int
    build_id: int
    caller: Optional[str] = None
    approved: bool = True
    notes: Optional[str] = None

class PlayerBuildApprovalRead(PlayerBuildApprovalCreate):
    id: int
    build_name: Optional[str] = None
    player_nick: Optional[str] = None

class AvailableBuildsResponse(BaseModel):
    player: UserRead
    builds: List[BuildRead]

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

class DashboardBucket(BaseModel):
    label: str
    total: int

class DashboardAnalyticsResponse(BaseModel):
    total_participants: int
    by_build: List[DashboardBucket] = []
    by_role: List[DashboardBucket] = []
    by_mount: List[DashboardBucket] = []
    by_content_type: List[DashboardBucket] = []
    top_builds: List[DashboardBucket] = []
    checkins: List[CheckInRead] = []

class DiscordLoginUrl(BaseModel):
    url: str

class DiscordCallbackResponse(Token):
    user: UserRead
