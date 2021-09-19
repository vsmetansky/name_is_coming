from os import getenv

REDIS_URL = getenv('REDIS_URL', 'redis://localhost:6379')
CACHE_RETENTION = getenv('CACHE_RETENTION', 30)  # seconds

API_LOGIN = getenv('SOURCE_LOGIN', '')
API_PASS = getenv('SOURCE_PASS', '')
API_AUTH_CREDS = {'identity': API_LOGIN, 'password': API_PASS}
API_AUTH_URL = 'https://www.space-track.org/ajaxauth/login'

API_POLL_URL = \
    'https://www.space-track.org/basicspacedata/query/class/gp' \
    '/decay_date/null-val/OBJECT_TYPE/Debris/epoch/>now-0.5/orderby/EPOCH asc/format/json'
