from typing import List, Tuple

from aioredis import Redis
from skyfield.api import EarthSatellite
from skyfield.api import wgs84

from skyfield.timelib import Timescale, Time

from server.storage import cache
from server.tle import to_triplet


def current_location(tle: str, ts: Timescale, time_now: Time) -> Tuple:
    tle_0, tle_1, tle_2 = to_triplet(tle)
    satellite = EarthSatellite(tle_1, tle_2, tle_0, ts)

    geocentric = satellite.at(time_now)
    subpoint = wgs84.subpoint(geocentric)

    return (
        subpoint.latitude.degrees,
        subpoint.longitude.degrees,
        subpoint.elevation.km
    )


async def process(r: Redis, ts: Timescale) -> List:
    tles = await cache.retrieve(r)
    time_now = ts.now()
    return [current_location(tle, ts, time_now) for tle in tles.values()]
