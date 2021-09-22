
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.io as pio
import numpy as np
from netCDF4 import Dataset
import pylab as plt
import numpy as np
import matplotlib
from matplotlib import cm
import pandas as pd
import glob
import time
from mpl_toolkits.basemap import Basemap
from screeninfo import get_monitors
for monitor in get_monitors():
    print(str(monitor))
    print(monitor.width)


def Etopo(lon_area, lat_area, resolution):
  ### Input
  # resolution: resolution of topography for both of longitude and latitude [deg]
  # (Original resolution is 0.0167 deg)
  # lon_area and lat_area: the region of the map which you want like [100, 130], [20, 25]
  ###
  ### Output
  # Mesh type longitude, latitude, and topography data
  ###

  # Read NetCDF data
  data = Dataset("ETOPO1_Ice_g_gdal.grd", "r")

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
  lon_input = np.zeros(lon_num); lat_input = np.zeros(lat_num)
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
    skip = int(resolution/spacing[0])
    lon = lon[::skip,::skip]
    lat = lat[::skip,::skip]
    topo = topo[::skip,::skip]

  topo = topo[::-1]

  # Select the range of map
  range1 = np.where((lon>=lon_area[0]) & (lon<=lon_area[1]))
  lon = lon[range1]; lat = lat[range1]; topo = topo[range1]
  range2 = np.where((lat>=lat_area[0]) & (lat<=lat_area[1]))
  lon = lon[range2]; lat = lat[range2]; topo = topo[range2]

  # Convert 2D again
  lon_num = len(np.unique(lon))
  lat_num = len(np.unique(lat))
  lon = np.reshape(lon, (lat_num, lon_num))
  lat = np.reshape(lat, (lat_num, lon_num))
  topo = np.reshape(topo, (lat_num, lon_num))

  return lon, lat, topo


def degree2radians(degree):
  # convert degrees to radians
  return degree*np.pi/180

def mapping_map_to_sphere(lon, lat, radius=1):
  # this function maps the points of coords (lon, lat) to points onto the sphere of radius radius
  lon=np.array(lon, dtype=np.float64)
  lat=np.array(lat, dtype=np.float64)
  lon=degree2radians(lon)
  lat=degree2radians(lat)
  xs=radius*np.cos(lon)*np.cos(lat)
  ys=radius*np.sin(lon)*np.cos(lat)
  zs=radius*np.sin(lat)
  return xs, ys, zs

def visual():
  # Import topography data
  # Select the area you want
  resolution = 0.4
  lon_area = [-180., 180.]
  lat_area = [-90., 90.]
  # Get mesh-shape topography data
  lon_topo, lat_topo, topo = Etopo(lon_area, lat_area, resolution)


  xs, ys, zs = mapping_map_to_sphere(lon_topo, lat_topo)

  Ctopo = [[0, 'rgb(0, 0, 70)'],[0.2, 'rgb(0,90,150)'],
          [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
          [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'],
          [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'],
          [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']]
  cmin = -8000
  cmax = 8000


  # Get list of of coastline, country, and state lon/lat
  cc_lons, cc_lats=get_coastline_traces()
  country_lons, country_lats=get_country_traces()

  #concatenate the lon/lat for coastlines and country boundaries:
  lons=cc_lons+[None]+country_lons
  lats=cc_lats+[None]+country_lats

  xs_bd, ys_bd, zs_bd = mapping_map_to_sphere(lons, lats, radius=1.001)# here the radius is slightly greater than 1
                                                           #to ensure lines visibility; otherwise (with radius=1)
                                                           # some lines are hidden by contours colors

  boundaries=dict(type='scatter3d',
                 x=xs_bd,
                 y=ys_bd,
                 z=zs_bd,
                 mode='lines',
                 line=dict(color='white', width=1)
                )

  topo_sphere=dict(type='surface',
    x=xs,
    y=ys,
    z=zs,
    colorscale=Ctopo,
    surfacecolor=topo,
    cmin=cmin,
    cmax=cmax)

  noaxis=dict(showbackground=False,
    showgrid=False,
    showline=False,
    showticklabels=False,
    ticks='',
    title='',
    zeroline=False)

  titlecolor = 'white'
  bgcolor = 'black'

  layout = go.Layout(
    autosize=False, width=(monitor.width-10), height=monitor.height,
    title = 'Debris map',
    titlefont = dict(family='Courier New', color=titlecolor),
    showlegend = False,
    scene = dict(
      xaxis = noaxis,
      yaxis = noaxis,
      zaxis = noaxis,
      aspectmode='manual',
      aspectratio=go.layout.scene.Aspectratio(
      x=1, y=1, z=1)),
    paper_bgcolor = bgcolor,
    plot_bgcolor = bgcolor)

  plot_data=[topo_sphere, boundaries]
  fig = go.Figure(data=plot_data, layout=layout)
  #fig.update_traces(showscale=False)
  fig.show()








# Functions converting coastline/country polygons to lon/lat traces
def polygons_to_traces(poly_paths, N_poly):
    m = Basemap(resolution='i')
    '''
    pos arg 1. (poly_paths): paths to polygons
    pos arg 2. (N_poly): number of polygon to convert
    '''
    # init. plotting list
    lons=[]
    lats=[]

    for i_poly in range(N_poly):
        poly_path = poly_paths[i_poly]

        # get the Basemap coordinates of each segment
        coords_cc = np.array(
            [(vertex[0],vertex[1])
             for (vertex,code) in poly_path.iter_segments(simplify=False)]
        )

        # convert coordinates to lon/lat by 'inverting' the Basemap projection
        lon_cc, lat_cc = m(coords_cc[:,0],coords_cc[:,1], inverse=True)


        lats.extend(lat_cc.tolist()+[None])
        lons.extend(lon_cc.tolist()+[None])

    return lons, lats

# Function generating coastline lon/lat
def get_coastline_traces():
    m = Basemap(resolution='i')
    poly_paths = m.drawcoastlines().get_paths() # coastline polygon paths
    N_poly = 91  # use only the 91st biggest coastlines (i.e. no rivers)
    cc_lons, cc_lats= polygons_to_traces(poly_paths, N_poly)
    return cc_lons, cc_lats

# Function generating country lon/lat
def get_country_traces():
    m = Basemap(resolution='i')
    poly_paths = m.drawcountries().get_paths() # country polygon paths
    N_poly = len(poly_paths)  # use all countries
    country_lons, country_lats= polygons_to_traces(poly_paths, N_poly)
    return country_lons, country_lats



def main():
  m = Basemap(resolution='i')
  visual()

if __name__ == "__main__":
    main()
