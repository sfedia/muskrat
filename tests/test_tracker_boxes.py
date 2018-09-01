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


class Alpha(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Alpha",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class AlphaTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Alpha()
        self.extractor = RegexString(r'[a-z]')

    def track(self):
        return True


class Digit(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Digit",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class DigitTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Digit()
        self.extractor = RegexString(r'\d')

    def track(self):
        return True


class Alphanumeric(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Alphanumeric",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class AlphanumericTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Alphanumeric()
        self.extractor = RegexString(r'[a-z0-9]')

    def track(self):
        return True


res_main = []


def test_main():
    parser = Parser()
    allocator = Allocator("a1b2c3d4ef", muskrat.allocator.WhitespaceVoid(), parser)

    alphanumeric_priority = TrackerBox(["Alphanumeric"], {"Alphanumeric": 0})
    allocator.tracker_boxes.append(alphanumeric_priority)

    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)

    def add_to_buffer(message):
        global res_main
        res_main.append(message)

    tree.print = add_to_buffer
    tree.build()

    sample1 = open("./tests/tb1_result1.txt", "r", encoding="utf-8").read()

    print("\n".join(res_main))

    assert "\n".join(res_main) == sample1
