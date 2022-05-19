from datetime import datetime, time
from typing import Any, Awaitable, Callable, TypeVar

from app_config import ScheduleConfig
from utils.config_util import ConfigUtil

from manager.config import Config, ConfigSchedule
from manager.logger import Logger
from manager.room import Room

logger = Logger(__file__).logger

_RET = TypeVar('_RET')


class IntervalAJob:
    def __init__(self, interval: int, cb: Awaitable[Callable[[Any], _RET]], *args, **kwargs):
        """Async run a interval job."""
        self.time = datetime.now()
        self.cb = cb
        self.args = args
        self.kwargs = kwargs
        self.interval = interval

    async def run(self) -> _RET | None:
        """Run :param:`cb` if interval >= last run time"""
        time = datetime.now()
        if (time-self.time).seconds >= self.interval:
            self.time = time
            return await self.cb(*self.args, **self.kwargs)


class Schedule:
    def __init__(self, room: Room, config: ConfigSchedule = None):
        """

        :param config: config.schedule
        :param room: Live room
        """
        self.room = room
        self.config = ConfigUtil(
            config or Config().get_schedule(), ScheduleConfig.schema_file, []).config

    def jobs(self) -> list[IntervalAJob]:
        """Get a list of scheduled jobs in config."""
        js: list[IntervalAJob] = []
        for c in self.config:
            try:
                seconds = to_seconds(c['interval'])
            except:
                logger.error(f'Schedule interval error with {c["interval"]}')
                logger.warn(f'Schedule ignored {c}')
                continue
            else:
                if c['message']:
                    js.append(IntervalAJob(
                        seconds, self.room.send, c['message']))
                else:
                    logger.warn(f'Schedule ignored {c}')
        return js


def to_seconds(t: str | int | datetime | time) -> int:
    """
    Convert :param:`t` to seconds.

    :param t: [[HH:]MM:]SS
    :raises TypeError: Unsupported type.
    """
    h, m, s = 0, 0, 0
    if isinstance(t, int):
        return t
    elif isinstance(t, str):
        nums = [int(i) for i in t.split(':')]
        s = nums.pop()
        if len(nums) > 0:
            m = nums.pop()
        if len(nums) > 0:
            h = nums.pop()
    elif isinstance(t, datetime):
        h = t.hour
        m = t.minute
        s = t.second
    elif isinstance(t, time):
        h = t.hour
        m = t.minute
        s = t.second
    else:
        raise TypeError(f'Unsupported type of t, got {type(t)}')
    return 3600*h + 60*m + s
