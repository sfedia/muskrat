#!/usr/bin/python3

"""
Muskrat: minimalistic non-BNF text parser and tree generator
Copyright (C) 2018 Fyodor Sizov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
from .pattern import *
from .filters import *
from .connectivity import Accept, Attach


feature_coming = """This feature is coming soon (check for the next version: see \
https://github.com/prodotiscus/muskrat or use PyPI)"""


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


def group_filter(group_name):
    return LogicalAND(by_type("Grouping"), by_property(kw_property="name", kw_value=group_name))


max_connection_depth = sys.getrecursionlimit()


class VersionOutOfDate(Exception):
    pass
