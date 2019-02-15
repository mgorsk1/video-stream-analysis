from . import Executor
from config import log


class GateOpener(Executor):
    # @todo finish take action which should open the gate
    def take_action(self, plate, confidence, image):
        log.info("#gate opened for plate", extra=dict(plate=plate, confidence=confidence))
        pass
