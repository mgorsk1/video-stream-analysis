from .logger import prepare
from os import path,  getenv
from json import loads

env = getenv('ENV', 'local')

BASE_PATH = path.dirname(__file__) + '/..'

with open('{}/config/app/{}.json'.format(BASE_PATH, env), 'r') as f:
    config = loads(f.read())

log = prepare(config.get('LOG_LEVEL', 'INFO'), '/onwelo/programming/_python/video_analysis', 'VideoAnalysis')