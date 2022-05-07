import asyncio

from manager.danmaku import Danmaku


async def main():
    client = Danmaku()
    await client.start()
    await asyncio.sleep(1000)
    await client.stop()


asyncio.get_event_loop().run_until_complete(main())
