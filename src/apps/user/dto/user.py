from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserDto(BaseModel):
    id: UUID
    tg_id: int
    tg_url: str
    first_name: str
    last_name: str | None
    tg_username: str | None
    coins: int
    is_active: bool
    is_admin: bool
    subscription: datetime | None
    created_at: datetime
    updated_at: datetime


class UserCreateDto(BaseModel):
    id: UUID | None = None
    tg_id: int
    tg_url: str
    first_name: str
    last_name: str | None
    tg_username: str | None
    coins: int
    is_active: bool
    is_admin: bool
    subscription: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
