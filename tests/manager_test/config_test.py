import json
import os
from tempfile import mkstemp
from unittest import TestCase
from manager.config import Config


class TestConfig(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.cfn = ''
        self.cfnv = ''
        self.cfnd = ''

    def tearDown(self) -> None:
        for n in [self.cfn, self.cfnv, self.cfnd]:
            if n:
                os.remove(n)

    def prepare(self, config: dict, verify: bool = True, default: dict = None):
        ps = {}
        (fd, fn) = mkstemp(text=True)
        with open(fd, 'w', encoding='utf-8') as cf:
            json.dump(config, cf)
        self.cfn = fn
        ps['config_file'] = fn
        if default:
            (fdd, fnd) = mkstemp(text=True)
            with open(fdd, 'w', encoding='utf-8') as cfd:
                json.dump(default, cfd)
            self.cfnd = fnd
            ps['default_config_file'] = fnd
        if not verify:
            (fdv, fnv) = mkstemp(text=True)
            with open(fdv, 'w', encoding='utf-8') as cfv:
                json.dump({}, cfv)
            self.cfnv = fnv
            ps['schema_file']=fnv
        self.config = Config(**ps)

    def test_get_room(self):
        CONFIG = {
            "room": {
                "id": 123
            },
        }
        self.prepare(CONFIG, False)
        room = self.config.get_room()
        self.assertDictEqual(room, CONFIG['room'])

    def test_combine(self):
        CONFIG = {}
        self.prepare(CONFIG, False)
        d = {"k1": 1, "k2": 2, "k3": [123], "k4": {"k1": 1}, "k5": {"k1": 1}}
        u = {"k1": 11, "k3": [321], "k4": {"k1": 11}}
        expect = {"k1": 11, "k2": 2, "k3": [
            321], "k4": {"k1": 11}, "k5": {"k1": 1}}
        result = self.config.combine(d, u)
        self.assertDictEqual(expect, result)

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
