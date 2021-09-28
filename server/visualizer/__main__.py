import aiohttp_cors
import aioredis
import uvloop
from aiohttp import web
from aiohttp.web_app import Application
from skyfield.api import load

from server import settings
from server.visualizer.routes import setup_routes


def setup_app(redis: aioredis.Redis) -> Application:
    app = Application()
    cors = aiohttp_cors.setup(app)
    setup_routes(app, cors)

    app['redis'] = redis
    app['timescale'] = load.timescale()

    return app


def entrypoint():
    uvloop.install()

    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app = setup_app(redis)

    web.run_app(app)


entrypoint()
