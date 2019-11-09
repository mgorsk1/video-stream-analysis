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
