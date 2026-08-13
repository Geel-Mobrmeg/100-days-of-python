"""Reading a source file, whatever shape it is in.

ONE INTERFACE, THREE IMPLEMENTATIONS (Day 49). A reader takes an open
TEXT STREAM — not a path — so every one of them can be tested with
io.StringIO and no temporary file (Day 53).

    Reader          the Protocol: read(stream, source) -> rows
    CsvReader       comma, semicolon or tab, sniffed
    JsonReader      a list of objects, or {"records": [...]}
    JsonLinesReader one object per line, streamable

Choosing between them is `for_path()`, which is the only function here
that knows a filename exists.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Protocol, runtime_checkable

from .errors import UnknownFormatError, UnreadableFileError

Row = Mapping[str, object]


@runtime_checkable
class Reader(Protocol):
    """Anything that can turn a text stream into numbered records."""

    extensions: tuple[str, ...]

    def read(self, stream: io.TextIOBase,
             source: str) -> Iterator[tuple[int, Row]]:
        """Yield (line number, record). The line is for error messages."""
        ...


class CsvReader:
    """Day 54, packaged. Sniffs the delimiter, normalises nothing."""

    extensions: tuple[str, ...] = (".csv", ".tsv", ".txt")

    def read(self, stream: io.TextIOBase,
             source: str) -> Iterator[tuple[int, Row]]:
        sample = stream.read(4096)
        stream.seek(0)
        if not sample.strip():
            return
        try:
            dialect: type[csv.Dialect] | csv.Dialect = csv.Sniffer().sniff(
                sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(stream, dialect=dialect)
        header = reader.fieldnames or []
        for record in reader:
            # A ragged row is a FILE problem, and DictReader is silent
            # about it (Day 54), so it is caught here rather than becoming
            # a None three functions away.
            if None in record or any(v is None for v in record.values()):
                yield reader.line_num, {"__ragged__": len(header)}
                continue
            yield reader.line_num, dict(record)


class JsonReader:
    """A whole document. No line numbers exist, so the INDEX is used."""

    extensions: tuple[str, ...] = (".json",)

    def read(self, stream: io.TextIOBase,
             source: str) -> Iterator[tuple[int, Row]]:
        text = stream.read()
        if not text.strip():
            return
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise UnreadableFileError(
                Path(source),
                f"invalid JSON at line {exc.lineno}, column {exc.colno}",
            ) from exc

        if isinstance(data, Mapping):
            data = data.get("records", [])
        if not isinstance(data, list):
            raise UnreadableFileError(
                Path(source),
                "expected a list of records, or an object with 'records'")

        for index, record in enumerate(data, 1):
            if not isinstance(record, Mapping):
                yield index, {"__not_an_object__": type(record).__name__}
                continue
            yield index, dict(record)


class JsonLinesReader:
    """One object per line — the format plain JSON should have been."""

    extensions: tuple[str, ...] = (".jsonl", ".ndjson")

    def read(self, stream: io.TextIOBase,
             source: str) -> Iterator[tuple[int, Row]]:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                yield line_number, {"__unparseable__": line[:60]}
                continue
            if not isinstance(record, Mapping):
                yield line_number, {"__not_an_object__": type(record).__name__}
                continue
            yield line_number, dict(record)


READERS: tuple[Reader, ...] = (CsvReader(), JsonReader(), JsonLinesReader())


def for_path(path: Path) -> Reader:
    """Pick a reader by extension, or say so precisely."""
    suffix = path.suffix.lower()
    for reader in READERS:
        if suffix in reader.extensions:
            return reader
    known = sorted({e for r in READERS for e in r.extensions})
    described = suffix or "a name with no extension"
    raise UnknownFormatError(path,
                        f"no reader for {described} "
                        f"(known: {', '.join(known)})")


def open_source(path: Path) -> io.TextIOBase:
    """Open a source file the way Day 53 and Day 54 argued for.

    utf-8-sig strips the BOM a spreadsheet leaves; newline="" keeps a
    newline inside a quoted CSV field intact; errors="strict" because a
    data file with an undecodable byte is a file to look at, not one to
    salvage.
    """
    try:
        return open(path, encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise UnreadableFileError(path, exc.strerror or str(exc)) from exc
    # NOTE: there is deliberately no `except UnicodeDecodeError` here.
    # open() does not decode anything — the bytes are read later — so a
    # handler here would be unreachable, which is exactly what a coverage
    # report showed. Decoding happens in pipeline.read_file(), and that is
    # where the error is translated.


__all__ = ["Reader", "CsvReader", "JsonReader", "JsonLinesReader",
           "READERS", "for_path", "open_source", "Row"]
