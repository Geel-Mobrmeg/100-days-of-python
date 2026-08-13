"""The parsing rules, as a table."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest
from tidy.errors import BadValueError, MissingFieldError, RecordError
from tidy.records import (
    Sale,
    missing_columns,
    normalise_key,
    parse,
    parse_date,
    parse_money,
    parse_units,
)


def test_a_clean_record_parses(raw_record):
    sale = parse(raw_record(), "f.csv", 2)
    assert sale == Sale("WID-001", "north", date(2026, 3, 1), 12,
                        Decimal("4.50"))
    assert sale.total == Decimal("54.00")


@pytest.mark.parametrize("given, expected", [
    ("SKU", "sku"), ("  Unit Price ", "unit_price"), ("Sold-On", "sold_on"),
    ("UNITS", "units"), ("Région", "region"), ("a  b", "a_b"), ("__x__", "x"),
])
def test_header_normalisation(given, expected):
    assert normalise_key(given) == expected


@pytest.mark.parametrize("field, value", [
    ("sku", ""), ("sku", "  "), ("sku", "-"), ("sku", "n/a"),
    ("region", ""), ("sold_on", ""), ("units", ""), ("unit_price", ""),
])
def test_a_missing_required_field_is_reported(raw_record, field, value):
    with pytest.raises(MissingFieldError) as caught:
        parse(raw_record(**{field: value}), "f.csv", 7)
    assert caught.value.field == field
    assert caught.value.line == 7
    assert caught.value.source == "f.csv"


@pytest.mark.parametrize("sku, ok", [
    ("WID-001", True), ("AB-123", True), ("ABCD-12345", True),
    ("wid-001", True),                      # upper-cased before checking
    ("W-001", False), ("WIDGET-001", False), ("WID-01", False),
    ("WID001", False), ("WID-0011111", False),
])
def test_sku_shape(raw_record, sku, ok):
    if ok:
        assert parse(raw_record(sku=sku), "f", 1).sku == sku.upper()
    else:
        with pytest.raises(BadValueError):
            parse(raw_record(sku=sku), "f", 1)


@pytest.mark.parametrize("region, ok", [
    ("north", True), ("NORTH", True), (" south ", True), ("east", True),
    ("west", True), ("northerly", False), ("middle", False),
])
def test_region_must_be_known(raw_record, region, ok):
    if ok:
        assert parse(raw_record(region=region), "f", 1).region \
            == region.strip().lower()
    else:
        with pytest.raises(BadValueError):
            parse(raw_record(region=region), "f", 1)


@pytest.mark.parametrize("raw, expected", [
    ("4.50", Decimal("4.50")), ("£12.00", Decimal("12.00")),
    ("$7", Decimal("7.00")), ("€1.5", Decimal("1.50")),
    ("4,50", Decimal("4.50")),              # European decimal comma
    ("1,299.00", Decimal("1299.00")),       # thousands separator
    (" 3.00 ", Decimal("3.00")),
])
def test_money_accepts(raw, expected):
    assert parse_money(raw, "unit_price", "f", 1) == expected


@pytest.mark.parametrize("raw, problem", [
    ("1,299", "ambiguous"),                 # 1299 or 1.299? refuse.
    ("free", "not a number"),
    ("0", "greater than zero"),
    ("-5", "greater than zero"),
    ("2000000", "implausibly large"),
])
def test_money_refuses(raw, problem):
    with pytest.raises(BadValueError) as caught:
        parse_money(raw, "unit_price", "f", 3)
    assert problem in caught.value.problem


def test_money_missing_is_a_missing_field_not_a_bad_value():
    with pytest.raises(MissingFieldError):
        parse_money("", "unit_price", "f", 1)


@pytest.mark.parametrize("raw, expected", [
    ("12", 12), (" 7 ", 7), ("1,200", 1200), (5, 5),
])
def test_units_accepts(raw, expected):
    assert parse_units(raw, "f", 1) == expected


@pytest.mark.parametrize("raw", ["0", "-1", "3.5", "many", ""])
def test_units_refuses(raw):
    with pytest.raises(RecordError):
        parse_units(raw, "f", 1)


@pytest.mark.parametrize("raw, expected", [
    ("2026-03-01", date(2026, 3, 1)),
    ("2026-03-01T09:30:00", date(2026, 3, 1)),
    (" 2026-12-31 ", date(2026, 12, 31)),
])
def test_dates_accepted(raw, expected):
    assert parse_date(raw, "f", 1) == expected


@pytest.mark.parametrize("raw", ["01/02/2026", "1 March 2026", "2026-13-01",
                                 "yesterday", ""])
def test_dates_refused(raw):
    """01/02/2026 is refused DELIBERATELY: it is 1 February in Britain and
    2 January in America, and guessing is wrong for half the users."""
    with pytest.raises(RecordError):
        parse_date(raw, "f", 1)


def test_missing_columns_names_what_is_absent():
    assert missing_columns(["SKU", "Region"]) == ["sold_on", "units",
                                                  "unit_price"]
    assert missing_columns(["sku", "region", "sold_on", "units",
                            "unit_price"]) == []


def test_a_sale_is_immutable_and_hashable(raw_record):
    sale = parse(raw_record(), "f", 1)
    with pytest.raises(FrozenInstanceError):
        sale.units = 99
    assert len({sale, parse(raw_record(), "f", 1)}) == 1


def test_as_row_is_all_strings(raw_record):
    row = parse(raw_record()).as_row() if False else \
        parse(raw_record(), "f", 1).as_row()
    assert all(isinstance(value, str) for value in row.values())
    assert row["total"] == "54.00"


def test_the_error_carries_enough_to_act_on(raw_record):
    with pytest.raises(BadValueError) as caught:
        parse(raw_record(units="lots"), "north.csv", 42)
    error = caught.value
    assert (error.source, error.line, error.field) == ("north.csv", 42,
                                                       "units")
    assert error.as_dict()["value"] == "lots"
    assert "north.csv:42" in str(error)


def test_a_record_error_is_also_a_value_error(raw_record):
    """Older code that says `except ValueError` keeps working (Day 52)."""
    with pytest.raises(ValueError):
        parse(raw_record(units="lots"), "f", 1)
