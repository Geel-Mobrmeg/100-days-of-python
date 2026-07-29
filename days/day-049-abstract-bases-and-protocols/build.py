"""Day 049 build — a plugin system the caller cannot see inside.

    python3 build.py

ONE interface. FOUR implementations that are genuinely unlike each other:

    JsonExporter      writes structured text
    CsvExporter       writes flat rows, and has to flatten nested data
    MarkdownExporter  writes a formatted table with computed column widths
    NullExporter      writes nothing at all, and exists to prove the
                      interface does not assume output happens

The runner at the bottom does not know which is which, and adding a fifth
requires changing nothing.

The interface is declared TWICE — once as an ABC and once as a Protocol —
so the difference between the two is visible on the same problem.
"""

import json
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

WIDTH = 78

RECORDS = [
    {"id": 1, "name": "Ada Lovelace", "role": "director",
     "tags": ["maths", "engines"], "salary": 165_000},
    {"id": 2, "name": "Alan Turing", "role": "engineer",
     "tags": ["logic"], "salary": 78_000},
    {"id": 3, "name": "Grace Hopper", "role": "manager",
     "tags": ["compilers", "navy"], "salary": 98_000},
]


# ###########################################################################
# THE INTERFACE, AS AN ABC
# ###########################################################################

class Exporter(ABC):
    """Turn a list of records into text.

    THREE methods, deliberately. Every one is an obligation for every
    implementer, so each has to earn its place:

        extension   needed to name the output file
        export      the actual job
        name        for the report; could be derived, and is abstract
                    anyway so implementations can say something better

    NOT in the interface, and it matters:
        * nothing about files, paths or encodings — an exporter that
          returns a string can be written to a file, a socket, a test
          assertion or nowhere. Putting `write_to_disk()` here would mean
          only file-writers could implement it.
        * nothing about the SHAPE of a record beyond "a mapping".
    """

    @property
    @abstractmethod
    def extension(self) -> str:
        """The file extension, without a dot."""

    @abstractmethod
    def export(self, records) -> str:
        """Return the records rendered as text."""

    @property
    def name(self) -> str:
        """CONCRETE, and inherited. Real code reuse, not just a contract."""
        return type(self).__name__.replace("Exporter", "").lower()

    def filename(self, stem="export"):
        """Also concrete: written once, correct for every implementation."""
        return f"{stem}.{self.extension}"


# ###########################################################################
# THE SAME INTERFACE, AS A PROTOCOL
# ###########################################################################

@runtime_checkable
class ExporterProtocol(Protocol):
    """The structural version. Nothing inherits from this.

    Any object with these three members satisfies it — including classes
    from libraries you do not control, which is the thing an ABC cannot do.
    """

    @property
    def extension(self) -> str: ...

    def export(self, records) -> str: ...


# ###########################################################################
# FOUR IMPLEMENTATIONS
# ###########################################################################

class JsonExporter(Exporter):
    """Structured. Keeps nested data as nested data."""

    def __init__(self, indent=2):
        self.indent = indent

    @property
    def extension(self):
        return "json"

    def export(self, records):
        return json.dumps(list(records), indent=self.indent)


class CsvExporter(Exporter):
    """Flat. Has to FLATTEN the nested tags, which JSON did not.

    This is why the interface says export(records) -> str and nothing
    about structure: the two implementations disagree completely about
    what to do with a list-valued field, and the interface does not care.
    """

    def __init__(self, delimiter=",", list_separator="|"):
        self.delimiter = delimiter
        self.list_separator = list_separator

    @property
    def extension(self):
        return "csv"

    def _flatten(self, value):
        if isinstance(value, (list, tuple)):
            return self.list_separator.join(str(v) for v in value)
        return str(value)

    def export(self, records):
        records = list(records)
        if not records:
            return ""
        columns = list(records[0])
        lines = [self.delimiter.join(columns)]
        for record in records:
            lines.append(self.delimiter.join(
                self._flatten(record.get(c, "")) for c in columns
            ))
        return "\n".join(lines)


