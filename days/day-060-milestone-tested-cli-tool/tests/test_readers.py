"""The three readers, all tested against io.StringIO — no files."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from tidy import readers
from tidy.errors import UnknownFormatError, UnreadableFileError
from tidy.readers import CsvReader, JsonLinesReader, JsonReader, Reader


def rows(reader, text, source="f"):
    return list(reader.read(io.StringIO(text), source))


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def test_csv_reads_records_with_line_numbers():
    got = rows(CsvReader(), "sku,units\nA,1\nB,2\n")
    assert got == [(2, {"sku": "A", "units": "1"}),
                   (3, {"sku": "B", "units": "2"})]


@pytest.mark.parametrize("text, delimiter", [
    ("a,b\n1,2\n3,4\n", ","),
    ("a;b\n1;2\n3;4\n", ";"),
    ("a\tb\n1\t2\n3\t4\n", "\t"),
    ("a|b\n1|2\n3|4\n", "|"),
])
def test_csv_sniffs_the_delimiter(text, delimiter):
    assert [record for _, record in rows(CsvReader(), text)] == [
        {"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


def test_csv_keeps_a_quoted_comma_in_one_field():
    got = rows(CsvReader(), 'sku,name\nA,"Gizmo, large"\n')
    assert got[0][1]["name"] == "Gizmo, large"


def test_csv_flags_a_ragged_row_instead_of_returning_none():
    """DictReader is SILENT about this (Day 54). The reader is not."""
    got = rows(CsvReader(), "a,b,c\n1,2\n")
    assert "__ragged__" in got[0][1]


def test_csv_flags_a_row_with_too_many_fields():
    got = rows(CsvReader(), "a,b\n1,2,3\n")
    assert "__ragged__" in got[0][1]


@pytest.mark.parametrize("text", ["", "   \n", "\n\n"])
def test_csv_on_an_empty_file_yields_nothing(text):
    assert rows(CsvReader(), text) == []


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def test_json_reads_a_bare_list():
    got = rows(JsonReader(), '[{"sku": "A"}, {"sku": "B"}]')
    assert got == [(1, {"sku": "A"}), (2, {"sku": "B"})]


def test_json_reads_a_records_key():
    got = rows(JsonReader(), '{"records": [{"sku": "A"}]}')
    assert got == [(1, {"sku": "A"})]


def test_json_flags_an_element_that_is_not_an_object():
    got = rows(JsonReader(), '["oops", {"sku": "A"}]')
    assert got[0][1]["__not_an_object__"] == "str"


def test_json_reports_the_line_and_column_of_a_syntax_error():
    with pytest.raises(UnreadableFileError) as caught:
        rows(JsonReader(), '{"sku": "A",}', source="bad.json")
    assert "line 1" in caught.value.reason
    assert "column" in caught.value.reason


def test_json_refuses_a_document_that_is_not_a_list():
    with pytest.raises(UnreadableFileError):
        rows(JsonReader(), "42", source="n.json")


def test_json_on_an_empty_file_yields_nothing():
    assert rows(JsonReader(), "  ") == []


# ---------------------------------------------------------------------------
# JSON Lines
# ---------------------------------------------------------------------------

def test_jsonl_reads_one_object_per_line():
    got = rows(JsonLinesReader(), '{"a": 1}\n{"a": 2}\n')
    assert got == [(1, {"a": 1}), (2, {"a": 2})]


def test_jsonl_skips_blank_lines_and_keeps_numbering():
    got = rows(JsonLinesReader(), '{"a": 1}\n\n{"a": 2}\n')
    assert [line for line, _ in got] == [1, 3]


def test_jsonl_flags_one_bad_line_and_keeps_the_rest():
    """The whole point of the format: one broken line is not a broken file."""
    got = rows(JsonLinesReader(), '{"a": 1}\nnot json\n{"a": 2}\n')
    assert "__unparseable__" in got[1][1]
    assert got[2][1] == {"a": 2}


def test_jsonl_flags_a_line_that_is_not_an_object():
    got = rows(JsonLinesReader(), "42\n")
    assert got[0][1]["__not_an_object__"] == "int"


# ---------------------------------------------------------------------------
# Choosing one
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name, expected", [
    ("a.csv", CsvReader), ("a.CSV", CsvReader), ("a.tsv", CsvReader),
    ("a.json", JsonReader), ("a.jsonl", JsonLinesReader),
    ("a.ndjson", JsonLinesReader),
])
def test_for_path_picks_by_extension(name, expected):
    assert isinstance(readers.for_path(Path(name)), expected)


@pytest.mark.parametrize("name", ["a.xlsx", "a.pdf", "README", "a."])
def test_for_path_says_what_it_knows(name):
    with pytest.raises(UnknownFormatError) as caught:
        readers.for_path(Path(name))
    assert "known:" in caught.value.reason


def test_every_reader_satisfies_the_protocol():
    assert all(isinstance(reader, Reader) for reader in readers.READERS)


def test_no_two_readers_claim_the_same_extension():
    seen = [e for reader in readers.READERS for e in reader.extensions]
    assert len(seen) == len(set(seen))


# ---------------------------------------------------------------------------
# Opening
# ---------------------------------------------------------------------------

def test_open_source_strips_a_byte_order_mark(tmp_path):
    path = tmp_path / "excel.csv"
    path.write_bytes(b"\xef\xbb\xbfsku,units\nA,1\n")
    with readers.open_source(path) as handle:
        assert next(iter(handle)).startswith("sku")


def test_open_source_reports_a_missing_file_as_ours(tmp_path):
    with pytest.raises(UnreadableFileError) as caught:
        readers.open_source(tmp_path / "nope.csv")
    assert caught.value.path.name == "nope.csv"
