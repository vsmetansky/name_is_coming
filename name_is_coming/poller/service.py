import asyncio
import logging
from typing import Dict

import elasticsearch
import redis

from name_is_coming.storage import cache, db
from name_is_coming.poller.client import SpaceTrackClient

logger = logging.getLogger(__name__)


class Service:
    def __init__(
            self,
            redis_url: str,
            api_poll_url: str,
            api_auth_url: str,
            api_auth_creds: Dict[str, str],
            api_poll_interval: int,
            api_poll_lookback: int,
            api_poll_lookback_when_empty: int,
            run_forever: bool,
            clear_cache: bool,
            lookback_historical: int = None,
            **kwargs
    ):
        self._client = SpaceTrackClient(
            api_poll_lookback,
            api_poll_url,
            api_auth_url,
            api_auth_creds,
            **kwargs
        )
        self._redis = redis.from_url(redis_url, decode_responses=True)
        # self._es = elasticsearch.Elasticsearch()

        self._api_poll_interval = api_poll_interval
        self._api_poll_lookback = api_poll_lookback
        self._api_poll_lookback_when_empty = api_poll_lookback_when_empty
        self._run_forever = run_forever
        self._clear_cache = clear_cache
        self._lookback_historical = lookback_historical

    async def close(self):
        await self._client.close()

    async def run(self):
        logger.info('starting cold run...')
        await self._run_cold()
        logger.info('completed cold run...')

        while self._run_forever:
            logger.info('starting warm run...')
            await self._run_once_safe()
            logger.info('waiting for the next update...')
            await asyncio.sleep(self._api_poll_interval)

    async def _run_once_safe(self):
        try:
            await self._run_once()
        except TypeError:
            logger.warning('failed, trying to authenticate...')
            await self._client.auth()
            logger.info('authenticated!')
            await self._run_once()

    async def _run_once(self):
        logger.info('fetching data...')
        results = await self._client.fetch()
        logger.info('updating cache...')
        await asyncio.to_thread(cache.update_satellites, self._redis, results)

    async def _run_cold(self):
        if self._clear_cache:
            logger.info('clearing cache...')
            await asyncio.to_thread(cache.clear_satellites, self._redis)

        empty_cache = self._clear_cache or await asyncio.to_thread(cache.is_empty, self._redis)

        if empty_cache:
            # enlarging lookback to fetch a lot of initial data
            self._client.poll_lookback = self._api_poll_lookback_when_empty

        await self._run_once_safe()

        if empty_cache:
            # reverting lookback for fetching updates
            self._client.poll_lookback = self._api_poll_lookback
