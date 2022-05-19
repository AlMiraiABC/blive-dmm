import json
import os
from unittest import TestCase

from al_utils.singleton import DEFAULT_CONTAINER_NAME, _containers
from app_config import AppConfig
from manager.config import Config
from utils.config_util import ConfigUtil


class TestConfig(TestCase):
    def setUp(self) -> None:
        _containers[DEFAULT_CONTAINER_NAME].pop(Config, None)

    def prepare(self, config: dict, verify: bool = True, default: dict = None):
        if verify:
            schema = AppConfig.schema_file
        else:
            schema = {}
        self.config = Config(ConfigUtil(config, schema, default))

    def test_get_room(self):
        CONFIG = {
            "room": {
                "id": 123
            },
        }
        self.prepare(CONFIG, False)
        room = self.config.get_room()
        self.assertDictEqual(room, CONFIG['room'])

    def test_get_danmaku(self):
        CONFIG = {
            "danmaku": {
                "style": {
                    "color": "ababab",
                }
            }
        }
        DEFAULT = {
            "danmaku": {
                "style": {
                    "color": "ffffff",
                    "position": "scroll"
                }
            }
        }
        expect = {
            "danmaku": {
                "style": {
                    "color": "ababab",
                    "position": "scroll"
                }
            }
        }
        self.prepare(CONFIG, False, DEFAULT)
        danmaku = self.config.get_danmaku()
        self.assertDictEqual(danmaku, expect["danmaku"])

    def test_reply(self):
        CONFIG = {
            "reply": {
                "enable": ['a', 'b']
            }
        }
        DEFAULT = {
            "reply": {
                "a": 1,
                "b": 2,
                "enable": []
            }
        }
        expect = {
            "reply": {
                "a": 1,
                "b": 2,
                "enable": ['a', 'b']
            }
        }
        self.prepare(CONFIG, False, DEFAULT)
        reply = self.config.get_reply()
        self.assertDictEqual(reply, expect["reply"])

    def test_from_env(self):
        BLDM_ROOM_ID = '1234567'
        os.environ['BLDM_ROOM_ID'] = BLDM_ROOM_ID
        config = Config(ConfigUtil({}, AppConfig.schema_file,
                                   AppConfig.default_config_file, AppConfig.required,
                                   AppConfig.resolver))
        self.assertEqual(config.get_room()["id"], BLDM_ROOM_ID)
