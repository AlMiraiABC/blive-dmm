import re

import blivedm

from manager.config import (ConfigNotifyWhenOn, ConfigReply,
                            ConfigReplyKeywordItem)
from manager.logger import Logger
from manager.notify import Notify
from manager.notify import notify as _notify
from manager.room import Room

logger = Logger(__file__).logger


class Reply(blivedm.BaseHandler):
    def __init__(self, room: Room, notify: Notify = None) -> None:
        self.room = room
        self.notify = notify or _notify
        self.keyword = self.get_keyword(self.room.reply)
        self.notify_events = None
        try:
            self.notify_events = notify.config['when']['on']
        except:
            pass
        super().__init__()

    def enable(self, t: str) -> str:
        msg = self.room.reply.get(t)
        enable = self.room.reply.get('enable')
        if t in enable and msg:
            return msg
        return ''

    def get_keyword(self, config: ConfigReply) -> dict[re.Pattern, ConfigReplyKeywordItem]:
        d: dict[re.Pattern, str] = {}
        if 'keyword' not in config.get('enable'):
            return {}
        keyword_config = config.get('keyword')
        if not keyword_config:
            return {}
        for kw in keyword_config:
            key = kw['key']
            if isinstance(key, str):
                kw['key'] = [key]
            for k in kw['key']:
                p = re.compile(k)
                d[p] = kw
        return d

    def reply_kw(self, message: str) -> ConfigReplyKeywordItem | None:
        for p, c in self.keyword.items():
            if re.search(p, message):
                return c

    async def _on_interact_word(self, client: blivedm.BLiveClient, message: blivedm.InteractWordMessage):
        if message.msg_type == 1:
            logger.info(f"[{client.room_id}] welcome "
                        f"{message.uid}({message.uname})")
            welcome = self.enable('welcome')
            if welcome:
                await self.room.send(format_message(message, welcome))
        elif message.msg_type == 2:
            logger.info(f"[{client.room_id}] follow"
                        f"{message.uid}({message.uname})")
            follow = self.enable('follow')
            if follow:
                await self.room.send(format_message(message, follow))
        else:
            logger.warn(f"Unexpect msg_type {message.msg_type}. {message}")

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        logger.info(f'[{client.room_id}] {message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) message '
                    f'"{message.msg}"')
        kw = self.reply_kw(message.msg)
        if kw and kw.get('message'):
            await self.room.send(format_message(message, kw['message']))
            if kw.get('notify') and \
                    self.notify_events and\
                    ConfigNotifyWhenOn.KEYWORD in self.notify_events:
                msg = kw['nitofy'].get(
                    'template', f'Triggerd keyword event\nkeyword: {kw["key"]}\n\n{message.__dict__}')
                self.notify.send(f'Triggered keyword {kw["key"]}', msg)

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        logger.info(f'[{client.room_id}] {message.uid}({message.uname}) gift '
                    f'{message.gift_name}x{message.num}'
                    f' coin {message.coin_type}x{message.total_coin}')
        msg = self.enable('gift')
        if msg:
            await self.room.send(format_message(message, msg))

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
