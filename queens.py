"""Entry point wrapper to run the Queens game."""

import sys
from pathlib import Path

# Remove the directory containing this script from sys.path[0] to prevent
# this file (queens.py) from shadowing the top-level 'queens' package in src/.
SCRIPT_DIR = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == SCRIPT_DIR:
    sys.path.pop(0)

# Ensure 'src' is available on sys.path if running without an editable install
SRC_DIR = str(SCRIPT_DIR / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from queens.gui import main

if __name__ == "__main__":
    main()
