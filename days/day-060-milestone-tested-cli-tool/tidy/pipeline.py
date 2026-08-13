"""Walk, read, validate, collect. The part with the rules in it.

NOTHING HERE PRINTS AND NOTHING HERE WRITES. run() returns a Result, and
the caller decides what to do with it — which is what makes the whole
pipeline testable without a filesystem or a captured stdout.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from . import readers, records
from .errors import RecordError, SourceError, UnreadableFileError
from .records import Sale


@dataclass(frozen=True, slots=True)
class Rejection:
    """One record that could not be used, and why."""

    source: str
    line: int
    field: str
    problem: str
    value: str = ""

    @classmethod
    def from_error(cls, error: RecordError) -> Rejection:
        return cls(error.source, error.line, error.field, error.problem,
                   "" if error.value is None else str(error.value))

    def as_row(self) -> dict[str, str]:
        return {
            "source": self.source, "line": str(self.line),
            "field": self.field, "problem": self.problem, "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class Result:
    """Everything one run produced. A value, not a report."""

    sales: tuple[Sale, ...] = ()
    rejections: tuple[Rejection, ...] = ()
    unreadable: tuple[tuple[str, str], ...] = ()
    files_read: int = 0

    @property
    def total_units(self) -> int:
        return sum(sale.units for sale in self.sales)

    @property
    def total_value(self) -> Decimal:
        return sum((sale.total for sale in self.sales), Decimal("0"))

    @property
    def rows_seen(self) -> int:
        return len(self.sales) + len(self.rejections)

    @property
    def ok(self) -> bool:
        """Did everything work? The exit code is built from this."""
        return not self.rejections and not self.unreadable


def find_sources(root: Path, recursive: bool = False) -> list[Path]:
    """Every file we have a reader for, in a stable order.

    sorted(), because glob returns an arbitrary order and a tool whose
    output changes between runs cannot be diffed (Day 56).
    """
    if root.is_file():
        return [root]
    candidates = root.rglob("*") if recursive else root.iterdir()
    known = {extension for reader in readers.READERS
             for extension in reader.extensions}
    return sorted(p for p in candidates
                  if p.is_file() and p.suffix.lower() in known
                  and not p.name.startswith("."))


def read_file(path: Path) -> Iterator[tuple[int, readers.Row]]:
    """Open, decode and parse one file, translating what goes wrong.

    The UnicodeDecodeError is caught HERE and not in open_source(), because
    open() does not decode: the bytes are read lazily, so the failure
    happens on the first iteration and nowhere earlier. A coverage report
    is what made that obvious — the handler in open_source() was
    unreachable, and this one was missing.
    """
    reader = readers.for_path(path)
    with readers.open_source(path) as stream:
        try:
            yield from reader.read(stream, path.name)
        except UnicodeDecodeError as exc:
            raise UnreadableFileError(
                path, f"not valid UTF-8 at byte {exc.start}") from exc


def process(path: Path) -> tuple[list[Sale], list[Rejection]]:
    """One file in, sales and rejections out. Never raises RecordError."""
    sales: list[Sale] = []
    rejections: list[Rejection] = []

    for line, record in read_file(path):
        if "__ragged__" in record:
            rejections.append(Rejection(
                path.name, line, "(row)",
                f"has a different number of fields than the "
                f"{record['__ragged__']}-column header"))
            continue
        if "__not_an_object__" in record:
            rejections.append(Rejection(
                path.name, line, "(row)",
                f"is a {record['__not_an_object__']}, not an object"))
            continue
        if "__unparseable__" in record:
            rejections.append(Rejection(
                path.name, line, "(row)", "is not valid JSON",
                str(record["__unparseable__"])))
            continue

        try:
            sales.append(records.parse(record, path.name, line))
        except RecordError as error:
            # EXPECTED. A bad row is data, not a bug — Day 51's rule, and
            # the reason this clause names RecordError and not Exception.
            rejections.append(Rejection.from_error(error))

    return sales, rejections


def run(root: Path, recursive: bool = False) -> Result:
    """The whole job. Returns a Result; writes nothing, prints nothing."""
    sales: list[Sale] = []
    rejections: list[Rejection] = []
    unreadable: list[tuple[str, str]] = []
    files_read = 0

    for path in find_sources(root, recursive=recursive):
        try:
            file_sales, file_rejections = process(path)
        except SourceError as error:
            # A whole FILE failed. Record it and carry on with the rest:
            # one broken export must not lose the other nine.
            unreadable.append((path.name, error.reason))
            continue
        files_read += 1
        sales.extend(file_sales)
        rejections.extend(file_rejections)

    return Result(tuple(sales), tuple(rejections), tuple(unreadable),
                  files_read)


@dataclass(frozen=True, slots=True)
class RegionSummary:
    """One line of the report.

    A dataclass rather than a dict, because Day 59: `group["orders"] + 1`
    on a dict[str, object] needs a cast or an ignore, and `summary.orders`
    needs neither. The types push you towards the clearer code.
    """

    region: str
    orders: int
    units: int
    value: Decimal

    @property
    def average_order(self) -> Decimal:
        return (self.value / self.orders).quantize(Decimal("0.01"))

    def as_row(self) -> dict[str, str]:
        return {
            "region": self.region,
            "orders": str(self.orders),
            "units": str(self.units),
            "value": f"{self.value:.2f}",
            "average_order": f"{self.average_order:.2f}",
        }


def by_region(sales: Iterable[Sale]) -> list[RegionSummary]:
    """The summary. Sorted by value, because a report needs an order."""
    orders: dict[str, int] = {}
    units: dict[str, int] = {}
    value: dict[str, Decimal] = {}
    for sale in sales:
        orders[sale.region] = orders.get(sale.region, 0) + 1
        units[sale.region] = units.get(sale.region, 0) + sale.units
        value[sale.region] = value.get(sale.region, Decimal("0")) + sale.total
    summaries = [RegionSummary(region, orders[region], units[region],
                               value[region]) for region in orders]
    return sorted(summaries, key=lambda s: s.value, reverse=True)


__all__ = ["Rejection", "Result", "RegionSummary", "find_sources",
           "process", "run", "by_region", "read_file"]
