# Copyright © 2018–2019 Io Mintz <io@mintz.cc>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This file primarily consists of code vendored from the CPython standard library.
# It is used under the Python Software Foundation License Version 2.
# See LICENSE for details.

import collections
import io
import re
import string
import tokenize as tokenize_
import typing
from token import *
# TODO only import what we need
vars().update({k: v for k, v in vars(tokenize_).items() if not k.startswith('_')})

from .constants import *

tokenize_.TokenInfo.value = property(lambda self: self.string)

is_import = lambda token: token.type == tokenize_.ERRORTOKEN and token.string == IMPORT_OP

NEWLINES = {NEWLINE, tokenize_.NL}

def fix_syntax(s: typing.AnyStr, filename=DEFAULT_FILENAME) -> bytes:
	try:
		tokens = list(tokenize(s))
	except tokenize_.TokenError as ex:
		message, (lineno, offset) = ex.args

		try:
			source_line = s.splitlines()[lineno-2]
		except IndexError:
			source_line = None

		raise SyntaxError(message, (filename, lineno-1, offset, source_line)) from None

	return Untokenizer().untokenize(tokens)

# modified from Lib/tokenize.py at 3.6
class Untokenizer:
	def __init__(self):
		self.tokens = collections.deque()
		self.indents = collections.deque()
		self.prev_row = 1
		self.prev_col = 0
		self.startline = False
		self.encoding = None

	def add_whitespace(self, start):
		row, col = start
		if row < self.prev_row or row == self.prev_row and col < self.prev_col:
			raise ValueError(
				"start ({},{}) precedes previous end ({},{})".format(row, col, self.prev_row, self.prev_col))

		col_offset = col - self.prev_col
		self.tokens.append(" " * col_offset)

	def untokenize(self, iterable):
		indents = []
		startline = False
		for token in iterable:
			if token.type == tokenize_.ENCODING:
				self.encoding = token.value
				continue

			if token.type == tokenize_.ENDMARKER:
				break

			# XXX this abomination comes from tokenize.py
			# i tried to move it to a separate method but failed

			if token.type == tokenize_.INDENT:
				indents.append(token.value)
				continue
			elif token.type == tokenize_.DEDENT:
				indents.pop()
				self.prev_row, self.prev_col = token.end
				continue
			elif token.type in NEWLINES:
				startline = True
			elif startline and indents:
				indent = indents[-1]
				start_row, start_col = token.start
				if start_col >= len(indent):
					self.tokens.append(indent)
					self.prev_col = len(indent)
				startline = False

			# end abomination

			self.add_whitespace(token.start)

			if is_import(token):
				self.tokens.append(MARKER)
			else:
				self.tokens.append(token.value)

			self.prev_row, self.prev_col = token.end

			# don't ask me why this shouldn't be "in NEWLINES",
			# but ignoring tokenize_.NL here fixes #3
			if token.type == NEWLINE:
				self.prev_row += 1
				self.prev_col = 0

		return "".join(self.tokens)

def tokenize(string: typing.AnyStr):
	if isinstance(string, bytes):
		# call the internal tokenize func to avoid sniffing the encoding
		# if it tried to sniff the encoding of a "# encoding: import_expression" file,
		# it would call our code again, resulting in a RecursionError.
		return tokenize_._tokenize(io.BytesIO(string).readline, encoding='utf-8')
	return tokenize_.generate_tokens(io.StringIO(string).readline)
