#!/usr/bin/python3

from .defaults import max_connection_depth


class LogicOR:
    def __init__(self, *args):
        self.filters = args

    def process(self, obj):
        for flt in self.filters:
            if unify(flt)(obj):
                return True
        return False


class LogicAND:
    def __init__(self, *args):
        self.filters = args

    def process(self, obj):
        for flt in self.filters:
            if not unify(flt)(obj):
                return False
        return True


def unify(flt):
    if isinstance(flt, LogicAND) or isinstance(flt, LogicOR):
        return flt.process
    else:
        return flt


def by_type(object_type):
    return lambda obj: obj.object_type == object_type


def has_childs():
    def scan_childs(obj):
        if obj.connected_objects:
            return True
        return False
    return scan_childs


def connection_depth(value=None, compare=None):
    """
    Generates function which compares connection depth of the element with the given value.
    :param value: value to compare to produce equality expression
    :param compare: expression (function) which takes depth as argument and returns boolean
    :return: function (function wrapper)
    """
    if value is None and compare is None:
        raise ValueError()

    def get_depth(obj):
        last, counter = obj.dive(counter=max_connection_depth)
        depth = max_connection_depth - counter
        if compare is None:
            return depth == value
        else:
            return compare(depth)
    return get_depth
