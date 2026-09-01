"""Test suite for AeonMosaic — exercises all five core classes plus the
Sophia framework, enhancements registry, and alignment formulas.

Run with::

    pytest tests/ -v
    python -m pytest tests/ -v
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Make the repo importable when run from anywhere
ROOT = Path(__file__).resolve().parent.parent
