"""Day 058 build — table-driven tests, and a clock you can move.

    python3 build.py             # run the suite and report
    python3 -m pytest tests/ -q  # the same suite, directly
    python3 -m pytest tests/ -v  # every case, by name

TWO CLAIMS, BOTH MEASURED BELOW:

    1. A validator with SEVEN rules and forty ways to break them needs
       about a dozen test FUNCTIONS, because @parametrize turns a table
       into tests.

    2. Time-dependent code needs no mocking library IF the time is a
       parameter — and the same rule written the other way needs a
       datetime subclass, a monkeypatch, and a lesson about which module
       to patch.

The suite also runs a retry with 13 seconds of configured backoff, in
about a millisecond.
"""

import ast
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

WIDTH = 78
HERE = Path(__file__).resolve().parent

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "day-040-milestone-your-own-toolkit"))

import bookings                                            # noqa: E402
import legacy                                              # noqa: E402
from bookings import Booking, validate                     # noqa: E402


def pytest_run(*arguments):
    started = time.perf_counter()
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", *arguments,
         "-p", "no:cacheprovider", "--no-header"],
        capture_output=True, text=True, cwd=HERE,
    )
    return finished.stdout + finished.stderr, time.perf_counter() - started


def calls_the_clock(source):
    """Does this source actually CALL now()/today()? Parsed, not grepped.

    A regular expression would match the words in a docstring — the same
    mistake Day 40's dependency check made, and fixed the same way.
    """
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("now", "today", "utcnow", "time")
        for node in ast.walk(ast.parse(source))
    )


NOW = datetime(2026, 3, 18, 10, 0)


def make(**overrides):
    defaults = {
        "reference": "AB-1234", "email": "ada@example.com",
        "starts_at": NOW + timedelta(hours=4),
        "ends_at": NOW + timedelta(hours=6),
        "party_size": 4, "created_at": NOW,
    }
    return Booking(**{**defaults, **overrides})


# ###########################################################################
# THE SUITE
# ###########################################################################

print("=" * WIDTH)
print(f"{'THE SUITE':^{WIDTH}}")
print("=" * WIDTH)

output, elapsed = pytest_run("tests/", "-q")
summary = next((line for line in output.splitlines() if " passed" in line
                or " failed" in line), "?")

collected, _ = pytest_run("tests/", "--collect-only", "-q")
case_count = len([ln for ln in collected.splitlines() if "::" in ln])

sources = sorted((HERE / "tests").glob("test_*.py"))
print()
print(f"  {'FILE':<40}{'FUNCTIONS':>11}{'CASES':>9}{'LINES':>9}")
print("  " + "-" * (WIDTH - 4))
for path in sources:
    text = path.read_text(encoding="utf-8")
    functions = len(re.findall(r"^def test_", text, re.MULTILINE))
    per_file, _ = pytest_run(str(path.relative_to(HERE)),
                             "--collect-only", "-q")
    cases = len([ln for ln in per_file.splitlines() if "::" in ln])
    print(f"  {path.name:<40}{functions:>11}{cases:>9}"
          f"{len(text.splitlines()):>9}")
print("  " + "-" * (WIDTH - 4))
print(f"  {summary.strip()}   (wall clock {elapsed:.2f}s)")

print(f"""
  {case_count} test cases from about thirty test functions. The difference is
  @parametrize: one function with a seventeen-row table is seventeen
  independently named, independently failing tests.

  A FAILURE LOOKS LIKE THIS:

      FAILED test_validators.py::test_one_bad_field_is_reported[
             overrides11-party_size]

  ...which names the rule AND the row, before you have opened anything.""")


# ###########################################################################
# THE TABLE, AS DATA
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE VALIDATOR, EXERCISED':^{WIDTH}}")
print("=" * WIDTH)

