from aiohttp import web
import aiohttp_jinja2
import jinja2


@aiohttp_jinja2.template('index.html')
def index_handler(request):
    pass


app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./views'))
app.router.add_get('/', index_handler)

web.run_app(app, port=8081)
