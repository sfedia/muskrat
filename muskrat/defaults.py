#!/usr/bin/python3

import sys

feature_coming = """This feature is coming soon (check for the next version: see \
https://github.com/prodotiscus/muskrat or use PyPI)"""


class Defaults:
    def __init__(self):
        self.max_connection_depth = sys.getrecursionlimit()
        self.methods_priority = dict(connect=0, insert=1, append=2)


defaults = Defaults()


class VersionOutOfDate(Exception):
    pass
