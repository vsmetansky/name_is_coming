__all__ = (
    'get_locations_handler',
)

import ujson
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aioredis import Redis
from skyfield.timelib import Timescale

from server.processor import process


async def get_locations_handler(request: Request) -> Response:
    redis: Redis = request.app['redis']
    timescale: Timescale = request.app['timescale']
    data = await process(redis, timescale)
    return web.json_response(data, dumps=ujson.dumps)
