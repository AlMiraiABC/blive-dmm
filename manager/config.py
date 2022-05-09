import json
import os
from typing import TypedDict

from al_utils.singleton import Singleton
from jsonschema import validate


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


class ConfigApp(TypedDict):
    log_config: str


class ConfigDict(TypedDict):
    room: ConfigRoom
    credential: ConfigCredential
    danmaku: ConfigDanmaku
    reply: ConfigReply
    app: ConfigApp


class Config(Singleton):
    """Get user's config."""

    def __init__(self, config_file: str = './config.json', schema_file: str = './config-schema.json', default_config_file: str = './defaultconfig.json') -> None:
        """
        Get configs from :param:`config_file`

        :param config_file: Path of user's config json file.
        :param schema_file: Path of json schema file to valid :param:`config_file`'s format.
        :param default_config_file: Path of default config json file.
        """
        config_file = config_file or './config.json'
        schema_file = schema_file or './config-schema.json'
        default_config_file = default_config_file or './defaultconfig.json'
        with open(default_config_file, 'r') as default_config_file:
            self._default_config: ConfigDict = json.load(default_config_file)
        if not os.path.exists(config_file):
            self._config = {}
        else:
            with open(config_file, 'r') as config_file:
                self._config: ConfigDict = json.load(config_file)
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        validate(self._config, schema)
        self.config: ConfigDict = self.combine(
            self._default_config.copy(), self._config)

    def combine(self, default: dict, user: dict):
        for k, v in user.items():
            if isinstance(v, dict):
                self.combine(default[k], user[k])
            else:
                default[k] = v
        return default

    def _get(self, d: dict, keys: list[str]):
        if len(keys) == 1:
            return d.get(keys[0])
        v = d.get(keys[0])
        if isinstance(v, dict):
            return self._get(v, keys[1:])

    def get(self, key: str, default=None):
        keys = key.split('.')
        return self._get(self.config, keys) or default

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
