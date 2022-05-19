import asyncio
import logging
from datetime import datetime, time
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import patch

from manager.config import ConfigSchedule
from manager.room import Room
from manager.schedule import IntervalAJob, Schedule, to_seconds


async def log(msg):
    logging.getLogger('test').info(msg)


class TestSchedule(IsolatedAsyncioTestCase):
    @patch.object(Room, '__init__', lambda *_: None)
    def test_valid_config(self):
        CONFIG: ConfigSchedule = [
            {
                "message": "test message",
                "interval": "1:2:3"
            }
        ]
        room = Room()
        schedule = Schedule(room, CONFIG)
        self.assertListEqual(CONFIG, schedule.config)

    @patch.object(Room, '__init__', lambda *_: None)
    async def test_jobs(self):
        CONFIG: ConfigSchedule = [
            {
                "message": "test message",
                "interval": "1:2:3"
            }
        ]
        room = Room()
        schedule = Schedule(room, CONFIG)
        jobs = schedule.jobs()
        self.assertEqual(len(jobs), len(CONFIG))
        self.assertEqual(jobs[0].cb, room.send)
        self.assertEqual(jobs[0].args, (CONFIG[0]['message'],))
        self.assertEqual(jobs[0].interval, 3600*1+60*2+3)


class TestIntervalAJob(IsolatedAsyncioTestCase):
    async def test_run(self):
        async def log(msg):
            logging.getLogger('test').info(msg)
        output = 'test message'
        job = IntervalAJob(2, log, output)
        with self.assertLogs('test') as l:
            t = 0
            while True:
                await job.run()
                await asyncio.sleep(0.5)
                t += 0.5
                if t > 4:  # 2 4
                    break
        self.assertListEqual(l.output, [f'INFO:test:{output}']*2)


class TestSched(TestCase):
    def test_to_seconds_int(self):
        T = 333
        ret = to_seconds(T)
        self.assertEqual(T, ret)

    def test_to_seconds_dt(self):
        T = datetime(2022, 1, 1, 3, 2, 1)
        ret = to_seconds(T)
        self.assertEqual(ret, 3600*3+60*2+1)

    def test_to_seconds_time(self):
        T = time(3, 2, 1)
        ret = to_seconds(T)
        self.assertEqual(ret, 3600*3+60*2+1)

    def test_to_seconds_str_hhmmss(self):
        T = '30:20:10'
        ret = to_seconds(T)
        self.assertEqual(ret, 3600*30+60*20+10)

    def test_to_seconds_str_mmss(self):
        T = '20:10'
        ret = to_seconds(T)
        self.assertEqual(ret, 60*20+10)

    def test_to_seconds_str_ss(self):
        T = '10'
        ret = to_seconds(T)
        self.assertEqual(ret, 10)

    def test_to_seconds_str_hms(self):
        T = '3:2:1'
        ret = to_seconds(T)
        self.assertEqual(ret, 3600*3+60*2+1)

    def test_to_seconds_str_err(self):
        T = '1:1:abc'
        with self.assertRaises(ValueError):
            to_seconds(T)

    def test_to_seconds_str_extra(self):
        T = '40:30:20:10'
        ret = to_seconds(T)
        self.assertEqual(ret, 3600*30+60*20+10)
