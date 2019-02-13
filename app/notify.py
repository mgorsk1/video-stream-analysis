from app.database import ResultDatabase, TemporaryDatabase
from time import time
from json import dumps


class Notifier:
    def __init__(self, reset_after_hours):
        self.reset_after_hours = reset_after_hours

        self.rdb = ResultDatabase()
        self.tdb = TemporaryDatabase()

    def notify(self, plate, confidence, image):
        print("YOU RASCAL YOU {}".format(plate))

        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        self.tdb.set_key(plate+':Y', value, ex=self.reset_after_hours*60*60)
