from . import Executor


class PoliceNotifier(Executor):
    # @todo finish take action which should notify police
    def take_action(self, plate, confidence, image):
        print('notified about plate {}'.format(plate))
        pass
