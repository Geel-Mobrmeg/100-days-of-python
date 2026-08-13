"""Day 059 build — the toolkit, annotated, at mypy --strict with no Any.

    python3 build.py

THE BRIEF: annotate the whole package and drive mypy to zero errors
WITHOUT using Any as an escape.

The package is Day 40's, which Day 57 fixed and Day 58 leaned on. Day 39
still holds the same code UNANNOTATED, so the before and after below are
two real directories rather than a remembered number.

    day-039/mytoolkit    the same functions, no annotations
    day-040/mytoolkit    annotated, py.typed, version 1.2.0

WHAT THE ANNOTATION ACTUALLY REQUIRED — none of it is decoration:

    a Protocol      because clamp() works on anything comparable, and
                    int, float, str, date and Decimal share no base class
    a TypeVar       because first-in/first-out of chunked() is the same
                    type, and `list[object]` would make callers cast
    a ParamSpec     because a decorator typed Callable[..., Any] deletes
                    the signature of every function it touches
    a TypedDict     because cache_info() returns a dict with known keys
    another
    Protocol        because @cache adds .cache_info() to the function it
                    returns, and until today NO TYPE SAID SO — which is a
                    gap in the API that 146 tests never noticed
"""

import ast
import shutil
import subprocess
import sys
import time
from pathlib import Path

WIDTH = 78
HERE = Path(__file__).resolve().parent
ANNOTATED = HERE.parent / "day-040-milestone-your-own-toolkit"
UNANNOTATED = HERE.parent / "day-039-modules-and-packages"
# Day 57's suite is the one that tests the rounding boundary; Day 40's own
# 32 tests never look at 1048575. The sabotage below has to be run against
# the suite that would actually notice it, or the comparison is rigged.
DAY_57 = HERE.parent / "day-057-testing-with-pytest"

sys.path.insert(0, str(ANNOTATED))


def mypy(target, *flags, cwd=None):
    started = time.perf_counter()
    finished = subprocess.run(
        [sys.executable, "-m", "mypy", str(target), "--no-color-output",
         "--cache-dir", "/tmp/day059-cache", *flags],
        capture_output=True, text=True, cwd=cwd or HERE,
    )
    output = finished.stdout + finished.stderr
    errors = [ln for ln in output.splitlines() if ": error:" in ln]
    return errors, output, time.perf_counter() - started


# ###########################################################################
# BEFORE AND AFTER
# ###########################################################################

print("=" * WIDTH)
print(f"{'THE SAME CODE, TWICE':^{WIDTH}}")
print("=" * WIDTH)

before, before_output, before_time = mypy("mytoolkit/", "--strict",
                                          cwd=UNANNOTATED)
after, after_output, after_time = mypy("mytoolkit/", "--strict",
                                       cwd=ANNOTATED)

print(f"\n  {'':<34}{'ERRORS':>9}{'SECONDS':>10}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'day 39 — the same functions':<34}{len(before):>9}{before_time:>9.1f}s")
print(f"  {'day 40 — annotated':<34}{len(after):>9}{after_time:>9.1f}s")
print("  " + "-" * (WIDTH - 4))

kinds: dict[str, int] = {}
for line in before:
    code = line.rsplit("[", 1)[-1].rstrip("]") if "[" in line else "?"
    kinds[code] = kinds.get(code, 0) + 1

print("\n  what --strict was complaining about before:")
for code, count in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print(f"    {code:<28}{count:>4}")

print("""
  MOST OF THAT IS `no-untyped-def` — "this function has no annotation" —
  which is the sound a checker makes when there is nothing to check. The
  interesting ones are the two at the bottom of the list, and they are in
  the next section.""")


# ###########################################################################
# THE SIGNATURES THAT REQUIRED A DECISION
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE SIX SIGNATURES THAT WERE NOT OBVIOUS':^{WIDTH}}")
print("=" * WIDTH)

