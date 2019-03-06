#!/usr/bin/python3

"""
Muskrat: minimalistic non-BNF text parser and tree generator
Copyright (C) 2019 Fyodor Sizov

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

from math import inf
from .parser import iterate_objects
from .filters import *


class ExecuteFromTree:
    def __init__(self, target, tree):
        self.target = target
        self.tree = tree
        self.argument_states = dict()

    def __new_arg_state(self, argument_name, **state):
        self.argument_states[argument_name] = state

    def raise_if_not_passed(self, argument_name, exception):
        if not self.argument_states[argument_name]["passed"]:
            raise exception

    def add_event_on_target(
            self,
            argument_name,
            attr_name,
            selector,
            identifier,
            when=lambda data: True,
            form=lambda data: data,
            blocks=False,
            args=None,
            kwargs=None,
            identifier_as_key=False):

        if argument_name in self.argument_states and self.argument_states[argument_name]["blocked"]:
            return

        data = selector(self.tree)

        if when(data):
            data = form(data)
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}

            if type(identifier) == int and not identifier_as_key:
                args.insert(identifier, data)
            else:
                kwargs[identifier] = data

            if attr_name == "__init__":
                self.target = self.target(*args, **kwargs)
            else:
                getattr(self.target, attr_name)(*args, **kwargs)

            if argument_name not in self.argument_states:
                self.__new_arg_state(argument_name, blocked=blocks, passed=True)


class AlignQueries:
    def __iter__(self):
        return self

    def __init__(self, objects, *query_functions, equal_length=True):
        self.queries = query_functions
        self.found = [query(objects) for query in self.queries]
        self.counter = 0
        if equal_length and len(set(query_functions)) > 1:
            raise DifferentLengthQueries

    def __next__(self):
        if self.counter == len(self.found[0]):
            raise StopIteration
        generated_tree = [query[self.counter] for query in self.queries]
        self.counter += 1
        return generated_tree


class AlignFilterQueries(AlignQueries):
    def __init__(self, objects, *filter_queries, equal_length=True):
        def filter_query_wrapper(filter_query):
            def query(o):
                return [
                    object_ for behind_, depth_, selected, object_ in iterate_objects(
                        o, inf, condition=lambda obj: unify(filter_query).process(obj)) if selected
                ]
            return query
        AlignQueries.__init__(self, objects, [filter_query_wrapper(flt) for flt in filter_queries], equal_length)


class CannotAddArgument(Exception):
    pass


class DifferentLengthQueries(Exception):
    pass
