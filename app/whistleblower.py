from app.database import TemporaryDatabase
from app.notify import Notifier
from json import loads
from time import time


class Whistleblower:
    def __init__(self, grace_period_seconds):
        # in seconds
        self.grace_period_seconds = grace_period_seconds

        self.db = TemporaryDatabase()

        self.notifier = Notifier(8)

    def process(self, plate, confidence, image):
        # check if record in redis
        #   if not - add to redis with expiration key of 2 minutes
        #   if yes - check how long it sits there
        #       if longer than 2 minutes - send to result database + notify police
        #   if no - do nothing

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


                if time_passed > self.grace_period_seconds:
                    #self.db.delete_key(plate)
                    self.notifier.notify(plate, confidence, image)
                return 1

            else:
                self.db.set_key(plate+':N',
                                dict(confidence=confidence,
                                     plate=plate,
                                     time_added=time()),
                                     ex=self.grace_period_seconds+60)

                return 0