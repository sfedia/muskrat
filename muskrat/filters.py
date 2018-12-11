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


from .defaults import *


class LogicalOR:
    def __init__(self, *args):
        self.filters = args

    def process(self, obj):
        for flt in self.filters:
            if unify(flt)(obj):
                return True
        return False


class LogicalAND:
    def __init__(self, *args):
        self.filters = args

    def process(self, obj):
        for flt in self.filters:
            if not unify(flt)(obj):
                return False
        return True


class LogicalNOT:
    def __init__(self, flt):
        self.filter = flt

    def process(self, obj):
        return not unify(self.filter)(obj)


def unify(flt):
    if isinstance(flt, LogicalAND) or isinstance(flt, LogicalOR) or isinstance(flt, LogicalNOT):
        return flt.process
    else:
        return flt


def by_type(object_type):
    return lambda obj: obj.pattern.object_type == object_type


def by_property(bool_property=None, kw_property=None, kw_value=None):
    if bool_property is None and kw_property is None:
        raise ValueError()
    if bool_property is not None:
        return lambda obj: obj.pattern.properties.property_exists(bool_property)
    else:
        def check_prop(obj):
            if obj.pattern.properties.property_exists(kw_property):
                prop = obj.pattern.properties.get_property(kw_property)
                return prop == kw_value
            else:
                return False
        return check_prop


def has_childs():
    def scan_childs(obj):
        if obj.connected_objects:
            return True
        return False
    return scan_childs


def connection_depth(value=None, compare=None):
    """
    Generates a function which compares connection depth of the element with the given value.
    :param value: value to compare with measured connection depth
    :param compare: expr. (function) which takes depth as argument, returns bool
    :return: function (function wrapper)
    """
    if value is None and compare is None:
        raise ValueError()

    def get_depth(obj):
        dive_dit = obj.dive(behind=max_connection_depth, return_dit=True)
        if compare is None:
            return dive_dit.counter == value
        else:
            return compare(dive_dit.counter)
    return get_depth
