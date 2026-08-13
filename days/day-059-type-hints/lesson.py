"""Day 059 — Type hints, and the checker that reads them.

    python3 lesson.py

This file writes small modules and runs mypy on them, so every error below
is one mypy actually produced. It takes a few seconds: a type checker reads
the whole standard library's stubs before it says anything.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

WIDTH = 76
WORK = Path(tempfile.mkdtemp(prefix="day059-"))


def check(source, *flags, name="demo.py"):
    """Write a module, run mypy on it, return the messages."""
    path = WORK / name
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, "-m", "mypy", str(path), "--no-color-output",
         "--cache-dir", str(WORK / ".mypy_cache"), *flags],
        capture_output=True, text=True, cwd=WORK,
    )
    text = finished.stdout + finished.stderr
    return [re.sub(r"^.*demo\.py:", "line ", line)
            for line in text.splitlines() if line.strip()]


def show(lines, indent="    "):
    for line in lines:
        print(f"{indent}{line[:WIDTH - len(indent)]}")


# ---------------------------------------------------------------------------
# 1. Annotations do nothing
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. THE INTERPRETER DOES NOT CARE':^{WIDTH}}")
print("=" * WIDTH)


def double(n: int) -> int:
    return n * 2


print(f"""
  def double(n: int) -> int:
      return n * 2

  double("ha")     -> {double("ha")!r}
  double([1, 2])   -> {double([1, 2])!r}

  BOTH RAN. Annotations are METADATA — Python stores them in
  __annotations__ and never checks them:

      {double.__annotations__}

  Nothing about type hints slows your program down or changes what it
  does. They exist for two readers: a HUMAN, and a CHECKER you run
  separately. If you never run the checker, hints are documentation that
  can quietly become wrong — which is worse than a comment, because it
  looks authoritative.""")


# ---------------------------------------------------------------------------
# 2. What mypy says about the same file
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. ...AND WHAT mypy SAYS ABOUT IT':^{WIDTH}}")
print("=" * WIDTH)

print("\n  Running mypy on exactly the code above:\n")
show(check('''
    def double(n: int) -> int:
        return n * 2

    double("ha")
    double([1, 2])
'''))

print("""
  Two errors, at your desk, in under a second, without running anything.
  That is the whole proposition: a class of bug moves from "found by a
  user" to "found by a command".""")


# ---------------------------------------------------------------------------
# 3. The syntax
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. THE SYNTAX, IN ONE SCREEN':^{WIDTH}}")
print("=" * WIDTH)
print('''
  name: str = "Ada"                   a variable
  count: int
  ratio: float                        int is acceptable where float is asked
  ok: bool
  nothing: None

  items: list[str]                    3.9+: lowercase builtins, no import
  pairs: dict[str, int]
  point: tuple[float, float]          exactly two
  row: tuple[str, ...]                any number, all str
  seen: set[int]
  maybe: str | None                   3.10+: instead of Optional[str]
  either: int | str                   instead of Union[int, str]

  def f(a: int, b: str = "x") -> bool: ...
  def g(*args: int, **kwargs: str) -> None: ...
  def h() -> None: ...                returns nothing — say so

  FROM collections.abc, FOR PARAMETERS:
      Iterable, Sequence, Mapping, Callable, Iterator

  THE RULE THAT MATTERS MOST:
      ACCEPT THE BROADEST THING THAT WORKS, RETURN THE MOST SPECIFIC.

      def summarise(rows: Iterable[str]) -> list[str]:

  ...accepts a list, a tuple, a set, a generator or a file, and promises
  the caller a real list they can index. `rows: list[str]` accepts one
  thing; `-> Iterable[str]` forces the caller to convert.''')

print("\n  What mypy does with the wrong container:\n")
show(check('''
    from collections.abc import Iterable, Sequence

    def wants_a_list(rows: list[str]) -> None: ...
    def wants_any_iterable(rows: Iterable[str]) -> None: ...

    wants_a_list(("a", "b"))            # a tuple
    wants_a_list(n for n in "ab")       # a generator
    wants_any_iterable(("a", "b"))      # fine
    wants_any_iterable(n for n in "ab") # fine

    def first(rows: Sequence[str]) -> str:
        return rows[0]

    first({"a", "b"})                   # a set has no [0]
'''))


