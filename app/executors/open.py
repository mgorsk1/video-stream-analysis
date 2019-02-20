from json import dumps
from time import time, sleep

from app.config import log
from . import Executor


class GateOpener(Executor):
    def __init__(self, *args, **kwargs):
        super(GateOpener, self).__init__(*args, **kwargs)

        self.open_time = 120

    def action(self, value, confidence, image, uuid, **kwargs):
        self.open_gate(value)

        self.save_image(value, image, uuid)

        self.rdb.index_result(value, confidence, uuid, **dict(kwargs))

        sleep(self.open_time)

        self.close_gate(value)

    def open_gate(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.set_key('gate:open', dumps(data))

        # @todo below actually trigger opening gate

        log.info("#gate opened for #vehicle", extra=dict(value=value))

    def close_gate(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.delete_key('gate:open')

        # @todo below actually trigger closing gate

        self.tdb.set_key('gate:close', dumps(data))

        log.info("#gate closed", extra=dict(value=value))
