from . import Analyzer
from app.executors.open import GateOpener


class Gatekeeper(Analyzer):
    def __init__(self, *args, **kwargs):
        super(Gatekeeper, self).__init__(*args, **kwargs)

        self.executor = GateOpener(3*60)

    def process(self, plate, confidence, image):
        # check if already opened the gate for this car
        #   if yes - do nothing
        #   if no - check if plate in database
        #       if yes - open the gate
        #       if no - do nothing

        already_opened = self.tdb.get_key(plate+':Y')

        if not already_opened:
            license_plate_allowed = self.tdb.get_key(plate+':A')

            if license_plate_allowed:
                self.executor.run(plate, confidence, image)