rows = [
    ("a valid booking", {}, 0),
    ("reference in lower case", {"reference": "ab-1234"}, 1),
    ("no dash in the reference", {"reference": "AB1234"}, 1),
    ("an email with no TLD", {"email": "ada@example"}, 1),
    ("a party of zero", {"party_size": 0}, 1),
    ("a party of thirteen", {"party_size": 13}, 1),
    ("party_size True", {"party_size": True}, 1),
    ("starting in the past", {"starts_at": NOW - timedelta(hours=1),
                              "ends_at": NOW + timedelta(hours=1)}, 1),
    ("fourteen minutes long", {"ends_at": NOW + timedelta(hours=4,
                                                         minutes=14)}, 1),
    ("nine hours long", {"ends_at": NOW + timedelta(hours=13)}, 1),
    ("starting at 7am", {"starts_at": NOW.replace(hour=7) + timedelta(days=1),
                         "ends_at": NOW.replace(hour=8) + timedelta(days=1)},
     1),
    ("everything wrong at once",
     {"reference": "x", "email": "no", "party_size": 99,
      "starts_at": NOW - timedelta(days=1),
      "ends_at": NOW - timedelta(days=2)}, 5),
]

print(f"\n  {'CASE':<32}{'PROBLEMS':>9}   FIRST MESSAGE")
print("  " + "-" * (WIDTH - 4))
for label, overrides, expected in rows:
    problems = validate(make(**overrides), now=NOW)
    first = str(problems[0])[:32] if problems else "-"
    flag = "" if len(problems) == expected else "  <- UNEXPECTED"
    print(f"  {label:<32}{len(problems):>9}   {first}{flag}")

print("""
  EVERY ROW BREAKS EXACTLY ONE RULE except the last, which breaks five and
  gets five messages — because validate() collects rather than stopping at
  the first, which is Day 52's argument applied without the ExceptionGroup
  machinery.""")


# ###########################################################################
# THE CLOCK: TWO WAYS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE SAME RULE, WITH AND WITHOUT A MOCK':^{WIDTH}}")
print("=" * WIDTH)

booking = make(created_at=NOW)

print("""
  THE RULE: a hold expires fifteen minutes after the booking was created.

  WITH THE CLOCK AS A PARAMETER — no fixture, no patching, no import:""")
print(f"\n  {'now':<28}{'hold_expired':>14}")
for minutes in (0, 14, 15, 60):
    moment = NOW + timedelta(minutes=minutes)
    print(f"  {moment:%H:%M} (+{minutes:>2} min){'':<12}"
          f"{str(bookings.hold_expired(booking, now=moment)):>14}")

print("""
  WITH THE CLOCK FETCHED FROM THE WORLD — legacy.hold_expired() calls
  datetime.now(), so the test needs all of this:

      class FrozenDatetime(datetime):
          @classmethod
          def now(cls, tz=None):
              return cls.frozen

      @pytest.fixture
      def frozen_clock(monkeypatch, now):
          FrozenDatetime.frozen = now
          monkeypatch.setattr(legacy, "datetime", FrozenDatetime)
          ...

  ...and, more importantly, it needs you to know that the last line says
  `legacy` and not `datetime`.""")

wrong_target = legacy.datetime is datetime
print(f"\n  {'legacy.py did `from datetime import datetime`':<52}True")
print(f"  {'...so patching the datetime MODULE would miss it':<52}"
      f"{wrong_target}")
print("""
  Both versions are tested in tests/test_isolating_the_world.py, four
  cases each, and the assertions are identical. Only the machinery
  differs — and the machinery is what breaks when somebody reorganises an
  import six months from now.""")


# ###########################################################################
# THE SLEEP THAT NEVER HAPPENED
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THIRTEEN SECONDS OF BACKOFF, IN A MILLISECOND':^{WIDTH}}")
print("=" * WIDTH)

retry_output, retry_time = pytest_run("tests/test_isolating_the_world.py",
                                      "-q", "-k", "retry or sleep")
configured = 3.5 + 3.5 + 3.0 + 13.0     # the delays the four tests declare

print(f"\n  {'delay configured across the retry tests':<52}"
      f"{configured:>8.1f}s")