interesting = [
    ("clamp", "def clamp(value: C, low: C, high: C) -> C",
     "C is bound to a Comparable Protocol. int, float, str, date and\n"
     "     Decimal all work and share no base class, so nominal typing\n"
     "     could not express this at all."),
    ("chunked", "def chunked(items: Iterable[T], size: int) -> list[list[T]]",
     "Iterable in (a generator works), list out (the caller can index).\n"
     "     T keeps the element type, so chunked(['a'], 1) is list[list[str]]."),
    ("unique", "def unique(items: Iterable[H]) -> list[H]",
     "H is bound to Hashable, because the implementation is\n"
     "     dict.fromkeys(). The bound is not decoration: it is the\n"
     "     precondition, finally written down."),
    ("dig", "def dig(data: object, *keys: object, default: object = None)\n"
            "         -> object",
     "`object`, not Any — the honest answer for something that walks\n"
     "     arbitrary nested data. The caller must narrow, which is correct:\n"
     "     dig() genuinely does not know what it found."),
    ("timer", "def timer(f: Callable[P, R]) -> Callable[P, R]   (+ overload)",
     "ParamSpec. Callable[..., Any] would erase the signature of every\n"
     "     decorated function. Two @overloads because @timer and\n"
     "     @timer(quiet=True) are different call shapes."),
    ("cache", "def cache(f: Callable[P, R]) -> Cached[P, R]",
     "Cached is a Protocol: callable, AND has cache_info() and\n"
     "     cache_clear(). See below — this one found something."),
]

for name, signature, why in interesting:
    print(f"\n  {name}")
    for line in signature.splitlines():
        print(f"     {line}")
    print(f"     -> {why}")


# ###########################################################################
# WHAT MYPY FOUND THAT 146 TESTS DID NOT
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE THING THE TESTS COULD NOT SEE':^{WIDTH}}")
print("=" * WIDTH)

gap = ANNOTATED / "_gap.py"
gap.write_text(
    "from mytoolkit import cache\n"
    "\n"
    "@cache\n"
    "def square(n: int) -> int:\n"
    "    return n * n\n"
    "\n"
    "square(4)\n"
    "print(square.cache_info()['hits'])\n"
    "print(square.cache_info()['hitrate'])\n",
    encoding="utf-8",
)
gap_errors, gap_output, _ = mypy("_gap.py", "--strict", cwd=ANNOTATED)

from mytoolkit import cache                                    # noqa: E402


@cache
def square(n: int) -> int:
    return n * n


square(4)
square(4)
runtime_info = square.cache_info()

print(f"""
  The package README has documented `square.cache_info()` since Day 40, and
  it works:

      {runtime_info}

  But until today no TYPE said so. @cache returned whatever
  functools.wraps produced, and mypy reported this at every call site:

      "function" has no attribute "cache_info"  [attr-defined]

  That is not a complaint about syntax. It is a real gap in the API: the
  documentation promised an attribute that the returned object's type did
  not have, so no caller could rely on it without a `# type: ignore`.

  THE FIX WAS A PROTOCOL, not a cast:

      class Cached(Protocol[P, R_co]):
          def __call__(self, *a: P.args, **k: P.kwargs) -> R_co: ...
          def cache_info(self) -> CacheInfo: ...
          def cache_clear(self) -> None: ...

  ...and CacheInfo is a TypedDict, so the KEYS are checked too. Here is
  mypy on a file that uses both, with one key misspelt:""")

print()
for line in gap_output.splitlines():
    if line.strip():
        print(f"    {line.replace(str(ANNOTATED) + '/', '')[:WIDTH - 6]}")

print("""
  `info['hits']` is fine and `info['hitrate']` is an error, on a dictionary,
  at your desk. No test in Day 57's suite could have found that typo —
  it would have been a KeyError at runtime, in whatever code path first
  asked for a hit rate.""")

gap.unlink(missing_ok=True)


