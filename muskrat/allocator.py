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
from .cursor import *
from .parser import Parser, ParsingObject
from .connectivity import *


class Allocator:
    """Allocator is used to divide the whole text into units"""
    def __init__(self, text, splitter, parser, position=0, parameters=None):
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
        self.tracker_boxes = []
        self.parallel_moving = False
        self.__char_equivalents = {}
        self.text = text
        self.parser = parser
        self.parser_add_boxes()
        self.units = []
        self.current = position
        self.cursor = AllocatorCursor(self.current, parameters if parameters else {})
        self.splitter = splitter
        if not issubclass(type(self.splitter), Extractor):
            raise ValueError()

    def make_units(self):
        if self.units:
            raise AlreadyAllocated()
        if self.end_position:
            self.text = self.text[:self.end_position]

        self.text = self.text.replace("\n", self.newline_equivalent)
        self.text = self.text.replace("\r", self.carriage_equivalent)

        if isinstance(self.splitter, WhitespaceVoid):
            self.units = self.text.split()

        elif isinstance(self.splitter, CharSequenceString):
            self.units = self.text.split(self.splitter.value)

        elif isinstance(self.splitter, RegexString):
            self.units = re.split(self.splitter.value, self.text)

        elif isinstance(self.splitter, RegexCompiledString):
            self.units = re.compile(*self.splitter.value).split(self.text)

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

        elif isinstance(self.splitter, NullVoid):
            self.units = [self.text]

        else:
            raise SplitterNotSupported

        if self.end_position and len(self.units) > 1:
            del self.units[-1]

    def parser_add_boxes(self):
        self.parser.BOX0 = ParsingObject(str(), muskrat.pattern.Pattern(
            "builtin:BOX0",
            Accept().add_default(connect=True, insert=True),
            Attach().add_default(connect=False, insert=False)
        ))

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

    def next_by_extractor(self, extractor, ahead=1, full_coverage=True, stop_at=None):
        for i in range(self.current, len(self.units)):
            if self.current - i > stop_at:
                break
            try:
                left, right = self.extract(self.units[i], extractor)
                if right and full_coverage:
                    continue
                else:
                    ahead -= 1
                    if ahead:
                        return self.units[i]
                    else:
                        continue
            except ExtractionFailed:
                continue
        return None

    def move_right(self):
        current = self.units[self.current]
        self.cursor.update(self.parser, self.current, current)
        trackers = []
        self.parser.depth_limit = self.cursor.left_depth_limit

        for tracker_super in self.cursor.tracker_family:
            for tracker in tracker_super.__subclasses__():
                tracking = tracker(self.parser, self)
                if tracking.track():
                    trackers.append(tracking)
        if not trackers:
            raise CannotMoveRight("Failed on unit %d = '%s'" % (self.current, current,))

        parts = []
        part_obj = namedtuple("Part", ["tracker", "pair"])
        for tracker in trackers:
            try:
                part = part_obj(tracker, self.extract(current, tracker.extractor, tracker.takes_all))
            except ExtractionFailed:
                continue
            parts.append(part)

        if not parts:
            raise CannotMoveRight("Failed on unit %d = '%s'" % (self.current, current,))

        if self.parallel_moving:
            raise VersionOutOfDate(feature_coming)

        for tb in self.tracker_boxes:
            if tb.check_target(parts):
                parts = tb.sort_parts(parts, self.cursor.greedy)
                break
        if not self.tracker_boxes:
            parts = sorted(parts, key=lambda x: len(x.pair[0]), reverse=self.cursor.greedy)
        left, right = parts[0].pair
        left_object = ParsingObject(left, parts[0].tracker.pattern)
        focused_prev = parts[0].tracker.pattern.focus_on(self.parser, left)

        if focused_prev is None:
            if not self.cursor.depend_on:
                self.parser.append(left_object)
            else:
                self.cursor.depend_on.connect(left_object)
                for conn_hook in parts[0].tracker.connection_hooks:
                    conn_hook(parts[0].tracker.parser, parts[0].tracker.allocator, left)
        else:
            mrg = merge_policies(
                focused_prev.pattern.accept_policy.get_policy(left_object),
                parts[0].tracker.pattern.attach_policy.get_policy(focused_prev)
            )
            if mrg.connect or mrg.insert:
                methods = sorted(
                    [m for m in [(mrg.connect, 'connect'), (mrg.insert, 'insert')] if m[0]],
                    key=lambda m: self.cursor.methods_priority[m[1]]
                )
                for m in methods:
                    if m[1] == "connect":
                        focused_prev.connect(left_object)
                        for conn_hook in parts[0].tracker.connection_hooks:
                            conn_hook(parts[0].tracker.parser, parts[0].tracker.allocator, left)
                    elif m[1] == "insert":
                        if not parts[0].tracker.pattern.insertion_prepend_value:
                            focused_prev.insert_content(left)
                        else:
                            focused_prev.insert_content(
                                parts[0].tracker.insertion_hook(
                                    left,
                                    focused_prev,
                                    parts[0].tracker.pattern.prepended_value,
                                    parts[0].tracker.parser,
                                    parts[0].tracker.allocator
                                )
                            )
            else:
                if not self.cursor.depend_on:
                    self.parser.append(left_object)
                else:
                    self.cursor.depend_on.connect(left_object)
                    for conn_hook in parts[0].tracker.connection_hooks:
                        conn_hook(parts[0].tracker.parser, parts[0].tracker.allocator, left)

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

        elif isinstance(extractor, CharSequenceCaseIString):
            if unit_string.lower().startswith(extractor.value.lower()):
                left = unit_string[:len(extractor.value)]
                right = unit_string[len(extractor.value):]
            else:
                left = None

        elif isinstance(extractor, WhitespaceVoid) and unit_string.startswith(" "):
            left = re.search(r'^\s+', unit_string)
            right = unit_string.lstrip(" ")

        elif isinstance(extractor, RegexString) or isinstance(extractor, RegexCompiledString):
            if isinstance(extractor, RegexCompiledString):
                extractor.value, *flags = extractor.value
            extractor.value = '^' + extractor.value.lstrip('^')
            if isinstance(extractor, RegexString):
                rs = re.search(extractor.value, unit_string)
            else:
                rs = re.compile(extractor.value, *flags).search(extractor.value)
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

        elif isinstance(extractor, PositiveVoid):
            if unit_string == "":
                left = None
            else:
                left = unit_string
                right = ""

        elif isinstance(extractor, NullVoid):
            if unit_string != "":
                left = None
            else:
                left = extractor.value
                right = ""

        if left is None or right is None:
            raise ExtractionFailed()
        else:
            if takes_all and right:
                raise ExtractionFailed()
            return left, right

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


