#!/usr/bin/python3

"""
Muskrat: minimalistic non-BNF text parser and tree generator
Copyright (C) 2018 Fyodor Sizov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from random import sample
from .pattern import *
from .defaults import *
from .parser import Parser, ParsingObject
from .connectivity import *


class Allocator:
    """Allocator is used to divide the whole text into units"""
    def __init__(self, text, splitter, parser, position=0):
        """
        Create an allocator instance
        :param text: the whole text
        :type text: str
        :param splitter: template to split the text into primary units
        :type splitter: Extractor
        :param parser: parser object which acquires the parsed units
        :type parser: Parser
        :param position: index of a char allocator should start the job from
        """
        self.newline_equivalent = " "
        self.carriage_equivalent = ""
        self.end_position = None
        self.greedy = True
        self.parallel_moving = False
        self.framing_group = None
        self.framing_substrings = []
        self._framing_start = None
        self.__char_equivalents = {}
        self.text = text
        self.parser = parser
        self.units = []
        self.current = position
        self.splitter = splitter
        if not issubclass(type(self.splitter), Extractor):
            raise ValueError()

    def get_frs(self):
        if self._framing_start is None:
            return None

        if self.current >= self._framing_start:
            return self._framing_start
        else:
            return self.current

    def set_frs(self, value):
        self._framing_start = value

    framing_start = property(get_frs, set_frs)

    def make_units(self):
        if self.units:
            raise AlreadyAllocated()

        if self.end_position:
            self.text = self.text[:self.end_position]

        if self.framing_substrings:
            self.framing_group = self.generate_framing_group()
            for fs in self.framing_substrings:
                self.text = self.text.replace(fs, self.framing_group)

        self.text = self.text.replace("\n", self.newline_equivalent)
        self.text = self.text.replace("\r", self.carriage_equivalent)

        if isinstance(self.splitter, WhitespaceVoid):
            self.units = self.text.split()

        elif isinstance(self.splitter, CharSequenceString):
            self.units = self.text.split(self.splitter.value)

        elif isinstance(self.splitter, RegexString):
            self.units = re.split(self.splitter.value, self.text)

        elif isinstance(self.splitter, LimitRegexString):
            self.units = [x.group(0) for x in re.finditer(self.splitter.value, self.text)]

        elif isinstance(self.splitter, CharList):
            self.units = re.split('[' + re.escape("".join(self.splitter.value)) + ']', self.text)

        elif isinstance(self.splitter, CharString):
            self.units = re.split('[' + re.escape(self.splitter.value) + ']', self.text)

        elif isinstance(self.splitter, LengthInteger):
            self.units = [
                self.text[n:n+self.splitter.value] for n in range(0, len(self.text), self.splitter.value)
            ]

        if self.end_position and len(self.units) > 1:
            del self.units[-1]

    def start_move(self):
        while self.current < len(self.units):
            self.move_right()

    def start(self):
        """Start the job"""
        self.make_units()
        self.start_move()

    def next(self, add=1):
        if self.current + add >= len(self.units):
            return None
        return self.units[self.current + add]

    def check_framing(self, index):
        if self.framing_group and self.framing_group in self.units[index]:
            left, right = self.units[index].split(self.framing_group)
            self.units[index] = left
            self.framing_start = index + 1
            self.units.insert(index, right)
            self.check_framing(self.framing_start)

    def move_right(self):
        if self.framing_group:
            self.check_framing(self.current)

        current = self.units[self.current]
        trackers = []

        if self.framing_group:
            self.parser.depth_limit = self.current - self.framing_start

        for tracker in Tracker.__subclasses__():
            tracking = tracker(self.parser, self)
            if tracking.track():
                trackers.append(tracking)
        if not trackers:
            raise CannotMoveRight("Failed on unit %d = '%s'" % (self.current, current,))

        parts = []
        part_obj = namedtuple('Part', 'pattern pair')
        for tracker in trackers:
            try:
                part = part_obj(tracker.pattern, self.extract(current, tracker.extractor, tracker.takes_all))
            except ExtractionFailed:
                continue
            parts.append(part)

        if not parts:
            raise CannotMoveRight("Failed on unit %d = '%s'" % (self.current, current,))

        if self.parallel_moving:
            raise VersionOutOfDate(feature_coming)

        parts = sorted(parts, key=lambda x: len(x.pair[0]), reverse=self.greedy)
        left, right = parts[0].pair
        left_object = ParsingObject(left, parts[0].pattern)
        focused_prev = parts[0].pattern.focus_on(self.parser)

        if focused_prev is None:
            self.parser.append(left_object)
        else:
            mrg = merge_policies(
                focused_prev.pattern.accept_policy.get_policy(parts[0]),
                parts[0].pattern.attach_policy.get_policy(focused_prev)
            )
            if mrg.connect or mrg.insert:
                methods = sorted(
                    [m for m in [(mrg.connect, 'connect'), (mrg.insert, 'insert')] if m[0]],
                    key=lambda m: defaults.methods_priority[m[1]]
                )
                for m in methods:
                    if m[1] == "connect":
                        focused_prev.connect(left_object)
                    elif m[1] == "insert":
                        focused_prev.insert_content(left)
            else:
                self.parser.append(left_object)

        self.current += 1
        if right:
            self.units.insert(self.current, right)

    @staticmethod
    def extract(unit_string, extractor, takes_all=False):
        left = None
        right = None

        if isinstance(extractor, CharSequenceString) and unit_string.startswith(extractor.value):
            left = extractor.value
            right = unit_string[len(extractor.value):]

        elif isinstance(extractor, WhitespaceVoid) and unit_string.startswith(" "):
            left = re.search(r'^\s+', unit_string)
            right = unit_string.lstrip(" ")

        elif isinstance(extractor, RegexString):
            extractor.value = '^' + extractor.value.lstrip('^')
            rs = re.search(extractor.value, unit_string)
            if rs:
                left = rs.group(0)
                right = unit_string[len(left):]

        elif isinstance(extractor, LimitRegexString):
            limit_search = re.search(extractor.value, unit_string)
            if not limit_search:
                left = unit_string
                right = ""
            else:
                left = unit_string[:limit_search.start()]
                right = unit_string[limit_search.start():]

        elif isinstance(extractor, LengthInteger) and len(unit_string) >= extractor.value:
            left = unit_string[:extractor.value]
            right = unit_string[extractor.value:]

        elif isinstance(extractor, CharList) or isinstance(extractor, CharString):
            if isinstance(extractor, CharString):
                extractor.value = list(extractor.value)
            left = ""
            n = 0
            for char in unit_string:
                if char in extractor.value:
                    left += char
                else:
                    break
                n += 1
            right = unit_string[n:]
            if not left:
                left = None

        if left is None or right is None:
            raise ExtractionFailed()
        else:
            if takes_all and right:
                raise ExtractionFailed()
            return left, right

    @staticmethod
    def generate_framing_group():
        return "".join([chr(x) for x in sample(range(0xe000, 0xf8ff), defaults.framing_group_length)])

    def add_char_equivalent(self, char, equivalent):
        """
        Add an A->B matching to replace chars before text splitting
        :param char: A side
        :param equivalent: B side
        """
        if len(char) + len(equivalent) != 2:
            raise ValueError()
        self.__char_equivalents[char] = equivalent


class Extractor:
    """Native templates which simplify char-sequence matching"""
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


class LimitRegexString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class LengthInteger(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class AlreadyAllocated(Exception):
    pass


class CannotMoveRight(Exception):
    pass


class ExtractionFailed(Exception):
    pass
