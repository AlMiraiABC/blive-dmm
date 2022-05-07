import aiohttp
import blivedm
from al_utils.async_util import async_wrap
from al_utils.logger import Logger
from bilibili_api import Credential
from bilibili_api.live import LiveRoom
from bilibili_api.utils.Danmaku import Danmaku as Dm

from manager.config import Config, ConfigCredential, ConfigDanmaku, ConfigRoom

logger = Logger('Danmaku').logger


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
        self.client = blivedm.BLiveClient(self.room, ssl=True)
        self.client.add_handler(_Handler(self))

    async def send(self, message: str):
        return await self.live.send_danmaku(Dm(message))

    async def start(self):
        await async_wrap(self.client.start)()

    async def stop(self):
        await self.client.stop_and_close()


class _Handler(blivedm.BaseHandler):
    def __init__(self, danmaku: Danmaku) -> None:
        self.danmaku = danmaku
        super().__init__()
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa
    _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()

    async def _on_welcome(self, client: blivedm.BLiveClient, command: dict):
        data = command['data']
        logger.info(f"[{client.room_id}] welcome "
                    f"{data['uid']}({data['uname']})")
        await self.danmaku.send(f"欢迎{data['uname']}进入直播间")

    _CMD_CALLBACK_DICT['INTERACT_WORD'] = _on_welcome

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        logger.info(f'[{client.room_id}] {message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) message '
                    f'"{message.msg}"')

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) gift '
                    f'{message.gift_name}x{message.num}'
                    f' coin {message.coin_type}x{message.total_coin}')
        await self.danmaku.send(
            f"感谢{message.uname}赠送的{message.num}个{message.gift_name}")

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.username}) guard '
                    f'{message.gift_id}/{message.guard_level}/{message.gift_name}/{message.price}x{message.num}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) superchat '
                    f'{message.price}-{message.message}')
