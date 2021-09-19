from collections import defaultdict, deque
from typing import Dict, Tuple

import aioredis


class KeyGenerator:
    cache_key: str = 'tle_cache'


class RedisCache:
    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def update(self, entries: Tuple[Dict[str, str]]):
        entries_to_update = await self._redis.hgetall(KeyGenerator.cache_key)
        entries = self._latest_entries_by_name(entries)
        entries_to_update.update(entries)
        await self._redis.hmset(KeyGenerator.cache_key, entries_to_update)

    async def retrieve(self) -> Dict[str, str]:
        return await self._redis.hgetall(KeyGenerator.cache_key)

    @staticmethod
    def _latest_entries_by_name(entries: Tuple[Dict[str, str]]) -> Dict[str, str]:
        grouped = defaultdict(deque)

        for entry in entries:
            object_name, = entry.keys()
            tle_value, = entry.values()
            grouped[object_name].append(tle_value)

        return {name: entries.pop() for name, entries in grouped.items()}
