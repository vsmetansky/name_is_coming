import logging
from abc import ABC, abstractmethod
from typing import List, Dict

import ujson
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class Client(ABC):
    def __init__(
            self,
            poll_url_tmpl: str
    ):
        self._poll_url_tmpl = poll_url_tmpl
        self._session = ClientSession()

    @abstractmethod
    async def fetch(self) -> List[Dict[str, str]]:
        pass

    async def close(self):
        await self._session.close()


class SpaceTrackClient(Client):
    def __init__(
            self,
            poll_lookback: int,
            poll_url_tmpl: str,
            auth_url: str,
            credentials: Dict[str, str],
            **kwargs
    ):
        super().__init__(poll_url_tmpl)
        self._poll_lookback = poll_lookback
        self._poll_url = self._poll_url_tmpl.format(self._poll_lookback)
        self._auth_url = auth_url
        self._credentials = credentials

    @property
    def poll_lookback(self) -> int:
        return self._poll_lookback

    @poll_lookback.setter
    def poll_lookback(self, val: int):
        self._poll_lookback = val
        self._poll_url = self._poll_url_tmpl.format(self._poll_lookback)

    async def auth(self):
        await self._session.post(self._auth_url, data=self._credentials)

    async def fetch(self) -> List[Dict[str, str]]:
        response = await self._session.get(self._poll_url)
        data = await response.json(loads=ujson.loads)
        logger.info(f'fetched {len(data)} datapoints')
        return data
