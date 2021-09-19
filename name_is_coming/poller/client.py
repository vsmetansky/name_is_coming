import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

import ujson
from aiohttp import ClientSession

from name_is_coming.tle import from_triplet

logger = logging.getLogger(__name__)


class Client(ABC):
    def __init__(
            self,
            poll_url: str
    ):
        self._poll_url = poll_url
        self._session = ClientSession()

    @abstractmethod
    async def fetch(self) -> Tuple[Tuple[Dict[str, str]]]:
        pass

    async def close(self):
        await self._session.close()


class SpaceTrackClient(Client):
    def __init__(
            self,
            poll_url: str,
            auth_url: str,
            credentials: Dict[str, str],
            **kwargs
    ):
        super().__init__(poll_url)
        self._auth_url = auth_url
        self._credentials = credentials

    async def auth(self):
        await self._session.post(self._auth_url, data=self._credentials)

    async def fetch(self) -> Tuple[Dict[str, str]]:
        try:
            return await self._fetch()
        except:
            logger.info('authenticating...')
            await self.auth()
            logger.info('authenticated!')
            return await self._fetch()

    async def _fetch(self) -> Tuple[Dict[str, str]]:
        response = await self._session.get(self._poll_url)
        data = await response.json(loads=ujson.loads)
        return self._normalize(data)

    @staticmethod
    def _normalize(data: List[dict]) -> Tuple[Dict[str, str]]:
        # schema definition https://www.space-track.org/basicspacedata/modeldef/class/gp/format/html
        return tuple(from_triplet(x['TLE_LINE0'], x['TLE_LINE1'], x['TLE_LINE2']) for x in data)
