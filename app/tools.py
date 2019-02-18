def format_plate_active(plate):
    return ':'.join([plate, 'Y'])


def format_plate_inactive(plate):
    return ':'.join([plate, 'N'])


def format_whitelist_key(plate):
    return ':'.join(['whitelist', plate])
