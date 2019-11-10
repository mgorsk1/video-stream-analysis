from math import ceil
from threading import Lock
from time import sleep
from time import time

from app.analyzers.base import BaseAnalyzer
from app.config import log
from app.tools import format_key_active, format_key_inactive

__all__ = ['Vigilante']


class Vigilante(BaseAnalyzer):
    def __init__(self, *args, **kwargs):
        super(Vigilante, self).__init__(*args, **kwargs)

        self.lock = Lock()

    def _analyze(self, value, confidence, image, **kwargs):
        # check if already notified about value
        #   if not - check if already detected value
        #       if yes - check value whether it's within its grace_period
        #           if yes - check how long it sits there and if exceeded grace_period - notify
        #           if no - skip
        #       if no - add to redis
        #   if yes - do nothing
        log.info("#started #analysis", extra=dict(value=value, confidence=confidence))

        while self.lock.locked():
            log.info("#waiting for #lock to be released")
            sleep(1)

        already_filed = self.tdb.get_val(format_key_active(value))

        if not already_filed:
            log.info("#action not taken yet", extra=dict(value=value))

            already_detected = self.tdb.get_val(format_key_inactive(value))

            if already_detected:
                log.info("detection #awaiting #action", extra=dict(value=value))

                data = already_detected

                time_added = data.get('time_added', time())

                now = time()
                time_passed = now - time_added

                if time_passed > self.grace_period:
                    log.info("grace period has #passed", extra=dict(value=value))

                    self.acquire_lock()
                    try:
                        self.take_action(value, confidence, image, **dict(kwargs))
                    except Exception:
                        log.warning("#error taking #action", exc_info=True)
                    finally:
                        self.release_lock()
                else:
                    log.info("grace period has #not #passed", extra=dict(value=value))
            else:
                log.info("#entering grace period", extra=dict(value=value))

                self.tdb.set_val(format_key_inactive(value),
                                 dict(confidence=confidence, value=value,
                                      time_added=time()),
                                 ex=ceil(self.grace_period * 1.25))
        else:
            log.info("#action already #taken", extra=dict(value=value))

        log.info("#finished #analysis", extra=dict(value=value, confidence=confidence))
