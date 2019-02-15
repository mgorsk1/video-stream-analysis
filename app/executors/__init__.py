from abc import abstractmethod
from json import dumps
from time import time
from threading import Thread

from app.database import ResultDatabase, TemporaryDatabase


class Executor:
    def __init__(self, reset_after):
        self.reset_after = reset_after

        self.rdb = ResultDatabase()
        self.tdb = TemporaryDatabase()

    def run(self, plate, confidence, image):
        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        if self.reset_after <= 0:
            self.tdb.set_key(plate + ':Y', value)
        else:
            self.tdb.set_key(plate+':Y', value, ex=self.reset_after)

        take_action = Thread(target=self.take_action, args=(plate, confidence, image,))
        save_image = Thread(target= self.save_image, args=(image,))

        take_action.start()
        save_image.start()

        take_action.join()
        save_image.join()

    # @todo finish save image which saves image somewhere
    @classmethod
    def save_image(cls, image):
        pass

    @abstractmethod
    def take_action(self, plate, confidence, image):
        raise NotImplementedError

