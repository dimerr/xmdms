"""Windows GUI launcher for XMDMS.

Double-click this file (or associate .pyw with pythonw.exe) to start the
application without opening a console window.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from xmdms import main


if __name__ == "__main__":
    sys.exit(main())
