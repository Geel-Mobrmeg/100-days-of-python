"""The pipeline and the writer, end to end, inside tmp_path."""

from __future__ import annotations

import csv
import json
from decimal import Decimal

import pytest
from tidy import pipeline, report
from tidy.errors import OutputError
from tidy.pipeline import Rejection, Result


# ---------------------------------------------------------------------------
# Finding files
# ---------------------------------------------------------------------------

def test_find_sources_ignores_files_it_cannot_read(sources):
    found = [p.name for p in pipeline.find_sources(sources)]
    assert "notes.md" not in found
    assert set(found) == {"north.csv", "south.json", "east.jsonl"}


def test_find_sources_is_sorted(sources):
    found = pipeline.find_sources(sources)
    assert found == sorted(found)


def test_find_sources_accepts_a_single_file(sources):
    one = sources / "north.csv"
    assert pipeline.find_sources(one) == [one]


def test_find_sources_skips_dotfiles(sources):
    (sources / ".hidden.csv").write_text("sku\n", encoding="utf-8")
    assert ".hidden.csv" not in [p.name for p in pipeline.find_sources(sources)]


def test_find_sources_recurses_only_when_asked(sources):
    nested = sources / "deep"
    nested.mkdir()
    (nested / "west.csv").write_text("sku,region,sold_on,units,unit_price\n"
                                     "WID-001,west,2026-03-01,1,1.00\n",
                                     encoding="utf-8")
    assert len(pipeline.find_sources(sources)) == 3
    assert len(pipeline.find_sources(sources, recursive=True)) == 4


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def test_run_reads_every_file_and_totals_them(sources):
    result = pipeline.run(sources)
    assert result.files_read == 3
    assert len(result.sales) == 5
    assert result.rejections == ()
    assert result.total_units == 12 + 3 + 40 + 5 + 60
    assert result.ok


def test_run_keeps_going_after_a_bad_row(sources):
    (sources / "north.csv").write_text(
        "sku,region,sold_on,units,unit_price\n"
        "WID-001,north,2026-03-01,1,1.00\n"
        "BAD,north,2026-03-01,1,1.00\n"
        "GZM-002,north,2026-03-02,2,2.00\n", encoding="utf-8")
    result = pipeline.run(sources)
    assert len(result.rejections) == 1
    assert result.rejections[0].line == 3
    assert not result.ok
    assert any(sale.sku == "GZM-002" for sale in result.sales)


def test_run_records_an_unreadable_file_and_reads_the_others(sources):
    (sources / "broken.json").write_text("{oops", encoding="utf-8")
    result = pipeline.run(sources)
    assert [name for name, _ in result.unreadable] == ["broken.json"]
    assert result.files_read == 3
    assert len(result.sales) == 5
    assert not result.ok


def test_run_on_an_empty_directory(tmp_path):
    result = pipeline.run(tmp_path)
    assert result == Result()
    assert result.ok
    assert result.total_value == Decimal("0")


def test_run_writes_nothing(sources):
    """The whole reason run() returns a value: no side effects to undo."""
    before = sorted(p.name for p in sources.iterdir())
    pipeline.run(sources)
    assert sorted(p.name for p in sources.iterdir()) == before


# ---------------------------------------------------------------------------
# Summarising
# ---------------------------------------------------------------------------

def test_by_region_groups_and_sorts_by_value(sources):
    regions = pipeline.by_region(pipeline.run(sources).sales)
    assert [r.region for r in regions] == ["south", "east", "north"]
    assert regions[0].value == Decimal("330.00")   # 40x2.25 + 5x48.00
    assert [r.value for r in regions] == sorted(
        (r.value for r in regions), reverse=True)


def test_by_region_of_nothing_is_nothing():
    assert pipeline.by_region([]) == []


def test_the_region_totals_add_up_to_the_grand_total(sources):
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    assert sum((r.value for r in regions), Decimal("0")) == result.total_value
    assert sum(r.units for r in regions) == result.total_units
    assert sum(r.orders for r in regions) == len(result.sales)


def test_average_order_is_value_over_orders(sources):
    for region in pipeline.by_region(pipeline.run(sources).sales):
        assert region.average_order == (region.value / region.orders
                                        ).quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def test_write_all_creates_four_files(sources, tmp_path):
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    written = report.write_all(result, regions, tmp_path / "out")
    assert [p.name for p in written] == ["summary.csv", "clean.csv",
                                         "rejects.csv", "summary.json"]
    assert all(p.exists() for p in written)


