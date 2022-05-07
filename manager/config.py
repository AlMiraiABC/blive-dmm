from typing import TypedDict
from al_utils.singleton import Singleton
from utils.config_util import ConfigUtil


class ConfigRoom(TypedDict):
    id: int


class ConfigReply(TypedDict):
    visit: str
    gift: str


class ConfigCredential(TypedDict):
    buvid3: str
    sessdata: str
    bilijct: str


class ConfigDanmaku(TypedDict):
    style: dict


class Config(Singleton):
    def __init__(self, config_file: str = './config.json') -> None:
        self.config = ConfigUtil(config_file)

    def get_room(self) -> ConfigRoom:
        c = self.config.get_key('room')
        return c

    def get_reply(self) -> ConfigReply:
        c = self.config.get_key('reply')
        return c

    def get_credential(self) -> ConfigCredential:
        c = self.config.get_key('credential')
        return c

    def get_danmaku(self) -> ConfigDanmaku:
        c = self.config.get_key('danmaku')
        return c
