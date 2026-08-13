"""tidy — validate and summarise sales exports.

The Phase 6 milestone: everything from days 51 to 59, in one tool.

    exceptions       one clause catches every deliberate failure
    custom errors    with the file, the line and the field on them
    files            streams, encodings, and atomic writes
    CSV and JSON     three readers behind one Protocol
    pathlib          a sorted walk, and a dry run by default
    pytest           a suite that fails when the code is wrong
    fixtures         a factory, and no test that touches the network
    types            mypy --strict, no Any

    python3 -m tidy examples/            # dry run
    python3 -m tidy examples/ --write    # ...and do it
"""

from .errors import (
    BadValueError,
    MissingFieldError,
    OutputError,
    RecordError,
    SourceError,
    TidyError,
    UnknownFormatError,
    UnreadableFileError,
)
from .pipeline import RegionSummary, Rejection, Result, by_region, run
from .records import Sale, parse

__version__ = "1.0.0"

__all__ = [
    "TidyError", "SourceError", "UnreadableFileError", "UnknownFormatError",
    "RecordError", "MissingFieldError", "BadValueError", "OutputError",
    "Sale", "parse",
    "Result", "Rejection", "RegionSummary", "run", "by_region",
    "__version__",
]
