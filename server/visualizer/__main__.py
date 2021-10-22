import uvloop
from aiohttp import web

from server.visualizer.resources import setup_app


def entrypoint():
    uvloop.install()

    app = setup_app()

    web.run_app(app)


entrypoint()