class MarkdownExporter(Exporter):
    """Formatted. Computes column widths, which neither of the others does."""

    @property
    def extension(self):
        return "md"

    def export(self, records):
        records = list(records)
        if not records:
            return "_(no records)_"
        columns = list(records[0])

        def cell(value):
            if isinstance(value, (list, tuple)):
                return ", ".join(str(v) for v in value)
            return str(value)

        widths = {
            c: max(len(c), max(len(cell(r.get(c, ""))) for r in records))
            for c in columns
        }
        header = "| " + " | ".join(c.ljust(widths[c]) for c in columns) + " |"
        rule = "| " + " | ".join("-" * widths[c] for c in columns) + " |"
        rows = [
            "| " + " | ".join(cell(r.get(c, "")).ljust(widths[c])
                              for c in columns) + " |"
            for r in records
        ]
        return "\n".join([header, rule, *rows])


class NullExporter(Exporter):
    """Writes nothing.

    Exists to prove the interface does not ASSUME output happens. An
    interface that cannot accommodate a do-nothing implementation has
    usually smuggled an assumption into itself.
    """

    @property
    def extension(self):
        return "null"

    def export(self, records):
        return ""


# ###########################################################################
# A CLASS THAT SATISFIES THE PROTOCOL WITHOUT INHERITING ANYTHING
# ###########################################################################

class YamlIshExporter:
    """Inherits from NOTHING. Satisfies ExporterProtocol structurally.

    This is the case an ABC cannot cover: a class from somewhere else, or
    one you do not want to couple to your base. The runner below accepts it
    without modification.
    """

    extension = "yml"

    def export(self, records):
        lines = []
        for record in records:
            lines.append(f"- id: {record['id']}")
            for key, value in record.items():
                if key == "id":
                    continue
                if isinstance(value, list):
                    lines.append(f"  {key}:")
                    lines.extend(f"    - {v}" for v in value)
                else:
                    lines.append(f"  {key}: {value}")
        return "\n".join(lines)


# ###########################################################################
# THE RUNNER — knows the interface, nothing else
# ###########################################################################

def run(exporters, records):
    """Takes anything Exporter-shaped. Never asks what it is."""
    results = []
    for exporter in exporters:
        text = exporter.export(records)
        results.append({
            "exporter": getattr(exporter, "name",
                                type(exporter).__name__.lower()),
            "file": getattr(exporter, "filename", lambda: "-")()
            if hasattr(exporter, "filename")
            else f"export.{exporter.extension}",
            "bytes": len(text.encode()),
            "lines": len(text.splitlines()),
            "text": text,
        })
    return results


print("=" * WIDTH)
print(f"{'PLUGIN SYSTEM':^{WIDTH}}")
print("=" * WIDTH)

plugins = [
    JsonExporter(indent=0),
    CsvExporter(),
    MarkdownExporter(),
    NullExporter(),
    YamlIshExporter(),                  # not an Exporter subclass at all
]

results = run(plugins, RECORDS)

print(f"{'EXPORTER':<14}{'FILE':<18}{'BYTES':>8}{'LINES':>8}   {'ABC?':<6}{'Protocol?':<10}")
print("-" * WIDTH)
for plugin, result in zip(plugins, results):
    print(f"{result['exporter'][:13]:<14}{result['file']:<18}"
          f"{result['bytes']:>8}{result['lines']:>8}   "
          f"{str(isinstance(plugin, Exporter)):<6}"
          f"{str(isinstance(plugin, ExporterProtocol)):<10}")

print("""
  Look at the last two columns. YamlIshExporter is NOT an Exporter — it
  inherits from nothing — and it satisfies the Protocol and works in the
  runner regardless.

  That is the difference: the ABC asks "what are you?", the Protocol asks
  "what can you do?". The runner only ever needed the second question.""")

# ---------------------------------------------------------------------------
# The output, which is genuinely different in each case
# ---------------------------------------------------------------------------

