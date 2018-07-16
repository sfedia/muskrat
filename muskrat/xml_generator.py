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

from lxml import etree
from .parser import ParsingObject


class XMLQuery:
    def __init__(self, object_row):
        """
        Translate sequence of ParsingObject to XML
        :param object_row: list of ParsingObject
        """
        self.default_tag = 'object'
        self.root_tag = 'root'
        self.root = etree.Element(self.root_tag)
        for obj in object_row:
            self.root.append(self.object2tag(obj))

    def object2tag(self, obj):
        """
        Convert ParsingObject to XML tag
        :param obj: ParsingObject instance
        :type obj: ParsingObject
        :return: XML tag
        :rtype: etree.Element
        """
        obj_tag = etree.Element(self.default_tag, self.get_parameters(obj))
        for child in obj.connected_objects:
            obj_tag.append(self.object2tag(child))
        return obj_tag

    @staticmethod
    def get_parameters(obj):
        return dict(
            {
                "type": obj.pattern.object_type,
                "content": obj.content
            },
            **obj.pattern.properties.dict_properties(".")
        )
