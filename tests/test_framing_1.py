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


class CommonTracker(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)


class PlainTextTracker(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)


class LTTag(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "<Tag",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class LTTagTr(CommonTracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = LTTag()
        self.extractor = CharSequenceString("<")

    def track(self):
        return True


class TagGT(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Tag>",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class TagGTTr(PlainTextTracker):
    def __init__(self, *args):
        PlainTextTracker.__init__(self, *args)
        self.pattern = TagGT()
        self.extractor = CharSequenceString(">")

    def track(self):
        return True


class LChar(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "LChar",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class LCharTr(PlainTextTracker):
    def __init__(self, *args):
        PlainTextTracker.__init__(self, *args)
        self.pattern = LChar()
        self.extractor = CharSequenceString("l")

    def track(self):
        return True


class XTest(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "XTest",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False).add_option(
                by_type("<Tag"), connect=True, insert=False
            )
        )


class XTestTr(PlainTextTracker):
    def __init__(self, *args):
        PlainTextTracker.__init__(self, *args)
        self.pattern = XTest()
        self.extractor = RegexString("m[a-z]+")

    def track(self):
        return True


class LMGreedy(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "LMGreedy",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class LMGreedyTr(CommonTracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = LMGreedy()
        self.extractor = CharSequenceString("lm")

    def track(self):
        return True


class AlphaChar(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "AlphaChar",
            Accept().add_default(connect=False, insert=False).add_option(
                by_type("<Tag"), connect=True, insert=False
            ),
            Attach().add_default(connect=False, insert=False)
        )


class AlphaCharTr(CommonTracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = AlphaChar()
        self.extractor = RegexString("[a-z]")

    def track(self):
        return True


res_main = []


def test_main():
    parser = Parser()
    text = "lmao <lmao> lmao"
    allocator = Allocator(text, CharSequenceString(" "), parser, parameters={
        "tracker_family": [CommonTracker]
    })
    allocator.cursor.add_dynamic_mapper(
        lambda p, c: p.get(1).pattern.object_type == "<Tag",
        lambda p, c: p.get(1).pattern.object_type == "Tag>",
        tracker_family=[PlainTextTracker],
        depend_on=lambda p, c: p.get(1)
    )

    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)

    def add_to_buffer(message):
        global res_main
        res_main.append(message)

    tree.print = add_to_buffer
    tree.build()

    fr1_sample = open("./tests/fr1_result1.txt", "r", encoding="utf-8").read()

    print("\n".join(res_main))

    assert "\n".join(res_main) == fr1_sample
