from . import Executor
from config import log


class GateOpener(Executor):
    # @todo finish take action which should open the gate
    def action(self, plate, confidence, image, uuid, **kwargs):
        self.save_image(plate, image, uuid)

        self.rdb.index_result(plate, confidence, uuid, **dict(kwargs))

        log.info("#gate opened for #vehicle", extra=dict(plate=plate))
