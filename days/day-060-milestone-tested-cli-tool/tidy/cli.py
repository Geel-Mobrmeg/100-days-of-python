"""The command line. Thin on purpose.

EVERY RULE LIVES ELSEWHERE. This file parses arguments, calls the
pipeline, formats numbers and returns an exit code. If it had to re-check
anything, the rules would be in the wrong place — and the next front end
(a scheduled job, a web handler, a test) would have to re-check them too.

    DRY RUN IS THE DEFAULT.  Writing needs --write.

Argument parsing is hand-rolled and about thirty lines. Day 64 replaces it
with argparse, which brings --help, abbreviations and type conversion for
free; today it is here so the CLI has no dependency on anything not yet
taught.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from . import pipeline, readers, report
from .errors import TidyError, UnknownFormatError

USAGE = """tidy — validate and summarise sales exports

  python3 -m tidy SOURCE [-o OUT] [--write] [--recursive] [--quiet]

  SOURCE        a file, or a directory of .csv/.json/.jsonl files
  -o, --out     where to write (default: ./tidy-output)
  --write       actually write. Without it, nothing is created.
  -r            recurse into subdirectories
  -q            only the summary line
  -h, --help    this

exit codes
  0  everything was accepted
  1  the run finished, and something was rejected
  2  the arguments were wrong
"""


@dataclass(frozen=True, slots=True)
class Options:
    source: Path
    out: Path = Path("tidy-output")
    write: bool = False
    recursive: bool = False
    quiet: bool = False


class UsageError(TidyError):
    """The arguments were wrong. Exit code 2, and print the usage."""


def parse_args(argv: Sequence[str]) -> Options:
    """A tiny parser. Returns Options or raises UsageError."""
    source: Path | None = None
    out = Path("tidy-output")
    write = recursive = quiet = False

    arguments = list(argv)
    while arguments:
        argument = arguments.pop(0)
        if argument in ("-h", "--help"):
            raise UsageError("")
        elif argument in ("-o", "--out"):
            if not arguments:
                raise UsageError("-o needs a directory")
            out = Path(arguments.pop(0))
        elif argument == "--write":
            write = True
        elif argument in ("-r", "--recursive"):
            recursive = True
        elif argument in ("-q", "--quiet"):
            quiet = True
        elif argument.startswith("-"):
            raise UsageError(f"unknown option {argument}")
        elif source is None:
            source = Path(argument).expanduser()
        else:
            raise UsageError("only one source is accepted")

    if source is None:
        raise UsageError("a source file or directory is required")
    if not source.exists():
        raise UsageError(f"{source} does not exist")
    if source.is_file():
        # NAMING one file we cannot read is a usage mistake, not a data
        # problem — so it is exit code 2 and it is caught here, before any
        # work starts. The same extension inside a DIRECTORY is simply not
        # picked up, because the user did not ask for it specifically.
        try:
            readers.for_path(source)
        except UnknownFormatError as error:
            raise UsageError(error.reason) from error
    return Options(source, out, write, recursive, quiet)


def render(result: pipeline.Result, regions: list[pipeline.RegionSummary],
           options: Options, out: TextIO) -> None:
    """Print the human report to `out`.

    A STREAM, not stdout, so a test captures it with io.StringIO and needs
    no capsys — and so the same function could write to a file tomorrow.
    Day 53's argument, and Day 59 is what forced the type to be precise:
    `out: object` does not have .write(), and mypy said so.
    """
    def line(text: str = "") -> None:
        print(text, file=out)

    if not options.quiet:
        line(f"{'REGION':<10}{'ORDERS':>8}{'UNITS':>8}{'VALUE':>14}"
             f"{'AVERAGE':>12}")
        line("-" * 52)
        for region in regions:
            line(f"{region.region:<10}{region.orders:>8}{region.units:>8}"
                 f"{report.money(region.value):>14}"
                 f"{report.money(region.average_order):>12}")
        line("-" * 52)

        if result.rejections:
            line()
            line(f"{len(result.rejections)} rejected:")
            for rejection in result.rejections[:10]:
                line(f"  {rejection.source}:{rejection.line} "
                     f"{rejection.field}: {rejection.problem}")
            if len(result.rejections) > 10:
                line(f"  ... {len(result.rejections) - 10} more "
                     f"(all of them are in rejects.csv)")

        for name, reason in result.unreadable:
            line(f"  UNREADABLE {name}: {reason}")

    line(f"{result.files_read} file(s), {result.rows_seen} rows, "
         f"{len(result.sales)} accepted, {len(result.rejections)} rejected, "
         f"{report.money(result.total_value)}")


def main(argv: Sequence[str] | None = None,
         out: TextIO | None = None) -> int:
    """Return an exit code. Never raises for anything a user can cause."""
    stream = sys.stdout if out is None else out
    try:
        options = parse_args(sys.argv[1:] if argv is None else argv)
    except UsageError as error:
        print(USAGE, file=stream)
        if str(error):
            print(f"error: {error}", file=stream)
        return 2

    try:
        result = pipeline.run(options.source, recursive=options.recursive)
        regions = pipeline.by_region(result.sales)
        render(result, regions, options, stream)

        if options.write:
            written = report.write_all(result, regions, options.out)
            for path in written:
                print(f"wrote {path}", file=stream)
        else:
            for path, rows in report.planned(result, regions, options.out):
                print(f"would write {path} ({rows} rows)", file=stream)
            print("(dry run — add --write to create these)", file=stream)
    except TidyError as error:
        # Every deliberate failure, in one clause. A bug still crashes.
        print(f"error: {error}", file=stream)
        return 2

    return 0 if result.ok else 1


__all__ = ["Options", "UsageError", "parse_args", "render", "main", "USAGE"]
