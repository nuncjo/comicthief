# -*- coding:utf-8 -*-

from configparser import ConfigParser
import os
from pathlib import Path, PurePath

CONFIG = 'default.ini'


class WithConfig:

    def __init__(self):
        self.config = get_config(CONFIG)
        self.img_dir = self.config['SETTINGS'].get('img_dir', 'img')


class SingleConfig:
    """Singleton forcing that there is only one configuration instance used"""
    class Config(ConfigParser):

        def get_config(self, name):
            self.read(name)
            return self

    instance = None

    def __init__(self):
        if not SingleConfig.instance:
            SingleConfig.instance = SingleConfig.Config()

    def __getattr__(self, item):
        return getattr(self.instance, item)


def get_config(name):
    config = SingleConfig()
    return config.get_config(str(Path(Path(__file__).parent, name)))
