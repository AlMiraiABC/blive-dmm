import blivedm
from al_utils.async_util import async_wrap
from al_utils.logger import Logger
from bilibili_api import Credential
from bilibili_api.live import LiveRoom
from bilibili_api.utils.Danmaku import Danmaku as Dm
from bilibili_api.utils.Danmaku import Mode as DmMode

from manager.config import (Config, ConfigCredential, ConfigDanmaku,
                            ConfigDanmakuStyle, ConfigReply, ConfigRoom)

logger = Logger('Danmaku').logger


class Danmaku:
    def __init__(self, credential: ConfigCredential = None, room: ConfigRoom = None, danmaku: ConfigDanmaku = None, reply: ConfigReply = None) -> None:
        credential = credential or Config().get_credential()
        room = room or Config().get_room()
        danmaku = danmaku or Config().get_danmaku()
        reply = reply or Config().get_reply()
        # self.session = aiohttp.ClientSession()
        self.credential = Credential(**credential)
        self.room = LiveRoom(room['id'], self.credential)
        self.client = blivedm.BLiveClient(room['id'], ssl=True)
        self.client.add_handler(_Handler(self))
        self.reply = reply
        self.danmaku_style = self.convert_style(danmaku['style'])

    def convert_style(self, style: ConfigDanmakuStyle) -> dict:
        d = {
            "scroll": DmMode.FLY,
            "top": DmMode.TOP,
            "bottom": DmMode.BOTTOM
        }
        return {'color': style['color'], 'mode': d[style['position']]}

    async def send(self, message: str):
        """Send a danmaku message to live room."""
        return await self.room.send_danmaku(Dm(message, **self.danmaku_style))

    async def start(self):
        logger.info("Starting client...")
        await async_wrap(self.client.start)()
        logger.info("Client started.")

    async def stop(self):
        logger.info("Closing client...")
        await self.client.stop_and_close()
        logger.info("Client stopped.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self):
        await self.stop()


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
        t = self.danmaku.reply.get('gift')
        if t:
            await self.danmaku.send(format_message(message, t))

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.username}) guard '
                    f'{message.gift_id}/{message.guard_level}/{message.gift_name}/{message.price}x{message.num}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) superchat '
                    f'{message.price}-{message.message}')


def format_message(message: object, template: str) -> str:
    d = message.__dict__
    for k, v in d.items():
        template = template.replace(f'${{{k}}}', str(v))
    return template