# ###########################################################################
# NO Any
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE BRIEF SAID: WITHOUT USING Any':^{WIDTH}}")
print("=" * WIDTH)


def count_names(source, wanted):
    """Count uses of a NAME in real code — parsed, not grepped."""
    return sum(
        1 for node in ast.walk(ast.parse(source))
        if (isinstance(node, ast.Name) and node.id in wanted)
        or (isinstance(node, ast.Attribute) and node.attr in wanted)
    )


modules = sorted((ANNOTATED / "mytoolkit").glob("*.py"))
print(f"\n  {'MODULE':<24}{'LINES':>8}{'Any':>6}{'type: ignore':>15}"
      f"{'cast':>7}")
print("  " + "-" * (WIDTH - 4))
total_any = total_ignore = total_cast = 0
for path in modules:
    source = path.read_text(encoding="utf-8")
    anys = count_names(source, {"Any"})
    ignores = source.count("# type: ignore")
    casts = count_names(source, {"cast"})
    total_any += anys
    total_ignore += ignores
    total_cast += casts
    print(f"  {path.name:<24}{len(source.splitlines()):>8}{anys:>6}"
          f"{ignores:>15}{casts:>7}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'':<24}{'':>8}{total_any:>6}{total_ignore:>15}{total_cast:>7}")

print(f"""
  ZERO Any AND ZERO `# type: ignore` across {len(modules)} modules.

  THE ONE cast() IS HONEST AND WORTH LOOKING AT. @cache attaches two
  functions to its wrapper with setattr, which mypy cannot follow — a
  plain function object really does not have cache_info(). The cast on the
  return says "I have added them, and the Protocol above is the promise".

  A cast is a claim you are making that the checker cannot verify. One of
  them, next to the three lines that justify it, is a different thing from
  a file sprinkled with `# type: ignore`.""")


# ###########################################################################
# THE DIVISION OF LABOUR, DEMONSTRATED
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'TWO SABOTAGES, TWO DIFFERENT ALARMS':^{WIDTH}}")
print("=" * WIDTH)

numbers = ANNOTATED / "mytoolkit" / "numbers.py"
original = numbers.read_text(encoding="utf-8")


def with_sabotage(replacement):
    """Apply a change, run both checkers, put it back."""
    numbers.write_text(replacement, encoding="utf-8")
    try:
        errors, _, _ = mypy("mytoolkit/", "--strict", cwd=ANNOTATED)
        tests = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no",
             "-p", "no:cacheprovider", "--no-header"],
            capture_output=True, text=True, cwd=DAY_57,
        )
        return len(errors), " failed" in (tests.stdout + tests.stderr)
    finally:
        numbers.write_text(original, encoding="utf-8")
        shutil.rmtree(ANNOTATED / "mytoolkit" / "__pycache__",
                      ignore_errors=True)


# A WRONG ANSWER: the boundary Day 57 found, put back.
wrong_answer = original.replace(
    "        shown = abs(size) if index == 0 else round(abs(size), 1)",
    "        shown = abs(size)")
# A WRONG TYPE: a return that no test exercises differently.
wrong_type = original.replace(
    '    return f"{size:.1f} {units[index]}"',
    "    return round(size, 1)")

clean_mypy, clean_tests = mypy("mytoolkit/", "--strict",
                               cwd=ANNOTATED)[0], False
answer_mypy, answer_tests = with_sabotage(wrong_answer)
type_mypy, type_tests = with_sabotage(wrong_type)

print(f"\n  {'SABOTAGE':<38}{'mypy':>10}{'pytest':>12}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'none':<38}{len(clean_mypy):>7} err{'green':>12}")
print(f"  {'a wrong ANSWER (the rounding bug)':<38}{answer_mypy:>7} err"
      f"{'RED' if answer_tests else 'green':>12}")
print(f"  {'a wrong TYPE (returns float not str)':<38}{type_mypy:>7} err"
      f"{'RED' if type_tests else 'green':>12}")
