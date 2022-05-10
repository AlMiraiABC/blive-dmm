import asyncio

from manager.config import Config
from manager.logger import Logger
from manager.room import Room


def init():
    Config()


logger = Logger(__file__).logger


async def main():
    room_id = Config().get_room()['id']
    app_monitor_interval = Config().get_app()['monitor']['interval']
    async with Room() as c:
        # keep running
        while True:
            await asyncio.sleep(app_monitor_interval)
            s = await c.status()
            logger.info(f'Live room {room_id} is living {s}.')
            if not s[0]:
                logger.warn(
                    f"Live room {room_id} is not boardcasting {s}.")
                break

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
