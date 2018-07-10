#!/usr/bin/python3

from collections import namedtuple
from .filters import unify

allowed_opts = namedtuple('AllowedOptions', 'connect insert')


class RelativePolicy:
    def __init__(self):
        self.options = {}
        self.default = None

    def add_option(self, flt, connect=True, insert=True):
        self.options[flt] = dict(connect=connect, insert=insert)
        return self

    def add_default(self, connect=True, insert=True):
        self.default = dict(connect=connect, insert=insert)
        return self

    def get_policy(self, obj):
        for (flt, options) in self.options.items():
            if unify(flt)(obj):
                return allowed_opts(options['connect'], options['insert'])
        if self.default is None:
            raise MissingDefault()
        return allowed_opts(self.default['connect'], self.default['insert'])


class Accept(RelativePolicy):
    def __init__(self):
        RelativePolicy.__init__(self)
        pass


class Attach(RelativePolicy):
    def __init__(self):
        RelativePolicy.__init__(self)
        self.default = dict(connect=False, insert=False)


def merge_policies(*args):
    connect = False not in [x.connect for x in args]
    insert = False not in [x.insert for x in args]
    return allowed_opts(connect, insert)


class MissingDefault(EnvironmentError):
    pass
