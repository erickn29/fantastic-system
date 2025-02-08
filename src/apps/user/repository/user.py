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
        pass

    async def get_stack(self, tg_id: int) -> list[str] | None:
        """Возвращает стек технологий пользователя"""
        pass
