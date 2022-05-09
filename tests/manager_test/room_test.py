import asyncio
import json
import os
from tempfile import mkstemp
from unittest import IsolatedAsyncioTestCase
from manager.config import Config
from manager.room import Room, format_message

CONFIG = {
    "room": {
        "id": os.environ.get("BLDM_ROOM_ID")
    },
    "credential": {
        "buvid3": os.environ.get('BLDM_BUVID3'),
        "sessdata": os.environ.get('BLDM_SESSDATA'),
        "bili_jct": os.environ.get('BLDM_BILI_JCT')
    },
    "user": {
        "id": os.environ.get('BLDM_USER_ID')
    }
}


class TestRoom(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (fd, fn) = mkstemp(text=True)
        with open(fd, 'w', encoding='utf-8') as cf:
            json.dump(CONFIG, cf)
        cls.cf = fn
        cls.config = Config(fn)
        cls.room = Room()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.cf)

    async def test_send(self):
        resp = await self.room.send('test message')
        print(resp)

    async def test_client(self):
        await self.room.start()
        await asyncio.sleep(30)
        await self.room.stop()

    def test_format_message(self):
        from blivedm.models import GiftMessage
        UNAME = 'userabc'
        NUM = 30
        GIFT_NAME = 'ggggnnnn'
        message = GiftMessage(uname=UNAME, num=NUM, gift_name=GIFT_NAME)
        template = '感谢${uname}赠送的${num}个${gift_name}'
        expect = f'感谢{UNAME}赠送的{NUM}个{GIFT_NAME}'
        truth = format_message(message, template)
        self.assertEquals(expect, truth)

    def test_format_message_none_attr(self):
        from blivedm.models import GiftMessage
        UNAME = 'userabc'
        NUM = None
        GIFT_NAME = 'ggggnnnn'
        message = GiftMessage(uname=UNAME, num=None, gift_name=GIFT_NAME)
        template = '感谢${uname}赠送的${num}个${gift_name}'
        expect = f'感谢{UNAME}赠送的{NUM}个{GIFT_NAME}'
        truth = format_message(message, template)
        self.assertEquals(expect, truth)

    def test_format_message_unexist_attr(self):
        from blivedm.models import GiftMessage
        UNAME = 'userabc'
        NUM = 30
        GIFT_NAME = 'ggggnnnn'
        message = GiftMessage(uname=UNAME, num=NUM, gift_name=GIFT_NAME)
        template = '感谢${uname}赠送的${un_attr}个${gift_name}'
        expect = f'感谢{UNAME}赠送的${{un_attr}}个{GIFT_NAME}'
        truth = format_message(message, template)
        self.assertEquals(expect, truth)

    async def test_status(self):
        status = self.room.status()
        self.assertTrue(status)
