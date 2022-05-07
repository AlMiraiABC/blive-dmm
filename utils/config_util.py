import json
import os
from copy import deepcopy

from al_utils.singleton import Singleton


class ConfigUtil(Singleton):
    def __init__(self, config_path: str = './config.json', default_config_path: str = './defaultconfig.json') -> None:
        """
        Read JSON configs.

        :param config_path: User's JSON config file path.
        :param default_config_path: Default JSON config file path.
        """
        with open(default_config_path, 'r') as default_config_file:
            self._default_config: dict = json.load(default_config_file)
        if not os.path.exists(config_path):
            self._config = {}
        else:
            with open(config_path, 'r') as config_file:
                self._config: dict = json.load(config_file)

    def get_key(self, key: str, env_key: str = None, default=None):
        if env_key:
            return os.getenv(env_key) or default
        keys = key.split('.')
        default_value = deepcopy(self._get(self._default_config, keys))
        value = self._get(self._config, keys) or default
        if isinstance(default_value, dict) and isinstance(value, dict):
            default_value.update(value)
            return default_value
        return value or default_value

    def _get(self, d: dict, keys: list[str]):
        if len(keys) == 1:
            return d.get(keys[0])
        v = d.get(keys[0])
        if isinstance(v, dict):
            return self._get(v, keys[1:])
