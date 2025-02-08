from typing import Protocol

from apps.user.dto.user import UserDto


class CacheServiceProtocol(Protocol):
    def __init__(self, host: str, port: int, db: int):
        pass

    async def set(self, key: str, value: str, expire: int = 60):
        """Устанавливает значение в кэш по ключу"""
        pass

    async def get(self, key, decode="utf-8"):
        """Получает значение из кэша по ключу"""
        pass

    async def delete(self, key: str):
        """Удаляет значение из кэша по ключу"""
        pass

    async def set_user(self, schema: UserDto):
        """Устанавливает значение в кэш по ключу"""
        pass

    async def get_user(self, key: str) -> UserDto | None:
        """Получает значение из кэша по ключу"""
        pass
