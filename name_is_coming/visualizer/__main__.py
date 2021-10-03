from name_is_coming.processor import process
from name_is_coming import settings
import redis
import dash
from dash.dependencies import Output, Input
from dash import html
from dash import dcc

import plotly.graph_objs as go
from netCDF4 import Dataset
import numpy as np
import redis
from mpl_toolkits.basemap import Basemap
from screeninfo import get_monitors

from name_is_coming.visualizer.constants import EARTH_ANGULAR_VELOCITY, EARTH_RADIUS, UPDATE_PERIOD

for monitor in get_monitors():
    print(str(monitor))
    print(monitor.width)


def Etopo(lon_area, lat_area, resolution):
    # Input
    # resolution: resolution of topography for both of longitude and latitude [deg]
    # (Original resolution is 0.0167 deg)
    # lon_area and lat_area: the region of the map which you want like [100, 130], [20, 25]
    ###
    # Output
    # Mesh type longitude, latitude, and topography data
    ###

    # Read NetCDF data
    data = Dataset("data/ETOPO1_Ice_g_gdal.grd", "r")

    # Get data
    lon_range = data.variables['x_range'][:]
    lat_range = data.variables['y_range'][:]
    topo_range = data.variables['z_range'][:]
    spacing = data.variables['spacing'][:]
    dimension = data.variables['dimension'][:]
    z = data.variables['z'][:]
    lon_num = dimension[0]
    lat_num = dimension[1]

    # Prepare array
    lon_input = np.zeros(lon_num)
    lat_input = np.zeros(lat_num)
    for i in range(lon_num):
        lon_input[i] = lon_range[0] + i * spacing[0]
    for i in range(lat_num):
        lat_input[i] = lat_range[0] + i * spacing[1]

    # Create 2D array
    lon, lat = np.meshgrid(lon_input, lat_input)

    # Convert 2D array from 1D array for z value
    topo = np.reshape(z, (lat_num, lon_num))

    # Skip the data for resolution
    if ((resolution < spacing[0]) | (resolution < spacing[1])):
        print('Set the highest resolution')
    else:
        skip = int(resolution / spacing[0])
        lon = lon[::skip, ::skip]
        lat = lat[::skip, ::skip]
        topo = topo[::skip, ::skip]

    topo = topo[::-1]

    # Select the range of map
    range1 = np.where((lon >= lon_area[0]) & (lon <= lon_area[1]))
    lon = lon[range1]
    lat = lat[range1]
    topo = topo[range1]
    range2 = np.where((lat >= lat_area[0]) & (lat <= lat_area[1]))
    lon = lon[range2]
    lat = lat[range2]
    topo = topo[range2]

    # Convert 2D again
    lon_num = len(np.unique(lon))
    lat_num = len(np.unique(lat))
    lon = np.reshape(lon, (lat_num, lon_num))
    lat = np.reshape(lat, (lat_num, lon_num))
    topo = np.reshape(topo, (lat_num, lon_num))

    return lon, lat, topo


def degree2radians(degree):
    return degree * np.pi / 180


def mapping_map_to_sphere(lon, lat, radius=EARTH_RADIUS):
    # this function maps the points of coords (lon, lat) to points onto the sphere of radius radius
    lon = np.array(lon, dtype=np.float64)
    lat = np.array(lat, dtype=np.float64)
    lon = degree2radians(lon)
    lat = degree2radians(lat)
    xs = radius * np.cos(lon) * np.cos(lat)
    ys = radius * np.sin(lon) * np.cos(lat)
    zs = radius * np.sin(lat)
    return xs, ys, zs


resolution = 1.6
lon_area = [-180., 180.]
lat_area = [-90., 90.]
# Get mesh-shape topography data
lon_topo, lat_topo, topo = Etopo(lon_area, lat_area, resolution)

xs, ys, zs = mapping_map_to_sphere(lon_topo, lat_topo)

