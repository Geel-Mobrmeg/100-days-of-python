"""Day 060 — What makes a tool, rather than a script.

    python3 lesson.py

No new syntax. Every idea here arrived on a numbered day between 51 and 59;
what is new is deciding where each one goes when you build the whole thing.

This file is about the SHAPE of tidy/ — why there are eight modules, why
the CLI contains no rules, and why the same eight decisions make the test
suite short enough that somebody actually writes it.
"""

from __future__ import annotations

import sys
from pathlib import Path

WIDTH = 76
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ---------------------------------------------------------------------------
# 1. The layers
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. FOUR LAYERS, AND WHAT MAY NOT KNOW WHAT':^{WIDTH}}")
print("=" * WIDTH)
print("""
      cli.py         arguments, formatting, EXIT CODES
        |            knows: pipeline, report.  Contains: no rules.
        v
      pipeline.py    walk, read, validate, collect
        |            knows: readers, records.  Contains: the workflow.
        v
      readers.py     one Protocol, three formats
      records.py     the value type and its rules
        |            knows: errors.  Contains: the domain.
        v
      errors.py      what can go wrong, as types
                     knows: nothing.

  THE ARROWS ONLY POINT DOWN. records.py has never heard of a file;
  readers.py has never heard of a sale; pipeline.py opens nothing by name;
  cli.py re-checks nothing.

  THAT IS NOT TIDINESS. It is what makes each layer testable on its own:

      parse()        needs a dict
      a reader       needs an io.StringIO
      run()          needs a directory
      main()         needs a list of strings and a stream

  Four of 154 tests need a real directory. The rest need nothing at all.""")


# ---------------------------------------------------------------------------
# 2. Return a value, print at the edge
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. THE RULE THAT DECIDES THE OTHERS':^{WIDTH}}")
print("=" * WIDTH)

from tidy import pipeline, report                            # noqa: E402

result = pipeline.run(HERE / "examples")
regions = pipeline.by_region(result.sales)

print(f"""
      result = pipeline.run(path)      -> a Result. Nothing printed.
      regions = by_region(result.sales) -> a list. Nothing written.
      render(result, regions, out)      -> printing, once, at the edge.

  run() just returned:

      {len(result.sales)} sales, {len(result.rejections)} rejections, """
      f"""{result.files_read} files read, {report.money(result.total_value)}

  ...as a frozen dataclass, so a test can assert on it directly:

      assert result.files_read == 3
      assert result.rejections[0].line == 5

  IF run() PRINTED, every one of those tests would need capsys and a
  regular expression. If it WROTE, they would need a temporary directory
  and a clean-up. Day 31 said "return, do not print"; this is what that
  buys at the scale of a whole program.""")


# ---------------------------------------------------------------------------
# 3. Errors as types
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. THE ERROR HIERARCHY IS AN API':^{WIDTH}}")
print("=" * WIDTH)

from tidy import errors                                      # noqa: E402


def tree(cls: type, depth: int = 0) -> None:
    subclasses = sorted(cls.__subclasses__(), key=lambda c: c.__name__)
    doc = (cls.__doc__ or "").strip().splitlines()[0]
    print(f"  {'  ' * depth}{cls.__name__:<{28 - 2 * depth}}{doc[:44]}")
    for subclass in subclasses:
        tree(subclass, depth + 1)


print()
tree(errors.TidyError)

print("""
  EACH LEVEL IS A DECISION SOMEBODY MAKES:

      except SourceError:      a whole file is unusable -> skip it, keep
                               going, and name it in the report
      except RecordError:      one row is unusable -> reject the row
      except TidyError:        anything of ours -> exit 2 with a message
      (no clause)              a bug -> crash, with a traceback

  cli.main() has exactly one `except TidyError`. There is no
  `except Exception` anywhere in the package, which is why a typo in
  tidy's own code still produces a traceback rather than "error:
  something went wrong".""")

sample = errors.BadValueError("north.csv", 42, "units", "must be > 0", "0")
print("\n  one error, three audiences:")
print(f"    for a person   {sample}")
print(f"    for a log      {type(sample).__name__} field={sample.field!r} "
      f"line={sample.line}")
print(f"    for a file     {sample.as_dict()}")


# ---------------------------------------------------------------------------
# 4. Dry run
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. WHY THE DRY RUN IS THE DEFAULT':^{WIDTH}}")
print("=" * WIDTH)

preview = report.planned(result, regions, Path("tidy-output"))
print()
for path, rows in preview:
    print(f"      would write {path}  ({rows} rows)")

print("""
  A TOOL THAT WRITES FILES CAN DESTROY THEM. The question is only whether
  the destructive path is the one you get by typing the short command.

      python3 -m tidy exports/            shows you
      python3 -m tidy exports/ --write    does it

  AND THE PREVIEW MUST NOT BE ABLE TO LIE. planned() and write_all() take
  the same arguments and produce the same list of paths — there is a test
  asserting exactly that — so the preview cannot drift from the action the
  way it would if somebody had written the message by hand.

  Day 56 made this argument about a renamer. It is the same argument, and
  it is the difference between a tool people trust with a directory and a
  tool they run once on a copy.""")


