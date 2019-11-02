from abc import ABC, abstractmethod
from os import getenv
from threading import Thread

from app.config import config, log
from app.dbs.temporary import TemporaryDatabase

__all__ = ['BaseAnalyzer']


class BaseAnalyzer(ABC):
    def __init__(self, *args, **kwargs):
        super(BaseAnalyzer, self).__init__(*args, **kwargs)
        # in seconds
        self.grace_period = kwargs.get('grace_period', 60)

        self.tdb = TemporaryDatabase(config.get('TDB_HOST'), config.get('TDB_PORT'), **dict(db_pass=getenv('TDB_PASS')))

    def analyze(self, value, confidence, image, **kwargs):
        log.info("starting thread for #analysis of #image",
                 extra=dict(target=self.analyze, args=(value, confidence, image)))

        t = Thread(target=self._analyze, args=(value, confidence, image,), kwargs=dict(kwargs))

        t.start()

    def search(self, *args, **kwargs):
        results, frame = super(BaseAnalyzer, self).search(*args, **kwargs)

        for result in results:
            value = result.get('value')
            confidence = result.get('confidence')
            image = result.get('image')
            metadata = result.get('metadata')

            self.analyze(value, confidence, image, **metadata)

        return results, frame

    @abstractmethod
    def _analyze(self, value: str, confidence: float, image, **kwargs) -> None:
        pass
