from typing import List, Tuple, Generator, Dict

import redis
from skyfield.api import EarthSatellite
from skyfield.api import load, wgs84
from skyfield.timelib import Timescale, Time
from skyfield.units import Angle, Distance

from name_is_coming import settings
from name_is_coming.utils import degree2radians
from name_is_coming.storage import cache
from name_is_coming.storage.satellite import satellite_to_tle_triplet
import numpy as np


def current_location(time_now: Time, satellite: EarthSatellite) -> Tuple[Angle, Angle, Distance]:
    geocentric = satellite.at(time_now)
    subpoint = wgs84.subpoint(geocentric)

    lat = degree2radians(subpoint.latitude.degrees)
    lon = degree2radians(subpoint.longitude.degrees)
    h = 6371 + subpoint.elevation.km
    x = h * np.cos(lon) * np.cos(lat)
    y = h * np.sin(lon) * np.cos(lat)
    z = h * np.sin(lat)

    if abs(x) > 55000 or abs(y) > 55000 or abs(z) > 55000:
        x = y = z = 0

    return x, y, z


def process_satellite(
    satellite: Dict[str, str],
    ts: Timescale,
    time_now: Time
):
    tle_0, tle_1, tle_2 = satellite_to_tle_triplet(satellite)
    satellite_ = EarthSatellite(tle_1, tle_2, tle_0, ts)

    X, Y, Z = current_location(time_now, satellite_)

    satellite.update({
        'X': X,
        'Y': Y,
        'Z': Z,
    })


def process_once(ts: Timescale, r: redis.Redis) -> Tuple[List, List]:
    satellites = cache.get_satellites(r)
    time_now = ts.now()

    for satellite in satellites:
        process_satellite(satellite, ts, time_now)

    return satellites


def process(r: redis.Redis) -> Generator[List[Tuple], None, None]:
    ts = load.timescale()
    while True:
        yield process_once(ts, r)


def entrypoint():
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    for result in process(r):
        print(result[0])


if __name__ == '__main__':
    entrypoint()
