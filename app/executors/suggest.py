from time import sleep

from app.config import log
from app.executors.base import FastTrackBaseExecutor


class TrashCanSuggester(FastTrackBaseExecutor):
    save_file_function = 'skip'

    def __init__(self, *args, **kwargs):
        super(TrashCanSuggester, self).__init__(*args, **kwargs)

        self.category_to_pin = dict(plastiki=1, szklo=2)

    def _action(self, value, confidence, image, uuid, **kwargs):
        log.info("suggesting #trash fraction", extra=dict(value=value))

        super(TrashCanSuggester, self)._action(value, confidence, image, uuid)

        self.turn_led_on(value)

        log.info("#trash fraction #suggested", extra=dict(value=value))

    def turn_led_on(self, category):
        led = self.category_to_pin.get(category)

        log.info("turning #led #on", extra=dict(category=category, led=led))

        sleep(3)

        log.info("turning #led #off", extra=dict(category=category, led=led))
