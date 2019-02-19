from datetime import datetime, timedelta
from json import dumps
from ssl import create_default_context

from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError
from redis import Redis

from config import log


class TemporaryDatabase:
    def __init__(self, host, port, **kwargs):
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

    def get_key(self, key):
        result = self.db.get(key)

        log.debug('#received result for #redis #key', extra=dict(key=key, result=result))

        return result

    def set_key(self, key, value, ex=None):
        if not isinstance(value, bytes):
            value_dumped = dumps(value).encode('utf-8')
        else:
            value_dumped = value

        if ex:
            self.db.set(key, value_dumped, ex=ex, nx=True)
        else:
            self.db.set(key, value_dumped, nx=True)

        log.debug('#set value for #redis #key', extra=dict(key=key, value=value_dumped))

    def delete_key(self, key):
        self.db.delete(key)

        log.debug('#deleted #redis #key', extra=dict(key=key))


class ResultDatabase:
    def __init__(self, host, port, index, **kwargs):

        kwargs = dict(kwargs)

        db_user = kwargs.get('db_user') if kwargs.get('db_user') else 'elastic'
        db_pass = kwargs.get('db_pass') if kwargs.get('db_pass') else 'changeme'

        db_scheme = kwargs.get('db_scheme') if kwargs.get('db_scheme') else 'http'

        context = create_default_context() if db_scheme.endswith('s') else None

        self.db = Elasticsearch(hosts=[dict(host=host, port=port)], http_auth=(db_user, db_pass), scheme=db_scheme,
                                ssl_context=context)

        try:
            db_info = self.db.info()

            log.info("established #connection with #elasticsearch", extra=dict(elasticsearch=db_info))
        except Exception as e:
            log.error("error while establishing #connection with #elasticsearch", exc_info=True)

            exit(1)

        self.index = index

        self._install_index_template()

    def check_if_exists(self, field, value, ago, fuzzy):
        time_ago = datetime.utcnow() - timedelta(seconds=ago)
        time_ago = time_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')

        try:
            self.db.indices.refresh(self.index)
        except NotFoundError:
            pass

        if fuzzy:
            query = {"query": {"bool": {"must": {"match": {field: {"query": value, "fuzziness": 1}}},
                "filter": {"range": {"@timestamp": {"gte": time_ago}}}}}}
        else:
            query = {"query": {
                "bool": {"must": {"match": {field: value}}, "filter": {"range": {"@timestamp": {"gte": time_ago}}}}}}
        try:
            search = self.db.search(self.index, 'default', query)
        except ElasticsearchException:
            log.error("#error querying #elasticsearch", exc_info=True)
            return False

        results = search.get('hits').get('hits')

        log.debug("#results for field #received", extra=dict(field=field, value=value, results=results))
        if len(results) > 0:
            return True
        else:
            return False

    def index_result(self, plate, confidence, id, **kwargs):
        body = dict(plate=plate, confidence=confidence)
        body['@timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

        body.update(dict(kwargs))

        self.db.index(self.index, 'default', body, id=id)

        log.info('#indexed doc for plate', extra=dict(plate=plate, confidence=confidence, id=id))

        self.db.indices.refresh(self.index)

    # @todo
    def _install_index_template(self):
        pass

    # @todo
    def _check_if_template_exists(self):
        pass
