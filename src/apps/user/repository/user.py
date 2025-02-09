from typing import Protocol

from apps.interview.repository.sql_alchemy import SQLAlchemyRepository
from apps.user.dto.user import UserDto


class UserRepositoryProtocol(Protocol):
    async def find_user(self, tg_id: int) -> UserDto | None:
        """Возвращает пользователя по tg_id"""
        pass


class UserRepositoryV1(SQLAlchemyRepository):
    model = None

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
