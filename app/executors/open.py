from . import Executor


class GateOpener(Executor):
    # @todo finish take action which should open the gate
    def take_action(self, plate, confidence, image):
        print('opened gate for plate {}'.format(plate))
        pass
