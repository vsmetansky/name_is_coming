"""
Schema definition https://www.space-track.org/basicspacedata/modeldef/class/gp/format/html
"""

from enum import IntEnum, auto
from functools import lru_cache
import ujson
from typing import Dict, List, Tuple
from collections import defaultdict, deque

__all__ = (
    'satellite_to_tle_triplet',
    'satellites_to_cached',
    'satellites_from_cached',
    'group_latest_by_name',
    'SatelliteType',
)

SATELLITE_TYPE = {'PAYLOAD',}
DEBRIS_TYPE = {'DEBRIS', 'ROCKET BODY', 'TBA'}
ALL_TYPE = SATELLITE_TYPE | DEBRIS_TYPE


class SatelliteType(IntEnum):
    ALL = auto()
    SATELLITE = auto()
    DEBRIS = auto()


SATELLITE_TYPES_MAP = {
    SatelliteType.ALL: ALL_TYPE,
    SatelliteType.SATELLITE: SATELLITE_TYPE,
    SatelliteType.DEBRIS: DEBRIS_TYPE
}


def satellite_to_tle_triplet(satellite: Dict[str, str]) -> Tuple[str, str, str]:
    return satellite['TLE_LINE0'], satellite['TLE_LINE1'], satellite['TLE_LINE2']


def satellites_to_cached(satellites: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{satellite['OBJECT_NAME']: ujson.dumps(satellite)} for satellite in satellites]


def satellites_from_cached(satellites_cached: Dict[str, str]) -> List[Dict[str, str]]:
    return list(map(ujson.loads, satellites_cached.values()))


def group_latest_by_name(satellites: List[Dict[str, str]]) -> Dict[str, str]:
    grouped = defaultdict(deque)

    for satellite in satellites:
        (name, datum), = satellite.items()
        grouped[name].append(datum)

    return {name: data.pop() for name, data in grouped.items()}

def filter_satellites(satellites: List[Dict[str, str]], objects_type=SatelliteType.ALL, alive_only=False):
    objects_types_verbose = SATELLITE_TYPES_MAP.get(objects_type)
    return [s for s in satellites if s['OBJECT_TYPE'] in objects_types_verbose]


def get_labels(satellite: Dict[str, str]):
    return [
        [satellite.get('OBJECT_NAME')],
        [satellite.get('COUNTRY_CODE')],
        [satellite.get('LAUNCH_DATE')],
        [satellite.get('OBJECT_TYPE')],
        [satellite.get('Purpose')],
    ]
