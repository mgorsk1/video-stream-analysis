from json import loads

from executors.open import GateOpener
from tools import format_whitelist_key
from config import log
from . import Analyzer


class Gatekeeper(Analyzer):
    def __init__(self, *args, **kwargs):
        super(Gatekeeper, self).__init__(*args, **kwargs)

        self.executor = GateOpener(3*60)

        whitelist = dict(kwargs).get('whitelist')

        if whitelist:
            for plate in whitelist:
                self.tdb.set_key(format_whitelist_key(plate), 'whitelisted')

    def process(self, plate, confidence, image, **kwargs):
        # check if gate already opened
        #   if yes - do nothing
        #   if no - check if plate in database
        #       if yes - open the gate, wait n-seconds, close the gate
        #       if no - do nothing

        gate_open = self.tdb.get_key('gate:open')

        if not gate_open:
            license_plate_allowed = self.tdb.get_key(format_whitelist_key(plate))

            if license_plate_allowed:
                self.executor.run(plate, confidence, image, **dict(kwargs))
            else:
                log.warning('#plate not in the #whitelist', extra=dict(plate=plate))
        else:
            log.warning('#gate already #opened', extra=dict(loads(gate_open)))
