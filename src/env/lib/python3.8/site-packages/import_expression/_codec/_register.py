try:
	from . import register
except ImportError:
	pass
else:
	register()
