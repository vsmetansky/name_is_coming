## Description
There are 2 main packages in the project: `poller` and `visualizer`.
  * `poller` collects latest data on satellites\debris positions from space-track.com API and saves it to Redis
  * `visualizer` grabs data from Redis inside a Dash callback, calculates actual positions of satellites\debris via processor module and renders results

## Setup

1. install and run Redis (or just do `docker-compose up redis`)
2. initiate and activate virtualenv
3. `pip install -r requirements.txt`
4. download `ETOPO1_Ice_g_gdal.grd.gz` from https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/ice_surface/grid_registered/netcdf/
5. unzip ETOPO1_Ice_g_gdal.grd.gz to data dir of repository root

## Run data collection

1. set your space-track.com `API_LOGIN` and `API_PASS` either in settings or through env
2. `python -m name_is_coming.poller`
    * by default `poller` runs only once using your existing cache
    * if cache is empty, we try to fetch data per last `API_POLL_LOOKBACK_WHEN_EMPTY` days first (you can also
      use `--clear-cache` flag to force it)
    * otherwise data is fetched per last `API_POLL_LOOKBACK` days
    * to run DC periodically add `--run-forever` flag and cache will be updated every `API_POLL_INTERVAL` seconds

## Run data visualization

1. `python -m name_is_coming.visualizer` (There may be problems with `basemap`, possible solutions: https://stackoverflow.com/questions/40374441/python-basemap-module-impossible-to-import)
