from typing import List, Tuple, Generator

from skyfield.api import EarthSatellite
from skyfield.api import load, wgs84

from skyfield.timelib import Timescale
from skyfield.units import Angle, Distance

from name_is_coming import settings
from name_is_coming.storage.cache import RedisCacheSync
from name_is_coming.tle import to_triplet
import numpy as np


def degree2radians(degree):
  return degree*np.pi/180

def sat_name(ts: Timescale, tle_0: str, tle_1: str, tle_2: str):
    satellite = EarthSatellite(tle_1, tle_2, tle_0, ts)
    return satellite.name


def current_location(ts: Timescale, tle_0: str, tle_1: str, tle_2: str) -> Tuple[Angle, Angle, Distance]:
    satellite = EarthSatellite(tle_1, tle_2, tle_0, ts)
    time_now = ts.now()

    # Check if TLE valid
    days_from_tle = time_now - satellite.epoch
    if abs(days_from_tle) > 14:
        print('TLE too old!')

    geocentric = satellite.at(time_now)
    subpoint = wgs84.subpoint(geocentric)


    lat = degree2radians(subpoint.latitude.degrees)
    lon = degree2radians(subpoint.longitude.degrees)
    h = 6371 + subpoint.elevation.km
    x=h*np.cos(lon)*np.cos(lat)
    y=h*np.sin(lon)*np.cos(lat)
    z=h*np.sin(lat)

    return x, y, z#6371*degree2radians(subpoint.latitude.degrees), degree2radians(subpoint.longitude.degrees), subpoint.elevation.km


def process_once(ts: Timescale, cache: RedisCacheSync) -> List:
    return [current_location(ts, *to_triplet(entry)) for entry in cache.retrieve().values()], [sat_name(ts, *to_triplet(entry)) for entry in cache.retrieve().values()]


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
