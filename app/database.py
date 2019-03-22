from datetime import datetime, timedelta
from json import dumps
from ssl import create_default_context

from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError
from redis import Redis
from sys import exit
from abc import abstractmethod

from app.config import log


class Database:
    def __init__(self, *args, **kwargs):
        self.db = None

        self.init(*args, **kwargs)

    @abstractmethod
    def init(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_val(self, key, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def set_val(self, key, value, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def del_val(self, key, **kwargs):
        raise NotImplementedError


class TemporaryDatabase(Database):
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


class ResultDatabase(Database):
    def __init__(self, host, port, index, **kwargs):
        super(ResultDatabase, self).__init__(host, port, index, **kwargs)

        self.index = index

    def init(self, host, port, index, **kwargs):
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

        self._install_index_template('video-analysis')

        self._create_index()

    def get_val(self, key, **kwargs):
        field = dict(kwargs).get('field')

        time_ago = datetime.utcnow() - timedelta(seconds=dict(kwargs).get('ago'))
        time_ago = time_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')

        try:
            self.db.indices.refresh(self.index)
        except NotFoundError:
            pass

        if dict(kwargs).get('fuzzy', False):
            query = {"query": {"bool": {"must": {"match": {field: {"query": key, "fuzziness": 1}}},
                "filter": {"range": {"@timestamp": {"gte": time_ago}}}}}}
        else:
            query = {"query": {
                "bool": {"must": {"match": {field: key}}, "filter": {"range": {"@timestamp": {"gte": time_ago}}}}}}
        try:
            search = self.db.search(self.index, 'default', query)
        except ElasticsearchException:
            log.error("#error querying #elasticsearch", exc_info=True)
            return None

        results = search.get('hits').get('hits')

        log.debug("#results for field #received", extra=dict(field=field, value=key, results=results))

        if len(results) > 0:
            return results
        else:
            return None

    def set_val(self, key, value, **kwargs):
        body = value
        body['@timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

        body.update(dict(kwargs))

        self.db.index(self.index, 'default', body, id=id)

        log.info('#indexed doc', extra=dict(value=value, id=id))

        self.db.indices.refresh(self.index)

    def del_val(self, key):
        try:
            self.db.delete(index=self.index, doc_type='default', id=key)
        except ElasticsearchException as e:
            log.error("#error while #delete document", exc_info=True, extra=dict(id=key))

    def _create_index(self):
        try:
            self.db.indices.create(self.index)
            log.info("#index successfully #created", extra=dict(index=self.index))
        except ElasticsearchException as e:
            log.error("#error #creating #index", exc_info=True, extra=dict(index=self.index))

    def _install_index_template(self, template_name):
        template_name_file = template_name.replace('-', '_') + '_template.json'

        if not self._check_if_template_exists(template_name):
            with open('../resources/elastic/{}'.format(template_name_file)) as f:
                template_body = f.read()

            try:
                if template_body is not None:
                    self.db.indices.put_template(name=template_name, body=template_body, master_timeout="60s")

                    log.info("Template {0} successfully registered".format(template_name))
                else:
                    log.warning('Template body {0} does not exist - index template has not been registered'.format(
                        template_name))
            except ElasticsearchException as e:
                log.error('Error registering index template: {e}'.format(e=e.args))
                raise e

    def _check_if_template_exists(self, template_name):
        try:
            self.db.indices.get_template(template_name)

            return True
        except NotFoundError:
            return False
