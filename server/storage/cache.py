__all__ = (
    'update',
    'clear',
    'retrieve',
    'is_empty'
)

from typing import Dict, Tuple

from aioredis import Redis

from server.tle import group_latest_by_name


class KeyGenerator:
    cache_key: str = 'tle_cache'


async def update(r: Redis, entries: Tuple[Dict[str, str]]):
    entries_to_update = await r.hgetall(KeyGenerator.cache_key)

    entries = group_latest_by_name(entries)
    entries_to_update.update(entries)

    await r.hset(KeyGenerator.cache_key, mapping=entries_to_update)


async def clear(r: Redis):
    await r.delete(KeyGenerator.cache_key)


async def retrieve(r: Redis) -> Dict[str, str]:
    return await r.hgetall(KeyGenerator.cache_key)


async def is_empty(r: Redis) -> bool:
    return bool(await retrieve(r))