topo_color = [
    [0, 'rgb(0, 0, 70)'], [0.2, 'rgb(0,90,150)'],
    [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
    [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'],
    [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'],
    [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']
]
topo_color_min = -8000
topo_color_max = 8000

lighting_effects = dict(ambient=0.3, diffuse=0.5, roughness=0.2, fresnel=0.2)
light_position = dict(x=-10000, y=0, z=0)

topo_sphere = dict(
    type='surface',
    x=xs,
    y=ys,
    z=zs,
    colorscale=topo_color,
    showscale=False,
    lighting=lighting_effects,
    lightposition=light_position,
    surfacecolor=topo,
    cmin=topo_color_min,
    cmax=topo_color_max,
    text=[],
    hoverinfo="text"
)

noaxis = dict(showbackground=False,
              showgrid=False,
              showline=False,
              showticklabels=False,
              ticks='',
              title='',
              zeroline=False)

titlecolor = 'white'
bgcolor = 'black'
camera = dict(
    center=dict(x=0, y=0, z=0))

layout = go.Layout(
    autosize=True,
    width=monitor.width, height=monitor.height,
    title='Debris map',
    titlefont=dict(family='Courier New', color=titlecolor),
    showlegend=False,
    uirevision=True,
    scene=dict(
        xaxis=dict(noaxis, showspikes=False),
        yaxis=dict(noaxis, showspikes=False),
        zaxis=dict(noaxis, showspikes=False),
        #  showspikes = False,
        aspectmode='data',
        dragmode = "orbit"),
    paper_bgcolor=bgcolor,
    plot_bgcolor=bgcolor)

r = redis.from_url(settings.REDIS_URL, decode_responses=True)
location_list, name_list = next(process(r))

debris = dict(type='scatter3d',
              x=[],
              y=[],
              z=[],
              mode='markers',
              marker=dict(
                  size=2,
                  color="#2CA02C",  # set color equal to a variable
                #  colorscale='Plasma'
              ),
              text=name_list,
              hoverinfo="text"
              #           line=dict(color='red', width=2)
              )

figure = go.Figure(
    data=(debris, topo_sphere),
    layout=layout
)
figure.update_traces(
    contours_x=dict(highlight=False), contours_y=dict(highlight=False),
    contours_z=dict(highlight=False), selector=dict(type='surface')
)


app = dash.Dash(__name__)

app.layout = html.Div((
    dcc.Graph(id='system', figure=figure),
    dcc.Interval(id='interval', interval=UPDATE_PERIOD, n_intervals=0),
), style={'overflow': 'hidden'})


@app.callback(
    Output('system', 'figure'),
    [Input('interval', 'n_intervals')])
def update_state(n_intervals):
    X_S, Y_S, Z_S = _move_satellites()
    X_E, Y_E, Z_E = _rotate_earth(n_intervals)

    satellites = dict(
        type='scatter3d',
        x=X_S,
        y=Y_S,
        z=Z_S,
        mode='markers',
        marker=dict(
            size=1,
            color="#2CA02C",
            colorscale='Plasma'
        ),
        text=name_list,
        hoverinfo="text"
    )
    earth = dict(
        type='surface',
        x=X_E,
        y=Y_E,
        z=Z_E,
        colorscale=topo_color,
        showscale=False,
        lighting=lighting_effects,
        lightposition=light_position,
        surfacecolor=topo,
        cmin=topo_color_min,
        cmax=topo_color_max,
        text=[],
        hoverinfo="text"
    )

    figure = go.Figure(
        data=(satellites, earth),
        layout=layout,
    )
    figure.update_traces(
        contours_x=dict(highlight=False), contours_y=dict(highlight=False),
        contours_z=dict(highlight=False), selector=dict(type='surface')
    )
    return figure


def _move_satellites():
    location_list, _ = next(process(r))

    X, Y, Z = zip(*location_list)

    return X, Y, Z


def _rotate_earth(n_intervals: int):
    a = EARTH_ANGULAR_VELOCITY * n_intervals

    X = xs * np.cos(a) - ys * np.sin(a)
    Y = xs * np.sin(a) + ys * np.cos(a)
    Z = zs

    return X, Y, Z


app.run_server(debug=True, port=8000)
