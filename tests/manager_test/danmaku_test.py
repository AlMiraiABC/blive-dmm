import asyncio
import json
import os
from tempfile import mkstemp
from unittest import IsolatedAsyncioTestCase

from manager.config import Config
from manager.danmaku import Danmaku

CONFIG = {
    "room": {
        "id": os.environ.get("BLDM_ROOM_ID")
    },
    "credential": {
        "buvid3": os.environ.get('BLDM_BUVID3'),
        "sessdata": os.environ.get('BLDM_SESSDATA'),
        "bili_jct": os.environ.get('BLDM_BILI_JCT')
    }
}


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

    async def test_send(self):
        resp = await self.danmaku.send('test message')
        print(resp)

    async def test_client(self):
        await self.danmaku.start()
        await asyncio.sleep(30)
        await self.danmaku.stop()
