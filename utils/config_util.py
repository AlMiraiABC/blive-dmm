import json
import os
import re
from typing import TypeVar

from jsonschema import RefResolver, validate


_TJ = TypeVar('_TJ', dict, list, int, str, bool)
VALID = tuple[list[type], list]

class ConfigUtil():
    """Config util."""

    def __init__(self, config: str | dict = {}, schema: str | dict = {}, default_config: str | dict = {}, valid: dict[str, VALID] = {}, resolver: RefResolver = None) -> None:
        """
        Get configs combine :param:`config` and :param:`default_config`.

        :param config: Path of user's config json file, or config dict.
        :param schema: Path of json schema file or schema dict to valid :param:`config_file`'s format.
        :param default_config: Path of default config json file, or config dict.
        """
        config = {} if config is None else config
        schema = {} if schema is None else schema
        default_config = {} if default_config is None else default_config
        self._default_config = self.load(default_config)
        self._config = self.load(config)
        self._schema = self.load(schema)
        self.config = self.set_envs(
            self.combine(self._default_config.copy(), self._config))
        validate(self.config, self._schema, resolver=resolver)
        self.valid(**valid)

    def load(self, c: str | dict | list, *args, **kwargs) -> dict | list:
        """
        Load config as dict.

        :param c: Config file path or config content.
        :param args kwargs: File open args.
        :returns: Dict config.
        """
        if type(c) in (dict, list):
            return c
        elif isinstance(c, str):
            if not os.path.exists(c):
                return {}
            with open(c, 'r', *args, **kwargs) as cf:
                return json.load(cf)
        else:
            raise TypeError(
                f'config must be str, dict or list, but got {type(c)}.')

    def valid(self, **kwargs: VALID):
        """
        Check value and type in config.

        :param args:
            1. Key name of config.
            2. List of expect value's :class:`type`.
            3. List of unexpected values.
        :returns: Raise ValueError if the value is unexpected or it's type is unexpected.
        """
        for (k, (ts, l)) in kwargs.items():
            v = self.get(k)
            if v in l:
                raise ValueError(f'{k} cannot be one of {l}, but got {v}.')
            if type(v) not in ts:
                raise ValueError(
                    f'{k} should be one of {ts} but got {type(v)} with value {v}')

    def combine(self, default: _TJ, user: _TJ):
        if user is None:
            return default
        if type(default) != type(user):
            raise TypeError(
                f'params default and user must be of the same type, but got default{type(default)} user{type(user)}.')
        if not default:
            return user
        if not isinstance(user, dict):
            return user
        for k, v in user.items():
            if k not in default:
                default[k] = v
                continue
            default[k] = self.combine(default[k], v)
        return default

    def _set_env(self, value: _TJ) -> _TJ:
        """
        Replace ${BLDM_*} in :param:`value` to environment variables.

        :param value: Value. all env_key must wraps in `${BLDM_<env_key>}`
        :returns: Replaced string if :param:`value` is str, otherwise :param:`value` directly.
        """
        if not isinstance(value, str):
            return value
        PREFIX = 'BLDM_'
        pattern = re.compile(f'.*?\$\{{{PREFIX}(.*?)\}}')
        match = re.match(pattern, value)
        if not match:
            return value
        key = f'{PREFIX}{match.group(1)}'
        v = os.environ.get(key)
        if v:
            return self._set_env(value.replace(f'${{{key}}}', v))
        else:
            value = value[:match.end(0)] + \
                self._set_env(value[match.end(0):])
            return value

    def set_envs(self, config: _TJ) -> _TJ:
        """Replace all ${BLDM_*} in config string to environment variables."""
        if isinstance(config, dict):
            for k, v in config.items():
                config[k] = self.set_envs(v)
        elif isinstance(config, list):
            for i, v in enumerate(config):
                config[i] = self.set_envs(v)
        return self._set_env(config)

    def _get(self, d: dict, keys: list[str]):
        if len(keys) == 1:
            return d.get(keys[0])
        v = d.get(keys[0])
        if isinstance(v, dict):
            return self._get(v, keys[1:])

    def get(self, key: str, default=None):
        keys = key.split('.')
        return self._get(self.config, keys) or default
