import json
import os
from tempfile import mkstemp
from unittest import TestCase
from manager.config import Config

CONFIG = {
    "room": {
        "id": 123
    },
}


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (fd, fn) = mkstemp(text=True)
        with open(fd,'w', encoding='utf-8') as cf:
            json.dump(CONFIG,cf)
        cls.cf = fn
        cls.config = Config(fn)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.cf)

    def test_get_room(self):
        room = self.config.get_room()
        self.assertDictEqual(room, CONFIG['room'])
