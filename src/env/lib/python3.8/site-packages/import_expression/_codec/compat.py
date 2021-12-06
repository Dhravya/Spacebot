import contextlib
from io import StringIO
from astunparse import Unparser

class Unparser(Unparser):
    def _Constant(self, t):
        value = t.value
        if isinstance(value, tuple):
            self.write("(")
            if len(value) == 1:
                self._write_constant(value[0])
                self.write(",")
            else:
                interleave(lambda: self.write(", "), self._write_constant, value)
            self.write(")")
        elif value is Ellipsis: # instead of `...` for Py2 compatibility
            self.write("...")
        else:
            with contextlib.suppress(AttributeError):
                if t.kind == "u":
                    self.write("u")
            self._write_constant(t.value)

def unparse(tree):
    out = StringIO()
    Unparser(tree, file=out)
    return out.getvalue()
