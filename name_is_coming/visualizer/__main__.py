from name_is_coming.processor import process
from name_is_coming import settings
import redis
import dash
from dash.dependencies import Output, Input
from dash import html
from dash import dcc

import numpy as np
import redis
from screeninfo import get_monitors

from name_is_coming.storage.satellite import get_labels
from name_is_coming.visualizer.constants import (
    EARTH_ANGULAR_VELOCITY, EARTH_RADIUS, UPDATE_PERIOD, TOPO_LON_AREA, TOPO_LAT_AREA, TOPO_RESOLUTION)
from name_is_coming.utils import map_to_sphere
from name_is_coming.visualizer.constructors import Etopo, construct_earth, construct_figure, construct_layout, construct_satellites

r = redis.from_url(settings.REDIS_URL, decode_responses=True)
app = dash.Dash(__name__)


LON_TOPO, LAT_TOPO, TOPO = Etopo(TOPO_LON_AREA, TOPO_LAT_AREA, TOPO_RESOLUTION)
X_E, Y_E, Z_E = map_to_sphere(LON_TOPO, LAT_TOPO, EARTH_RADIUS)
MONITOR, = get_monitors()

layout = construct_layout(MONITOR.width, MONITOR.height)
earth = construct_earth(TOPO)
satellites = construct_satellites()
figure = construct_figure(layout, satellites, earth)

app.layout = html.Div((
    dcc.Graph(id='system', figure=figure),
    dcc.Interval(id='interval', interval=UPDATE_PERIOD, n_intervals=0),
))


@app.callback(
    Output('system', 'figure'),
    [Input('interval', 'n_intervals')])
def update_state(n_intervals):
    X_S, Y_S, Z_S, labels = _move_satellites()
    X_E, Y_E, Z_E = _rotate_earth(n_intervals)

    satellites = construct_satellites(X_S, Y_S, Z_S, labels)
    earth = construct_earth(TOPO, X_E, Y_E, Z_E)
    figure = construct_figure(layout, satellites, earth)

    return figure


def _move_satellites():
    satellites = next(process(r))

    X, Y, Z, labels = zip(
        *map(
            lambda s: (s['X'], s['Y'], s['Z'], get_labels(s)),
            satellites
        )
    )

    return X, Y, Z, labels


def _rotate_earth(n_intervals: int):
    a = EARTH_ANGULAR_VELOCITY * n_intervals

    X = X_E * np.cos(a) - Y_E * np.sin(a)
    Y = X_E * np.sin(a) + Y_E * np.cos(a)
    Z = Z_E

    return X, Y, Z


app.run_server(debug=True, port=8000)
