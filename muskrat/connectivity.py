#!/usr/bin/python3

from collections import namedtuple
from .filters import unify

allowed_opts = namedtuple('AllowedOptions', 'connect insert')


class RelativePolicy:
    def __init__(self):
        self.__options = {}
        self.__default = None

    def add_option(self, flt, connect=True, insert=True):
        self.__options[flt] = dict(connect=connect, insert=insert)
        return self

    def add_default(self, connect=True, insert=True):
        self.__default = dict(connect=connect, insert=insert)
        return self

    def get_policy(self, obj):
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


def merge_policies(*args):
    connect = False not in [x.connect for x in args]
    insert = False not in [x.insert for x in args]
    return allowed_opts(connect, insert)


class MissingDefault(EnvironmentError):
    pass
