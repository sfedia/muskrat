#!/usr/bin/python3

import muskrat
from muskrat.parser import *
from muskrat.allocator import *
from muskrat.connectivity import Accept, Attach

from . import scan_row, object_model


class Transition(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Transition",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=True, insert=False)
        )


class TransitionTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = Transition()
        self.extractor = CharSequenceString(">")

    def track(self):
        return True


class AType(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "A",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class ATypeTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = AType()
        self.extractor = CharSequenceString("A")

    def track(self):
        return True


class BType(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "B",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False)
        )
        self.focus_on = lambda p, c: p.get(2)


class BTypeTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = BType()
        self.extractor = CharSequenceString("B")

    def track(self):
        return True


class CType(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "C",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False)
        )
        self.focus_on = lambda p, c: p.get(2)


class CTypeTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = CType()
        self.extractor = CharSequenceString("C")

    def track(self):
        return True


class DType(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "D",
            Accept().add_default(connect=True, insert=False),
            Attach().add_default(connect=True, insert=False)
        )
        self.focus_on = lambda p, c: p.get(2)


class DTypeTr(Tracker):
    def __init__(self, *args):
        Tracker.__init__(self, *args)
        self.pattern = DType()
        self.extractor = CharSequenceString("D")

    def track(self):
        return True


res_main = []
res_negative = []


def test_main():
    hierarchy_string = "A>B>C>D"
    parser = Parser()
    allocator = Allocator(hierarchy_string, muskrat.allocator.WhitespaceVoid(), parser)
    allocator.start()
    finish()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)

    def add_to_buffer(message):
        global res_main
        res_main.append(message)

    tree.print = add_to_buffer
    tree.build()

    sample1 = open("./tests/pg1_result1.txt", "r", encoding="utf-8").read()

    print("\n".join(res_main))

    assert "\n".join(res_main) == sample1


def test_negative():
    hierarchy_string = "A>B>C>D"
    parser = Parser()
    allocator = Allocator(hierarchy_string, muskrat.allocator.WhitespaceVoid(), parser)
    allocator.start()
    finish()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)
    res_negative = []

    def add_to_buffer(message):
        global res_negative
        res_negative.append(message)

    tree.print = add_to_buffer
    tree.build()

    sample2 = open("./tests/pg1_result2.txt", "r", encoding="utf-8").read()

    assert "\n".join(res_negative) != sample2


def finish():
    for sc in Pattern.__subclasses__():
        try:
            exec('del %s' % sc.__name__)
        except NameError:
            pass

    for sc in Tracker.__subclasses__():
        try:
            exec('del %s' % sc.__name__)
        except NameError:
            pass
