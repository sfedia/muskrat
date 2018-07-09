#!/usr/bin/python3
import re


class Allocator:
    def __init__(self, text, splitter, position=0):
        self.newline_equivalent = " "
        self.carriage_equivalent = ""
        self.__char_equivalents = {}
        self.text = text
        self.units = []
        self.splitter = splitter
        if not issubclass(self.splitter, Extractor):
            raise ValueError()

    def make_units(self):
        if self.units:
            raise AlreadyAllocated()

        self.text = self.text.replace("\n", self.newline_equivalent)
        self.text = self.text.replace("\r", self.carriage_equivalent)

        if isinstance(self.splitter, WhitespaceVoid):
            self.units = self.text.split()
        elif isinstance(self.splitter, CharSequenceString):
            self.units = self.text.split(self.splitter.value)
        elif isinstance(self.splitter, RegexString):
            self.units = re.split(self.splitter.value, self.text)
        elif isinstance(self.splitter, CharList):
            self.units = re.split('[' + re.escape("".join(self.splitter.value)) + ']', self.text)
        elif isinstance(self.splitter, CharString):
            self.units = re.split('[' + re.escape(self.splitter.value) + ']', self.text)
        elif isinstance(self.splitter, LengthInteger):
            self.units = [
                self.text[n:n+self.splitter.value] for n in range(0, len(self.text), self.splitter.value)
            ]

    def add_char_equivalent(self, char, equivalent):
        if len(char) + len(equivalent) != 2:
            raise ValueError()
        self.__char_equivalents[char] = equivalent


class Extractor:
    def __init__(self, value):
        self.value = value


class CharSequenceString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class WhitespaceVoid(Extractor):
    def __init__(self):
        Extractor.__init__(self, " ")


class CharList(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class CharString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class RegexString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class LengthInteger(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class AlreadyAllocated(Exception):
    pass
