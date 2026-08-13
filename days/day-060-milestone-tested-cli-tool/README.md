# Day 060 — Milestone: tested CLI tool 🏁

**Phase 6 · Robust code** · ~180 minutes

> **Today's build:** a file-processing tool with a test suite above 90% coverage, full type hints and a README.

**Concepts:** a real utility · test coverage · type checking · documentation

---

## The article

### What this milestone is testing

Not whether you can write a program that works. Whether you can write one that **keeps** working
when somebody else changes it — which is the entire subject of Phase 6 and comes down to four
artefacts and one habit.

The tool is `tidy`: point it at a folder of sales exports in CSV, JSON or JSON Lines, and it
validates every row, summarises what it accepted and tells you precisely what it could not use.

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
  north.csv:7 sold_on: must be an ISO date (YYYY-MM-DD)
  north.csv:9 unit_price: is ambiguous (1,299 or 1.299?)
  south.json:4 (row): is a str, not an object
3 file(s), 17 rows, 10 accepted, 7 rejected, £3,379.18
```

### 1. Where every day of Phase 6 ended up

| day | in `tidy` |
|---|---|
| 51 exceptions | one `except TidyError` in `cli.main()`; a bug still crashes |
| 52 custom errors | eight types, each carrying the file, the line and the field |
| 53 files | streams not paths, `utf-8-sig`, `newline=""`, every write through `os.replace` |
| 54 CSV | a sniffed delimiter, a BOM stripped, a ragged row caught instead of a silent `None` |
| 55 JSON | two readers, a decode error reported with line and column, `sort_keys` for stable diffs |
| 56 pathlib | a sorted walk, dotfiles skipped, **dry run by default** |
| 57 pytest | 154 tests, and a sabotage that proves they bite |
| 58 fixtures | a factory fixture, `tmp_path`, and `io.StringIO` instead of files |
| 59 types | `mypy --strict`, no `Any`, no `# type: ignore` |

### 2. Four layers, and the arrows only point down

```
cli.py         arguments, formatting, EXIT CODES     — contains no rules
   ↓
pipeline.py    walk, read, validate, collect         — contains the workflow
   ↓
readers.py     one Protocol, three formats           — knows nothing about sales
records.py     the value type and its rules          — knows nothing about files
   ↓
errors.py      what can go wrong, as types           — knows nothing at all
```

That is not tidiness. It is what makes each layer testable on its own:

| to test | you need |
|---|---|
| `parse()` | a dict |
| a reader | an `io.StringIO` |
| `run()` | a directory |
| `main()` | a list of strings and a stream |

**Four of the 154 tests need a real directory.** The rest need nothing at all — and that is why the
suite got written rather than planned.

### 3. The rule that decides all the others

```python
result = pipeline.run(path)         # a Result. Nothing printed.
regions = by_region(result.sales)   # a list. Nothing written.
render(result, regions, out)        # printing, once, at the edge.
```

`run()` returns a frozen dataclass, so a test asserts on it directly:

```python
assert result.files_read == 3
assert result.rejections[0].line == 5
```

If `run()` printed, every one of those tests would need `capsys` and a regular expression. If it
*wrote*, they would need a temporary directory and a clean-up. Day 31 said *return, do not print*;
this is what that buys at the scale of a whole program.

### 4. An error hierarchy is a set of decisions

```
TidyError                   everything of ours
  OutputError               we could not write the result
  RecordError               one record is unusable  (also a ValueError)
    BadValueError
    MissingFieldError
  SourceError               we could not read the input at all
    UnknownFormatError
    UnreadableFileError
```

Each level is a decision somebody makes:

- `except SourceError:` — a whole file is unusable → skip it, keep going, name it in the report
- `except RecordError:` — one row is unusable → reject the row, carry on with the file
- `except TidyError:` — anything of ours → exit 2 with a message
- **no clause** — a bug → crash, with a traceback

There is exactly one `except TidyError` in the package and **no `except Exception` anywhere**, which
is why a typo in tidy's own code produces a traceback rather than "error: something went wrong".

