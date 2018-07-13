#!/usr/bin/python3

from lxml import etree


class XMLQuery:
    def __init__(self, object_row):
        """
        Translating sequence of ParsingObject to XML
        :param object_row: list of ParsingObject
        """
        self.default_tag = 'object'
        self.root_tag = 'root'
        self.root = etree.Element(self.root_tag)
        for obj in object_row:
            self.root.append(self.object2tag(obj))

    def object2tag(self, obj):
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
