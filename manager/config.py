from typing import TypedDict

from al_utils.singleton import Singleton
from app_config import AppConfig
from utils.config_util import ConfigUtil


class ConfigRoom(TypedDict):
    id: int


class ConfigReply(TypedDict):
    welcome: str
    gift: str
    enable: list[str]


class ConfigCredential(TypedDict):
    buvid3: str
    sessdata: str
    bilijct: str


class ConfigDanmakuStyle(TypedDict):
    position: str
    color: str


class ConfigDanmaku(TypedDict):
    style: ConfigDanmakuStyle


class ConfigAppLog(TypedDict):
    config: str


class ConfigAppMonitor(TypedDict):
    interval: int


class ConfigApp(TypedDict):
    log: ConfigAppLog
    monitor: ConfigAppMonitor


class ConfigUser(TypedDict):
    id: str


class ConfigDict(TypedDict):
    user: ConfigUser
    room: ConfigRoom
    credential: ConfigCredential
    danmaku: ConfigDanmaku
    reply: ConfigReply
    app: ConfigApp


class Config(Singleton):
    def __init__(self, cfg: ConfigUtil = None):
        self.config = cfg or ConfigUtil(AppConfig.config_file, AppConfig.schema_file,
                                        AppConfig.default_config_file, AppConfig.required)

    def get_room(self) -> ConfigRoom:
        return self.config.get('room')

    def get_reply(self) -> ConfigReply:
        return self.config.get('reply')

    def get_credential(self) -> ConfigCredential:
        return self.config.get('credential')

    def get_danmaku(self) -> ConfigDanmaku:
        return self.config.get('danmaku')

    def get_app(self) -> ConfigApp:
        return self.config.get('app')

    def get_user(self) -> ConfigUser:
        return self.config.get('user')
