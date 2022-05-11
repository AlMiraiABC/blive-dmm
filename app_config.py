"""Application used configs"""


import os


class AppConfig:
    default_config_file = './defaultconfig.json'
    schema_file = './schema.json'
    config_file = os.environ.get('BLDM_CF', './config.json')
    required = {
        'room.id': (int, [0, '']),
        'user.id': (int, [0, '']),
        'credential.buvid3': (str, ['']),
        'credential.sessdata': (str, ['']),
        'credential.bili_jct': (str, ['']),
    }
