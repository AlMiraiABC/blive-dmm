import os
from smtplib import SMTP
from unittest import TestCase
from unittest.mock import patch
from manager.config import ConfigNotify, ConfigNotifyWhenOn
from manager.notify import Notify, get_notify_event_config, notify_send
from al_utils.singleton import _containers, DEFAULT_CONTAINER_NAME


class TestNotify(TestCase):
    def setUp(self) -> None:
        _containers[DEFAULT_CONTAINER_NAME].pop(Notify, None)
        return super().setUp()

    def test_pre_minimum(self):
        CONFIG: ConfigNotify = {
            "sender": {
                "email": "hello@test.com"
            },
            "server": {
                "host": "imtp.test.com",
                "passcode": "1234567"
            },
            "when": {
                "on": ["live_room_closed"]
            }
        }
        sender = CONFIG["sender"]
        sender["nickname"] = ''
        self.setUp()
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

    @patch.object(SMTP, 'connect', lambda *args, **kwargs: (220, ''))
    @patch.object(SMTP, 'login', lambda *args, **kw: None)
    @patch.object(SMTP, 'send_message', lambda *args, **kwargs: None)
    @patch.object(SMTP, 'quit', lambda *args, **kwargs: None)
    def mock_smtp_success(self):
        """Mock SMTP with successfully return."""

    @patch.object(SMTP, 'connect', lambda *args, **kwargs: (_ for _ in ()).throw(Exception('Cannot connect to smtp host.')))
    def mock_smtp_fail(self):
        """Mock SMTP but failed and raise and exception."""

    def test_send_one(self):
        CONFIG: ConfigNotify = {
            "sender": {
                "email": os.environ["BLDM_EMAIL_SENDER"],
                "nickname": "BLDM"
            },
            "server": {
                "host": os.environ["BLDM_EMAIL_HOST"],
                "passcode": os.environ["BLDM_EMAIL_PASSCODE"]
            },
            "when": {
                "on": ["live_room_closed"]
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

    def test_get_notify_event_config(self):
        CONFIG: ConfigNotify = {
            "when": {
                "live_room_closed": {
                    "template": "test"
                },
                "on": ["live_room_closed"]
            }
        }
        ret = get_notify_event_config(
            ConfigNotifyWhenOn.LIVE_ROOM_CLOSED, CONFIG)
        self.assertDictEqual(ret, CONFIG['when']["live_room_closed"])

    def test_get_notify_event_config_not_on(self):
        CONFIG: ConfigNotify = {
            "when": {
                "live_room_closed": {
                    "template": "test"
                },
                "on": []
            }
        }
        ret = get_notify_event_config(
            ConfigNotifyWhenOn.LIVE_ROOM_CLOSED, CONFIG)
        self.assertIsNone(ret)

    @patch('manager.notify.Notify', spec=Notify)
    def test_notify_send(self, notify):
        notify.send.return_value = (True, None)
        ret = notify_send(
            ConfigNotifyWhenOn.LIVE_ROOM_CLOSED, 'closed', notify)
        self.assertTrue(ret)
