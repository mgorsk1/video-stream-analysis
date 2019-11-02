from json import loads
from time import time

from app.analyzers.base import BaseAnalyzer
from app.config import log
from app.executors.notify import PoliceNotifier
from app.tools import format_key_active, format_key_inactive

__all__ = ['PoliceWhistleblower']


class PoliceWhistleblower(PoliceNotifier, BaseAnalyzer):
    def __init__(self, *args, **kwargs):
        print("WHISTLEBLOWER INIT")
        super(PoliceWhistleblower, self).__init__(*args, **kwargs)

    def analyze(self, value, confidence, image, **kwargs):
        # check if already notified about value
        #   if not - check if already detected value
        #       if yes - check value whether it's within its grace_period
        #           if yes - check how long it sits there and if exceeded grace_period - notify
        #           if no - skip
        #       if no - add to redis
        #   if yes - do nothing
        log.info("performing #analysis", extra=dict(value=value, confidence=confidence))

        already_filed = self.tdb.get_val(format_key_active(value))

        if not already_filed:
            already_detected = self.tdb.get_val(format_key_inactive(value))

            if already_detected:

                data = loads(already_detected.decode('utf-8'))

                time_added = data.get('time_added', time())

                now = time()
                time_passed = now - time_added

                if time_passed > self.grace_period:
                    self.take_action(value, confidence, image, **dict(kwargs))
            else:
                self.tdb.set_val(format_key_inactive(value),
                                 dict(confidence=confidence, value=value,
                                      time_added=time()),
                                 ex=self.grace_period + 60)
        else:
            log.info("detection already filed", extra=dict(value=value))
