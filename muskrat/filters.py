#!/usr/bin/python3

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


def unify(flt):
    if isinstance(flt, LogicalAND) or isinstance(flt, LogicalOR):
        return flt.process
    else:
        return flt


def by_type(object_type):
    return lambda obj: obj.pattern.object_type == object_type


def by_property(bool_property=None, kw_property=None, kw_value=None):
    if bool_property is None or kw_property is None:
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
    :param value: value to compare to produce equality expression
    :param compare: expression (function) which takes depth as argument and returns boolean
    :return: function (function wrapper)
    """
    if value is None and compare is None:
        raise ValueError()

    def get_depth(obj):
        last, counter = obj.dive(counter=defaults.max_connection_depth)
        depth = defaults.max_connection_depth - counter
        if compare is None:
            return depth == value
        else:
            return compare(depth)
    return get_depth
