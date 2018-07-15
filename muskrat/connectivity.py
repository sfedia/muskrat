#!/usr/bin/python3

from collections import namedtuple
from .defaults import *
from .filters import unify
from .parser import ParsingObject

allowed_opts = namedtuple('AllowedOptions', 'connect insert')


class RelativePolicy:
    """Policy used to dictate interaction strategies between objects"""
    def __init__(self):
        self.options = {}
        self.default = None

    def add_option(self, flt, connect=True, insert=True):
        """
        Add a new connect/insert rule for objects which satisfy filter conditions
        :param flt: filter conditions
        :param connect: allow connection
        :type connect: bool
        :param insert: allow insertion
        :type insert: bool
        """
        self.options[flt] = dict(connect=connect, insert=insert)
        return self

    def add_default(self, connect=True, insert=True):
        """
        Add default connect/insert rule
        :param connect: allow connection
        :type connect: bool
        :param insert: allow insertion
        :type insert: bool
        """
        self.default = dict(connect=connect, insert=insert)
        return self

    def add_group_connection(self, group_name):
        self.add_option(group_filter(group_name), connect=True, insert=False)

    def get_policy(self, obj):
        """
        Get connect/insert policy in point of the object
        :param obj: object to check
        :type obj: ParsingObject
        :return: (connect=bool, insert=bool)
        """
        for (flt, options) in self.options.items():
            if unify(flt)(obj):
                return allowed_opts(options['connect'], options['insert'])
        if self.default is None:
            raise MissingDefault()
        return allowed_opts(self.default['connect'], self.default['insert'])


class Accept(RelativePolicy):
    """A<-B accepting policy"""
    def __init__(self):
        RelativePolicy.__init__(self)
        pass


class Attach(RelativePolicy):
    """B->A attachment policy"""
    def __init__(self):
        RelativePolicy.__init__(self)
        self.default = dict(connect=False, insert=False)


def merge_policies(*args):
    connect = False not in [x.connect for x in args]
    insert = False not in [x.insert for x in args]
    return allowed_opts(connect, insert)


class MissingDefault(EnvironmentError):
    pass
