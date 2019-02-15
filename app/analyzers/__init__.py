from abc import abstractmethod
from app.database import TemporaryDatabase


class Analyzer:
    def __init__(self, grace_period):
        # in seconds
        self.grace_period = grace_period

        self.tdb = TemporaryDatabase("localhost", 6379)

    @abstractmethod
    def process(self):
        raise NotImplementedError
