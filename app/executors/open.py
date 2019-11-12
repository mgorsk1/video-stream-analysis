from abc import abstractmethod, ABC
from json import dumps
from time import time, sleep

from app.config import log
from app.executors.base import BaseExecutor
from app.tools import format_key_open, format_key_close


class BaseOpener(ABC, BaseExecutor):
    def __init__(self, *args, **kwargs):
        super(BaseOpener, self).__init__(*args, **kwargs)

        self.open_time = kwargs.get('opener_open_time', 120)

    def _action(self, value, confidence, image, uuid, **kwargs):
        super(BaseOpener, self)._action(value, confidence, image, uuid, **kwargs)

        self._open_gate(value)

        sleep(self.open_time)

        self._close_gate(value)

    def open(self, value):
        data = dict(timestamp=time(), value=value)
        log.info(f'#opening #{self.o}', extra=data)

        self.tdb.set_val(format_key_open(self.o), dumps(data))

        self._open(value)

        log.info(f'#{self.o} opened', extra=dict(value=value))

    def close(self, value):
        data = dict(timestamp=time(), value=value)
        log.info(f'#closing #{self.o}', extra=data)

        self.tdb.del_val(format_key_open(self.o))

        self._close(value)

        self.tdb.set_val(format_key_close(self.o), dumps(data))

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
