import logging
import logging.config
from datetime import datetime
from json import loads
from os import path, makedirs
from sys import exc_info

import pythonjsonlogger.jsonlogger


class CustomJsonFormatter(pythonjsonlogger.jsonlogger.JsonFormatter):
    # list of fields that need to be renamed
    keys_to_rename = [('levelname', 'level'), ('lineno', 'lineNo'), ('exc_info', 'exception')]

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # add timestamp here since we cannot achieve this with datefmt in config
        log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

        for mapping in self.keys_to_rename:
            old, new = mapping

            # check if field exists and needs to be renamed and if so - rename accordingly
            try:
                log_record[new] = log_record.pop(old)
            except KeyError:
                pass


class CustomLoggingAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        try:
            mdc = kwargs.pop('extra')

            kwargs['extra'] = dict(mdc=mdc)
            kwargs['extra'].update(self.extra)
        except KeyError:
            kwargs['extra'] = self.extra
        finally:
            return msg, kwargs


def prepare(log_level, log_dir, app_name, **kwargs):
    log_dir = log_dir if log_dir.endswith('/log') else '{}/log'.format(log_dir)

    # create log_dir
    try:
        if not path.exists(log_dir):
            makedirs(log_dir)
    except Exception:
        print(exc_info())

    # load json config and replace placeholders with actual values
    with open('{}/../config/logger/main.json'.format(path.dirname(path.realpath(__file__))), 'r') as f:
        d = f.read()

        d = d.replace('{log_file_path}', log_dir)
        d = d.replace('{log_level}', log_level)
        d = d.replace('{app_name}', app_name)

    logging.config.dictConfig(loads(d))

    log_tmp = logging.getLogger(app_name)
    log = CustomLoggingAdapter(log_tmp, dict(kwargs))

    return log