for result in results:
    if not result["text"]:
        continue
    print()
    print("-" * WIDTH)
    print(f"{result['exporter'].upper()}  ->  {result['file']}")
    print("-" * WIDTH)
    for line in result["text"].splitlines()[:6]:
        print(f"  {line[:WIDTH - 4]}")
    if result["lines"] > 6:
        print(f"  ... {result['lines'] - 6} more lines")

# ###########################################################################
# WHAT THE ABC GUARANTEES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT EACH MECHANISM CATCHES':^{WIDTH}}")
print("=" * WIDTH)


class ForgotExport(Exporter):
    @property
    def extension(self):
        return "oops"


class ForgotExtension(Exporter):
    def export(self, records):
        return ""


class WrongShape:
    """Has neither method. Should not satisfy the Protocol."""

    def render(self, records):
        return ""


print("  ABC — fails at CONSTRUCTION, naming what is missing:")
for cls in (ForgotExport, ForgotExtension, Exporter):
    try:
        cls()
        print(f"    {cls.__name__:<20}instantiated — the guarantee is broken")
    except TypeError as exc:
        # The message says "...abstract method X" or "...methods X, Y".
        detail = str(exc).split("abstract method")[-1].lstrip("s").strip()
        print(f"    {cls.__name__:<20}TypeError: missing {detail}")

print("\n  Protocol — a static check, plus a weak runtime one:")
for obj in (JsonExporter(), YamlIshExporter(), WrongShape()):
    print(f"    {type(obj).__name__:<20}"
          f"isinstance -> {isinstance(obj, ExporterProtocol)}")

print("""
  The ABC's failure is EARLY and PRECISE: you cannot build a broken
  exporter at all, and the message names the method you forgot.

  The Protocol's runtime check catches WrongShape but would happily accept
  a class with the right method names and completely wrong signatures
  (lesson.py section 3). Its real value is mypy, at Day 59.

  USE BOTH, for different things:
    ABC        for plugins you own and register — early failure, and
               filename()/name() shared for free
    Protocol   for the runner's PARAMETER type — so anything that works
               is accepted, including classes you never anticipated""")

# ###########################################################################
# THE TEST OF AN INTERFACE
# ###########################################################################

print()
print("=" * WIDTH)
print(f"""THE TEST: CAN YOU WRITE A SECOND, GENUINELY DIFFERENT IMPLEMENTATION?

  json      keeps nesting                    {results[0]['bytes']:>5} bytes
  csv       FLATTENS the tags list           {results[1]['bytes']:>5} bytes
  markdown  computes column widths           {results[2]['bytes']:>5} bytes
  null      produces nothing at all          {results[3]['bytes']:>5} bytes
  yaml-ish  inherits from nothing            {results[4]['bytes']:>5} bytes

Those five disagree about structure, about what to do with a list-valued
field, about whether to pad, and about whether to emit anything. If the
interface had said `write_row()` or `get_columns()`, only three of them
could have existed.

WHAT IS NOT IN THE INTERFACE IS THE DESIGN:
  no files, no paths, no encodings   -> export() returns a STRING, so the
                                        caller decides where it goes
  no assumption of output            -> NullExporter is legal
  no assumption about record shape   -> beyond "a mapping"

An interface with one plausible implementation is a description of your
class. This one has five.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add an HtmlExporter. Nothing above it changes — that is the test.
#
#   * Add `write_to_disk(path)` to the interface. Now NullExporter is
#     absurd and every implementation must know about the filesystem.
#     Revert it, and you have felt why the interface returns a string.
#
#   * Make YamlIshExporter inherit from Exporter. It gains name() and
#     filename() for free — the ABC's real advantage over the Protocol.
#
#   * Write the whole thing with NEITHER mechanism, relying on plain duck
#     typing. It works. Then delete a method from one exporter and find out
#     when you notice.
#
#   * On Day 59, add type hints and run mypy. The Protocol starts being
#     checked, and the ABC's guarantee moves from runtime to both.
