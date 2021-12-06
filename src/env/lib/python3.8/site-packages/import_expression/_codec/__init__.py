import ast
from . import compat as astunparse
import codecs, io, encodings
from encodings import utf_8

import import_expression as ie
from ..constants import IMPORTER

IMPORT_STATEMENT = ast.parse(f'from importlib import import_module as {IMPORTER}').body[0]

def decode(b, errors='strict'):
	if not b:
		return '', 0

	decoded = codecs.decode(b, errors=errors, encoding='utf-8')
	parsed = ie.parse(decoded)
	parsed.body.insert(0, IMPORT_STATEMENT)
	unparsed = astunparse.unparse(parsed)
	return unparsed, len(decoded)

# copied from future_fstrings.py at bd6bf81

class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
	def _buffer_decode(self, input, errors, final):
		if final:
			return decode(input, errors)
		else:
			return '', 0

class StreamReader(utf_8.StreamReader):  # pragma: no cover
	"""decode is deferred to support better error messages"""
	_stream = None
	_decoded = False

	@property
	def stream(self):
		if not self._decoded:
			text, _ = decode(self._stream.read())
			self._stream = io.BytesIO(text.encode('utf-8'))
			self._decoded = True
		return self._stream

	@stream.setter
	def stream(self, stream):
		self._stream = stream
		self._decoded = False

def search_function(encoding, codec_names={'import_expression', 'ie'}):
	if encoding not in codec_names:  # pragma: no cover
		return None
	utf8 = encodings.search_function('utf-8')
	return codecs.CodecInfo(
		name='import_expression',
		encode=utf8.encode,
		decode=decode,
		incrementalencoder=utf8.incrementalencoder,
		incrementaldecoder=IncrementalDecoder,
		streamreader=StreamReader,
		streamwriter=utf8.streamwriter,
	)

def register():
	codecs.register(search_function)
