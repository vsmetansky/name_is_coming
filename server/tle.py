__all__ = (
    'from_triplet',
    'to_triplet',
    'group_latest_by_name'
)

from collections import defaultdict, deque
from typing import Tuple, Dict

TLE_LINE_SEP = '\n'


def from_triplet(tle_0: str, tle_1: str, tle_2: str) -> Dict[str, str]:
    object_name, tle_value = tle_0, TLE_LINE_SEP.join((tle_0, tle_1, tle_2))
    return {object_name: tle_value}


def to_triplet(tle_value: str) -> Tuple[str, ...]:
    return tuple(tle_value.split(TLE_LINE_SEP))


def group_latest_by_name(tles: Tuple[Dict[str, str]]) -> Dict[str, str]:
    grouped = defaultdict(deque)

    for tle in tles:
        (object_name, tle_value), = tle.items()
        grouped[object_name].append(tle_value)

    return {name: tles.pop() for name, tles in grouped.items()}
