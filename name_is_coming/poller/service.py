import asyncio
import logging
from typing import Dict

from name_is_coming.storage.cache import RedisCache
from name_is_coming.poller.client import SpaceTrackClient

logger = logging.getLogger(__name__)


class Service:
    def __init__(
            self,
            redis_url: str,
            cache_retention: int,
            api_poll_url: str,
            api_auth_url: str,
            api_auth_creds: Dict[str, str],
            **kwargs
    ):
        self._client = SpaceTrackClient(api_poll_url, api_auth_url, api_auth_creds, **kwargs)
        self._cache = RedisCache(redis_url)
        self._cache_retention = cache_retention

    async def close(self):
        await self._client.close()

    async def run(self):
        while True:
            await self._run_once()
            logger.info('waiting for the next update...')
            await asyncio.sleep(self._cache_retention)

    async def _run_once(self):
        logger.info('fetching data...')
        results = await self._client.fetch()
        logger.info('updating cache...')
        await self._cache.update(results)
