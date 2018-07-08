#!/usr/bin/python3

from .pattern import *

class Parser:
    def __init__(self):
        self.objects = []

    def get(self, behind=1, condition=lambda x: True):
        for obj in reversed(self.objects):
            fc, behind = obj.dive(behind, condition)
            if fc is not None:
                return fc
        return None

    def append(self, obj):
        self.objects.append(obj)


class ParsingObject:
    def __init__(self, content, parser, allocator):
        self.connected_objects = []
        self.content = content
        self._pattern = None
        for tracker in Tracker.__subclasses__():
            tracking = tracker(parser, allocator)
            if tracking.track():
                self._pattern = tracking.pattern
                break

    @property
    def pattern(self):
        if self._pattern is None:
            raise PatternNotFound()
        return self._pattern

    def connect(self, object2connect):
        self.connected_objects.append(object2connect)

    def dive(self, counter=1, condition=lambda x: True):
        for obj in reversed(self.connected_objects):
            if condition(obj):
                counter -= 1
            if counter < 0:
                break
            elif not counter:
                return self, 0
            found_child, counter = obj.dive(counter, condition)
            if found_child is not None:
                return found_child, counter
        return None, counter

    def insert_content(self, content2insert, update_function=None):
        self.content += content2insert
        if update_function is not None:
            self.content = update_function(self.content)

class LineProcessing:
    def __init__(self, line_text):
        self.line_units = line_text.split()
        self.current_index = 0

    def current(self):
        return self.line_units[self.current_index]

    def next(self, add=0):
        return self.line_units[self.current_index + 1 + add]


class ParsingUnit:
    def __init__(self, line_units, unit_index):
        self.content = line_units[unit_index]

    def what(self):
        ...


class UnitEntity:
    def __init__(self):