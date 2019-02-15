from redis import Redis
from json import dumps
from elasticsearch import Elasticsearch

from config import log


class TemporaryDatabase:
    def __init__(self, host, port):
        try:
            self.db = Redis(host=host, port=port)
        except Exception as e:
            log.error('#error establishing connection with #redis', exc_info=True, extra=dict(host=host, port=port))

        log.info('#established connection with #redis', extra=dict(host=host, port=port))

    def get_key(self, key):
        result = self.db.get(key)

        log.debug('#received result for #redis #key', extra=dict(key=key, result=result))

        return result

    def set_key(self, key, value, ex=None):
        if not isinstance(value, bytes):
            vaule_dumped = dumps(value).encode('utf-8')
        else:
            vaule_dumped = value

        if ex:
            self.db.set(key, vaule_dumped, ex=ex, nx=True)
        else:
            self.db.set(key, vaule_dumped, nx=True)

        log.debug('#set value for #redis #key', extra=dict(key=key, value=value))

    def delete_key(self, key):
        self.db.delete(key)

        log.debug('#deleted #redis #key', extra=dict(key=key))


class ResultDatabase:
    def __init__(self):
        self.db = Elasticsearch()

    def check_if_exists(self, field, value, fuzzy):
        fuzzy_query = dict()
        pass
