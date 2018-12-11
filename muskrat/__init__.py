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


from . import allocator
from . import connectivity
from . import defaults
from . import filters
from . import parser
from . import pattern
from . import txt_tree_generator
from . import xml_generator


__author__ = "Fyodor Sizov"
__copyright__ = "Copyright 2018, Fyodor Sizov"
__license__ = "GPL 3.0"
__version__ = "1.0.12"
__email__ = "prodotiscus@gmail.com"
