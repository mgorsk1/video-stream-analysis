def format_key_active(key):
    return ':'.join([key, 'Y'])


def format_key_inactive(key):
    return ':'.join([key, 'N'])


def format_whitelist_key(key):
    return ':'.join(['whitelist', key])
