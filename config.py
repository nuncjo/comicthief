# -*- coding:utf-8 -*-

from configparser import ConfigParser

CONFIG = 'default.ini'


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
    return config.get_config(name)
