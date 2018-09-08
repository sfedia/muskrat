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

from .parser import Parser, ParsingObject
import muskrat.allocator


class Pattern:
    def __init__(self, object_type, accept_policy, attach_policy, properties=None, focus_on=None):
        """
        Pattern subclass-instances are used to assign properties to objects, give them names, \
        create policies for them etc.
        :param object_type: object type
        :param accept_policy: Accept class instance
        :param attach_policy: Attach class instance
        :param properties: properties to be set when creating the instance
        :param focus_on: function to search any previous element in Parser
        """
        self.object_type = object_type
        self.accept_policy = accept_policy
        self.attach_policy = attach_policy
        self.focus_on = lambda parser, content: parser.get(1)
        self.insertion_prepend_value = False
        self.prepended_value = " "

        if properties is None:
            self.properties = PatternProperties()
        else:
            self.properties = properties

        if focus_on is not None:
            self.focus_on = focus_on


class PatternProperties:
    def __init__(self):
        self.both_side = {}
        self.bool_like = {}

    def add_property(self, key, value=None):
        """
        Add a property to the object pattern
        :param key: property name
        :param value: value of the property
        """
        if value is None:
            self.bool_like[key] = None
        else:
            self.both_side[key] = value

    def get_property(self, key):
        """
        Get a property of the object pattern
        :param key: property name
        """
        if key in self.both_side:
            return self.both_side[key]
        elif key in self.bool_like:
            return self.bool_like[key]

    def set_property(self, key, value):
        """
        Set a property of the object pattern
        :param key: property name
        :param value: value of the property
        :raises: ValueError
        """
        if key in self.both_side:
            self.both_side[key] = value
        else:
            raise ValueError

    def property_exists(self, key):
        """
        Check if a property exists for the object pattern
        :param key: property name
        :rtype: bool
        """
        return key in self.both_side or key in self.bool_like

    def remove_property(self, key):
        """
        Remove a property of the object pattern
        :param key: property name
        :raises: KeyError
        """
        if key in self.both_side:
            del self.both_side[key]
        elif key in self.bool_like:
            del self.bool_like[key]

    def dict_properties(self, bl_equivalent):
        """
        Return properties as a single dict-type object
        :param bl_equivalent: value to pass into k/v pair for bool-like properties
        :return: properties of the object pattern
        :rtype: dict
        """
        result = self.both_side
        for k in self.bool_like:
            result[k] = bl_equivalent
        return result


class Tracker:
    """Trackers are used to extract meaningful units from the text"""
    def __init__(self, parser, allocator):
        """
        :param parser: parser instance
        :type parser: Parser
        :param allocator: allocator instance
        :type allocator: muskrat.allocator.Allocator
        """
        self.parser = parser
        self.allocator = allocator
        self._pattern = None
        self._extractor = None
        self.connection_hooks = []
        self.insertion_hook = lambda left, fe, pv, p, a: pv + left
        self.takes_all = False

    def track(self):
        # This one may be redefined by the inherited tracker class
        return False

    def get_pattern(self):
        if self._pattern is None:
            raise PatternNotFound(self.__class__.__name__)
        return self._pattern

    def set_pattern(self, value):
        self._pattern = value

    def get_extractor(self):
        if self._extractor is None:
            raise ExtractorNotFound()
        return self._extractor

    def set_extractor(self, value):
        self._extractor = value

    def prev(self, index=1, condition=None):
        """
        Get the previous object (call the parser)
        :param index: number of steps taken backwards
        :param condition: object-checking condition if the form of function
        :rtype: ParsingObject
        """
        if condition is not None:
            return self.parser.get(index, condition)
        else:
            return self.parser.get(index)

    def next(self, index=1):
        """
        Get the previous object (call the parser)
        :param index: number of steps taken backwards
        :rtype: ParsingObject
        """
        return self.allocator.next(index)

    def next_by_extractor(self, *args):
        return self.allocator.next_by_extractor(*args)

    def current(self):
        return self.allocator.units[self.allocator.current]

    def add_connection_hook(self, conn_hook):
        self.connection_hooks.append(conn_hook)

    extractor = property(get_extractor, set_extractor)
    pattern = property(get_pattern, set_pattern)


class PatternNotFound(Exception):
    pass


class ExtractorNotFound(Exception):
    pass
