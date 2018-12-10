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

import muskrat.pattern
from collections import namedtuple


class Parser:
    """
    Parser class-instances receive parsed objects from allocator
    """
    def __init__(self):
        self.objects = []
        self.depth_limit = None

    def get(self, behind=1, condition=lambda obj: True, return_dit=False):
        """
        Method used to acquire certain object from the parser
        :param behind: number of element to select which satisfies the condition
        :type behind: int
        :param condition: object-checking condition if the form of function
        :param return_dit: parameter which determines if the whole 'dit' should be returned
        :rtype: ParsingObject
        """
        dit = DiveIterator(self.objects, behind, condition, self.depth_limit)
        for fg_child in dit:
            pass

        if return_dit:
            return dit

        return dit.this if dit.this else None

    def append(self, obj):
        """
        Add an object to the parser
        :param obj: object to append
        :type obj: ParsingObject
        """
        self.objects.append(obj)


class ParsingObject:
    """A single entity which represents parsing object"""
    def __init__(self, content, pattern_=None):
        """
        Create the parsing object instance
        :param content: content of the object
        :param pattern_: pattern of the object
        :type pattern_: muskrat.pattern.Pattern
        """
        self.connected_objects = []
        self.content = content
        self._pattern = pattern_

    @property
    def pattern(self):
        """
        Get the pattern
        :return: pattern
        """
        if self._pattern is None:
            raise muskrat.pattern.PatternNotFound()
        return self._pattern

    def connect(self, object2connect):
        """
        Append a child object to the current object
        :param object2connect: child object
        :type object2connect: ParsingObject
        """
        self.connected_objects.append(object2connect)

    def dive(self, behind=1, condition=lambda obj: True, depth_limit=None, return_dit=False):
        dit = DiveIterator(self.connected_objects, behind, condition, depth_limit)
        for fg_child in dit:
            pass

        if return_dit:
            return dit

        return dit.this if dit.this else None

    def insert_content(self, content2insert, update_function=None):
        """
        Insert content to the current object
        :param content2insert: text content
        :type content2insert: int
        :param update_function: function which modifies the content of the element after insertion
        """
        self.content += content2insert
        if update_function is not None:
            self.content = update_function(self.content)


class DiveIterator:
    def __iter__(self):
        return self

    def __init__(self, objects, behind=1, condition=lambda obj: True, depth_limit=None):
        self.objects = list(reversed(objects))
        self.behind = behind
        self.condition = condition
        self.depth_limit = depth_limit
        self.current_object = 0
        self.counter = 0
        self.this = None
        self.is_selected = False
        self.object_wrapper = namedtuple("ObjectWrapper", ["selected", "obj"])

    def __next__(self):
        if self.current_object == len(self.objects):
            raise StopIteration

        self.is_selected = False
        self.counter += 1
        child_di = DiveIterator(
            self.objects[self.current_object].connected_objects,
            self.behind,
            self.condition,
            self.depth_limit
        )

        for o in child_di:
            pass

        self.counter += child_di.counter
        self.behind = child_di.behind

        if child_di.this:
            self.this = child_di.this
        elif self.depth_limit is not None and self.counter < self.depth_limit or self.counter:
            if self.condition(self.objects[self.current_object]):
                if self.behind == 1:
                    self.this = self.objects[self.current_object]
                elif self.behind > 1:
                    self.is_selected = True
                    self.behind -= 1

        if self.this:
            raise StopIteration

        self.current_object += 1

        return self.object_wrapper(self.is_selected, self.objects[self.current_object - 1])
