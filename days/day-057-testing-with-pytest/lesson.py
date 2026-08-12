"""Day 057 — pytest: assert, and about six other things.

    python3 lesson.py

This file WRITES small test files into a temporary directory and RUNS
pytest on them, so every piece of output below is real. Nothing is quoted
from memory.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

WIDTH = 76
WORK = Path(tempfile.mkdtemp(prefix="day057-"))


def run_pytest(source, *flags, name="test_demo.py"):
    """Write a test file, run pytest on it, return the output."""
    path = WORK / name
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", str(path), "-p", "no:cacheprovider",
         *flags],
        capture_output=True, text=True, cwd=WORK,
    )
    text = finished.stdout + finished.stderr
    return re.sub(r"^(rootdir|plugins|platform|configfile).*\n", "",
                  text, flags=re.MULTILINE)


def show(output, first=None, last=None, indent="    "):
    lines = [ln for ln in output.splitlines() if ln.strip()]
    chosen = lines[:first] if first else lines
    if last:
        chosen = lines[-last:]
    for line in chosen:
        print(f"{indent}{line[:WIDTH - len(indent)]}")


# ---------------------------------------------------------------------------
# 1. assert is the whole API
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. THE FAILURE REPORT IS THE FEATURE':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    def totals(rows):
        return {"count": len(rows), "sum": sum(rows)}

    def test_totals():
        assert totals([1, 2, 3]) == {"count": 3, "sum": 7}
''', "-q", "--tb=long", "--no-header")

print("\n  ONE plain `assert`, and this is what pytest prints:\n")
show(output, first=14)

print("""
  There is no assertEqual, assertIn, assertGreater or assertAlmostEqual to
  learn. pytest REWRITES the assert statement as it imports your file, so
  a bare `==` reports both sides, and a dict comparison reports the
  differing key.

  `assert a == b` with the standard library's `unittest` prints
  "AssertionError" and nothing else. That difference is most of why pytest
  won.""")


# ---------------------------------------------------------------------------
# 2. Discovery
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. HOW pytest FINDS YOUR TESTS':^{WIDTH}}")
print("=" * WIDTH)
print("""
  FILES        test_*.py  or  *_test.py
  FUNCTIONS    test_*
  CLASSES      Test*  (with no __init__)
  WHERE        the directory you point it at, recursively

  That is the entire rule. No registration, no suite object, no
  inheritance. A file of functions named test_something IS a test suite.

  THE LAYOUT THAT WORKS:

      myproject/
        mypackage/
          __init__.py
        tests/
          test_numbers.py
          test_text.py
        conftest.py          <- pytest's own config; also puts its
        pyproject.toml          directory on sys.path

  Keep tests OUT of the package. They are not something a user installs,
  and they should import the package the same way a user would — which is
  also how you find out that your package cannot actually be imported.""")


# ---------------------------------------------------------------------------
# 3. Arrange, act, assert
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. THE SHAPE OF ONE TEST':^{WIDTH}}")
print("=" * WIDTH)
print('''
      def test_clamp_pulls_a_value_above_the_range_down_to_the_top():
          value, low, high = 15, 0, 10        # ARRANGE
          result = clamp(value, low, high)    # ACT   — exactly one call
          assert result == 10                 # ASSERT — exactly one claim

  THREE RULES, AND THE THIRD IS THE ONE PEOPLE BREAK:

    1. THE NAME IS A SENTENCE. When it fails, the report says
       `test_clamp_pulls_a_value_above_the_range_down_to_the_top` and you
       already know what broke. `test_clamp_2` tells you nothing.

    2. ONE ACT. If the test calls the thing under test three times, a
       failure does not say which call was wrong.

    3. ONE CLAIM. Six asserts in a test means the first failure hides the
       other five, and you fix them one run at a time.

  A TEST HAS NO BRANCHES. No if, no loops over cases (parametrize instead),
  no try/except. If a test needs logic to decide what is correct, that
  logic can be wrong, and nothing tests it.''')


# ---------------------------------------------------------------------------
# 4. Errors and floats
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. TESTING WHAT SHOULD GO WRONG':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    import pytest

    def clamp(value, low, high):
        if low > high:
            raise ValueError(f"low ({low}) is above high ({high})")
        return max(low, min(value, high))

    def test_an_inverted_range_raises():
        with pytest.raises(ValueError):
            clamp(5, 10, 0)

    def test_the_message_names_both_numbers():
        with pytest.raises(ValueError, match=r"low \\(10\\) is above"):
            clamp(5, 10, 0)

    def test_the_exception_object_is_available():
        with pytest.raises(ValueError) as caught:
            clamp(5, 10, 0)
        assert "10" in str(caught.value)

    def test_floats_need_approx():
        assert 0.1 + 0.2 == pytest.approx(0.3)
''', "-q", "--no-header")

print()
show(output, last=3)
print("""
      with pytest.raises(ValueError):              it raised, and the type
      with pytest.raises(ValueError, match=r"..."):  ...and the message
      as caught:  caught.value is the exception    ...and its attributes

  `match` takes a REGULAR EXPRESSION and searches (not matches), so escape
  your brackets. Testing the message is testing the contract: Day 52 spent
  a page arguing the message is part of the interface, and this is where
  that claim gets enforced.

      assert 0.1 + 0.2 == 0.3                      FAILS
      assert 0.1 + 0.2 == pytest.approx(0.3)       passes

  Never compare floats with ==. approx() takes rel= and abs= when the
  default tolerance is wrong.""")


# ---------------------------------------------------------------------------
# 5. parametrize
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. ONE TEST, MANY CASES':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    import pytest

    def duration(seconds):
        seconds = int(seconds)
        hours, rest = divmod(seconds, 3600)
        minutes, secs = divmod(rest, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @pytest.mark.parametrize("seconds, expected", [
        (0, "0:00"),
        (59, "0:59"),
        (60, "1:00"),
        (3599, "59:59"),
        (3600, "1:00:00"),
        (-5, "-0:05"),
    ])
    def test_duration(seconds, expected):
        assert duration(seconds) == expected
''', "-v", "--no-header", "--tb=no")

print()
interesting = [ln for ln in output.splitlines()
               if "::" in ln or "passed" in ln or "failed" in ln]
show("\n".join(interesting))

print("""
  SIX TESTS FROM ONE FUNCTION, each named after its own inputs, each
  passing or failing independently. Compare with the loop people write
  instead:

      def test_duration():
          for seconds, expected in cases:
              assert duration(seconds) == expected     <- stops at the first

  The loop reports ONE failure and hides the rest. The parametrised version
  reported five passes and one failure, and the failure's name contains the
  input that caused it.

  Stack the decorator to get a grid — two parametrize decorators with three
  cases each run nine tests, which is how today's suite runs the same four
  bug assertions against two different modules.""")


# ---------------------------------------------------------------------------
# 6. Markers
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. SKIP, AND THE ONE WORTH LEARNING':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    import sys
    import pytest

    @pytest.mark.skip(reason="not written yet")
    def test_something_planned():
        assert False

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
    def test_on_posix_only():
        assert True

    @pytest.mark.xfail(strict=True, reason="known bug, ticket #412")
    def test_a_known_bug():
        assert 1024 * 1024 - 1 == 0

    @pytest.mark.xfail(strict=True, reason="this one was FIXED")
    def test_that_now_passes():
        assert True
''', "-q", "--no-header", "--tb=line")

print()
show(output, last=6)
print("""
  READ THE LAST TWO LINES. The fourth test PASSED, and pytest reports the
  run as FAILED — because the marker said it should fail and it did not.

  That is what strict=True buys. A non-strict xfail on a bug somebody has
  since fixed stays green forever, and the marker rots into a lie.

    skip        "this cannot run here" — a missing dependency
    skipif      the same, conditionally
    xfail       "this SHOULD pass and does not, and I know why"
                Always with strict=True and always with a reason.

  DO NOT SKIP A TEST BECAUSE IT FAILS. That is deleting the test with extra
  steps. xfail it, with the ticket number in the reason, and the day it
  starts passing your suite tells you.""")


# ---------------------------------------------------------------------------
# 7. Running it
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. THE FLAGS YOU WILL ACTUALLY USE':^{WIDTH}}")
print("=" * WIDTH)
print("""
  pytest                      everything, from the project root
  pytest tests/test_text.py   one file
  pytest -k "slug"            every test whose NAME matches
  pytest -x                   stop at the first failure
  pytest --lf                 only what failed last time
  pytest -q  /  -v            quieter / one line per test
  pytest --tb=short           shorter tracebacks (line, long, no)
  pytest -s                   let print() through (it is captured by
                              default, and shown only for failures)

  THE LOOP THAT WORKS:  pytest -x --lf   until green, then plain pytest.

  ...and the one that matters most in a repository:

      pytest -q  &&  ruff check  &&  mypy

  three commands, in a Makefile or a CI file (Day 96), so nobody has to
  remember them.""")


# ---------------------------------------------------------------------------
# 8. What to test
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'8. WHAT TO TEST, WHEN YOU HAVE TWENTY MINUTES':^{WIDTH}}")
print("=" * WIDTH)
print("""
  IN THIS ORDER:

    1. THE HAPPY PATH, once. It is the cheapest test and the least likely
       to find anything.
    2. THE BOUNDARIES. 0, 1, the limit, the limit minus one, the limit plus
       one. Today's suite found a real bug at 1024*1024 - 1.
    3. THE EMPTY CASE. Empty list, empty string, zero, None.
    4. THE ERROR CASE. What SHOULD raise, and with what message.
    5. THE PROPERTY. Not "chunked([1..5], 2) == [[1,2],[3,4],[5]]" but
       "flattening the chunks gives the input back, for every size" —
       which is one test covering forty cases you did not think of.

  A GOOD TEST FAILS WHEN THE CODE IS WRONG AND ONLY THEN. Two ways to be
  useless:

    * it never fails               (asserts something trivially true, or
                                    asserts nothing at all)
    * it fails when the code is
      still correct                (depends on dict ordering, the clock,
                                    the network, or another test)

  THE CHECK THAT COSTS NOTHING: break the code on purpose and confirm the
  test goes red. A test you have never seen fail is a test you have not
  finished writing.""")

print()
print("=" * WIDTH)
print("""  1. Plain `assert`. The rewritten failure report is the feature.
  2. test_*.py, test_*, and nothing else to learn.
  3. One act, one claim, a name that is a sentence.
  4. pytest.raises for errors, with match= for the message.
  5. pytest.approx for floats.
  6. parametrize instead of a loop: N independent, individually named runs.
  7. xfail(strict=True) with a reason. Never skip a failing test.
  8. Boundaries, empties, errors, properties — in that order.
  9. See every test fail once.""")
print("=" * WIDTH)

shutil.rmtree(WORK, ignore_errors=True)


# ---------------------------------------------------------------------------
# Now write some
# ---------------------------------------------------------------------------
#
#   * Take a function you wrote before Day 40 and write four tests: happy
#     path, boundary, empty, error. Time how long the boundary one takes to
#     find something.
#
#   * Convert a loop-over-cases test to @parametrize and break one case.
#     Compare the two failure reports.
#
#   * Write a test with two asserts, break both, and count how many runs it
#     takes to learn everything that is wrong.
#
#   * Add xfail(strict=True) to a test of a bug, then fix the bug without
#     touching the test. Your suite should go red.
#
#   * Run `pytest -k` with a substring and watch it select across files.
