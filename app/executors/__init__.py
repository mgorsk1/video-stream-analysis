import cv2

from abc import abstractmethod
from json import dumps
from time import time
from threading import Thread
from uuid import uuid4

from app.database import ResultDatabase, TemporaryDatabase
from config import log, BASE_PATH


class Executor:
    def __init__(self, reset_after):
        self.reset_after = reset_after

        self.rdb = ResultDatabase("localhost", 9200)
        self.tdb = TemporaryDatabase("localhost", 6379)

    def run(self, plate, confidence, image, **kwargs):
        run_uuid = uuid4()

        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        if self.reset_after <= 0:
            self.tdb.set_key(plate + ':Y', value)
        else:
            self.tdb.set_key(plate+':Y', value, ex=self.reset_after)

        self.take_action(plate, confidence, image, run_uuid, **dict(kwargs))

    # @todo finish save image which saves image somewhere
    @classmethod
    def save_image(cls, plate, image, uuid):
        filename = "{}_{}.png".format(plate, uuid)
        cv2.imwrite("{}/output/{}".format(BASE_PATH, filename), image)

        log.info("#saved #image", extra=dict(file=filename))

    @abstractmethod
    def take_action(self, plate, confidence, image, **kwargs):
        raise NotImplementedError

