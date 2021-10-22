from typing import Dict, List
import logging

from aioredis import Redis

from server.storage.satellite import group_latest_by_name, satellites_from_cached, satellites_to_cached

logger = logging.getLogger(__name__)


class KeyGenerator:
    satellites_key: str = 'satellites_cache'


async def update_satellites(redis: Redis, satellites: List[Dict[str, str]]):
    satellites = satellites_to_cached(satellites)
    satellites = group_latest_by_name(satellites)

    satellites_to_update = await redis.hgetall(KeyGenerator.satellites_key)

    satellites_to_update.update(satellites)

    await redis.hset(KeyGenerator.satellites_key, satellites_to_update)


async def clear_satellites(redis: Redis):
    await redis.delete(KeyGenerator.satellites_key)


async def get_satellites(redis: Redis) -> List[Dict[str, str]]:
    satellites_cached = await redis.hgetall(KeyGenerator.satellites_key)
    return satellites_from_cached(satellites_cached)


async def is_empty(redis: Redis) -> bool:
    return bool(await get_satellites(redis))
