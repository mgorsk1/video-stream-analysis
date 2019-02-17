from abc import abstractmethod
from app.database import TemporaryDatabase
from os import getenv

from config import config


class Analyzer:
    def __init__(self, grace_period, **kwargs):
        # in seconds
        self.grace_period = grace_period

        self.tdb = TemporaryDatabase(config.get('TDB_HOST'), config.get('TDB_PORT'), **dict(db_pass=getenv('TDB_PASS')))

    @abstractmethod
    def process(self):
        raise NotImplementedError
