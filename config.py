from app.logger import prepare
from os import path

log = prepare('INFO', '/onwelo/programming/_python/video_analysis', 'VideoAnalysis')
BASE_PATH = path.dirname(__file__)