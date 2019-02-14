from app.database import TemporaryDatabase
from app.notify import Notifier
from json import loads
from time import time

from . import Analyzer


class Whistleblower(Analyzer):
    def __init__(self, grace_period):
        # in seconds
        self.grace_period = grace_period

        self.db = TemporaryDatabase()

        self.notifier = Notifier(8*60*60)

    def process(self, plate, confidence, image):
        # check if already notified about plate
        #   if not - check if already detected plate
        #       if yes - check plate whether it's within its grace_period
        #           if yes - check how long it sits there and if exceeded grace_period - notify
        #           if no - skip
        #       if no - add to redis
        #   if yes - do nothing
        # statuses: 0 - plate completely new, 1 - plate within grace period, 2 - plate already filed

        already_filed = self.db.get_key(plate+':Y')

        if already_filed:
            return 2
        else:
            already_detected = self.db.get_key(plate+':N')

            if already_detected:

                data = loads(already_detected.decode('utf-8'))

                time_added = data.get('time_added', time())

                now = time()
                time_passed = now - time_added

                if time_passed > self.grace_period:
                    self.notifier.notify(plate, confidence, image)
                    return 2
                else:
                    return 1
            else:
                self.db.set_key(plate+':N',
                                dict(confidence=confidence,
                                     plate=plate,
                                     time_added=time()),
                                     ex=self.grace_period+60)

                return 0