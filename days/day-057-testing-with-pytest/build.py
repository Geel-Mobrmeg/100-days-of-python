"""Day 057 build — the test suite that found four bugs in Day 40's toolkit.

    python3 build.py            # run the suite and report
    python3 -m pytest tests/    # the same suite, directly
    python3 -m pytest tests/ -v # one line per test

WHAT HAPPENED, IN ORDER:

    1. The suite was written against the package's DOCSTRINGS, not its
       code — boundaries, empty cases, error cases and properties.
    2. Four assertions failed.
    3. Each was reduced to one line, reproduced, and confirmed to be a
       defect rather than a misunderstanding.
    4. The package was fixed and its version went 1.0.0 -> 1.1.0, because
       all four fixes change documented behaviour.
    5. The buggy functions were kept, in as_shipped.py, so the tests can
       demonstrate the failure and the fix on the SAME assertions.

Day 40's own build.py ran 28 acceptance checks and its doctests passed.
None of them found any of this, and the reason is worth more than the bugs
are: they all tested the examples the author had already thought of.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

WIDTH = 78
HERE = Path(__file__).resolve().parent

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "day-040-milestone-your-own-toolkit"))

import as_shipped                                          # noqa: E402
import mytoolkit                                           # noqa: E402


def run(*arguments):
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", *arguments,
         "-p", "no:cacheprovider", "--no-header"],
        capture_output=True, text=True, cwd=HERE,
    )
    return finished.stdout + finished.stderr


# ###########################################################################
# THE SUITE
# ###########################################################################

print("=" * WIDTH)
print(f"{'THE SUITE':^{WIDTH}}")
print("=" * WIDTH)

output = run("tests/", "-q")
summary = next((line for line in output.splitlines()
                if " passed" in line or " failed" in line), "?")

files = sorted((HERE / "tests").glob("test_*.py"))
print()
for path in files:
    text = path.read_text(encoding="utf-8")
    functions = len(re.findall(r"^def test_", text, re.MULTILINE))
    parametrised = len(re.findall(r"@pytest\.mark\.parametrize", text))
    print(f"  {path.name:<36}{functions:>4} functions, "
          f"{parametrised:>2} parametrised")

print(f"\n  {'lines of test code':<36}"
      f"{sum(len(p.read_text(encoding='utf-8').splitlines()) for p in files):>4}")
print(f"  {'lines of package code':<36}"
      f"{sum(len(p.read_text(encoding='utf-8').splitlines()) for p in (HERE.parent / 'day-040-milestone-your-own-toolkit' / 'mytoolkit').glob('*.py')):>4}")
print(f"\n  {summary.strip()}")

print("""
  MORE TEST CODE THAN LIBRARY CODE, and that is normal rather than
  alarming. The tests carry the cases; the library carries the rules.

  The four `xfailed` are the bugs, asserted against the code as Day 40
  shipped it. They are marked strict=True, so if anybody "fixes"
  as_shipped.py the suite goes RED and tells them to delete the marker.""")


# ###########################################################################
# THE FOUR BUGS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE FOUR BUGS, REPRODUCED':^{WIDTH}}")
print("=" * WIDTH)

bugs = [
    ("human_bytes at a rounding boundary",
     "human_bytes(1024 * 1024 - 1)",
     lambda m: m.human_bytes(1024 * 1024 - 1),
     "1.0 MB",
     "compares the value BEFORE formatting it, so 1023.99902 KB prints\n"
     "     as '1024.0 KB' — a quantity that does not exist"),
    ("duration of a negative number",
     "duration(-5)",
     lambda m: m.duration(-5),
     "-0:05",
     "divmod floors: divmod(-5, 3600) is (-1, 3595), so minus five\n"
     "     seconds renders as minus one hour, fifty-nine minutes"),
    ("slugify is not URL-safe",
     "slugify('Café')",
     lambda m: m.slugify("Café"),
     "cafe",
     "str.isalnum() is True for every letter in every script, so the\n"
     "     'URL-safe' slug kept the é (and the README claimed 'caf')"),
    ("dig hides a stored null",
     "dig({'a': None}, 'a', default='MISSING')",
     lambda m: m.dig({"a": None}, "a", default="MISSING"),
     None,
     "folding None into the default made 'the key is absent' and 'the\n"
     "     key holds null' the same answer — the exact question dig() asks"),
]

for index, (title, call, run_it, expected, why) in enumerate(bugs, 1):
    before = run_it(as_shipped)
    after = run_it(mytoolkit)
    print(f"\n  {index}. {title.upper()}")
    print(f"     {call}")
    print(f"     {'as shipped (1.0.0)':<26}{before!r}")
    print(f"     {'expected':<26}{expected!r}")
    print(f"     {'fixed (1.1.0)':<26}{after!r}"
          f"{'   ok' if after == expected else '   STILL WRONG'}")
    print(f"     why: {why}")

print("""
  NOTE WHAT THEY HAVE IN COMMON. Not one is in the happy path, and not one
  would be found by using the library normally. Three are BOUNDARIES —
  the value just below a unit change, zero going negative, the first
  non-ASCII character — and the fourth is a value (null) that the author
  never wrote a docstring example for.

  That is where bugs live, and it is why "the boundaries" is second on the
  list of what to test.""")


# ###########################################################################
# WHY DAY 40'S OWN CHECKS MISSED THEM
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHY 28 ACCEPTANCE CHECKS AND 28 DOCTESTS FOUND NOTHING':^{WIDTH}}")
print("=" * WIDTH)
print("""
  DOCTESTS test the examples the author chose. Every doctest in the package
  passed, on Day 40 and today, because human_bytes(2048) really is
  '2.0 KB'. An author who had thought of 1048575 would have written the
  code correctly in the first place.

  ACCEPTANCE CHECKS tested the package's PROMISES — return rather than
  print, no mutation of arguments, a docstring on everything public, zero
  dependencies. All true, all still true, and none of them about whether
  the answers are right.

  A TEST SUITE IS DIFFERENT IN ONE SPECIFIC WAY: it is written by somebody
  asking "how could this be wrong?" rather than "does this work?". The two
  questions produce different files.

  THE FOUR TESTS THAT FOUND THESE ARE ALL PROPERTIES, not examples:

    test_human_bytes_never_prints_a_value_of_1024_or_more
        checks 120 inputs across 40 decades, and would have caught the bug
        without anybody thinking of 1048575

    test_duration_of_a_negative_is_the_negative_of_the_duration
        states the rule instead of three cases

    test_slugify_output_is_always_url_safe
        asserts a property of the OUTPUT over twelve hostile inputs

    test_chunked_never_loses_or_duplicates_an_item
        flatten the chunks, get the input back, for every size 1..39

  Write examples to document. Write properties to find bugs.""")


# ###########################################################################
# THE REGRESSION GUARD
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'AND THE FIX DID NOT BREAK ANYTHING':^{WIDTH}}")
print("=" * WIDTH)

unchanged = [
    ("human_bytes(512)", lambda m: m.human_bytes(512)),
    ("human_bytes(2048)", lambda m: m.human_bytes(2048)),
    ("human_bytes(1_500_000_000)", lambda m: m.human_bytes(1_500_000_000)),
    ("duration(75)", lambda m: m.duration(75)),
    ("duration(3725)", lambda m: m.duration(3725)),
    ("slugify('Hello, World!')", lambda m: m.slugify("Hello, World!")),
    ("dig({'a': 1}, 'a', 'b', default='-')",
     lambda m: m.dig({"a": 1}, "a", "b", default="-")),
]

print(f"\n  {'CALL':<40}{'1.0.0':<14}{'1.1.0':<14}SAME?")
print("  " + "-" * (WIDTH - 4))
same = 0
for call, run_it in unchanged:
    before, after = run_it(as_shipped), run_it(mytoolkit)
    same += before == after
    print(f"  {call:<40}{str(before):<14}{str(after):<14}"
          f"{'yes' if before == after else 'NO'}")

print("""
  Those are the doctest examples, run against both versions. A fix that
  changes an answer nobody asked you to change is a second bug, and this
  table is how you find out before your users do.

  IT IS ALSO WHY THE VERSION WENT TO 1.1.0 AND NOT 1.0.1. All four fixes
  change DOCUMENTED behaviour: somebody's filenames used to contain 'café'
  and now contain 'cafe'. A patch release promises nothing changes;
  this is a minor one, with the change written down (Day 40's rule,
  applied to Day 40's package).""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

passed = int(re.search(r"(\d+) passed", summary).group(1)) if "passed" in summary else 0
xfailed = int(re.search(r"(\d+) xfailed", summary).group(1)) if "xfailed" in summary else 0

# Sabotage: break the package on purpose and confirm the suite goes red.
numbers = (HERE.parent / "day-040-milestone-your-own-toolkit"
           / "mytoolkit" / "numbers.py")
original = numbers.read_text(encoding="utf-8")
sabotaged = original.replace('return f"{int(size)} {units[index]}"',
                             'return f"{int(size) + 1} {units[index]}"')
assert sabotaged != original, "the sabotage did not apply"        # noqa: S101
numbers.write_text(sabotaged, encoding="utf-8")
try:
    sabotage_output = run("tests/test_numbers.py", "-q", "--tb=no")
finally:
    numbers.write_text(original, encoding="utf-8")
    # Clear the bytecode cache too: Python validates a .pyc against the
    # source's (mtime, size), and two writes inside one filesystem
    # timestamp tick can leave a stale one in place.
    shutil.rmtree(numbers.parent / "__pycache__", ignore_errors=True)

sabotage_caught = " failed" in sabotage_output
restored = run("tests/test_numbers.py", "-q", "--tb=no")

claims = [
    ("the suite passes", " failed" not in summary),
    ("...with more than a hundred cases", passed > 100),
    ("the four bugs are still reproducible on the shipped code",
     xfailed == 4),
    ("bug 1 is fixed",
     mytoolkit.human_bytes(1024 * 1024 - 1) == "1.0 MB"),
    ("bug 2 is fixed", mytoolkit.duration(-5) == "-0:05"),
    ("bug 3 is fixed", mytoolkit.slugify("Café") == "cafe"),
    ("bug 4 is fixed",
     mytoolkit.dig({"a": None}, "a", default="M") is None),
    ("every doctest example still gives the same answer",
     same == len(unchanged)),
    ("the version was bumped", mytoolkit.__version__ == "1.1.0"),
    ("SABOTAGE: a one-character change to the package turns the suite red",
     sabotage_caught),
    ("...and the suite is green again once it is reverted",
     " failed" not in restored),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

print("""
  THE LAST TWO ARE THE ONLY ONES THAT PROVE THE SUITE IS WORTH HAVING.

  A test suite that has never failed is a suite nobody has checked. This
  build breaks the package on purpose — one character, in one return
  statement — runs the tests, confirms they go red, and puts it back.

  Do that to your own suite once. If it stays green, you have written
  something that costs time to run and finds nothing.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 -m pytest tests/ -v` and read the parametrised test
#     names. Each one contains its own inputs.
#
#   * Delete strict=True from the xfail markers, "fix" as_shipped.py, and
#     watch the suite stay green while lying to you.
#
#   * Write the property test for `unique`: the output has no duplicates,
#     every element of the output is in the input, and the order matches
#     first appearance. Three assertions, no examples.
#
#   * mytoolkit.truncate() has no bug that these tests found. Spend ten
#     minutes trying to find one. Then add whatever you tried as a test,
#     passing, so the next person does not have to.
#
#   * On Day 58, replace the repeated `{"a": {"b": [10, 20]}}` in
#     test_dig_* with a fixture, and mock the clock in the @cache tests.
#
#   * On Day 60, run this with --cov and find out which lines of the
#     package no test has ever executed.
