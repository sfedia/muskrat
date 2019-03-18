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


class Variables:
    def __init__(self):
        self.vars = dict()

    def add_var(self, var_name, var_value):
        self.vars[var_name] = var_value


class Exec1Tracker(Tracker):
    def __init__(self, *args):
        super().__init__(*args)


class VarName(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "VarName",
            Accept().add_default(connect=False, insert=False).add_option(
                LogicalOR(by_type("Is"), by_type("Value")), connect=True, insert=False
            ),
            Attach().add_default(connect=False, insert=False)
        )


class VarNameTr(Exec1Tracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = VarName()
        self.extractor = RegexString(r"[a-z]")

    def track(self):
        return True


class IsOperator(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Is",
            Accept().add_default(connect=False, insert=False).add_option(
                by_type("Value"), connect=True, insert=False
            ),
            Attach().add_default(connect=False, insert=False).add_option(
                by_type("VarName"), connect=True, insert=False
            )
        )


class IsOperatorTr(Exec1Tracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = IsOperator()
        self.extractor = CharSequenceString("=")

    def track(self):
        return True


class Value(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Value",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False).add_option(
                by_type("Is"), connect=True, insert=False
            )
        )


class ValueTr(Exec1Tracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = Value()
        self.extractor = RegexString("\d+")

    def track(self):
        return True


class Comma(Pattern):
    def __init__(self):
        Pattern.__init__(
            self,
            "Comma",
            Accept().add_default(connect=False, insert=False),
            Attach().add_default(connect=False, insert=False)
        )


class CommaTr(Exec1Tracker):
    def __init__(self, *args):
        super().__init__(*args)
        self.pattern = Comma()
        self.extractor = CharSequenceString(",")

    def track(self):
        return True


def test_main():
    my_vars = Variables()
    parser = Parser()
    text = "a = 1, b = 2, c = 3"
    allocator = Allocator(text, muskrat.allocator.WhitespaceVoid(), parser, parameters={
        "tracker_family": [Exec1Tracker]
    })
    allocator.start()

    tree = muskrat.txt_tree_generator.TXTTree(parser.objects, 2)
    tree.build()

    for var_name, value in align_filter_queries(parser.objects, by_type("VarName"), by_type("Value")):
        value.content = int(value.content)
        add_vars = ExecuteFromTree(my_vars, [var_name, value])
        add_vars.add_event_on_target(
            "name&value", "add_var", lambda t: [e.content for e in t], range(2), iterable_identifier=True
        )

    assert my_vars.vars['a'] == 1
    assert my_vars.vars['b'] == 2
    assert my_vars.vars['c'] == 3
