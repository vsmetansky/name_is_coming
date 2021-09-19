__all__ = (
    'from_triplet',
    'to_triplet'
)

from typing import Tuple, Dict

TLE_LINE_SEP = '\n'


def from_triplet(tle_0: str, tle_1: str, tle_2: str) -> Dict[str, str]:
    object_name, tle_value = tle_0, TLE_LINE_SEP.join((tle_0, tle_1, tle_2))
    return {object_name: tle_value}


def to_triplet(tle: Dict[str, str]) -> Tuple[str, ...]:
    tle_value, = tle.values()
    return tuple(tle_value.split(TLE_LINE_SEP))
