from abc import abstractmethod
from os import getenv

from app.database import TemporaryDatabase
from app.config import config


class Analyzer:
    def __init__(self, grace_period, reset_after, **kwargs):
        # in seconds
        self.grace_period = grace_period
        self.reset_after = reset_after

        self.tdb = TemporaryDatabase(config.get('TDB_HOST'), config.get('TDB_PORT'), **dict(db_pass=getenv('TDB_PASS')))

    @abstractmethod
    def analyze(self):
        raise NotImplementedError
