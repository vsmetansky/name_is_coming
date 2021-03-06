"""
Schema definition https://www.space-track.org/basicspacedata/modeldef/class/gp/format/html
"""

__all__ = (
    'satellite_to_tle_triplet',
    'satellites_to_cached',
    'satellites_from_cached',
    'group_latest_by_name'
)

from collections import defaultdict, deque
from typing import Dict, List, Tuple

import ujson


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