def test_the_written_csv_round_trips(sources, tmp_path):
    result = pipeline.run(sources)
    report.write_all(result, pipeline.by_region(result.sales),
                     tmp_path / "out")
    with open(tmp_path / "out" / "clean.csv", encoding="utf-8",
              newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(result.sales)
    assert rows[0]["sku"] == result.sales[0].sku
    assert Decimal(rows[0]["total"]) == result.sales[0].total


def test_the_written_json_matches_the_result(sources, tmp_path):
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    report.write_all(result, regions, tmp_path / "out")
    payload = json.loads((tmp_path / "out" / "summary.json").read_text(
        encoding="utf-8"))
    assert payload["accepted"] == len(result.sales)
    assert Decimal(payload["total_value"]) == result.total_value
    assert len(payload["regions"]) == len(regions)


def test_writing_twice_gives_byte_identical_output(sources, tmp_path):
    """sort_keys and a stable sort: a re-run with no changes is no diff."""
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    report.write_all(result, regions, tmp_path / "a")
    report.write_all(result, regions, tmp_path / "b")
    for name in ("summary.csv", "clean.csv", "summary.json"):
        assert (tmp_path / "a" / name).read_bytes() \
            == (tmp_path / "b" / name).read_bytes()


def test_a_failed_write_leaves_the_previous_file_intact(sources, tmp_path):
    destination = tmp_path / "out"
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    report.write_all(result, regions, destination)
    before = (destination / "summary.csv").read_bytes()

    # A directory where the temporary file wants to be: the write fails.
    (destination / "summary.csv.tmp").mkdir()
    with pytest.raises(OutputError):
        report.write_csv(destination / "summary.csv", report.SUMMARY_FIELDS,
                         [{"region": "x"}])
    assert (destination / "summary.csv").read_bytes() == before


def test_no_temporary_file_is_left_behind(sources, tmp_path):
    result = pipeline.run(sources)
    report.write_all(result, pipeline.by_region(result.sales),
                     tmp_path / "out")
    assert not list((tmp_path / "out").glob("*.tmp"))


def test_planned_matches_what_write_all_produces(sources, tmp_path):
    """The dry run and the action must not be able to disagree."""
    result = pipeline.run(sources)
    regions = pipeline.by_region(result.sales)
    preview = report.planned(result, regions, tmp_path / "out")
    written = report.write_all(result, regions, tmp_path / "out")
    assert [path for path, _ in preview] == written


def test_rejections_are_written_with_their_line_numbers(tmp_path):
    result = Result(rejections=(Rejection("f.csv", 9, "units", "bad", "x"),))
    report.write_all(result, [], tmp_path / "out")
    with open(tmp_path / "out" / "rejects.csv", encoding="utf-8",
              newline="") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row == {"source": "f.csv", "line": "9", "field": "units",
                   "problem": "bad", "value": "x"}


def test_money_formatting():
    assert report.money(Decimal("1234.5")) == "£1,234.50"
    assert report.money(Decimal("0")) == "£0.00"


# ---------------------------------------------------------------------------
# The error paths a coverage report asked for
# ---------------------------------------------------------------------------

def test_a_ragged_csv_row_is_rejected_with_a_reason(tmp_path):
    (tmp_path / "a.csv").write_text(
        "sku,region,sold_on,units,unit_price\nWID-001,north,2026-03-01\n",
        encoding="utf-8")
    result = pipeline.run(tmp_path)
    assert len(result.rejections) == 1
    assert "different number of fields" in result.rejections[0].problem


def test_a_json_element_that_is_not_an_object_is_rejected(tmp_path):
    (tmp_path / "a.json").write_text('["oops"]', encoding="utf-8")
    result = pipeline.run(tmp_path)
    assert result.rejections[0].problem == "is a str, not an object"


def test_an_unparseable_jsonl_line_is_rejected(tmp_path):
    (tmp_path / "a.jsonl").write_text("not json\n", encoding="utf-8")
    result = pipeline.run(tmp_path)
    assert result.rejections[0].problem == "is not valid JSON"


def test_a_file_that_is_not_utf8_is_reported_not_crashed(tmp_path):
    """A latin-1 byte in a UTF-8 file. Day 53's failure, translated.

    This is caught in read_file() and NOT in open_source(), because open()
    does not decode — a coverage report showed the handler there was
    unreachable.
    """
    (tmp_path / "a.csv").write_bytes(
        b"sku,region,sold_on,units,unit_price\nWID-001,caf\xe9,2026-03-01,1,1\n")
    result = pipeline.run(tmp_path)
    assert result.files_read == 0
    assert "not valid UTF-8" in result.unreadable[0][1]
    assert not result.ok


def test_write_json_reports_a_failure_as_ours(tmp_path):
    (tmp_path / "summary.json.tmp").mkdir(parents=True)
    with pytest.raises(OutputError) as caught:
        report.write_json(tmp_path / "summary.json", {"a": 1})
    assert caught.value.path.name == "summary.json"
