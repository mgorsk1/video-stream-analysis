from json import dumps
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

            log.info("established #connection with #redis", extra=dict(elasticsearch=db_info))
        except Exception as e:
            log.error("error while establishing #connection with #redis", exc_info=True)

            exit(1)

    def get_val(self, key, **kwargs):
        result = self.db.get(key)

        log.debug('#received result for #redis #key', extra=dict(key=key, result=result))

        return result

    def set_val(self, key, val, **kwargs):
        ex = dict(**kwargs).get('ex', False)

        if not isinstance(val, bytes):
            value_dumped = dumps(val).encode('utf-8')
        else:
            value_dumped = val

        if ex:
            self.db.set(key, value_dumped, ex=ex, nx=True)
        else:
            self.db.set(key, value_dumped, nx=True)

        log.debug('#set value for #redis #key', extra=dict(key=key, value=value_dumped))

    def del_val(self, key):
        self.db.delete(key)

        log.debug('#deleted #redis #key', extra=dict(key=key))
