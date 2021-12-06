import argparse
import shutil
import sys

import import_expression
import import_expression._codec

def main():
	import argparse

	version_info = (
		f'Import Expression Parser {import_expression.__version__}\n'
		f'Python {sys.version}'
	)

	parser = argparse.ArgumentParser(
		prog='import-expression-rewrite',
		description='rewrites import expresion python to standard python',
	)
	parser.add_argument('-i', '--in-place', dest='in_place', action='store_true', help='whether to rewrite in place')
	parser.add_argument('filename', metavar='module', help='path to a python file to rewrite to stdout')

	args = parser.parse_args()

	import_expression._codec.register()
	if args.in_place:
		with open(args.filename, 'r+', encoding='import_expression') as infp:
			buf = infp.read()
			infp.seek(0)
			infp.write(buf)
	else:
		with open(args.filename, encoding='import_expression') as infp:
			shutil.copyfileobj(infp, sys.stdout)

if __name__ == '__main__':
	main()