# ---------------------------------------------------------------------------
# 5. Exit codes
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. EXIT CODES ARE THE OTHER HALF OF THE INTERFACE':^{WIDTH}}")
print("=" * WIDTH)
print("""
      0   everything was accepted
      1   the run finished, and something was rejected or unreadable
      2   the arguments were wrong, or nothing could be written

  THE DISTINCTION BETWEEN 1 AND 2 IS THE USEFUL ONE. 1 means "I did my
  job and the data has problems"; 2 means "I could not do my job". A
  nightly script wants to treat those differently:

      python3 -m tidy exports/ --write || notify "check rejects.csv"

  ...and a shell only ever sees the number. Everything printed is for a
  human; the exit code is for a machine, and it is the only part of the
  output another program can rely on.

  A TOOL THAT ALWAYS EXITS 0 CANNOT BE AUTOMATED. That is the whole
  reason main() returns an int instead of calling sys.exit() itself —
  __main__.py does the exiting, and every test calls main() and reads
  the number.""")


# ---------------------------------------------------------------------------
# 6. What the suite is shaped like
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. 154 TESTS, AND WHAT THEY ARE FOR':^{WIDTH}}")
print("=" * WIDTH)
print("""
  test_records.py     the RULES, as tables. Both sides of every boundary:
                      14 units passes and 0 fails, 15 minutes passes and
                      14 fails, '1,299.00' passes and '1,299' is refused.

  test_readers.py     every reader against io.StringIO. Not one temporary
                      file, because read() takes a STREAM (Day 53).

  test_pipeline...py  the workflow, in tmp_path: a bad row does not stop
                      the file, a bad file does not stop the run, the
                      region totals add up to the grand total, and writing
                      twice is byte-identical.

  test_cli.py         exit codes, the dry run, and one end-to-end
                      subprocess that runs the real command.

  THREE KINDS OF TEST, IN ORDER OF VALUE:

    THE PROPERTY      "the region totals equal the grand total", for
                      whatever data arrives. One test, no examples.
    THE BOUNDARY      the value on each side of every limit.
    THE EXAMPLE       one happy path, to document the shape.

  AND THE ONE THAT PROVES THE OTHERS: build.py breaks the tool five ways
  and checks the suite goes red each time. A suite that has never failed
  is a suite nobody has checked.""")


# ---------------------------------------------------------------------------
# 7. The three commands
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. THE COMMANDS, AND WHY THEY LIVE IN pyproject.toml':^{WIDTH}}")
print("=" * WIDTH)
print("""
      pytest                 the suite, with coverage, failing under 90%
      python3 -m mypy tidy   strict, no Any
      ruff check .           the style rules

  ALL THREE ARE CONFIGURED IN pyproject.toml, and that is the point:

      [tool.pytest.ini_options]
      addopts = "--cov=tidy --cov-report=term-missing --cov-fail-under=90"

  A flag somebody has to remember is a flag that gets forgotten, and a
  coverage threshold nobody enforces is a number in a README. Putting
  --cov-fail-under in the config means the suite FAILS when coverage
  drops, which is the difference between a target and a rule.

  COVERAGE IS A BAD GOAL AND A GOOD ALARM. It cannot tell you the
  assertions are any good — a file of `assert True` reaches 100% — but it
  can name lines no test has ever run. Two tests in this suite exist
  because a coverage report pointed at their lines, and one of those lines
  turned out to be DEAD: an `except UnicodeDecodeError` around open(),
  which cannot fire, because open() does not decode anything.

  On Day 96 these three go in a CI file and stop depending on anybody
  remembering at all.""")

print()
print("=" * WIDTH)
print("""  1. Layers, and the arrows only point down.
  2. Return a value; print at the edge. Everything else follows.
  3. An error hierarchy is a set of decisions you offer the caller.
  4. Dry run by default, and the preview computed by the same code.
  5. Exit codes are the machine-readable half of the output.
  6. Properties, then boundaries, then examples.
  7. Configure the commands so nobody has to remember them.
  8. Coverage is an alarm, not a goal — and a suite you have never seen
     fail is not evidence of anything.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now build yours
# ---------------------------------------------------------------------------
#
#   * Take the tool you keep meaning to write and draw the four layers
#     before you type. Which module may know about the filesystem?
#
#   * Write main(argv, out) -> int before you write anything it calls. The
#     signature forces the rest to be testable.
#
#   * Add --cov-fail-under to a project of your own and watch the next
#     untested function break the build.
#
#   * Break your own tool five ways and count how many the suite catches.
#     That number, not the coverage percentage, is what your tests are
#     worth.
