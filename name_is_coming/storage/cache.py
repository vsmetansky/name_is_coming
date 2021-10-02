from typing import Dict, List

from redis import Redis

from name_is_coming.storage.satellite import group_latest_by_name, satellites_from_cached, satellites_to_cached


class KeyGenerator:
    satellites_key: str = 'satellites_cache'


def update_satellites(redis: Redis, satellites: List[Dict[str, str]]):
    satellites = satellites_to_cached(satellites)

    satellites_to_update = redis.hgetall(KeyGenerator.satellites_key)

    satellites = group_latest_by_name(satellites)
    satellites_to_update.update(satellites)

    redis.hmset(KeyGenerator.satellites_key, satellites_to_update)


def clear_satellites(redis: Redis):
    redis.delete(KeyGenerator.satellites_key)


def get_satellites(redis: Redis) -> List[Dict[str, str]]:
    satellites_cached = redis.hgetall(KeyGenerator.satellites_key)
    return satellites_from_cached(satellites_cached)


def is_empty(redis: Redis) -> bool:
    return bool(get_satellites(redis))
