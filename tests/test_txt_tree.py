#!/usr/bin/python3

import importlib
import muskrat
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach
muskrat = importlib.reload(muskrat)
importlib.reload(muskrat)
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach

from . import scan_row, object_model


class SpecialChar(Pattern):
    def __init__(self):
        sc_prop = PatternProperties()
        sc_prop.add_property("char-cat", "special")
        sc_prop.add_property("is_char")
        sc_prop.add_property("void_prop_to_be_removed")
        sc_prop.add_property("prop_to_be", "removed")
        Pattern.__init__(
            self,
            "SpecialChar",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False),
            properties=sc_prop
        )


class SpecialCharTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = SpecialChar()
        self.extractor = CharString("!@#$%^&*()")

    def track(self):
        return True


def test_basic_output():
    parsed_string = "!@#"
    parser = Parser()
    allocator = Allocator(parsed_string, muskrat.allocator.WhitespaceVoid(), parser)
    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)
    tree.build()
