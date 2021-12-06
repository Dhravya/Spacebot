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

import builtins
import contextlib
import inspect
import os
import sys
import warnings

from . import eval as ie_eval, exec as ie_exec

def patch(globals=sys.modules['__main__'].__dict__):
	"""monkey patch sys.excepthook so that import expressions work at the repl

	If a line has a syntax error, import_expression.eval is attempted on it.
	If this also results in a syntax error, import_expression.exec will be run instead.
	Both cases will run in the context of the given globals dict, or if None, globals produced by statements will be saved to the __main__ module

	This function is deprecated in favor of python -m import_expression.
	"""
	warnings.warn(DeprecationWarning('import_expression.patch is deprecated in favor of python -m import_expression'))

	if not _is_tty():
		raise RuntimeError('patch() only works at the REPL, where stdin is a TTY.')

	sys.excepthook = _make_excepthook(globals)

def _make_excepthook(globals):
	def excepthook(_, error, __):
		if (
			type(error) is not SyntaxError
			or error.lineno != 1  # we don't have all the code
			or error.text is None
		):
			return sys.__excepthook__(type(error), error, error.__traceback__)

		try:
			result = ie_eval(error.text, globals)
		except SyntaxError:
			try:
				ie_exec(error.text, globals)
			except BaseException as error:
				return sys.__excepthook__(type(error), error, error.__traceback__)
		except BaseException as error:
			return sys.__excepthook__(type(error), error, error.__traceback__)
		else:
			sys.displayhook(result)

	return excepthook

def _is_tty():
	return os.isatty(sys.stdin.fileno())
