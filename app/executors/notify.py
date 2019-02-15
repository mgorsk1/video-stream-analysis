from . import Executor
from config import log


class PoliceNotifier(Executor):
    # @todo finish take action which should notify police
    def take_action(self, plate, confidence, image):
        log.info("#notification send about plate", extra=dict(plate=plate, confidence=confidence))
        pass
