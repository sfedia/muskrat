#!/usr/bin/python3

from .filters import *


class Pattern:
    def __init__(self, object_type, accept_policy, attach_policy, properties=None):
        self.object_type = object_type
        self.accept_policy = accept_policy
        self.attach_policy = attach_policy
        if properties is None:
            self.properties = PatternProperties()
        else:
            self.properties = properties


class PatternProperties:
    def __init__(self):
        self.both_side = {}
        self.bool_like = {}

    def add_property(self, key, value=None):
        if value is None:
            self.bool_like[key] = None
        else:
            self.both_side[key] = value

    def get_property(self, key):
        if key in self.both_side:
            return self.both_side[key]
        elif key in self.bool_like:
            return self.bool_like[key]

    def set_property(self, key, value):
        if key in self.both_side:
            self.both_side[key] = value
        else:
            raise ValueError

    def remove_property(self, key):
        if key in self.both_side:
            del self.both_side[key]
        elif key in self.bool_like:
            del self.bool_like[key]

    def dict_properties(self, bl_equivalent):
        """
        Return properties as a single dict-type object
        :param bl_equivalent: value to pass in k,v pair for bool-like properties
        :return: dict-type object
        """
        result = self.both_side
        for k in self.bool_like:
            result[k] = bl_equivalent
        return result


class Tracker:
    def __init__(self, parser, allocator):
        self.parser = parser
        self.allocator = allocator
        self._pattern = None
        self._extractor = None

    def track(self):
        # This one may be redefined by the inherited tracker class
        return False

    @property
    def pattern(self):
        if self._pattern is None:
            raise PatternNotFound()
        return self._pattern

    def get_extractor(self):
        if self._extractor is None:
            raise ExtractorNotFound()
        return self._extractor

    def set_extractor(self, value):
        self._extractor = value

    def prev(self, index, condition=None):
        if condition is not None:
            return self.parser.get(index, condition)
        else:
            return self.parser.get(index)

    def next(self, index):
        self.allocator.next(index)

    extractor = property(get_extractor, set_extractor)


class PatternNotFound(Exception):
    pass


class ExtractorNotFound(Exception):
    pass
