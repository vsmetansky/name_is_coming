UPDATE_PERIOD = 3000

EARTH_RADIUS = 6371
EARTH_ANGULAR_VELOCITY = 7.3 * 1e-4  # the actual speed is lower

EARTH_COLOR = [
    [0, 'rgb(0, 0, 70)'], [0.2, 'rgb(0,90,150)'],
    [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
    [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'],
    [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'],
    [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']
]
EARTH_COLOR_MIN = -8000
EARTH_COLOR_MAX = 8000
EARTH_LIGHT_EFFECTS = dict(ambient=0.3, diffuse=0.5, roughness=0.2, fresnel=0.2)
EARTH_LIGHT_POSITION = dict(x=-10000, y=0, z=0)

TOPO_RESOLUTION = 1.6
TOPO_LON_AREA = [-180., 180.]
TOPO_LAT_AREA = [-90., 90.]

TITLE_COLOR = 'white'
BACKGROUND_COLOR = 'black'

SATELLITES_SIZE = 2
SATELLITES_COLOR = '#2CA02C'

PREDICTION_SIZE = SATELLITES_SIZE // 2
PREDICTION_COLOR = 'white'
PREDICTION_PERIOD = 60 * 60 * 2
PREDICTION_STEP = 5
