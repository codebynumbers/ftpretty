import sys

if sys.version_info[0] < 3:
    PY2 = True
    PY3 = False
    from cStringIO import StringIO
    file_type = file
else:
    PY2 = False
    PY3 = True
    from io import StringIO, IOBase
    file_type = IOBase
