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


class TXTTree:
    def __init__(self, object_row, indent=2):
        self.object_row = object_row
        self.indent = indent

    def print_row(self, row, indent):
        for obj in row:
            self.print(" " * indent + '<%s> = "%s"' % (obj.pattern.object_type, obj.content,))
            for (prop, value) in obj.pattern.properties.dict_properties(None).items():
                prop_msg = " " * indent + "- " + prop
                if value:
                    prop_msg += ": " + '"%s"' % value
                self.print(prop_msg)
            self.print_row(obj.connected_objects, indent + self.indent)

    def print(self, message):
        print(message)

    def build(self):
        self.print_row(self.object_row, 0)
