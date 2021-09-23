from typing import List, Tuple, Generator

from skyfield.api import EarthSatellite
from skyfield.api import load, wgs84

from skyfield.timelib import Timescale
from skyfield.units import Angle, Distance

from name_is_coming import settings
from name_is_coming.storage.cache import RedisCacheSync
from name_is_coming.tle import to_triplet


def current_location(ts: Timescale, tle_0: str, tle_1: str, tle_2: str) -> Tuple[Angle, Angle, Distance]:
    satellite = EarthSatellite(tle_1, tle_2, tle_0, ts)
    time_now = ts.now()

    # Check if TLE valid
    days_from_tle = time_now - satellite.epoch
    if abs(days_from_tle) > 14:
        print('TLE too old!')

    geocentric = satellite.at(time_now)
    subpoint = wgs84.subpoint(geocentric)

    return subpoint.latitude, subpoint.longitude, subpoint.elevation.km


def process_once(ts: Timescale, cache: RedisCacheSync) -> List:
    return [current_location(ts, *to_triplet(entry)) for entry in cache.retrieve().values()]


def process(cache: RedisCacheSync) -> Generator[List[Tuple], None, None]:
    ts = load.timescale()
    while True:
        yield process_once(ts, cache)


def entrypoint():
    cache = RedisCacheSync(
        settings.REDIS_URL
    )
    for result in process(cache):
        print(result[0])


if __name__ == '__main__':
    entrypoint()
