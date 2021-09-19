from abc import ABC, abstractmethod
from typing import List, Dict

import ujson
from aiohttp import ClientSession


class Client(ABC):
    def __init__(
            self,
            poll_url: str,
            session: ClientSession
    ):
        self._poll_url = poll_url
        self._session = session

    @abstractmethod
    async def fetch(self) -> List:
        pass


class SpaceTrackClient(Client):
    def __init__(
            self,
            poll_url: str,
            auth_url: str,
            credentials: Dict[str, str],
            session: ClientSession
    ):
        super().__init__(poll_url, session)
        self._auth_url = auth_url
        self._credentials = credentials

    async def auth(self):
        await self._session.post(self._auth_url, data=self._credentials)

    async def fetch(self) -> List:
        response = await self._session.get(self._poll_url)
        return await response.json(loads=ujson.loads)
