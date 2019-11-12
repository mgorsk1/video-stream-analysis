from json import dumps, loads
from sys import exit

from redis import Redis

from app.config import log
from app.dbs.base import BaseDatabase


class TemporaryDatabase(BaseDatabase):
    def __init__(self, host, port, **kwargs):
        super(TemporaryDatabase, self).__init__(host, port, **kwargs)

        self.index = None

    def init(self, host, port, **kwargs):
        kwargs = dict(kwargs)

        db_pass = kwargs.get('db_pass')

        if db_pass:
            self.db = Redis(host=host, port=port, password=db_pass)
        else:
            self.db = Redis(host=host, port=port)

        try:
            db_info = self.db.info()

            log.info('established #connection with #redis', extra=dict(redis=db_info))
        except Exception:
            log.error('error while establishing #connection with #redis', exc_info=True)

            exit(1)

    def _get_val(self, key, **kwargs):
        result = self.db.get(key)

        try:
            result = loads(result)
        except TypeError:
            result = None

        return result, kwargs

    def _set_val(self, key, val, **kwargs):
        ex = dict(**kwargs).get('ex', False)

        if not isinstance(val, bytes):
            value_dumped = dumps(val).encode('utf-8')
        else:
            value_dumped = val

        if ex:
            self.db.set(key, value_dumped, ex=ex, nx=True)
        else:
            self.db.set(key, value_dumped, nx=True)

        return kwargs

    def _del_val(self, key):
        self.db.delete(key)
