import os
from unittest import TestCase
from manager.config import ConfigNotify
from manager.nofity import Notify


class TestNotify(TestCase):
    def test_pre_minimum(self):
        CONFIG: ConfigNotify = {
            "sender": {
                "email": "hello@test.com"
            },
            "server": {
                "host": "imtp.test.com",
                "passcode": "1234567"
            }
        }
        sender = CONFIG["sender"]
        sender["nickname"] = ''
        notify = Notify(CONFIG)
        config = notify.config
        self.assertEqual(config["sender"]["email"], sender["email"])
        self.assertEqual(config["sender"]["nickname"], '')
        self.assertDictEqual(config["receiver"][0], sender)
        self.assertEqual(config["server"]["username"],
                         CONFIG["sender"]["email"])
        self.assertEqual(config["server"]["host"], CONFIG["server"]["host"])
        self.assertEqual(config["server"]["passcode"],
                         CONFIG["server"]["passcode"])
        self.assertEqual(config["server"]["ssl"], True)
        self.assertEqual(config["server"]["port"], 465)

    def test_send_one(self):
        CONFIG: ConfigNotify = {
            "sender": {
                "email": os.environ["BLDM_EMAIL_SENDER"],
                "nickname": "BLDM"
            },
            "server": {
                "host": os.environ["BLDM_EMAIL_HOST"],
                "passcode": os.environ["BLDM_EMAIL_PASSCODE"]
            }
        }
        notify = Notify(CONFIG)
        (ret, ex) = notify.send("blive-dmm 测试邮件标题", "blive-dmm 邮件内容")
        self.assertTrue(ret)
        self.assertIsNone(ex)

    def test_send_more(self):
        CONFIG: ConfigNotify = {
            "sender": {
                "email": os.environ["BLDM_EMAIL_SENDER"],
                "nickname": "BLDM"
            },
            "server": {
                "host": os.environ["BLDM_EMAIL_HOST"],
                "passcode": os.environ["BLDM_EMAIL_PASSCODE"]
            },
            "receiver": [
                {
                    "email": "live.almirai@outlook.com"
                },
                {
                    "email": "mr_liuzhao@126.com"
                }
            ]
        }
        notify = Notify(CONFIG)
        (ret, ex) = notify.send("blive-dmm 测试邮件标题", "blive-dmm 邮件内容")
        self.assertTrue(ret)
        self.assertIsNone(ex)
