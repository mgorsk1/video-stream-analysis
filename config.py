from app.logger import prepare
from os import path, environ, getenv
from json import loads

env = getenv('ENV', 'local')

log = prepare('DEBUG', '/onwelo/programming/_python/video_analysis', 'VideoAnalysis')
BASE_PATH = path.dirname(__file__)

with open('{}/config/app/{}.json'.format(BASE_PATH, env), 'r') as f:
    config = loads(f.read())
