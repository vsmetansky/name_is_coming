__all__ = (
    'get_locations_handler',
)

import ujson
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from server.processor import process


async def get_locations_handler(request: Request) -> Response:
    satellites = request.app['satellites']

    data = await process(satellites)

    return web.json_response(data, dumps=ujson.dumps)
