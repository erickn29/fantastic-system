import json

import redis.asyncio as redis

from redis import RedisError

from apps.user.dto.user import UserDto
from core.config import config


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

    async def set_user(self, schema: UserDto):
        user_dict = schema.model_dump()
        user_dict["created_at"] = user_dict["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        user_dict["updated_at"] = user_dict["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        if schema.subscription:
            user_dict["subscription"] = user_dict["subscription"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        await self.set(
            f"user:{str(schema.tg_id)}",
            json.dumps(user_dict),
            60 * 60 * 24 * 7,
        )

    async def get_user(self, key: str) -> UserDto | None:
        res = await self.get(key)
        if res:
            schema = UserDto.model_validate(json.loads(res))
            schema.id = int(schema.id)
            schema.tg_id = int(schema.tg_id)
            return UserDto.model_validate(schema)
        return None


cache = Cache()
