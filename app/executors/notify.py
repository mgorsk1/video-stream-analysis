from . import Executor
from config import log


class PoliceNotifier(Executor):
    # @todo finish take action which should notify police
    def take_action(self, plate, confidence, image, uuid, **kwargs):
        key = plate + ':Y'

        if not self.rdb.check_if_exists(self.index_name, plate, False):
            log.info("#plate does not exist in result #database", extra=dict(plate=plate))
            if not self.rdb.check_if_exists('plate', plate, True):
                log.info("#similar #plate does not exist in result #database", extra=dict(plate=plate))
                if not self.rdb.check_if_exists('candidates', plate, False):
                    log.info("#plate does not exist amongst candidates in #database", extra=dict(plate=plate))

                    self.save_image(plate, image, uuid)

                    self.rdb.index_result(plate, confidence, uuid, **dict(kwargs))

                    log.info("#notification send about plate", extra=dict(plate=plate, confidence=confidence))
                else:
                    log.info("#plate existed amongst candidates in #database", extra=dict(plate=plate))
            else:
                log.info("#plate matched another #similar plate in #database", extra=dict(plate=plate))
        else:
            log.info("#plate existed in #database", extra=dict(plate=plate))

        pass