# ---------------------------------------------------------------------------
# 4. Any is an off switch
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. Any IS NOT A TYPE. IT IS AN OFF SWITCH.':^{WIDTH}}")
print("=" * WIDTH)

print()
show(check('''
    from typing import Any

    def with_any(data: Any) -> int:
        return data.anything_at_all().nonsense[42] + "not a number"

    def with_object(data: object) -> int:
        return data.anything_at_all()
'''))

print("""
  THE FIRST FUNCTION IS NONSENSE AND mypy SAID NOTHING. `Any` means "stop
  checking", and it is contagious: everything an Any touches becomes
  unchecked too, so one Any in a signature can switch off a whole call
  chain.

  `object` is the honest version of "I do not know what this is". It
  accepts anything AND lets you do nothing with it until you narrow:

      if isinstance(data, str):
          return len(data)          <- mypy now knows it is a str

  WHEN Any IS RIGHT: a boundary where the data genuinely has no static
  shape — json.loads(), **kwargs forwarded to an untyped library, a
  plugin registry. Even then, narrow it as soon as you can and annotate
  what you narrowed it TO.

  `# type: ignore[error-code]` is the other escape hatch. With the code in
  brackets it is a targeted, greppable exception. Bare `# type: ignore`
  silences everything on that line forever, including the error you
  introduce next year.""")


# ---------------------------------------------------------------------------
# 5. Generics
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. WHEN THE ANSWER DEPENDS ON THE ARGUMENT':^{WIDTH}}")
print("=" * WIDTH)
print('''
  first(["a", "b"]) is a str. first([1, 2]) is an int. One signature has
  to say both:

      T = TypeVar("T")

      def first(items: Sequence[T]) -> T:
          return items[0]

  A TypeVar is a promise that two places hold the SAME type — here, the
  element type of the argument and the return type. Without it the honest
  return type is `object`, and the caller has to cast.

  BOUNDED, when the function needs the type to be able to do something:

      class Comparable(Protocol):
          def __lt__(self, other: object, /) -> bool: ...

      C = TypeVar("C", bound=Comparable)

      def clamp(value: C, low: C, high: C) -> C: ...

  That is the real signature of the toolkit's clamp(), and the Protocol is
  necessary because int, float, str, date and Decimal are all comparable
  and share no base class. Day 49 argued for structural typing; this is
  where it becomes checkable.''')

print("\n  The TypeVar keeping its promise, and catching a mixed call:\n")
show(check('''
    from collections.abc import Sequence
    from typing import TypeVar

    T = TypeVar("T")

    def first(items: Sequence[T]) -> T:
        return items[0]

    number: int = first([1, 2, 3])       # fine
    word: str = first([1, 2, 3])         # int is not str
    reveal_type(first(["a", "b"]))
'''))


# ---------------------------------------------------------------------------
# 6. Decorators
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. THE HARD ONE: DECORATORS':^{WIDTH}}")
print("=" * WIDTH)

print("\n  A decorator typed the lazy way, and what it costs:\n")
show(check('''
    from collections.abc import Callable
    from typing import Any, ParamSpec, TypeVar
    import functools

    def lazy(f: Callable[..., Any]) -> Callable[..., Any]:
        return f

    P = ParamSpec("P")
    R = TypeVar("R")

    def careful(f: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return f(*args, **kwargs)
        return wrapper

    @lazy
    def add_lazily(a: int, b: int) -> int:
        return a + b

    @careful
    def add_carefully(a: int, b: int) -> int:
        return a + b

    add_lazily("x", "y", "z", nonsense=True)     # not an error. It should be.
    add_carefully("x", "y")                      # caught
    add_carefully(1, 2, 3)                       # caught
'''))

print("""
  `Callable[..., Any]` on a decorator DELETES the signature of every
  function it decorates. That is why decorated functions used to lose
  their checking entirely, and why so much code has @decorator followed by
  a function nobody can call wrongly enough to be told about.

  ParamSpec (3.10) fixes it: P captures the whole parameter list and R the
  return type, so the wrapper is checked as if it were the original.
  Two lines, and @timer stops being a hole in your types.""")


