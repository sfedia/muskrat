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


class Latin(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Latin",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class LatinTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Latin()
        self.extractor = RegexString('[A-Za-z]+')

    def track(self):
        return True


class Digit(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Digit",
            Accept().add_default(connect=False, insert=False),
            Attach().add_option(muskrat.filters.by_type("Latin"), connect=True, insert=False)
        )


class DigitTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Digit()
        self.extractor = RegexString(r'\d+')

    def track(self):
        try:
            return self.parser.get(1).pattern.object_type == "Latin"
        except AttributeError:
            return False


res_main = []


def test_main():
    parser = Parser()
    text = "lorem1 ipsum2 dolor3 sit4 amet5"
    allocator = Allocator(text, muskrat.allocator.WhitespaceVoid(), parser)
    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)

    def add_to_buffer(message):
        global res_main
        res_main.append(message)

    tree.print = add_to_buffer
    tree.build()

    li1_sample = open("./tests/li1_result1.txt", "r", encoding="utf-8").read()

    print("\n".join(res_main))

    assert "\n".join(res_main) == li1_sample
