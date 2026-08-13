# tidy

Validate and summarise sales exports — CSV, JSON or JSON Lines — and say
precisely what it could not use.

```bash
python3 -m tidy examples/            # a dry run: writes nothing
python3 -m tidy examples/ --write    # ...and do it
```

```
REGION      ORDERS   UNITS         VALUE     AVERAGE
----------------------------------------------------
north            4      57     £2,778.00     £694.50
south            3     114       £315.25     £105.08
east             2      67       £189.93      £94.96
west             1       2        £96.00      £96.00
----------------------------------------------------

7 rejected:
  east.jsonl:3 (row): is not valid JSON
  north.csv:5 sku: must look like AB-1234
  north.csv:6 region: must be one of north, south, east, west
  north.csv:7 sold_on: must be an ISO date (YYYY-MM-DD)
  north.csv:8 units: must be greater than zero
  north.csv:9 unit_price: is ambiguous (1,299 or 1.299?)
  south.json:4 (row): is a str, not an object
3 file(s), 17 rows, 10 accepted, 7 rejected, £3,379.18
```

---

## Install

Nothing to install — it uses only the standard library and needs Python 3.11+.

```bash
python3 -m tidy --help
```

Or, as a real command:

```bash
pip install -e .
tidy examples/
```

## Usage

```
python3 -m tidy SOURCE [-o OUT] [--write] [--recursive] [--quiet]

  SOURCE        a file, or a directory of .csv/.json/.jsonl files
  -o, --out     where to write (default: ./tidy-output)
  --write       actually write. Without it, nothing is created.
  -r            recurse into subdirectories
  -q            only the summary line
  -h, --help    this
```

**Exit codes**, because this is meant to go in a script:

| code | meaning |
|---:|---|
| `0` | everything was accepted |
| `1` | the run finished, and something was rejected or unreadable |
| `2` | the arguments were wrong, or nothing could be written |

```bash
python3 -m tidy exports/ --write || echo "check tidy-output/rejects.csv"
```

## What it writes

| file | one row per |
|---|---|
| `summary.csv` | region — orders, units, value, average order |
| `clean.csv` | accepted sale, normalised |
| `rejects.csv` | rejected row, **with its source file and line number** |
| `summary.json` | the same numbers, for another program |

Every file is written to a temporary name and then renamed into place, so a
crash halfway through leaves the previous report intact rather than half a new
one.

## What counts as a valid record

| field | rule |
|---|---|
| `sku` | `AB-1234` — two to four letters, a dash, three to five digits |
| `region` | one of `north`, `south`, `east`, `west` (case-insensitive) |
| `sold_on` | **ISO only**: `2026-03-01` |
| `units` | a whole number, greater than zero |
| `unit_price` | greater than zero, at most 1,000,000 |

Column names are normalised first, so `SKU`, `sku` and `  Unit Price ` all work.
Currency symbols are stripped. `4,50` is read as four and a half.

## Known limits

Stated rather than discovered.

- **`01/02/2026` is refused.** It is 1 February in Britain and 2 January in
  America, and nothing in a CSV says which. Guessing would be wrong for half of
  its users, silently. Convert to ISO before feeding it in.
- **`1,299` is refused** for the same reason — 1299 in Britain, 1.299 in
  Germany. `1,299.00` and `4,50` are unambiguous and are accepted.
- **One problem per row.** A row with a bad SKU *and* a bad date is reported
  once, for the SKU. Fix and re-run.
- **The whole result is held in memory.** Fine for the hundreds of thousands of
  rows a sales export contains; not a tool for a 10 GB file. `pipeline.run()`
  would need to stream, and the summary is the only part that genuinely has to
  accumulate.
- **A file with an undecodable byte is skipped entirely**, not partially read.
  For a data file that is the right call; for a log it would not be.
- **A directory scan ignores extensions it has no reader for**, without
  mentioning them. Naming such a file directly *is* an error, because you asked
  for it specifically.
- **No `--undo`.** `--write` overwrites the previous report. Keep the output
  directory outside anything precious.

## Adding a format

Write a class with `extensions` and `read(stream, source)`, and add it to
`READERS` in `readers.py`. Nothing else changes — the pipeline never asks what
kind of reader it has.

```python
class YamlReader:
    extensions: tuple[str, ...] = (".yaml", ".yml")

    def read(self, stream, source):
        yield from ...
```

## Developing

```bash
pytest                      # 154 tests, with coverage, fails under 90%
python3 -m mypy tidy        # strict, no Any
ruff check .
```

All three are configured in `pyproject.toml`, so there are no flags to remember.

## Versioning

- **MAJOR** — an output column changes, or a rule starts rejecting what it used
  to accept
- **MINOR** — a new format, a new flag, a new output file
- **PATCH** — a fix that changes no documented behaviour
