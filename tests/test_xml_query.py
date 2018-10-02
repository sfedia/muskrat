#!/usr/bin/python3

import importlib
import muskrat
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach
from muskrat.xml_generator import *
muskrat = importlib.reload(muskrat)
importlib.reload(muskrat)
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach
from muskrat.xml_generator import *

from . import scan_row, object_model


class DescBracket(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "DescBracket",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class DescBracketTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = DescBracket()
        self.extractor = CharSequenceString("[")

    def track(self):
        try:
            if self.current().startswith("["):
                self.parser.get(1).pattern.properties.add_property("parent")
        except AttributeError:
            return False
        return True


class StopBracket(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "StopBracket",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class StopBracketTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = StopBracket()
        self.extractor = CharSequenceString("]")

    def track(self):
        return True


class ListingComma(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "ListingComma",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class ListingCommaTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = ListingComma()
        self.extractor = CharSequenceString(",")

    def track(self):
        return True


class ElementQ(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "ElementQ",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False),
            focus_on=lambda p, c: p.get(
                condition=lambda o: "Element" in o.pattern.object_type and o.pattern.properties.property_exists("parent")
            )
        )


class ElementQTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = ElementQ()
        self.extractor = RegexString('[a-z]\?')

    def track(self):
        return True


class Element(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Element",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False),
            focus_on=lambda p, c: p.get(
                condition=lambda o: "Element" in o.pattern.object_type and o.pattern.properties.property_exists("parent")
            )
        )


class ElementTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Element()
        self.extractor = RegexString('[a-z]')

    def track(self):
        return True


def test_global_search():
    parser = Parser()
    allocator = Allocator("a[b?,c?[u, q?[l, j?, t?]]", muskrat.allocator.WhitespaceVoid(), parser)

    allocator.start()

    po = XMLQuery(parser.objects)

    assert [e.get('content') for e in po.root.xpath("//*/object[@type='ElementQ']")] == ['b?', 'c?', 'q?', 'j?', 't?']
