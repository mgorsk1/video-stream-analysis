from json import dumps
from time import time, sleep

from app.config import log
from app.executors.base import BaseExecutor


class GateOpener(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super(GateOpener, self).__init__(*args, **kwargs)

        self.open_time = 120

    def _action(self, value, confidence, image, uuid, **kwargs):
        file = super(GateOpener, self)._action(value, confidence, image, uuid)

        self._open_gate(value)

        sleep(self.open_time)

        self._close_gate(value)

    def _open_gate(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.set_val('gate:open', dumps(data))

        # @todo below actually trigger opening gate

        log.info("#gate opened for #vehicle", extra=dict(value=value))

    def _close_gate(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.del_val('gate:open')

        # @todo below actually trigger closing gate

        self.tdb.set_val('gate:close', dumps(data))

        log.info("#gate closed", extra=dict(value=value))
