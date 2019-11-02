from abc import ABC, abstractmethod
from os import getenv

from app.config import config
from app.dbs.temporary import TemporaryDatabase

__all__ = ['BaseAnalyzer']


class BaseAnalyzer(ABC):
    def __init__(self, *args, **kwargs):
        super(BaseAnalyzer, self).__init__(*args, **kwargs)
        # in seconds
        self.grace_period = kwargs.get('grace_period', 60)

        self.tdb = TemporaryDatabase(config.get('TDB_HOST'), config.get('TDB_PORT'), **dict(db_pass=getenv('TDB_PASS')))

    @abstractmethod
    def analyze(self, value: str, confidence: float, image, **kwargs) -> None:
        pass
