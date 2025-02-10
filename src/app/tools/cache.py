import json

from typing import Protocol
from uuid import UUID

import redis.asyncio as redis

from redis import RedisError

from app.apps.user.dto.user import UserDto
from core.config import config


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

    async def set_stack(self, user_id: UUID, stack: list[str]):
        """Сохраняет стек технологий пользователя"""
        pass

    async def get_stack(self, user_id: UUID) -> list[str] | None:
        """Возвращает стек технологий пользователя"""
        pass

    async def set_user_last_question(self, user_id: UUID, question_id: int):
        """Сохраняет последний вопрос пользователя"""
        pass

    async def get_user_last_question(self, user_id: UUID) -> int | None:
        """Возвращает последний вопрос пользователя"""
        pass


class Cache:
    def __init__(
        self, host=config.redis.HOST, port=config.redis.PORT, db=config.redis.DB
    ):
        self.host = host
        self.port = port
        self.db = db
        self.connection_pool = redis.ConnectionPool(
            host=self.host, port=self.port, db=self.db
        )
        self.redis_cache = redis.StrictRedis(connection_pool=self.connection_pool)

    async def set(self, key: str, value: str, expire: int = 60):
        try:
            await self.redis_cache.set(key, value, expire)
        except RedisError:
            return

    async def get(self, key, decode="utf-8"):
        res = await self.redis_cache.get(key)
        if res:
            return res.decode(decode)
        return res

    async def delete(self, key: str):
        await self.redis_cache.delete(key)

    async def set_user(self, user: UserDto):
        user_dict = user.model_dump()
        user_dict["created_at"] = user_dict["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        user_dict["updated_at"] = user_dict["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        if user.subscription:
            user_dict["subscription"] = user_dict["subscription"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        await self.set(
            f"user:{str(user.tg_id)}",
            json.dumps(user_dict),
            60 * 60 * 24 * 7,
        )

    async def get_user(self, key: str) -> UserDto | None:
        res = await self.get(key)
        if res:
            user = UserDto.model_validate(json.loads(res))
            return user
        return None

    async def set_stack(self, user_id: UUID, stack: list[str]):
        """Сохраняет стек технологий пользователя"""
        if not user_id or not stack:
            return
        key = f"user_id:{user_id}:stack"
        await self.set(key, json.dumps(stack), 60 * 60 * 24 * 365)

    async def get_stack(self, user_id: UUID) -> list[str] | None:
        """Возвращает стек технологий пользователя"""
        if not user_id:
            return None
        key = f"user_id:{user_id}:stack"
        user_stack = await self.get(key)
        if not user_stack:
            return None
        stack: list[str] = json.loads(user_stack)
        return stack

    async def set_user_last_question(self, user_id: UUID, question_id: int):
        """Сохраняет последний вопрос пользователя"""
        if not user_id or not question_id:
            return
        key = f"user_id:{user_id}:last_question"
        ttl = 60 * 60 * 24 * 7 * 55
        await self.set(key, str(question_id), ttl)

    async def get_user_last_question(self, user_id: UUID) -> int | None:
        """Возвращает последний вопрос пользователя"""
        if not user_id:
            return None
        key = f"user_id:{user_id}:last_question"
        if question_id := await self.get(key):
            return int(question_id)
        return None


cache = Cache()
