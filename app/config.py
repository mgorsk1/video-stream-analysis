from os import path
from types import SimpleNamespace

from piny import YamlLoader

from app.logger import prepare


class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)


BASE_PATH = path.dirname(__file__) + '/..'

config = NestedNamespace(YamlLoader(path='{}/config/application/application.yaml'.format(BASE_PATH)).load())

log = prepare(config.log.level.upper(), '/tmp', 'VideoAnalysis')
