from app.database import ResultDatabase, TemporaryDatabase
from time import time
from json import dumps
# from cv2 import imencode
# from base64 import b64encode, b64decode
#
# import pickle


class Notifier:
    def __init__(self, reset_after):
        self.reset_after = reset_after

        self.rdb = ResultDatabase()
        self.tdb = TemporaryDatabase()

    def notify(self, plate, confidence, image):

        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        if self.reset_after <= 0:
            self.tdb.set_key(plate + ':Y', value)
        else:
            self.tdb.set_key(plate+':Y', value, ex=self.reset_after)