# ---------------------------------------------------------------------------
# 7. The other useful ones
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. FOUR MORE THAT EARN THEIR KEEP':^{WIDTH}}")
print("=" * WIDTH)
print('''
  TypedDict          a dict with a KNOWN set of keys

      class CacheInfo(TypedDict):
          hits: int
          hit_rate: float

      info["hit_rate"]     checked
      info["hitrate"]      an error, at your desk

  Literal            one of a fixed set of VALUES

      def align(where: Literal["left", "right"]) -> str: ...
      align("centre")      an error

  Final              a name that must not be reassigned

      MAX_SIZE: Final = 128

  NewType            a distinct type with no runtime cost

      UserId = NewType("UserId", int)
      def load(user: UserId) -> None: ...
      load(42)             an error: 42 is an int, not a UserId

  ...and `from __future__ import annotations` at the top of a file makes
  every annotation a string, so a class can refer to itself and slow
  imports get cheaper. In 3.11 it is still opt-in.''')


# ---------------------------------------------------------------------------
# 8. Adopting it
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'8. TURNING IT ON, IN A CODEBASE THAT HAS NONE':^{WIDTH}}")
print("=" * WIDTH)
print("""
  NOT ALL AT ONCE. mypy is designed for gradual adoption, and the order
  that works is:

    1. mypy with no flags. It checks only what is already annotated, so
       the number it prints is your real starting point.
    2. Annotate the PUBLIC surface first — the functions other files call.
       That is where a wrong assumption costs the most.
    3. --disallow-untyped-defs, one package at a time.
    4. --strict, and a per-module override for anything not there yet.

  IN pyproject.toml, so nobody has to remember the flags:

      [tool.mypy]
      python_version = "3.11"
      strict = true

      [[tool.mypy.overrides]]
      module = ["tests.*"]
      disallow_untyped_defs = false

  AND SHIP py.typed. An empty file in your package (PEP 561) is the only
  thing that tells other people's type checkers your annotations exist.
  Without it, every one of them treats your library as untyped and all
  this work is invisible downstream.""")


# ---------------------------------------------------------------------------
# 9. Types and tests
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'9. WHAT EACH ONE CATCHES':^{WIDTH}}")
print("=" * WIDTH)
print("""
  A TYPE CHECKER CATCHES              A TEST CATCHES
  a typo in an attribute name         a wrong answer
  a forgotten None case               an off-by-one
  a renamed parameter                 a boundary
  a call with the wrong arity         a rule you misunderstood
  an unreachable branch               a regression
  ...in every line, including the     ...only in the lines it runs
     ones no test reaches

  NEITHER REPLACES THE OTHER, and the division is sharp: mypy has no
  opinion about whether human_bytes(1048575) should say '1.0 MB' — Day 57
  needed a test for that. A test has no opinion about the eighty per cent
  of your code no test touches.

  RUN BOTH, in one line, so neither is optional:

      pytest -q && ruff check && mypy""")

print()
print("=" * WIDTH)
print("""  1. Annotations are metadata. Nothing checks them unless you run mypy.
  2. list[str], dict[str, int], str | None. No typing imports needed.
  3. Accept Iterable, return list.
  4. Any switches checking OFF. `object` is the honest version.
  5. TypeVar when the answer's type depends on the argument's.
  6. ParamSpec, or your decorators erase every signature they touch.
  7. TypedDict, Literal, Final, NewType — small, and each catches a class
     of mistake.
  8. Adopt gradually, configure in pyproject.toml, ship py.typed.
  9. Types and tests catch different things. Run both.""")
print("=" * WIDTH)

shutil.rmtree(WORK, ignore_errors=True)


# ---------------------------------------------------------------------------
# Now try it
# ---------------------------------------------------------------------------
#
#   * Annotate one module of your own and run mypy with no flags. Then with
#     --strict. The gap between the two numbers is the work.
#
#   * Put `Any` on a parameter and write nonsense with it. Then change it
#     to `object` and read what mypy says instead.
#
#   * Type a decorator as Callable[..., Any], apply it, and call the
#     decorated function with the wrong arguments. Then use ParamSpec.
#
#   * Use reveal_type(x) — a mypy-only builtin — to ask the checker what it
#     thinks something is. It is the print() of type debugging.
#
#   * Add `-> None` to a function that returns a value and watch mypy find
#     every caller that used it.
