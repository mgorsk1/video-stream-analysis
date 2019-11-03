from json import loads

from app.analyzers.base import BaseAnalyzer
from app.config import log
from app.tools import format_whitelist_key

__all__ = ['Gatekeeper']


class Gatekeeper(BaseAnalyzer):
    def __init__(self, *args, **kwargs):
        super(Gatekeeper, self).__init__(*args, **kwargs)

        whitelist = dict(kwargs).get('whitelist')

        if whitelist:
            for value in whitelist:
                self.tdb.set_val(format_whitelist_key(value), 'whitelisted')

    def _analyze(self, value, confidence, image, **kwargs):
        # check if gate already opened
        #   if yes - do nothing
        #   if no - check if value in database
        #       if yes - open the gate, wait n-seconds, close the gate
        #       if no - do nothing
        log.info("#starting #analysis", extra=dict(value=value))

        gate_open = self.tdb.get_val('gate:open')

        if not gate_open:
            log.info("#gate #not #opened yet", extra=dict(value=value))

            license_value_allowed = self.tdb.get_val(format_whitelist_key(value))

            if license_value_allowed:
                log.info("license plate #allowed", extra=dict(value=value))

                self.take_action(value, confidence, image, **dict(kwargs))
            else:
                log.warning('license plate #not #allowed', extra=dict(value=value))
        else:
            log.warning('#gate already #opened', extra=dict(loads(gate_open)))

        log.info("#finished #analysis", extra=dict(value=value))
