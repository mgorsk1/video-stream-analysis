def format_value_active(value):
    return ':'.join([value, 'Y'])


def format_value_inactive(value):
    return ':'.join([value, 'N'])


def format_whitelist_key(value):
    return ':'.join(['whitelist', value])
