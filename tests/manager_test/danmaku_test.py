import json
import os
from tempfile import mkstemp
from unittest import IsolatedAsyncioTestCase, skipIf

from manager.config import Config
from manager.danmaku import Danmaku

"""
NOTE: UPDATE CONFIG BEFORE TESTING.
"""
CONFIG = {
    "room": {
        "id": 7441943
    },
    "credential": {
        "buvid3": "45D4111E-FD6B-5590-1F82-331BAFC4E5DE14331infoc",
        "sessdata": "04bb406b%2C1667457161%2C2b200*51",
        "bili_jct": "fa1d1a08fd208116f49826c62a9b4e7d"
    }
}

START_LIVE = False


class TestDanmaku(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (fd, fn) = mkstemp(text=True)
        with open(fd, 'w', encoding='utf-8') as cf:
            json.dump(CONFIG, cf)
        cls.cf = fn
        cls.config = Config(fn)
        cls.danmaku = Danmaku()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.cf)

    @skipIf(START_LIVE)
    async def test_send(self):
        resp = await self.danmaku.send('test message')
        print(resp)
