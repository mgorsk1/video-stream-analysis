from datetime import datetime, timedelta
from ssl import create_default_context
from sys import exit
from uuid import uuid4

from elasticsearch import Elasticsearch, ElasticsearchException, NotFoundError

from app.config import log
from app.dbs.base import BaseDatabase


class ResultDatabase(BaseDatabase):
    def __init__(self, host, port, index, **kwargs):
        super(ResultDatabase, self).__init__(host, port, index, **kwargs)

        self.index = index
        self.index_type = kwargs.get('elasticsearch_index_type', '_doc')

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
        except ElasticsearchException:
            log.error("error while establishing #connection with #elasticsearch", exc_info=True)

            exit(1)

        self.index = index

        self._install_index_template('video-analysis')

        self._create_index()

    def _get_val(self, key, **kwargs):
        field = dict(kwargs).get('field')

        extra = dict(key=key)
        extra['kwargs'] = kwargs

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

        search = self.db.search(self.index, self.index_type, query)

        results = search.get('hits').get('hits')

        if len(results) > 0:
            return results, extra
        else:
            return None, extra

    def _set_val(self, key, value, **kwargs):
        extra = dict(index=self.index, doc_type=self.index_type)
        extra['kwargs'] = kwargs

        body = value
        body['@timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

        _id = uuid4()

        body.update(dict(kwargs))

        self.db.index(self.index, self.index_type, body, id=_id)

        self.db.indices.refresh(self.index)

        return extra

    def _del_val(self, key):
        extra = dict(index=self.index, doc_type=self.index_type, key=key)

        self.db.delete(index=self.index, doc_type=self.index_type, id=key)

        return extra

    def _create_index(self):
        try:
            self.db.indices.create(self.index)
            log.info("#index successfully #created", extra=dict(index=self.index))
        except ElasticsearchException:
            log.warn("#index #exists", exc_info=True, extra=dict(index=self.index))

    def _install_index_template(self, template_name):
        template_name_file = template_name.replace('-', '_') + '_template.json'

        if not self._check_if_template_exists(template_name):
            with open('../resources/elastic/{}'.format(template_name_file)) as f:
                template_body = f.read()

            try:
                if template_body is not None:
                    self.db.indices.put_template(name=template_name, body=template_body, master_timeout="60s")

                    log.info("#template successfully #registered", extra=dict(template_name=template_name,
                                                                              template_body=template_body))
                else:
                    log.warning('#template body does #not #exist - index template has not been registered',
                                extra=dict(template_name=template_name))
            except ElasticsearchException as e:
                log.warn('#template #exists', extra=dict(template_name=template_name),
                         exc_info=True)

                raise e

    def _check_if_template_exists(self, template_name):
        try:
            self.db.indices.get_template(template_name)

            return True
        except NotFoundError:
            return False
