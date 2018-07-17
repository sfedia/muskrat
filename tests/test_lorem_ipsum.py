#!/usr/bin/python3


import muskrat
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


def test_main():
    parser = Parser()
    text = "lorem1 ipsum2 dolor3 sit4 amet5"
    allocator = Allocator(text, muskrat.allocator.WhitespaceVoid(), parser)
    allocator.start()
    assert scan_row(
        parser.objects,
        [
            object_model(
                type="Latin",
                content="lorem",
                connected=[
                    object_model(
                        type="Digit",
                        content="1",
                        connected=[]
                    )
                ]
            ),
            object_model(
                type="Latin",
                content="ipsum",
                connected=[
                    object_model(
                        type="Digit",
                        content="2",
                        connected=[]
                    )
                ]
            ),
            object_model(
                type="Latin",
                content="dolor",
                connected=[
                    object_model(
                        type="Digit",
                        content="3",
                        connected=[]
                    )
                ]
            ),
            object_model(
                type="Latin",
                content="sit",
                connected=[
                    object_model(
                        type="Digit",
                        content="4",
                        connected=[]
                    )
                ]
            ),
            object_model(
                type="Latin",
                content="amet",
                connected=[
                    object_model(
                        type="Digit",
                        content="5",
                        connected=[]
                    )
                ]
            )
        ]
    )
