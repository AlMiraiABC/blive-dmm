"""Application used configs"""


import os

from jsonschema import RefResolver

from utils.config_util import VALID

SCHEMA_DIR = os.path.realpath('./schema')


class AppConfig:
    default_config_file = './config.default.json'
    schema_file = './schema/index.json'
    config_file = os.environ.get('BLDM_CF', './config.json')
    required: dict[str, VALID] = {
        'room.id': ([str], ['']),
        'user.id': ([str], ['']),
        'credential.buvid3': ([str], ['']),
        'credential.sessdata': ([str], ['']),
        'credential.bili_jct': ([str], ['']),
    }
    resolver = RefResolver(f'file://{SCHEMA_DIR}/', None)


class NotifyConfig:
    default_config_file = './config.notify.default.json'
    schema_file = './schema/notify.json'
    required = {
        'sender.email': ([str], ['']),
        'server.host': ([str], ['']),
        'server.passcode': ([str], ['']),
    }


class ScheduleConfig:
    schema_file = './schema/schedule.json'
