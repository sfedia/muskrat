#!/usr/bin/python3
import re
from .pattern import *
from .defaults import *
from .parser import ParsingObject
from .connectivity import *


class Allocator:
    def __init__(self, text, splitter, parser, position=0):
        self.newline_equivalent = " "
        self.carriage_equivalent = ""
        self.greedy = True
        self.parallel_moving = False
        self.__char_equivalents = {}
        self.text = text
        self.parser = parser
        self.units = []
        self.current = position
        self.splitter = splitter
        if not issubclass(type(self.splitter), Extractor):
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

    def start_move(self):
        while self.current < len(self.units):
            self.move_right()

    def start(self):
        self.make_units()
        self.start_move()

    def move_right(self):
        current = self.units[self.current]
        trackers = []

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
                part = part_obj(tracker.pattern, self.extract(current, tracker.extractor))
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
    def extract(unit_string, extractor):
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
            return left, right

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


class CannotMoveRight(Exception):
    pass


class ExtractionFailed(Exception):
    pass
