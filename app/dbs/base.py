from abc import ABC, abstractmethod
from json import loads
from typing import Optional, Dict, Tuple

from app.config import log


class BaseDatabase(ABC):
    def __init__(self, *args, **kwargs):
        self.db = None

        self.init(*args, **kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def _get_val(self, key, **kwargs) -> Tuple[Optional[Dict], Optional[Dict]]:
        pass

    @abstractmethod
    def _set_val(self, key, value, **kwargs) -> Optional[Dict]:
        pass

    @abstractmethod
    def _del_val(self, key, **kwargs) -> Optional[Dict]:
        pass

    def get_val(self, key, **kwargs):
        extra = dict(key=key)
        extra['kwargs'] = kwargs
        log.info("#getting #value", extra=extra)

        try:
            result, metadata = self._get_val(key, **kwargs)
            extra['result'] = result
        except Exception as e:
            log.error("#error #retrieving data", extra=extra, exc_info=True)

            raise e

        log.info("value retrieved", extra=extra)

        return result

    def set_val(self, key, value, **kwargs):
        try:
            extra = dict(key=key, payload=loads(value), kwargs=kwargs)
        except TypeError:
            extra = dict(key=key, payload=value, kwargs=kwargs)

        try:
            result = self._set_val(key, value, **kwargs)
            extra['result'] = result

            log.info("#setting value", extra=extra)
        except Exception as e:
            log.error("#error #setting value", extra=extra, exc_info=True)

            raise e

        log.info("value #set", extra=extra)

    def del_val(self, key, **kwargs):
        extra = dict(key=key)
        extra['kwargs'] = kwargs

        log.info("#deleting value", extra=extra)

        try:
            result = self._del_val(key, **kwargs)
            extra.update(result)
        except Exception as e:
            log.error("#error #deleting value", extra=extra, exc_info=True)

            raise e

        log.info("value #deleted", extra=extra)
