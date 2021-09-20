## Setup

1. install Redis
2. initiate and activate virtualenv
3. `pip install -r requirements.txt`

## Run data collection

1. set your space-track.com `API_LOGIN` and `API_PASS` either in settings or through env
2. `python -m name_is_coming.poller`
    * by default DC runs only once using your existing cache
    * if cache is empty, we try to fetch data per last `API_POLL_LOOKBACK_WHEN_EMPTY` days first (you can also
      use `--clear-cache` flag to force it)
    * otherwise data is fetched per last `API_POLL_LOOKBACK` days
    * to run DC periodically add `--run-forever` flag and cache will be updated every `API_POLL_INTERVAL` seconds

## Run data processing

1. `python -m name_is_coming.processor`

## Run data visualization

2. `python -m name_is_coming.visualizer`
