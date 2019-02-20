from json import loads
from time import time

from app.executors.notify import PoliceNotifier
from app.tools import format_plate_active, format_plate_inactive
from . import Analyzer


class Whistleblower(Analyzer):
    def __init__(self, *args, **kwargs):
        super(Whistleblower, self).__init__(*args, **kwargs)

        self.executor = PoliceNotifier(self.reset_after)

    def process(self, plate, confidence, image, **kwargs):
        # check if already notified about plate
        #   if not - check if already detected plate
        #       if yes - check plate whether it's within its grace_period
        #           if yes - check how long it sits there and if exceeded grace_period - notify
        #           if no - skip
        #       if no - add to redis
        #   if yes - do nothing

        already_filed = self.tdb.get_key(format_plate_active(plate))

        if not already_filed:
            already_detected = self.tdb.get_key(format_plate_inactive(plate))

            if already_detected:

                data = loads(already_detected.decode('utf-8'))

                time_added = data.get('time_added', time())

                now = time()
                time_passed = now - time_added

                if time_passed > self.grace_period:
                    self.executor.run(plate, confidence, image, **dict(kwargs))
            else:
                self.tdb.set_key(format_plate_inactive(plate),
                                 dict(confidence=confidence,
                                      plate=plate,
                                      time_added=time()),
                                      ex=self.grace_period+60)

