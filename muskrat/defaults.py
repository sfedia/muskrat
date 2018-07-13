#!/usr/bin/python3

import sys
from .pattern import *
from .connectivity import Accept, Attach

feature_coming = """This feature is coming soon (check for the next version: see \
https://github.com/prodotiscus/muskrat or use PyPI)"""


class Defaults:
    def __init__(self):
        self.max_connection_depth = sys.getrecursionlimit()
        self.methods_priority = dict(connect=0, insert=1, append=2)


defaults = Defaults()


class Grouping(Pattern):
    """Default pattern subclass for creating object groups"""
    def __init__(self, grouping_name, properties=None):
        """
        :param grouping_name: name of the group
        :param properties: group properties
        """
        accept_policy = Accept()
        accept_policy.add_default(connect=True, insert=False)
        attach_policy = Attach()
        attach_policy.add_default(connect=True, insert=False)
        props = dict({"name": grouping_name}, **({} if properties is None else properties))
        Pattern.__init__(self, "Grouping", accept_policy, attach_policy, props)


class VersionOutOfDate(Exception):
    pass
