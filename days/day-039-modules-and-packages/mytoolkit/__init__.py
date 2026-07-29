"""mytoolkit — small utilities worth keeping.

The public surface of the package. Everything a user needs is importable
from here:

    from mytoolkit import slugify, clamp, timer

...and WHERE each of those lives is an implementation detail. text.py could
be renamed or split tomorrow without breaking a single caller, which is the
entire point of having this file.

    Day 31  toolkit.py, one flat module, 10 functions
    Day 37  decorators.py alongside it
    Day 39  both reorganised into this package          <- here
    Day 40  documented, exampled, with a __main__
    Day 57  a pytest suite
    Day 59  fully typed
    Day 97  published

KEEP THIS FILE THIN. It runs on every import of anything in the package, so
slow work here slows down everything. Imports and metadata, no logic.
"""

# Relative imports (the leading dot) — they say "from THIS package", so the
# package can be renamed without editing every module inside it.
from .containers import chunked, dig, unique
from .decorators import RetryError, cache, retry, timer, validated
from .numbers import clamp, duration, human_bytes, percent
from .text import initials, slugify, truncate

__version__ = "0.3.0"
__author__ = "100 Days of Python"

# __all__ declares the public surface. It is what `from mytoolkit import *`
# would take — which is a reason to DEFINE it, not a reason to USE that.
# It also documents intent: anything not listed here is internal and may
# change without warning.
__all__ = [
    # numbers
    "clamp",
    "percent",
    "human_bytes",
    "duration",
    # text
    "truncate",
    "slugify",
    "initials",
    # containers
    "chunked",
    "unique",
    "dig",
    # decorators
    "timer",
    "retry",
    "cache",
    "validated",
    "RetryError",
    # metadata
    "__version__",
]
