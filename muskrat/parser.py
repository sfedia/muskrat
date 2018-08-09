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


class Parser:
    """
    Parser class-instances receive parsed objects from allocator
    """
    def __init__(self):
        self.objects = []
        self.depth_limit = None

    def get(self, behind=1, condition=lambda obj: True):
        """
        Method used to acquire certain object from the parser
        :param behind: number of element to select which satisfies the condition
        :type behind: int
        :param condition: object-checking condition if the form of function
        :rtype: ParsingObject
        """
        if self.depth_limit and behind > self.depth_limit:
            return None

        for obj in reversed(self.objects):
            fc, behind = obj.dive(behind, condition)
            if fc is not None:
                return fc
            if condition(obj):
                behind -= 1
            if not behind:
                return obj
        return None

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

    def dive(self, counter=1, condition=lambda obj: True):
        """
        Internal method used to find connected (child) objects
        :param counter: number of element to select which satisfies the condition
        :type counter: int
        :param condition: object-checking condition if the form of function
        :rtype: (ParsingObject, int)
        """
        for obj in reversed(self.connected_objects):
            if condition(obj):
                counter -= 1
            if counter < 0:
                break
            elif not counter:
                return obj, 0
            found_child, counter = obj.dive(counter, condition)
            if found_child is not None:
                return found_child, counter
        return None, counter

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
