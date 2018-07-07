#!/usr/bin/python3

from .filters import unify
from collections import namedtuple


class RelativePolicy:
    def __init__(self):
        self.__options = {}
        self.__default = None

    def add_option(self, fltr, connect=True, insert=True):
        self.__options[fltr] = dict(connect=connect, insert=insert)

    def add_default(self, connect=True, insert=True):
        self.__default = dict(connect=connect, insert=insert)

    def get_policy(self, obj):
        allowed_opts = namedtuple('AllowedOptions', 'connect insert')
        for (flt, options) in self.__options.items():
            if unify(flt)(obj):
                return allowed_opts(options['connect'], options['insert'])
        if self.__default is None:
            raise MissingDefault()
        return allowed_opts(self.__default['connect'], self.__default['insert'])


class Accept(RelativePolicy):
    def __init__(self):
        RelativePolicy.__init__(self)
        pass


class Attach(RelativePolicy):
    def __init__(self):
        RelativePolicy.__init__(self)
        pass


class MissingDefault(EnvironmentError):
    pass
