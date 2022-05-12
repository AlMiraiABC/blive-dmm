"""Application used configs"""


import os

from jsonschema import RefResolver

SCHEMA_DIR = os.path.realpath('./schema')


class AppConfig:
    default_config_file = './defaultconfig.json'
    schema_file = './schema/index.json'
    config_file = os.environ.get('BLDM_CF', './config.json')
    required = {
        'room.id': (int, [0, '']),
        'user.id': (int, [0, '']),
        'credential.buvid3': (str, ['']),
        'credential.sessdata': (str, ['']),
        'credential.bili_jct': (str, ['']),
    }
    resolver = RefResolver(f'file://{SCHEMA_DIR}/', None)


class NotifyConfig:
    schema_file = './schema/notify.json'
    required = {
        'sender.email': (str, ['']),
        'server.host': (str, ['']),
        'server.passcode': (str, ['']),
    }