And one error object serves three audiences without anybody re-typing a field name:

```
for a person   north.csv:42 units: must be > 0
for a log      BadValueError field='units' line=42
for a file     {'source': 'north.csv', 'line': 42, 'field': 'units', ...}
```

### 5. Dry run by default, and a preview that cannot lie

```
would write tidy-output/summary.csv (4 rows)
would write tidy-output/clean.csv (10 rows)
would write tidy-output/rejects.csv (7 rows)
would write tidy-output/summary.json (1 rows)
(dry run — add --write to create these)
```

`planned()` and `write_all()` take the same arguments and produce the same list of paths — and there
is a test asserting exactly that, so the preview cannot drift from the action the way it would if
somebody had written the message by hand.

### 6. Exit codes are the machine-readable half

| code | meaning |
|---:|---|
| `0` | everything was accepted |
| `1` | the run finished, and something was rejected or unreadable |
| `2` | the arguments were wrong, or nothing could be written |

**The distinction between 1 and 2 is the useful one.** `1` means *I did my job and the data has
problems*; `2` means *I could not do my job*.

```bash
python3 -m tidy exports/ --write || notify "check rejects.csv"
```

`main()` returns an `int` rather than calling `sys.exit()` itself, so `__main__.py` does the exiting
and every test calls `main()` and reads the number. **A tool that always exits 0 cannot be
automated.**

### 7. Decisions the tool refuses to make

Two inputs are rejected on purpose, and both are in the README's *Known limits*:

- **`01/02/2026`** — 1 February in Britain, 2 January in America. Nothing in a CSV says which.
- **`1,299`** — 1299 in Britain, 1.299 in Germany. (`1,299.00` and `4,50` are unambiguous and are
  accepted.)

Guessing would be wrong for half its users, silently, by a factor of a thousand. Refusing costs one
line in a report.

### 8. Coverage: 100%, and why that is not the achievement

```
Name               Stmts   Miss Branch BrPart  Cover
tidy/cli.py           95      0     44      0   100%
tidy/errors.py        29      0      0      0   100%
tidy/pipeline.py     106      0     14      0   100%
tidy/readers.py       80      0     26      0   100%
tidy/records.py       89      0     26      0   100%
tidy/report.py        52      0      0      0   100%
TOTAL                456      0    110      0   100%
```

**Coverage measures which lines ran, not whether the assertions were any good.** A file of
`assert True` reaches 100% and protects nothing.

What it is genuinely good for is the other direction: naming lines no test has ever executed. Two
tests here exist because a coverage report pointed at their lines — and one of those lines turned
out to be **dead code**: an `except UnicodeDecodeError` around `open()`, which cannot fire, because
`open()` does not decode anything. The handler now sits in `read_file()`, where the decoding
actually happens, with a test that feeds it a real latin-1 byte.

Two coverage decisions are written into `pyproject.toml` rather than argued about:

- `__main__.py` is **omitted** — it is four lines and an `if __name__` guard, and it is covered by an
  end-to-end test that runs it as a real subprocess (whose lines coverage cannot see).
- A `Protocol` method's `...` body is **excluded** — never executing it is what a Protocol *is*.

### 9. The check that proves the rest

`build.py` breaks the tool five ways and runs both checkers:

| change | tests | mypy |
|---|---|---|
| a rule loosened (`units <= 0` → `< 0`) | **RED** | clean |
| a boundary moved | **RED** | clean |
| the sort reversed | **RED** | clean |
| an atomic write made unsafe | **RED** | clean |
| the dry run made to write | **RED** | clean |

Five deliberate changes of the kind somebody makes at five o'clock on a Friday, and the suite catches
every one. **Note the mypy column:** clean throughout, because none of them is a *type* error. A
validator that accepts zero units is perfectly well typed and completely wrong — Day 59's division,
on this tool's own code.

### 10. Configure the commands, do not remember them

