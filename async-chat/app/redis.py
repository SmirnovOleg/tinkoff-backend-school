from typing import Any, Optional

import aioredis
from aioredis import Redis

from app.config import settings


class RedisCache:
    def __init__(self, pool: Optional[Redis] = None) -> None:
        self.redis_cache: Any = pool

    async def init_cache(self) -> None:
        self.redis_cache = self.redis_cache or (
            await aioredis.create_redis_pool(settings.redis_url)
        )

    async def set(self, key: Any, value: Any) -> Any:
        return await self.redis_cache.set(key, value)

    async def get(self, key: Any) -> Any:
        return await self.redis_cache.get(key)

    async def subscribe(self, channel: str) -> Any:
        res = await self.redis_cache.subscribe(channel)
        return res[0]

    async def publish(self, channel: str, message: str) -> None:
        await self.redis_cache.publish(channel, message)

    async def rpush(self, list_name: str, message: str) -> None:
        await self.redis_cache.rpush(list_name, message)

    async def ltrim(self, list_name: str, start: Any, stop: Any) -> None:
        await self.redis_cache.ltrim(list_name, start, stop)

    async def lrange(self, list_name: str, start: Any, stop: Any) -> Any:
        return await self.redis_cache.lrange(list_name, start, stop)

    async def close(self) -> None:
        self.redis_cache.close()
        await self.redis_cache.wait_closed()


redis = RedisCache()
