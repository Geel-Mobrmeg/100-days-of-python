"""Writing the result out, safely.

THREE FILES, and none of them is written until every one can be:

    summary.csv     one line per region
    clean.csv       every accepted sale
    rejects.csv     every rejected row, WITH its line number

Every write goes through the Day 53 pattern — write a temporary file, then
os.replace() — so a crash halfway through leaves the previous report
intact rather than half a new one.
"""

from __future__ import annotations

import contextlib
import csv
import json
import os
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from .errors import OutputError
from .pipeline import RegionSummary, Result

SUMMARY_FIELDS = ("region", "orders", "units", "value", "average_order")
CLEAN_FIELDS = ("sku", "region", "sold_on", "units", "unit_price", "total")
REJECT_FIELDS = ("source", "line", "field", "problem", "value")


def _discard(temporary: Path) -> None:
    """Remove a half-written temporary file, whatever it turned out to be.

    A plain unlink(missing_ok=True) raises IsADirectoryError if something
    is sitting where the temporary file wanted to be — so the CLEANUP
    would replace the real error with a confusing one. A test found this.
    """
    with contextlib.suppress(OSError):
        temporary.unlink(missing_ok=True)


def write_csv(path: Path, fields: Sequence[str],
              rows: Sequence[dict[str, str]]) -> Path:
    """Atomic: a temporary file, then one rename. Day 53."""
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(temporary, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fields))
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
    except OSError as exc:
        _discard(temporary)
        raise OutputError(path, exc.strerror or str(exc)) from exc
    return path


def write_json(path: Path, payload: dict[str, object]) -> Path:
    """sort_keys and indent, so a re-run with no changes is an empty diff."""
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True,
                      ensure_ascii=False, allow_nan=False, default=str)
            handle.write("\n")
        os.replace(temporary, path)
    except OSError as exc:
        _discard(temporary)
        raise OutputError(path, exc.strerror or str(exc)) from exc
    return path


def summary_payload(result: Result,
                    regions: Sequence[RegionSummary]) -> dict[str, object]:
    """The machine-readable version of the same numbers."""
    return {
        "files_read": result.files_read,
        "rows_seen": result.rows_seen,
        "accepted": len(result.sales),
        "rejected": len(result.rejections),
        "unreadable_files": [
            {"file": name, "reason": reason}
            for name, reason in result.unreadable
        ],
        "total_units": result.total_units,
        "total_value": f"{result.total_value:.2f}",
        "regions": [region.as_row() for region in regions],
    }


def write_all(result: Result, regions: Sequence[RegionSummary],
              destination: Path) -> list[Path]:
    """Write every output file. Returns what was written, in order."""
    written = [
        write_csv(destination / "summary.csv", SUMMARY_FIELDS,
                  [region.as_row() for region in regions]),
        write_csv(destination / "clean.csv", CLEAN_FIELDS,
                  [sale.as_row() for sale in result.sales]),
        write_csv(destination / "rejects.csv", REJECT_FIELDS,
                  [rejection.as_row() for rejection in result.rejections]),
        write_json(destination / "summary.json",
                   summary_payload(result, regions)),
    ]
    return written


def planned(result: Result, regions: Sequence[RegionSummary],
            destination: Path) -> list[tuple[Path, int]]:
    """What write_all() WOULD write. The dry run's whole implementation.

    Same inputs, same shapes, no side effects — so the preview cannot
    disagree with the action (Day 56).
    """
    return [
        (destination / "summary.csv", len(regions)),
        (destination / "clean.csv", len(result.sales)),
        (destination / "rejects.csv", len(result.rejections)),
        (destination / "summary.json", 1),
    ]


def money(amount: Decimal) -> str:
    return f"£{amount:,.2f}"


__all__ = ["write_csv", "write_json", "write_all", "planned",
           "summary_payload", "money", "SUMMARY_FIELDS", "CLEAN_FIELDS",
           "REJECT_FIELDS"]
