"""The value type, and the rules that decide whether one is usable.

A Sale is a frozen dataclass (Day 48): defined by its contents, immutable,
comparable, and impossible to put into an invalid state — parse() is the
only way to make one from raw text, and it either returns a valid Sale or
raises.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from .errors import BadValueError, MissingFieldError, RecordError

REQUIRED = ("sku", "region", "sold_on", "units", "unit_price")
REGIONS = ("north", "south", "east", "west")
NULLS = frozenset({"", "-", "n/a", "na", "none", "null", "?"})
SKU = re.compile(r"^[A-Z]{2,4}-\d{3,5}$")


@dataclass(frozen=True, slots=True, order=True)
class Sale:
    """One row of a sales export, after cleaning."""

    sku: str
    region: str
    sold_on: date
    units: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.units

    def as_row(self) -> dict[str, str]:
        """A flat dict of strings, ready for csv.DictWriter (Day 54)."""
        return {
            "sku": self.sku,
            "region": self.region,
            "sold_on": self.sold_on.isoformat(),
            "units": str(self.units),
            "unit_price": f"{self.unit_price:.2f}",
            "total": f"{self.total:.2f}",
        }


def normalise_key(name: str) -> str:
    """'  Unit Price ' -> 'unit_price'. Day 54, step one."""
    folded = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", stripped.strip().lower()).strip("_")


def _text(raw: object) -> str:
    return "" if raw is None else str(raw).strip()


def _require(record: Mapping[str, object], field: str, source: str,
             line: int) -> str:
    value = _text(record.get(field))
    if value.lower() in NULLS:
        raise MissingFieldError(source, line, field, "is required")
    return value


def parse_money(raw: object, field: str, source: str, line: int) -> Decimal:
    """Day 54's rule, kept: refuse the ambiguous rather than guess.

    '1,299' is 1299 in Britain and 1.299 in Germany. Nothing in the file
    says which, so this raises instead of picking one and being wrong by a
    factor of a thousand.
    """
    text = _text(raw)
    for symbol in ("£", "$", "€", " ", " "):
        text = text.replace(symbol, "")
    if text.lower() in NULLS:
        raise MissingFieldError(source, line, field, "is required")

    if "," in text and "." in text:
        text = text.replace(",", "")
    elif text.count(",") == 1:
        whole, _, fraction = text.partition(",")
        if len(fraction) == 2:
            text = f"{whole}.{fraction}"
        else:
            raise BadValueError(source, line, field,
                           "is ambiguous (1,299 or 1.299?)", raw)

    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise BadValueError(source, line, field, "is not a number", raw) from None
    if amount <= 0:
        raise BadValueError(source, line, field, "must be greater than zero", raw)
    if amount > Decimal("1000000"):
        raise BadValueError(source, line, field, "is implausibly large", raw)
    return amount.quantize(Decimal("0.01"))


def parse_units(raw: object, source: str, line: int) -> int:
    text = _text(raw).replace(",", "")
    if text.lower() in NULLS:
        raise MissingFieldError(source, line, "units", "is required")
    try:
        units = int(text)
    except ValueError:
        raise BadValueError(source, line, "units", "is not a whole number",
                       raw) from None
    if units <= 0:
        raise BadValueError(source, line, "units", "must be greater than zero", raw)
    return units


def parse_date(raw: object, source: str, line: int) -> date:
    """ISO only, deliberately.

    01/02/2026 is 1 February in Britain and 2 January in America, and a
    tool that guesses is wrong for half its users without ever saying so.
    """
    text = _text(raw)
    if text.lower() in NULLS:
        raise MissingFieldError(source, line, "sold_on", "is required")
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        raise BadValueError(source, line, "sold_on",
                       "must be an ISO date (YYYY-MM-DD)", raw) from None


def parse(record: Mapping[str, object], source: str, line: int) -> Sale:
    """Turn one raw record into a Sale, or raise the FIRST problem.

    First-problem rather than collect-all, on purpose: pipeline.py catches
    one RecordError per row and moves to the next row, so a bad file
    produces one line of report per bad row rather than five.
    """
    normalised = {normalise_key(str(k)): v for k, v in record.items()}

    sku = _require(normalised, "sku", source, line).upper()
    if not SKU.match(sku):
        raise BadValueError(source, line, "sku", "must look like AB-1234", sku)

    region = _require(normalised, "region", source, line).lower()
    if region not in REGIONS:
        raise BadValueError(source, line, "region",
                       f"must be one of {', '.join(REGIONS)}", region)

    return Sale(
        sku=sku,
        region=region,
        sold_on=parse_date(normalised.get("sold_on"), source, line),
        units=parse_units(normalised.get("units"), source, line),
        unit_price=parse_money(normalised.get("unit_price"), "unit_price",
                               source, line),
    )


def missing_columns(header: list[str]) -> list[str]:
    """Which required columns a file does not have at all."""
    present = {normalise_key(name) for name in header}
    return [name for name in REQUIRED if name not in present]


__all__ = ["Sale", "RecordError", "parse", "normalise_key", "missing_columns",
           "parse_money", "parse_units", "parse_date", "REQUIRED", "REGIONS"]
