import cv2

from abc import abstractmethod
from json import dumps
from time import time
from uuid import uuid4
from inflection import underscore

from app.database import ResultDatabase, TemporaryDatabase
from config import log, BASE_PATH


class Executor:
    def __init__(self, reset_after):
        self.reset_after = reset_after

        self.index_name = underscore(self.__class__.__name__)
        self.rdb = ResultDatabase("localhost", 9200, self.index_name)
        self.tdb = TemporaryDatabase("localhost", 6379)

    def run(self, plate, confidence, image, **kwargs):
        run_uuid = uuid4()

        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        if self.reset_after <= 0:
            self.tdb.set_key(plate + ':Y', value)
        else:
            self.tdb.set_key(plate+':Y', value, ex=self.reset_after)

        self.take_action(plate, confidence, image, run_uuid, **dict(kwargs))

    def take_action(self, plate, confidence, image, uuid, **kwargs):
        if not self.rdb.check_if_exists(self.index_name, plate, False):
            log.info("#plate does not exist in result #database", extra=dict(plate=plate))
            if not self.rdb.check_if_exists('plate', plate, True):
                log.info("#similar #plate does not exist in result #database", extra=dict(plate=plate))
                if not self.rdb.check_if_exists('candidates', plate, False):
                    log.info("#plate does not exist amongst candidates in #database", extra=dict(plate=plate))

                    self.action(plate, confidence, image, uuid, **dict(kwargs))

                    log.info("#notification send about plate", extra=dict(plate=plate, confidence=confidence))
                else:
                    log.info("#plate existed amongst candidates in #database", extra=dict(plate=plate))
            else:
                log.info("#plate matched another #similar plate in #database", extra=dict(plate=plate))
        else:
            log.info("#plate existed in #database", extra=dict(plate=plate))

        pass

    # @todo finish save image which saves image somewhere
    @classmethod
    def save_image(cls, plate, image, uuid):
        filename = "{}_{}.png".format(plate, uuid)
        cv2.imwrite("{}/output/{}".format(BASE_PATH, filename), image)

        log.info("#saved #image", extra=dict(file=filename))

    @abstractmethod
    def action(self, plate, confidence, image, **kwargs):
        raise NotImplementedError

