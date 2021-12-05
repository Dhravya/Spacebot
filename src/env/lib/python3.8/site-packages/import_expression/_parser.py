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

import ast
import contextlib
from collections import namedtuple

from .constants import *

def parse_ast(root_node, **kwargs): return ast.fix_missing_locations(Transformer(**kwargs).visit(root_node))

def find_imports(root_node, **kwargs):
	t = ListingTransformer(**kwargs)
	t.visit(root_node)
	return t.imports

def remove_string_right(haystack, needle):
	left, needle, right = haystack.rpartition(needle)
	if not right:
		return left
	# needle not found
	return haystack

def remove_import_op(name): return remove_string_right(name, MARKER)
def has_any_import_op(name): return MARKER in name
def has_invalid_import_op(name):
	removed = remove_import_op(name)
	return MARKER in removed or not removed
def find_valid_imported_name(name):
	"""return a name preceding an import op, or False if there isn't one"""
	return name.endswith(MARKER) and remove_import_op(name)

# source: CPython Objects/exceptions.c:1362 at v3.8.0
SyntaxErrorContext = namedtuple('SyntaxErrorContext', 'filename lineno offset text')

class Transformer(ast.NodeTransformer):
	def __init__(self, *, filename=None, source=None):
		self.filename = filename
		self.source_lines = source.splitlines() if source is not None else None

	def visit_Attribute(self, node):
		"""
		convert Attribute nodes containing import expressions into Attribute nodes containing import calls
		"""
		self._ensure_only_valid_import_ops(node)

		maybe_transformed = self._transform_attribute_attr(node)
		if maybe_transformed:
			return maybe_transformed
		else:
			transformed_lhs = self.visit(node.value)
			return ast.copy_location(
				ast.Attribute(
					value=transformed_lhs,
					ctx=node.ctx,
					attr=node.attr),
				node)

	def visit_Name(self, node):
		"""convert solitary Names that have import expressions, such as "a!", into import calls"""
		self._ensure_only_valid_import_ops(node)

		id = find_valid_imported_name(node.id)
		if id:
			return ast.copy_location(self.import_call(id, node.ctx), node)
		return node

	@staticmethod
	def import_call(attribute_source, ctx):
		return ast.Call(
			func=ast.Name(id=IMPORTER, ctx=ctx),
			args=[ast.Str(attribute_source)],
			keywords=[])

	def _transform_attribute_attr(self, node):
		"""convert an Attribute node's left hand side into an import call"""

		attr = find_valid_imported_name(node.attr)
		if not attr:
			return None

		node.attr = attr
		as_source = self.attribute_source(node)

		return ast.copy_location(
			self.import_call(as_source, node.ctx),
			node)

	def attribute_source(self, node: ast.Attribute, _seen_import_op=False):
		"""return a source-code representation of an Attribute node"""
		if self._find_valid_imported_name(node):
			_seen_import_op = True

		stripped = self._remove_import_op(node)
		if type(node) is ast.Name:
			if _seen_import_op:
				raise self._syntax_error('multiple import expressions not allowed', node) from None
			return stripped

		lhs = self.attribute_source(node.value, _seen_import_op)
		rhs = stripped

		return lhs + '.' + rhs

	def visit_def_(self, node):
		if not has_any_import_op(node.name):
			# it's valid so far, just ensure that arguments and body are also visited
			return self.generic_visit(node)

		if isinstance(node, ast.ClassDef):
			type_name = 'class'
		else:
			type_name = 'function'

		raise self._syntax_error(
			f'"{IMPORT_OP}" not allowed in the name of a {type_name}',
			node
		) from None

	visit_FunctionDef = visit_def_
	visit_ClassDef = visit_def_

	def visit_arg(self, node):
		"""ensure foo(x! = 1) or def foo(x!) does not occur"""
		if node.arg is not None and has_any_import_op(node.arg):
			raise self._syntax_error(
				f'"{IMPORT_OP}" not allowed in function arguments',
				node
			) from None

		# regular arguments may have import expr annotations as children
		return super().generic_visit(node)

	def visit_keyword(self, node):
		self.visit_arg(node)
		# keyword arguments may have import expressions as children
		return super().generic_visit(node)

	def visit_alias(self, node):
		# from x import y **as z**
		self._ensure_no_import_ops(node)
		return node

	def visit_ImportFrom(self, node):
		self._ensure_no_import_ops(node)
		# ImportFrom nodes can have alias children that we also need to check
		return super().generic_visit(node)

	def _ensure_only_valid_import_ops(self, node):
		if self._for_any_child_node_string(has_invalid_import_op, node):
			raise self._syntax_error(
				f'"{IMPORT_OP}" only allowed at end of attribute name',
				node
			) from None

	def _ensure_no_import_ops(self, node):
		if self._for_any_child_node_string(has_any_import_op, node):
			raise self._syntax_error(
				'import expressions are only allowed in variables and attributes',
				node
			) from None

	@classmethod
	def _for_any_child_node_string(cls, predicate, node):
		for child_node in ast.walk(node):
			if cls._for_any_node_string(predicate, node):
				return True

		return False

	@staticmethod
	def _for_any_node_string(predicate, node):
		for field, value in ast.iter_fields(node):
			if isinstance(value, str) and predicate(value):
				return True

		return False

	def _call_on_name_or_attribute(func):
		def checker(self, node):
			if type(node) is ast.Attribute:
				to_check = node.attr
			elif type(node) is ast.Name:
				to_check = node.id
			else:
				raise self._syntax_error('invalid syntax', node)
			return func(to_check)

		return checker

	_find_valid_imported_name = _call_on_name_or_attribute(find_valid_imported_name)
	_remove_import_op = _call_on_name_or_attribute(remove_import_op)

	del _call_on_name_or_attribute

	def _syntax_error(self, message, node):
		lineno = getattr(node, 'lineno', None)
		offset = getattr(node, 'col_offset', None)
		line = None
		if self.source_lines is not None and lineno:
			with contextlib.suppress(IndexError):
				line = self.source_lines[lineno-1]
		ctx = SyntaxErrorContext(filename=self.filename, lineno=lineno, offset=offset, text=line)
		return SyntaxError(message, ctx)

class ListingTransformer(Transformer):
	"""like the parent class but lists all imported modules as self.imports"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.imports = []

	def import_call(self, attribute_source, *args, **kwargs):
		self.imports.append(attribute_source)
		return super().import_call(attribute_source, *args, **kwargs)