```toml
[tool.pytest.ini_options]
addopts = "--cov=tidy --cov-report=term-missing --cov-fail-under=90 -q"
```

A flag somebody has to remember is a flag that gets forgotten, and a coverage threshold nobody
enforces is a number in a README. `--cov-fail-under` in the config is the difference between a
target and a rule.

```bash
pytest && python3 -m mypy tidy && ruff check .
```

On Day 96 those three go into CI and stop depending on anybody remembering at all.

---

## The code

| File | What it is |
|---|---|
| `tidy/errors.py` | Eight exception types carrying file, line and field. |
| `tidy/records.py` | `Sale`, and every rule about what a valid one is. |
| `tidy/readers.py` | One `Protocol`, three formats, all taking streams. |
| `tidy/pipeline.py` | Walk, read, validate, collect. Returns a `Result`. |
| `tidy/report.py` | Four output files, every one written atomically. |
| `tidy/cli.py` | Arguments, formatting, exit codes. No rules. |
| `tidy/README.md` | The tool's own docs: install, usage, exit codes, known limits. |
| `tests/` | 154 tests in four files, 100% branch coverage. |
| `lesson.py` | Why the tool is shaped this way. |
| `build.py` | 23 acceptance checks, including five sabotages. |

```bash
python3 lesson.py
python3 build.py                     # the acceptance report
python3 -m tidy examples/            # the tool, dry run
python3 -m tidy examples/ --write
pytest                               # 154 tests, coverage gate at 90%
python3 -m mypy tidy
```

---

## The brief

Build yours before reading `tidy/`. It must have:

- [ ] a job worth doing — files in, something useful out
- [ ] **layers**, with the arrows pointing one way
- [ ] functions that **return values**; printing only at the edge
- [ ] an **exception hierarchy** of your own, with the location on each error
- [ ] one `except <YourBase>` at the top, and **no `except Exception`**
- [ ] **atomic writes** — temporary file, then `os.replace`
- [ ] a **dry run as the default**, computed by the same code that acts
- [ ] **exit codes** that distinguish "bad data" from "bad invocation"
- [ ] a test suite **above 90% coverage**, with the threshold enforced in config
- [ ] **`mypy --strict`** with no `Any`
- [ ] a README with install, usage, exit codes and **known limits**
- [ ] **five sabotages** you have run, and a suite that caught all five

---

## Common mistakes

**A tool that prints instead of returning.** Every test now needs `capsys`.

**Rules in the CLI.** They will not be there for the next caller.

**`except Exception` at the top.** Your own bugs become "an error occurred".

**Writing in place.** A crash mid-write destroys the previous output.

**Destructive by default.** One forgotten flag and somebody's directory is gone.

**Always exiting 0.** The tool cannot be used in a script.

**Guessing at ambiguous data.** Wrong by a factor of a thousand, silently.

**Coverage as a goal.** 100% of a suite that never fails is 100% of nothing.

**A threshold in the README instead of the config.** It is a wish, not a rule.

**Never seeing the suite fail.**

---

## Phase 6 checklist

You are leaving Robust code. Before you do:

- [ ] I catch the narrowest exception that can occur, and never bare `except:`
- [ ] I raise types of my own, with data on them and a message people can act on
- [ ] I always use `with`, always pass `encoding=`, and write atomically
- [ ] I never parse CSV by hand, and I always pass `newline=""`
- [ ] I know what JSON loses in a round trip, and I never store money as a float
- [ ] I use `pathlib`, resolve before comparing, and dry-run by default
- [ ] I write tests that fail when the code is wrong — boundaries, empties, errors, properties
- [ ] I use fixtures and `monkeypatch`, and prefer a parameter to a mock
- [ ] I annotate, run `mypy --strict`, and know what types catch that tests do not
- [ ] **I have broken my own tool on purpose and watched the suite go red**

Tomorrow: the outside world. Dates, regex, HTTP, real CLIs, logging and Git — the standard library
and the ecosystem that make Python worth choosing.
