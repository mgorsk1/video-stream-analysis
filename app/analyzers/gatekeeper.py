from json import loads

from app.executors.open import GateOpener
from app.tools import format_whitelist_key
from app.config import log
from . import Analyzer


class Gatekeeper(Analyzer):
    def __init__(self, *args, **kwargs):
        super(Gatekeeper, self).__init__(*args, **kwargs)

        self.executor = GateOpener(self.reset_after)

        whitelist = dict(kwargs).get('whitelist')

        if whitelist:
            for value in whitelist:
                self.tdb.set_key(format_whitelist_key(value), 'whitelisted')

    def process(self, value, confidence, image, **kwargs):
        # check if gate already opened
        #   if yes - do nothing
        #   if no - check if value in database
        #       if yes - open the gate, wait n-seconds, close the gate
        #       if no - do nothing

        gate_open = self.tdb.get_key('gate:open')

        if not gate_open:
            license_value_allowed = self.tdb.get_key(format_whitelist_key(value))

            if license_value_allowed:
                self.executor.run(value, confidence, image, **dict(kwargs))
            else:
                log.warning('#value not in the #whitelist', extra=dict(value=value))
        else:
            log.warning('#gate already #opened', extra=dict(loads(gate_open)))
