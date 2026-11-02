"""Make bin/ importable so pytest can test the pipeline scripts directly."""

import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent / "bin"
sys.path.insert(0, str(BIN))
