from redis import Redis
from json import dumps


class TemporaryDatabase:
    def __init__(self):
        self.db = Redis(host="localhost", port=6379)

    def get_key(self, key):
        result = self.db.get(key)

        return result

    def set_key(self, key, value, ex=None):
        if not isinstance(value, bytes):
            value = dumps(value).encode('utf-8')

        if ex:
            self.db.set(key, value, ex=ex, nx=True)
        else:
            self.db.set(key, value, nx=True)

    def delete_key(self, plate):
        self.db.delete(plate)


class ResultDatabase:
    def __init__(self):
        self.db = 1