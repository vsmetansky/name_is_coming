import asyncio
import logging
from argparse import Namespace, ArgumentParser

import uvloop

from name_is_coming import settings
from name_is_coming.poller.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument('--run-forever', dest='run_forever', action='store_true')
    parser.add_argument('--clear-cache', dest='clear_cache', action='store_true')
    parser.add_argument('--lookback-historical', dest='lookback_historical', type=int)

    return parser.parse_args()


async def run():
    args = get_args()

    service = Service(
        settings.REDIS_URL,
        settings.API_POLL_URL_TMPL,
        settings.API_AUTH_URL,
        settings.API_AUTH_CREDS,
        settings.API_POLL_INTERVAL,
        settings.API_POLL_LOOKBACK,
        settings.API_POLL_LOOKBACK_WHEN_EMPTY,
        args.run_forever,
        args.clear_cache,
        args.lookback_historical
    )

    try:
        await service.run()
    finally:
        await service.close()


def entrypoint():
    uvloop.install()
    asyncio.run(run())


entrypoint()
