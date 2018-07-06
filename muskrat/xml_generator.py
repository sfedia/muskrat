#!/usr/bin/python3

from lxml import etree


class XMLQuery:
    def __init__(self, object_row):
        """
        Translating sequence of ParsingObject to XML syntax
        :param object_row: list of ParsingObject
        """
        self.default_tag = 'object'
        self.xml_string = "".join([self.object2tag(obj) for obj in object_row])

    def object2tag(self, obj):
        obj_tag = XMLElement(self.default_tag)
        obj_tag.left_slice = self.create_left(obj)
        for child in obj.connected_objects:
            obj_tag.insert(self.object2tag(child))

        return obj_tag.build()

    @staticmethod
    def xml_escape(markup):
        escape = {
            '"': '&quot;',
            "'": '&apos;',
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '\n': '&#10;'
        }
        for (fm, to) in escape.items():
            markup = markup.replace(fm, to)
        return markup

    @staticmethod
    def get_parameters(obj):
        return dict(
            {
                "type": obj.object_type
            },
            **obj.properties.dict_properties(None)
        )

    def create_left(self, obj):
        parameters = []
        for (k, v) in self.get_parameters(obj).items():
            if v is not None:
                parameters.append('%s="%s"' % (k, v,))
            else:
                parameters.append(k)

        return "<object %s>" % " ".join(parameters)

    def tree(self):
        return etree.XML(self.xml_string)


class XMLElement:
    def __init__(self, tag_name):
        self.tag_name = tag_name
        self.left_slice = None
        self.inner_content = []
        self.right_slice = '</%s>' % self.tag_name

    def insert(self, content):
        self.inner_content.append(content)

    def get_inner(self):
        return " ".join(self.inner_content)

    def build(self):
        return self.left_slice + self.inner_content + self.right_slice