import aiohttp
from bilibili_api import Credential
from bilibili_api.live import LiveRoom
from bilibili_api.utils.Danmaku import Danmaku as Dm

from manager.config import Config, ConfigCredential, ConfigDanmaku, ConfigRoom


class Danmaku:
    def __init__(self, credential: ConfigCredential = None, room: ConfigRoom = None, danmaku: ConfigDanmaku = None) -> None:
        credential = credential or Config().get_credential()
        room = room or Config().get_room()
        danmaku = danmaku or Config().get_danmaku()
        self.room = room['id']
        self.data = danmaku['style']
        self.session = aiohttp.ClientSession()
        self.credential = Credential(**credential)
        self.live = LiveRoom(self.room, self.credential)

    async def send(self, message: str):
        return await self.live.send_danmaku(Dm(message))
