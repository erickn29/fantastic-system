import json

from typing import Protocol

from apps.dependencies.protocol.cache_service import CacheServiceProtocol


class UserRepositoryProtocol(Protocol):
    def __init__(self, cache_service: CacheServiceProtocol):
        pass

    async def get_stack(self, tg_id: int) -> list[str] | None:
        """Возвращает стек технологий пользователя"""
        pass


class UserRepositoryV1:

    def __init__(self, cache_service: CacheServiceProtocol):
        self._cache_service = cache_service

    async def get_stack(self, tg_id: int) -> list[str] | None:
        """Возвращает стек технологий пользователя"""
        if not tg_id:
            return None
        key = f"tg_user_id:{tg_id}:stack"
        user_stack = await self._cache_service.get(key)
        if not user_stack:
            return None
        stack: list[str] = json.loads(user_stack)
        return stack
