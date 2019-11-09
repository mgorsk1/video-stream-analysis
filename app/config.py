from json import loads
from os import path, getenv

from .logger import prepare

env = getenv('ENV', 'local')

BASE_PATH = path.dirname(__file__) + '/..'

with open('{}/config/app/{}.json'.format(BASE_PATH, env), 'r') as f:
    config = loads(f.read())

log = prepare('DEBUG', '/tmp', 'VideoAnalysis')
