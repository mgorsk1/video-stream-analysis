from json import dumps
from time import time, sleep

from app.config import log
from . import Executor


class GateOpener(Executor):
    def __init__(self, *args, **kwargs):
        super(GateOpener, self).__init__(*args, **kwargs)

        self.open_time = 120

    def action(self, plate, confidence, image, uuid, **kwargs):
        self.open_gate(plate)

        self.save_image(plate, image, uuid)

        self.rdb.index_result(plate, confidence, uuid, **dict(kwargs))

        sleep(self.open_time)

        self.close_gate(plate)

    def open_gate(self, plate):
        data = dict(timestamp=time(), plate=plate)

        self.tdb.set_key('gate:open', dumps(data))

        # @todo below actually trigger opening gate

        log.info("#gate opened for #vehicle", extra=dict(plate=plate))

    def close_gate(self, plate):
        data = dict(timestamp=time(), plate=plate)

        self.tdb.delete_key('gate:open')

        # @todo below actually trigger closing gate

        self.tdb.set_key('gate:close', dumps(data))

        log.info("#gate closed", extra=dict(plate=plate))
