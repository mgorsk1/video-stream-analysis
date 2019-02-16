from redis import Redis
from json import dumps
from elasticsearch import Elasticsearch, ElasticsearchException
from datetime import datetime

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
    def __init__(self, host, port, index):
        self.db = Elasticsearch(hosts=[dict(host=host, port=port)])

        self.index = index

    def check_if_exists(self, field, value, fuzzy):
        if fuzzy:
            query = {
                "query": {
                    "match": {
                        field: {
                            "query": value,
                            "fuzziness": 1
                        }
                    }
                }
            }
        else:
            query = {
                "query": {
                    "match": {
                        field: value
                    }
                }
            }

        try:
            search = self.db.search(self.index, 'default', query)
        except ElasticsearchException:
            log.error("#error querying #elasticsearch", exc_info=True)
            return False

        results = search.get('hits').get('hits')

        log.debug("#results for field #received", extra=dict(field=field,
                                                             value=value,
                                                             results=results))
        if len(results) > 0:
            return True
        else:
            return False

    def index_result(self, plate, confidence, id, **kwargs):
        body = dict(plate=plate, confidence=confidence, fileName="{}_{}.png".format(plate, id))
        body['@timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

        body.update(dict(kwargs))

        self.db.index(self.index, 'default', body, id=id)
        self.db.indices.refresh(self.index)
