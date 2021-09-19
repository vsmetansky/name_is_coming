import asyncio
import logging

import uvloop

from name_is_coming import settings
from name_is_coming.poller.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint():
    uvloop.install()

    service = Service(
        settings.REDIS_URL,
        settings.CACHE_RETENTION,
        settings.API_POLL_URL,
        settings.API_AUTH_URL,
        settings.API_AUTH_CREDS,
    )

    try:
        await service.run()
    finally:
        await service.close()


uvloop.install()
asyncio.run(entrypoint())
