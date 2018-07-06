#!/usr/bin/python3


def by_type(object_type):
    return lambda obj: obj.object_type == object_type


def has_childs():
    def scan_childs(obj):
        if obj.connected_objects:
            return True
        return False
    return scan_childs


def connection_depth(number):
    def get_depth(obj):
        inf = 9999
        last, counter = obj.dive(counter=inf)
        return inf - counter
    return get_depth