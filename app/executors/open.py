from json import dumps
from time import time, sleep
from abc import abstractmethod, ABC

from app.config import log
from app.executors.base import BaseExecutor


class BaseOpener(ABC, BaseExecutor):
    def __init__(self, *args, **kwargs):
        super(BaseOpener, self).__init__(*args, **kwargs)

        self.open_time = kwargs.get('open_time', 120)

    def _action(self, value, confidence, image, uuid, **kwargs):
        super(BaseOpener, self)._action(value, confidence, image, uuid, **kwargs)

        self._open_gate(value)

        sleep(self.open_time)

        self._close_gate(value)

    def open(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.set_val(f'#{self.o} open', dumps(data))

        self._open(value)

        log.info(f"#{self.o} opened", extra=dict(value=value))

    def close(self, value):
        data = dict(timestamp=time(), value=value)

        self.tdb.del_val(f'#{self}:open')

        self._close(value)

        self.tdb.set_val(f'#{self}:close', dumps(data))

        log.info(f'#{self} closed', extra=dict(value=value))

    @abstractmethod
    def _open(self):
        pass

    @abstractmethod
    def _close(self):
        pass


class GateOpener(BaseExecutor):
    o = 'gate'

    def _open(self, value):
        # @todo below actually trigger opening gate
        pass

    def _close_gate(self, value):
        # @todo below actually trigger closing gate
        pass