print("  " + "-" * (WIDTH - 4))

print("""
  READ THE TWO ROWS. The rounding bug is invisible to mypy — '1024.0 KB'
  and '1.0 MB' are both perfectly good strings — and the tests catch it.
  The wrong return type is caught by BOTH here, because the tests compare
  against a string; in a function whose result is only passed along, it
  would be caught by mypy alone, in every line, including the ones no test
  reaches.

  THAT IS THE DIVISION, and it is why the answer is never "types instead
  of tests":

      mypy    every line, shallow    "this cannot be right"
      pytest  the lines it runs,     "this answer is wrong"
              deep""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

pyproject = (ANNOTATED / "pyproject.toml").read_text(encoding="utf-8")
init = (ANNOTATED / "mytoolkit" / "__init__.py").read_text(encoding="utf-8")
tests_pass = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no",
     "-p", "no:cacheprovider", "--no-header"],
    capture_output=True, text=True, cwd=ANNOTATED,
)
doctests = subprocess.run(
    [sys.executable, "-m", "pytest", "--doctest-modules", "mytoolkit/", "-q",
     "--tb=no", "-p", "no:cacheprovider", "--no-header"],
    capture_output=True, text=True, cwd=ANNOTATED,
)

annotated_defs = 0
unannotated_defs = 0
for path in modules:
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                unannotated_defs += 1
            else:
                annotated_defs += 1

claims = [
    ("mypy --strict finds nothing", len(after) == 0),
    ("...where the same code unannotated has dozens", len(before) > 25),
    ("every function has a return annotation", unannotated_defs == 0),
    ("no Any anywhere in the package", total_any == 0),
    ("no `# type: ignore` anywhere", total_ignore == 0),
    ("exactly one cast(), where setattr made it necessary", total_cast == 1),
    ("py.typed is present", (ANNOTATED / "mytoolkit" / "py.typed").exists()),
    ("...and is shipped in the wheel", "py.typed" in pyproject),
    ("mypy is configured in pyproject, not in anybody's shell",
     "[tool.mypy]" in pyproject and "strict = true" in pyproject),
    ("tests are exempted deliberately, and it says why",
     "tests.*" in pyproject),
    ("the version was bumped for the new capability",
     '__version__ = "1.2.0"' in init),
    ("the 32 tests still pass", " failed" not in tests_pass.stdout),
    ("the doctests still pass", " failed" not in doctests.stdout),
    ("cache_info() works at runtime, as it always did",
     runtime_info["hits"] == 1 and runtime_info["misses"] == 1),
    ("mypy catches a wrong TYPE", type_mypy > 0),
    ("...and is blind to a wrong ANSWER", answer_mypy == 0),
    ("...which the tests catch instead", answer_tests),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

print("""
  THE LAST THREE ARE THE ARGUMENT OF THE WHOLE DAY, stated as a
  measurement rather than an opinion: one sabotage is caught by mypy and
  not pytest, another by pytest and not mypy.

  Neither tool is a substitute for the other, and both are one command:

      pytest -q && ruff check && mypy""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change one parameter to `Any` and re-run mypy. It still says zero
#     errors, and it is now checking less. That silence is the danger.
#
#   * Delete py.typed and run mypy from a directory that imports the
#     package. Every annotation becomes invisible.
#
#   * Annotate day 58's bookings.py. `validate()` returns list[Problem] and
#     takes `now: datetime` — and the annotation makes the design decision
#     from that day visible in the signature.
#
#   * Type Day 50's inventory system. The frozen dataclasses annotate
#     themselves; Warehouse.stock_of() is the one that needs thought.
#
#   * Add a Literal["left", "right", "centre"] parameter to something and
#     misspell it at a call site.
#
#   * Run mypy on a file with `from __future__ import annotations` at the
#     top and one without. Then read what changed and decide.
