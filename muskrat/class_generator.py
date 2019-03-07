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
from collections import deque
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
        generated_tree = [query[self.counter] for query in self.found]
        self.counter += 1
        return generated_tree


class AlignFilterQueries(AlignQueries):
    def __init__(self, objects, *filter_queries, equal_length=True):
        def filter_query_wrapper(filter_query):
            def query(o):
                return [
                    object_ for behind_, depth_, level, selected, object_ in iterate_objects(
                        o, inf, condition=lambda obj: unify(filter_query).process(obj)) if selected
                ]
            return query
        AlignQueries.__init__(self, objects, [filter_query_wrapper(flt) for flt in filter_queries], equal_length)


class PairedTypesGroup:
    def __init__(self):
        self.this_row = deque([])
        self.pgt_in = deque([])

    def add_object(self, object_):
        if not self.pgt_in:
            self.this_row.appendleft(object_)
        else:
            self.pgt_in[0].add_object(object_)

    def add_pgt(self):
        self.this_row.appendleft(PairedTypesGroup())
        self.pgt_in.appendleft(self.this_row[0])

    def remove_last_pgt(self):
        try:
            self.pgt_in.pop()
            return True
        except IndexError:
            return False

    def equalize_levels(self):
        i = 0
        while i < len(self.this_row) - 1:
            this = self.this_row[i]
            nxt = self.this_row[i + 1]
            if isinstance(this, PairedTypesGroup):
                this.equalize_levels()
            if isinstance(nxt, PairedTypesGroup):
                nxt.equalize_levels()
            elif not isinstance(this, PairedTypesGroup) and nxt.level > this.level:
                self.this_row.pop(i + 1)
            i += 1
        return self

    def get_objects_only(self):
        yield from [obj for obj in self.this_row if not isinstance(obj, PairedTypesGroup)]

    def get_pgt_only(self):
        yield from [obj for obj in self.this_row if isinstance(obj, PairedTypesGroup)]

    def get_group(self, *path, stop_at_max=False):
        path = list(path)
        pgt = self
        while path:
            pgt_in = [obj for obj in pgt.get_pgt_only()]
            try:
                pgt = pgt_in[path.pop()]
            except IndexError:
                if stop_at_max:
                    pgt = pgt_in[-1]
                else:
                    raise IndexError
        return pgt


def between_paired_types(objects, left_border, right_border, include_borders=True, equalize=True):
    between = deque([])
    inside_last = False

    for behind_, depth_, level, selected, object_ in iterate_objects(objects, behind=inf):
        object_.level = level
        if right_border(object_):
            if not inside_last:
                between.appendleft(PairedTypesGroup())
                inside_last = True
                if include_borders:
                    between[0].add_object(object_)
            else:
                between[0].add_pgt()
                if include_borders:
                    between[0].add_object(object_)
        elif left_border(object_):
            if include_borders:
                between[0].add_object(object_)
                inside_last = between[0].remove_last_pgt()
        elif inside_last:
            between[0].add_object(object_)

    if not equalize:
        yield from between
    else:
        yield from [ptg.equalize_levels() for ptg in between]


class CannotAddArgument(Exception):
    pass


class DifferentLengthQueries(Exception):
    pass
