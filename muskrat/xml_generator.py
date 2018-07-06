#!/usr/bin/python3

from lxml import etree


class XMLQuery:
    def __init__(self, object_row):
        """
        Translating sequence of ParsingObject to XML
        :param object_row: list of ParsingObject
        """
        self.default_tag = 'object'
        self.row = [self.object2tag(obj) for obj in object_row]

    def object2tag(self, obj):
        obj_tag = etree.Element(self.default_tag, self.get_parameters(obj))
        for child in obj.connected_objects:
            obj_tag.append(self.object2tag(child))
        return obj_tag

    @staticmethod
    def get_parameters(obj):
        return dict(
            {
                "type": obj.object_type,
                "content": obj.content
            },
            **obj.properties.dict_properties(".")
        )
