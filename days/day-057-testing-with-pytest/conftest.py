"""Make Day 40's package importable from this day's tests.

A conftest.py is pytest's own configuration file. pytest imports it before
collecting tests, and — this is the part that matters — it also adds its
directory to sys.path, so `tests/` can import from here.

In a real project you would `pip install -e .` and none of this would be
needed. It is here because the thing under test lives seventeen days ago.
"""

import sys
from pathlib import Path

DAY_40 = Path(__file__).resolve().parents[1] / "day-040-milestone-your-own-toolkit"
sys.path.insert(0, str(DAY_40))
