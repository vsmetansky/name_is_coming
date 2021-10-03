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

from name_is_coming.storage.satellite import SatelliteType, get_labels
from name_is_coming.visualizer.constants import (
    EARTH_ANGULAR_VELOCITY, EARTH_RADIUS, UPDATE_PERIOD, TOPO_LON_AREA, TOPO_LAT_AREA, TOPO_RESOLUTION)
from name_is_coming.utils import map_to_sphere
from name_is_coming.visualizer.constructors import (
    Etopo, construct_earth, construct_figure, construct_layout, construct_satellites, construct_predictions)


LON_TOPO, LAT_TOPO, TOPO = Etopo(TOPO_LON_AREA, TOPO_LAT_AREA, TOPO_RESOLUTION)
X_E, Y_E, Z_E = map_to_sphere(LON_TOPO, LAT_TOPO, EARTH_RADIUS)
MONITOR, = get_monitors()

r = redis.from_url(settings.REDIS_URL, decode_responses=True)
app = dash.Dash(__name__)

layout = construct_layout(MONITOR.width, MONITOR.height)
earth = construct_earth(TOPO)
satellites = construct_satellites()
figure = construct_figure(layout, satellites, earth)

app.layout = html.Div((
    dcc.Graph(id='system', figure=figure),
    dcc.Interval(id='interval', interval=UPDATE_PERIOD, n_intervals=0),
    html.Div((
        dcc.Dropdown(
            id='switch-type',
            options=[
                {'label': 'All', 'value': SatelliteType.ALL},
                {'label': 'Debris', 'value': SatelliteType.DEBRIS},
                {'label': 'Satellites', 'value': SatelliteType.SATELLITE}
            ],
            placeholder='Choose objects type',
            value=SatelliteType.ALL
        ),
        dcc.Dropdown(
            id='show-orbit',
            placeholder='Orbit prediction',
            multi=False
        ),
    ), style={
        'width': '10vw',
        'position': 'absolute',
        'top': '10vh',
        'left': '5vw',
    })
))


@app.callback(
    Output('show-orbit', 'options'),
    Input('switch-type', 'value')
)
def update_show_orbit_options(objects_type):
    satellites = next(process(r, objects_type))
    return [{'label': s['OBJECT_NAME'], 'value': s['OBJECT_NAME']} for s in satellites]


@app.callback(
    Output('system', 'figure'),
    [Input('interval', 'n_intervals'),
     Input('switch-type', 'value'),
     Input('show-orbit', 'value')])
def update_state(n_intervals, objects_type, name_to_predict):
    X_S, Y_S, Z_S, labels = _move_satellites(objects_type, name_to_predict)
    X_E, Y_E, Z_E = _rotate_earth(n_intervals)

    earth = construct_earth(TOPO, X_E, Y_E, Z_E)
    if not name_to_predict:
        satellites = construct_satellites(X_S, Y_S, Z_S, labels)
        figure = construct_figure(layout, satellites, earth)
    else:
        satellites = construct_satellites(X_S[:1], Y_S[:1], Z_S[:1], labels)
        predictions = construct_predictions(X_S[1:], Y_S[1:], Z_S[1:])
        figure = construct_figure(layout, satellites, predictions, earth)

    return figure


def _move_satellites(objects_type, name_to_predict):
    satellites = next(process(r, objects_type, name_to_predict))

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
