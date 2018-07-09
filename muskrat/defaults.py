#!/usr/bin/python3

import sys

max_connection_depth = sys.getrecursionlimit()
feature_coming = """This feature is coming soon (check for the next version: see \
https://github.com/prodotiscus/muskrat or use PyPI)"""


class VersionOutOfDate(Exception):
    pass
