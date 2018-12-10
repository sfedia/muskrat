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
from collections import namedtuple
from .pattern import Tracker


class AllocatorCursor:
    def __init__(self, position):
        self.defaults = SliceAttributes()
        self.current = position
        self.dynamic_mappers = []
        self.dynamic_mapper = namedtuple("DynamicMapper", ["start_if", "finalize_if", "attributes"])
        self.compiled_mapper = namedtuple("CompiledMapper", ["dm_index", "attributes"])
        self.dl_stack = []
        self.dm_stack = []

    def update(self, parser, current, content):
        self.current = current
        if self.dm_stack:
            if self.dynamic_mappers[self.dm_stack[-1].dm_index].finalize_if(parser, content):
                if self.dl_stack and self.dl_stack[-1][0] == self.dm_stack[-1].dm_index:
                    self.dl_stack.pop()
                self.dm_stack.pop()

        for n, dmp in enumerate(self.dynamic_mappers):
            if dmp.start_if(parser, content):
                self.dm_stack.append(
                    self.mapper_compile(
                        self.compiled_mapper(n, dmp.attributes),
                        ["depend_on"],
                        parser,
                        content
                    )
                )
                if "left_depth_limit" in dmp.attributes:
                    self.dl_stack.append((n, current, dmp.attributes["left_depth_limit"]))

    @staticmethod
    def mapper_compile(mapper, attrs2compile, *args):
        for attr in attrs2compile:
            if attr in mapper.attributes and mapper.attributes[attr] is not None:
                mapper.attributes[attr] = mapper.attributes[attr](*args)
        return mapper

    def get_current_cursor(self):
        if not self.dm_stack:
            return self.defaults
        else:
            return SliceAttributes(**self.dm_stack[-1].attributes)

    def add_dynamic_mapper(self, start_if, finalize_if, **kwargs):
        self.dynamic_mappers.append(self.dynamic_mapper(start_if, finalize_if, kwargs))

    def get_attribute(self, attr_name):
        current = self.get_current_cursor()
        return getattr(current, attr_name)

    @property
    def max_connection_depth(self):
        return self.get_attribute("max_connection_depth")

    @property
    def methods_priority(self):
        return self.get_attribute("methods_priority")

    @property
    def tracker_family(self):
        return self.get_attribute("tracker_family")

    @property
    def left_depth_limit(self):
        if not self.dl_stack:
            return None
        else:
            return self.dl_stack[-1][2] + self.current - self.dl_stack[-1][1]

    @property
    def depend_on(self):
        return self.get_attribute("depend_on")


class SliceAttributes:
    def __init__(self, **kwargs):
        attribute_names = [
            "methods_priority",
            "tracker_family",
            "left_depth_limit",
            "depend_on"
        ]

        attribute_values = (
            dict(connect=0, insert=1, append=2),
            [Tracker],
            None,
            None
        )

        if sys.version_info >= (3, 7):
            self.attr_proto = namedtuple("SliceAttributeStorage", attribute_names, defaults=attribute_values)
        else:
            self.attr_proto = namedtuple("SliceAttributeStorage", attribute_names)
            self.attr_proto.__new__.__defaults__ = attribute_values

        self.attributes = self.attr_proto(**kwargs)

    def set_tracker_family(self, *args):
        self.attributes.tracker_family = args
