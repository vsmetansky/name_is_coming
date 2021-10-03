import plotly.graph_objs as go
import numpy as np
from netCDF4 import Dataset

from name_is_coming.visualizer.constants import (
    BACKGROUND_COLOR, EARTH_COLOR, EARTH_COLOR_MAX, EARTH_COLOR_MIN, EARTH_LIGHT_EFFECTS,
    EARTH_LIGHT_POSITION, SATELLITES_COLOR, SATELLITES_SIZE, TITLE_COLOR)


def construct_layout(width, height):
    noaxis = dict(
        showbackground=False,
        showgrid=False,
        showline=False,
        showticklabels=False,
        ticks='',
        title='',
        zeroline=False
    )
    return go.Layout(
        autosize=True,
        width=width, height=height,
        title='Debris map',
        titlefont=dict(family='Courier New', color=TITLE_COLOR),
        showlegend=False,
        uirevision=True,
        scene=dict(
            xaxis=dict(noaxis, showspikes=False),
            yaxis=dict(noaxis, showspikes=False),
            zaxis=dict(noaxis, showspikes=False),
            aspectmode='data',
            dragmode="orbit"),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )


def construct_earth(topo, X=[], Y=[], Z=[], text=[]):
    return dict(
        type='surface',
        x=X,
        y=Y,
        z=Z,
        colorscale=EARTH_COLOR,
        showscale=False,
        lighting=EARTH_LIGHT_EFFECTS,
        lightposition=EARTH_LIGHT_POSITION,
        surfacecolor=topo,
        cmin=EARTH_COLOR_MIN,
        cmax=EARTH_COLOR_MAX,
        text=text,
        hoverinfo='text'
    )


def construct_satellites(X=[], Y=[], Z=[], customdata=[]):
    return dict(
        type='scatter3d',
        x=X,
        y=Y,
        z=Z,
        mode='markers',
        marker=dict(
            size=SATELLITES_SIZE,
            color=SATELLITES_COLOR,
        ),
        customdata=customdata,
        hovertemplate=
            '<b>Name: %{customdata[0]}</b><br><br>'

            'X: %{x}<br>'
            'Y: %{y}<br>'
            'Z: %{z}<br><br>'

            'Region: %{customdata[1]}<br>'
            'Launch date: %{customdata[2]}<br>'
            'Type: %{customdata[3]}<br>'
            'Purpose: %{customdata[4]}<br>'
            '<extra></extra>'
    )


def construct_figure(layout, *data):
    figure = go.Figure(
        data=data,
        layout=layout
    )
    figure.update_traces(
        contours_x=dict(highlight=False), contours_y=dict(highlight=False),
        contours_z=dict(highlight=False), selector=dict(type='surface')
    )
    return figure


def Etopo(lon_area, lat_area, resolution):
    data = Dataset("data/ETOPO1_Ice_g_gdal.grd", "r")

    # Get data
    lon_range = data.variables['x_range'][:]
    lat_range = data.variables['y_range'][:]
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
