import json
import os
import re
from typing import TypeVar

from jsonschema import RefResolver, validate


_TJ = TypeVar('_TJ', dict, list, int, str, bool)


class ConfigUtil():
    """Config util."""

    def __init__(self, config: str | dict = {}, schema: str | dict = {}, default_config: str | dict = {}, valid: dict[str, tuple[type, list]] = {}, resolver: RefResolver = None) -> None:
        """
        Get configs combine :param:`config` and :param:`default_config`.

        :param config: Path of user's config json file, or config dict.
        :param schema: Path of json schema file or schema dict to valid :param:`config_file`'s format.
        :param default_config: Path of default config json file, or config dict.
        """
        config = config or {}
        schema = schema or {}
        default_config = default_config or {}
        self._default_config = self.load(default_config)
        self._config = self.load(config)
        self._schema = self.load(schema)
        validate(self._config, self._schema, resolver = resolver)
        self.config = self.set_envs(
            self.combine(self._default_config.copy(), self._config))
        self.valid(**valid)

    def load(self, c: str | dict, *args, **kwargs) -> dict:
        """
        Load config as dict.

        :param c: Config file path or dict.
        :param args kwargs: File open args.
        :returns: Dict config.
        """
        if isinstance(c, dict):
            return c
        elif isinstance(c, str):
            if not os.path.exists(c):
                return {}
            with open(c, 'r', *args, **kwargs) as cf:
                return json.load(cf)
        else:
            raise TypeError(f'config must be str or dict, but got {type(c)}.')

    def valid(self, **kwargs: tuple[type, list]):
        """
        Check value and type in config.

        :param args:
            1. Key name of config.
            2. Expect value's :class:`type`.
            3. List of unexpected values.
        :returns: Raise ValueError if the value is unexpected or it's type is unexpected.
        """
        for (k, (t, l)) in kwargs.items():
            v = self.get(k)
            if v in l:
                raise ValueError(f'{k} is required.')
            if not isinstance(v, t):
                raise ValueError(f'{k} should be {t} but got {type(v)}')

    def combine(self, default: dict, user: dict):
        for k, v in user.items():
            if isinstance(v, dict):
                if k not in default:
                    default[k] = {}
                self.combine(default[k], user[k])
            else:
                default[k] = v
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
