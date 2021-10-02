import redis
import ujson

from name_is_coming.settings import REDIS_URL
from name_is_coming.storage import cache

FILE_PATH = 'data/cache_export.json'


def main():
    r = redis.from_url(REDIS_URL, decode_responses=True)

    satellites = cache.get_satellites(r)

    with open(FILE_PATH, 'w+') as f:
        ujson.dump(satellites, f)


if __name__ == '__main__':
    main()
