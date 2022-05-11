import os
from unittest import TestCase

from utils.config_util import ConfigUtil


class TestConfigUtil(TestCase):
    def test_combine(self):
        config = ConfigUtil()
        d = {"k1": 1, "k2": 2, "k3": [123], "k4": {"k1": 1}, "k5": {"k1": 1}}
        u = {"k1": 11, "k3": [321], "k4": {"k1": 11}}
        expect = {"k1": 11, "k2": 2, "k3": [
            321], "k4": {"k1": 11}, "k5": {"k1": 1}}
        result = config.combine(d, u)
        self.assertDictEqual(expect, result)

    def clean(self, *envs):
        for e in envs:
            os.environ.pop(e, '')

    def test__set_env(self):
        ENV_VALUE = 'test env'
        KEY = 'BLDM_testenv'
        pre = 'aaaaaaaa'
        suf = 'bbbbbbbbbb'
        VALUE = f'{pre}${{{KEY}}}{suf}'
        expect = f'{pre}{ENV_VALUE}{suf}'
        os.environ[KEY] = ENV_VALUE
        config = ConfigUtil()
        result = config._set_env(VALUE)
        self.clean(KEY)
        self.assertEquals(result, expect)

    def test__set_env_unexist(self):
        KEY = 'BLDM_testenv'
        pre = 'aaaaaaaa'
        suf = 'bbbbbbbbbb'
        VALUE = f'{pre}${{{KEY}}}{suf}'
        expect = VALUE
        config = ConfigUtil()
        result = config._set_env(VALUE)
        self.assertEquals(result, expect)

    def test__set_env_multi(self):
        ENV_VALUE = 'test env'
        KEY = 'BLDM_testenv'
        pre = 'aaaaaaaa'
        suf = 'bbbbbbbbbb'
        VALUE = f'{pre}${{{KEY}}}{suf}{KEY}'
        expect = f'{pre}{ENV_VALUE}{suf}{KEY}'
        os.environ[KEY] = ENV_VALUE
        config = ConfigUtil()
        result = config._set_env(VALUE)
        self.clean(KEY)
        self.assertEquals(result, expect)

    def test_set_envs(self):
        ENV_VALUE = 'test env'
        KEY = 'BLDM_testenv'
        os.environ[KEY] = ENV_VALUE
        CONFIG = {"k1": 1, "k2": 2, "k3": [
            f'aaa${{{KEY}}}bbb'], "k4": {"k1": f'aaa${{{KEY}}}bbb'}, "k5": {"k1": f'aaa${{BLDM_unexist}}bbb${{{KEY}}}'}}
        expect = {"k1": 1, "k2": 2, "k3": [
            f'aaa{ENV_VALUE}bbb'], "k4": {"k1": f'aaa{ENV_VALUE}bbb'}, "k5": {"k1": f'aaa${{BLDM_unexist}}bbb{ENV_VALUE}'}}
        config = ConfigUtil()
        result = config.set_envs(CONFIG)
        self.clean(KEY)
        self.assertDictEqual(result, expect)
