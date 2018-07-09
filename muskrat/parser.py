#!/usr/bin/python3

from .pattern import PatternNotFound


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
    def __init__(self, content, pattern_=None):
        self.connected_objects = []
        self.content = content
        self._pattern = pattern_

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
