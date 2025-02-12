from typing import Protocol

from app.apps.user.dto.user import UserDto
from app.tools.repository.sql_alchemy.sql_alchemy import SQLAlchemyRepository
from model.user import User


class UserRepositoryProtocol(Protocol):
    async def find_user(self, tg_id: int) -> UserDto | None:
        """Возвращает пользователя по tg_id"""
        pass


class SQLAlchemyUserRepositoryV1(SQLAlchemyRepository):
    model = User

    async def find_user(self, tg_id: int) -> UserDto | None:
        """Возвращает пользователя по tg_id"""
        if not tg_id:
            return None
        user = await self.find(tg_id=tg_id)
        if not user:
            return None
        return UserDto(
            id=user.id,
            tg_id=user.tg_id,
            tg_url=user.tg_url,
            first_name=user.first_name,
            last_name=user.last_name,
            tg_username=user.tg_username,
            coins=user.coins,
            is_active=user.is_active,
            is_admin=user.is_admin,
            subscription=user.subscription,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