class TrackerBox:
    def __init__(self, target_group, placing, positive=True):
        self.target_group = target_group
        self.placing = placing
        self.__positive = positive
        self.greedy = False
        self.pl_values = []

    def negative(self):
        self.__positive = False
        return self

    def positive(self):
        self.__positive = True
        return self

    def add_or_statement(self, ptn):
        self.target_group.append(ptn)
        return self

    def check_list(self, tracker_list):
        for tr in tracker_list:
            if tr.pattern.object_type in self.target_group:
                return self.__positive
        return not self.__positive

    def check_target(self, parts):
        return self.check_list([part.tracker for part in parts])

    def placing_reverse(self):
        self.pl_values = list(self.placing.values())
        self.pl_values = sorted(self.pl_values)
        pl_reversed = sorted(self.pl_values, reverse=True)
        for (pt, index) in self.placing.items():
            self.placing[pt] = pl_reversed[self.pl_values.index(index)]

    def placing_index(self, object_type):
        if object_type in self.placing:
            return self.placing[object_type]
        else:
            return (self.pl_values[-1] + 1) if not self.greedy else (self.pl_values[0] - 1)

    def sort_parts(self, parts, greedy):
        self.greedy = greedy
        if greedy:
            self.placing_reverse()
        return sorted(
            parts, key=lambda x: (self.placing_index(x.tracker.pattern.object_type), len(x.pair[0])),
            reverse=self.greedy
        )


class CharSequenceString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class CharSequenceCaseIString(Extractor):
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


class RegexCompiledString(Extractor):
    def __init__(self, *args):
        Extractor.__init__(self, args)


class LimitRegexString(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class LengthInteger(Extractor):
    def __init__(self, value):
        Extractor.__init__(self, value)


class PositiveVoid(Extractor):
    def __init__(self):
        Extractor.__init__(self, None)


class NullVoid(Extractor):
    def __init__(self, replace_with=""):
        Extractor.__init__(self, replace_with)


class AlreadyAllocated(Exception):
    pass


class CannotMoveRight(Exception):
    pass


class ExtractionFailed(Exception):
    pass


class SplitterNotSupported(Exception):
    pass
