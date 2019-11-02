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
        log.info("performing #analysis", extra=dict(value=value, confidence=confidence))

        gate_open = self.tdb.get_val('gate:open')

        if not gate_open:
            license_value_allowed = self.tdb.get_val(format_whitelist_key(value))

            if license_value_allowed:
                self.take_action(value, confidence, image, **dict(kwargs))
            else:
                log.warning('#value not in the #whitelist', extra=dict(value=value))
        else:
            log.warning('#gate already #opened', extra=dict(loads(gate_open)))
