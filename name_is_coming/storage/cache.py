from typing import Dict, Tuple
from abc import ABC, abstractmethod

import aioredis
import redis

from name_is_coming.tle import group_latest_by_name


class KeyGenerator:
    cache_key: str = 'tle_cache'


class Cache(ABC):
    @abstractmethod
    def update(self, entries: Tuple[Dict[str, str]]):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def retrieve(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass


class RedisCache(Cache):
    def __init__(self, redis_url: str):
        super().__init__()
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def update(self, entries: Tuple[Dict[str, str]]):
        entries_to_update = await self._redis.hgetall(KeyGenerator.cache_key)

        entries = group_latest_by_name(entries)
        entries_to_update.update(entries)

        await self._redis.hmset(KeyGenerator.cache_key, entries_to_update)

    async def clear(self):
        await self._redis.delete(KeyGenerator.cache_key)

    async def retrieve(self) -> Dict[str, str]:
        return await self._redis.hgetall(KeyGenerator.cache_key)

    async def is_empty(self) -> bool:
        return bool(await self.retrieve())


class RedisCacheSync(Cache):
    def __init__(self, redis_url: str):
        super().__init__()
        self._redis = redis.from_url(redis_url, decode_responses=True)

    def update(self, entries: Tuple[Dict[str, str]]):
        entries_to_update = self._redis.hgetall(KeyGenerator.cache_key)

        entries = group_latest_by_name(entries)
        entries_to_update.update(entries)

        self._redis.hmset(KeyGenerator.cache_key, entries_to_update)

    def clear(self):
        self._redis.delete(KeyGenerator.cache_key)

    def retrieve(self) -> Dict[str, str]:
        return self._redis.hgetall(KeyGenerator.cache_key)

    def is_empty(self) -> bool:
        return bool(self.retrieve())
