import functools

from app.config import log


def format_key_active(key):
    return ':'.join([key, 'Y'])


def format_key_inactive(key):
    return ':'.join([key, 'N'])


def format_whitelist_key(key):
    return ':'.join(['whitelist', key])


def format_key_open(key):
    return ':'.join([key, 'open'])


def format_key_close(key):
    return ':'.join([key, 'close'])


def log_function(func):
    f_name = func.__name__
    f_module = func.__module__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log.debug("#started #function", extra=dict(function=f_name, module=f_module, args=args, kwargs=kwargs))
        res = func(*args, **kwargs)
        log.debug("#finished #function", extra=dict(function=f_name, module=f_module, args=args, kwargs=kwargs))
        return res

    return wrapper
