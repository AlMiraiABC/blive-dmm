import asyncio

from manager.config import Config, ConfigNotifyWhenOn
from manager.logger import Logger
from manager.notify import notify_send
from manager.room import Room
from manager.schedule import IntervalAJob, Schedule


def init():
    Config()


logger = Logger(__file__).logger


async def main():
    room_id = Config().get_room()['id']
    app_monitor_interval = Config().get_app()['monitor']['interval']
    async with Room() as room:
        schedules = Schedule(room).jobs()
        monitor = IntervalAJob(app_monitor_interval, room.status)
        # keep running
        while True:
            await asyncio.sleep(1)
            s = await monitor.run()
            logger.info(f'Live room {room_id} is living {s}.')
            if s: # may be None if not executed
                if not s[0]:
                    logger.warn(
                        f"Live room {room_id} is not boardcasting {s}.")
                    template = f"""
                    Live room {room_id} is not boardcasting {s}.
                    Please check it.
                    The BLDM has been closed automatically.
                    """
                    notify_send(ConfigNotifyWhenOn.LIVE_ROOM_CLOSED, template)
                    break
            for job in schedules:
                await job.run()

if __name__ == '__main__':
    try:
        logger.info("Application initialization...")
        init()
        logger.info("Application initialized.")
        logger.info('Application starting....')
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Application stopped.')
