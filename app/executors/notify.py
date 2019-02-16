from . import Executor
from config import log


class PoliceNotifier(Executor):
    # @todo finish action which should notify police
    def action(self, plate, confidence, image, uuid, **kwargs):
        self.save_image(plate, image, uuid)

        self.rdb.index_result(plate, confidence, uuid, **dict(kwargs))

        log.info("#police notified about #rascal", extra=dict(plate=plate))