print(f"  {'time those tests actually took':<52}{retry_time:>8.2f}s")
print(f"  {'speed-up':<52}{configured / max(retry_time, 0.01):>8.0f}x")
print("""
  monkeypatch.setattr(time, "sleep", fake_sleep) — one line in a fixture.

  AND IT DOES MORE THAN SAVE TIME. The fake records what it was asked to
  wait for, so the backoff SCHEDULE becomes data:

      assert no_waiting == [0.5, 1.0, 2.0]

  Without the patch that assertion is impossible to write: you can only
  observe that the whole thing took roughly three and a half seconds,
  which is not the same claim.

  A SUITE THAT TAKES A MINUTE IS A SUITE PEOPLE RUN BEFORE LUNCH. A suite
  that takes a second is one they run before every commit.""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

# Sabotage: make one boundary wrong and confirm the table notices.
source = HERE / "bookings.py"
original = source.read_text(encoding="utf-8")
sabotaged = original.replace("MINIMUM = timedelta(minutes=15)",
                             "MINIMUM = timedelta(minutes=10)")
assert sabotaged != original                                  # noqa: S101
source.write_text(sabotaged, encoding="utf-8")
try:
    sabotage_output, _ = pytest_run("tests/test_validators.py", "-q",
                                    "--tb=no")
finally:
    source.write_text(original, encoding="utf-8")
    # AND CLEAR THE BYTECODE CACHE. Python validates a .pyc against the
    # source's (mtime, size). The sabotage changed "15" to "10" — the same
    # SIZE — and both writes can land inside one filesystem timestamp
    # tick, so the stale .pyc is reused and the "reverted" run still sees
    # the sabotage. This check failed intermittently until that line
    # existed, which is a better argument for `git clean` than any
    # paragraph.
    shutil.rmtree(HERE / "__pycache__", ignore_errors=True)

restored, _ = pytest_run("tests/test_validators.py", "-q", "--tb=no")

no_problems = validate(make(), now=NOW)
functions_total = sum(
    len(re.findall(r"^def test_", p.read_text(encoding="utf-8"), re.MULTILINE))
    for p in sources)

claims = [
    ("the suite passes", " failed" not in summary),
    ("...and runs in well under a second", elapsed < 5),
    ("a table of rows produces many more cases than functions",
     case_count > functions_total * 2),
    ("a valid booking has no problems", no_problems == []),
    ("validation never mutates the diary",
     (lambda d: (validate(make(reference='CD-5678'), now=NOW, existing=d),
                 len(d) == 3)[1])([make(reference='ZZ-000%d' % n)
                                   for n in (1, 2, 3)])),
    ("touching bookings do not count as overlapping",
     validate(make(reference="CD-5678",
                   starts_at=NOW + timedelta(hours=11),
                   ends_at=NOW + timedelta(hours=12)),
              now=NOW,
              existing=[make(reference="ZZ-0001",
                             starts_at=NOW + timedelta(hours=12),
                             ends_at=NOW + timedelta(hours=13))]) == []),
    ("the clock is a parameter, not a call",
     not calls_the_clock(original)),
    ("...whereas the legacy version fetches it",
     calls_the_clock((HERE / "legacy.py").read_text(encoding="utf-8"))),
    ("patching the datetime module would NOT reach legacy.py",
     legacy.datetime is datetime),
    ("the retry tests do not really sleep", retry_time < 2.0),
    ("SABOTAGE: moving one boundary by five minutes turns the suite red",
     " failed" in sabotage_output),
    ("...and it is green again once reverted", " failed" not in restored),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

print("""
  THE SABOTAGE IS THE ONE THAT MATTERS AGAIN. Changing the minimum booking
  length from fifteen minutes to ten is the sort of edit somebody makes on
  purpose, and the table notices because it tests BOTH SIDES of the
  boundary: 14 must fail and 15 must pass. A table with only the failing
  side would have stayed green.

  TEST BOTH SIDES OF EVERY BOUNDARY. It is one more row.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a field to Booking. One fixture changes; no test does. That is
#     what the factory fixture bought.
#
#   * Change the `no_waiting` fixture to a real time.sleep and run the
#     suite. Then decide how many such tests you would tolerate.
#
#   * Make `diary` a module-scoped fixture, then have one test append to
#     it. Watch a later test fail, and watch it pass when run alone.
#
#   * Patch legacy.datetime by string — monkeypatch.setattr("legacy.
#     datetime", Frozen) — and confirm it does the same thing.
#
#   * Replace the Mock in test_confirm_* with a five-line FakeNotifier
#     that records its calls in a list. Then rename Notifier.send() and
#     see which version of the test notices.
#
#   * On Day 60, run this with --cov and find the branches of validate()
#     that no row reaches.
