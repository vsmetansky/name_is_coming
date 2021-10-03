from typing import Dict, List
import logging

from redis import Redis
import ujson

from name_is_coming.settings import ADDITIONAL_INFO_PATH
from name_is_coming.storage.satellite import group_latest_by_name, satellites_from_cached, satellites_to_cached

logger = logging.getLogger(__name__)


class KeyGenerator:
    satellites_key: str = 'satellites_cache'


def update_satellites(redis: Redis, satellites: List[Dict[str, str]]):
    append_additional_satellites_info(satellites)
    satellites = satellites_to_cached(satellites)
    satellites = group_latest_by_name(satellites)

    satellites_to_update = redis.hgetall(KeyGenerator.satellites_key)

    satellites_to_update.update(satellites)

    redis.hmset(KeyGenerator.satellites_key, satellites_to_update)


def clear_satellites(redis: Redis):
    redis.delete(KeyGenerator.satellites_key)


def get_satellites(redis: Redis) -> List[Dict[str, str]]:
    satellites_cached = redis.hgetall(KeyGenerator.satellites_key)
    return satellites_from_cached(satellites_cached)


def is_empty(redis: Redis) -> bool:
    return bool(get_satellites(redis))


def append_additional_satellites_info(satellites: List[Dict[str, str]]):
    try:
        logger.info('Reading additional info file...')

        with open(ADDITIONAL_INFO_PATH, 'r') as f:
            info = ujson.load(f)

        lookup_table = {
            str(satellite_id): position for position, satellite_id in info.get('NORAD_CAT_ID').items()
        }

        logger.info('appending additional info...')

        for satellite in satellites:
            satellite_id = satellite.get('NORAD_CAT_ID')

            lookup_id = lookup_table.get(satellite_id, '')

            satellite['Purpose'] = info['Purpose'].get(lookup_id, 'N/A')
            satellite['DetailedPurpose'] = info['Detailed Purpose'].get(lookup_id, 'N/A')
            satellite['Comments'] = info['Comments'].get(lookup_id, 'N/A')
        
        logger.info('appended additional info...')

    except FileNotFoundError:
        logger.warning(
            'File not found, not updating satellites with additional info'
        )



if __name__ == '__main__':
    append_additional_satellites_info([])
