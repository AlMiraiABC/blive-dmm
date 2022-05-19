import asyncio
import os
import re
from unittest import IsolatedAsyncioTestCase, skip
from unittest.mock import patch
from manager.config import ConfigReply, ConfigReplyKeyword

from manager.room import _Handler, Room, format_message
from utils.config_util import ConfigUtil

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
        ConfigUtil(CONFIG)
        cls.room = Room()

    async def test_send(self):
        resp = await self.room.send('test message')
        print(resp)

    @skip('nesting asyncio loop.')
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


class Test_Handler(IsolatedAsyncioTestCase):
    @patch.object(_Handler, '__init__', lambda *_: None)
    def test_get_keyword(self):
        ks = ["k1", "k2", "k3"]
        ms = ['msg1', 'msg2']
        CONFIG: ConfigReply = {
            "enable": ['keyword'],
            "keyword": [
                {
                    "key": ks[0],
                    "message": ms[0]
                },
                {
                    "key": ks[1:],
                    "message":ms[1]
                }
            ]
        }
        expect: dict[re.Pattern, str] = {
            re.compile(ks[0]): ms[0],
            re.compile(ks[1]): ms[1],
            re.compile(ks[2]): ms[1]
        }
        handler = _Handler()
        ret = handler.get_keyword(CONFIG)
        self.assertDictEqual(ret, expect)

    @patch.object(_Handler, '__init__', lambda *_: None)
    def test_reply_kw(self):
        handler = _Handler()
        handler.keyword={
            re.compile('bug\d+'):'There is a bug',
            re.compile('\w+track'): 'track occured.'
        }
        ret = handler.reply_kw('occuredtrack')
        self.assertEqual(ret, 'track occured.')
