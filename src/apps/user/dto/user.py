from datetime import datetime

from pydantic import BaseModel


class UserDto(BaseModel):
    id: int
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
