from os import getenv

REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379')

API_LOGIN = getenv('API_LOGIN', '')
API_PASS = getenv('API_PASS', '')
API_AUTH_CREDS = {'identity': API_LOGIN, 'password': API_PASS}
API_AUTH_URL = 'https://www.space-track.org/ajaxauth/login'

API_POLL_URL_TMPL = \
    'https://www.space-track.org/basicspacedata/query/class/gp' \
    '/decay_date/null-val/epoch/>now-{}/orderby/EPOCH asc/format/json'
API_POLL_INTERVAL = int(getenv('API_POLL_INTERVAL', 20))  # seconds
API_POLL_LOOKBACK = int(getenv('API_POLL_LOOKBACK', 1))  # days
API_POLL_LOOKBACK_WHEN_EMPTY = int(getenv('API_POLL_LOOKBACK_WHEN_EMPTY', 30))  # days
