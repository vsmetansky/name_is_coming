from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig, ResourceOptions

from server.visualizer.handlers import get_locations_handler


def setup_routes(app: Application, cors: CorsConfig):
    route = app.router.add_route('GET', '/api/v1/locations', get_locations_handler)
    cors.add(route, {'*': ResourceOptions(expose_headers='*', allow_headers='*')})
