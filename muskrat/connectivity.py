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

from collections import namedtuple
from .defaults import *
from .filters import unify
from .parser import ParsingObject

allowed_opts = namedtuple("AllowedOptions", ["connect", "insert"])


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
        if self.__class__.__name__ == "Attach":
            self.add_option(group_filter(group_name), connect=True, insert=False)
        else:
            raise DirectionConfused()

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


class DirectionConfused(Exception):
    pass
