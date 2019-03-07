#!/usr/bin/python3


import importlib
import muskrat
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach
from muskrat.class_generator import *
muskrat = importlib.reload(muskrat)
importlib.reload(muskrat)
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach
from muskrat.class_generator import *

from . import scan_row, object_model


class PTGTracker(Tracker):
    def __init__(self, *args):
        super().__init__(*args)


class LeftParen(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "LeftParen",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class LeftParenTr(PTGTracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = LeftParen()
        self.extractor = CharSequenceString("(")

    def track(self):
        return True


class Content(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Content",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class ContentTr(PTGTracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = Content()
        self.extractor = RegexString(r"[^\(\)]+")

    def track(self):
        return True


class RightParen(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "RightParen",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False),
            focus_on=lambda p, c: p.get(condition=lambda o: o.pattern.object_type == "LeftParen")
        )


class RightParenTr(PTGTracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = RightParen()
        self.extractor = CharSequenceString(")")

    def track(self):
        return True


def test_main():
    parser = Parser()
    text = "a(bc(d)ef(gh))"
    allocator = Allocator(text, muskrat.allocator.WhitespaceVoid(), parser, parameters={
        "tracker_family": [PTGTracker]
    })
    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)
    tree.build()

    for pgt in between_paired_types(
            parser.objects,
            lambda o: o.pattern.object_type == "LeftParen",
            lambda o: o.pattern.object_type == "RightParen"):
        group0 = ['(', 'd', ')']
        for e, obj in enumerate(pgt.get_group(0).get_objects_only()):
            assert obj.content == group0[e]
        group1 = ['(', 'gh', ')']
        for e, obj in enumerate(pgt.get_group(1).get_objects_only()):
            assert obj.content == group1[e]
        pgt_goo = ['(', 'bc', 'ef', ')']
        for e, obj in enumerate(pgt.get_objects_only()):
            assert obj.content == pgt_goo[e]

    for pgt in between_paired_types(
            parser.objects,
            lambda o: o.pattern.object_type == "LeftParen",
            lambda o: o.pattern.object_type == "RightParen",
            include_borders=False):
        group0 = ['d']
        for e, obj in enumerate(pgt.get_group(0).get_objects_only()):
            assert obj.content == group0[e]
        group1 = ['gh']
        for e, obj in enumerate(pgt.get_group(1).get_objects_only()):
            assert obj.content == group1[e]
        pgt_goo = ['bc', 'ef']
        for e, obj in enumerate(pgt.get_objects_only()):
            assert obj.content == pgt_goo[e]


test_main()
