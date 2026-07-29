"""Day 040 — Milestone techniques: what makes something a library.

No new syntax. This is about the difference between "code that works" and
"code somebody else can use", which is four things, none of them clever.

    python3 lesson.py
"""

import inspect

import mytoolkit

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. A PUBLIC SURFACE — the promise you are making
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("1. THE PUBLIC SURFACE")
print("=" * WIDTH)

public = [n for n in mytoolkit.__all__ if not n.startswith("__")]
everything = [n for n in dir(mytoolkit) if not n.startswith("_")]

print(f"{'names in __all__ (the promise)':<44}{len(public):>{WIDTH - 44}}")
print(f"{'names actually reachable':<44}{len(everything):>{WIDTH - 44}}")
print(f"{'internal, may change without warning':<44}"
      f"{len(everything) - len(public):>{WIDTH - 44}}")

print("""
The gap is the point. `mytoolkit.text` is reachable — Python has no private
— but it is not in __all__, so it is not promised. Callers who reach into
it are on their own, and you are free to rename it.

A LIBRARY IS A PROMISE ABOUT WHICH NAMES WILL KEEP WORKING. __all__ is
where you write the promise down. Without it, everything you ever wrote is
public by accident and you can never change any of it.""")


# ---------------------------------------------------------------------------
# 2. A DOCSTRING IS AN INTERFACE, NOT A COMMENT
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("2. DOCSTRINGS")
print("=" * WIDTH)

for name in ("truncate", "percent", "dig"):
    function = getattr(mytoolkit, name)
    first_line = (function.__doc__ or "").strip().splitlines()[0]
    signature = inspect.signature(function)
    print(f"  {name}{signature}")
    print(f"      {first_line}")

print("""
Each of those first lines says what the function RETURNS, in the
imperative, in one sentence. That is not a style preference:

  * If you cannot write it, the function does more than one thing.
  * It is what help() and every editor tooltip shows.
  * It is the contract. `truncate`'s says the limit INCLUDES the suffix —
    the other choice is equally defensible and the caller cannot guess, so
    not saying is a bug.""")


# ---------------------------------------------------------------------------
# 3. EXAMPLES THAT RUN
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("3. EXAMPLES THAT ARE ALSO TESTS")
print("=" * WIDTH)

print(inspect.getdoc(mytoolkit.chunked))

print("""
Those `>>>` lines are DOCTESTS. They are simultaneously:

    documentation   the first thing a reader looks for
    examples        copy-pasteable
    tests           `pytest --doctest-modules` runs them

and — the part that matters — THEY CANNOT GO STALE, because the test suite
fails the moment the documented behaviour changes. Prose documentation
rots silently; a doctest cannot.

This package has 28 of them and they run on every commit.""")


# ---------------------------------------------------------------------------
# 4. STATE THE LIMITS
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("4. KNOWN LIMITS")
print("=" * WIDTH)
print("""
The README has a section called "Known limits" listing five things this
package does badly or not at all — @cache needs hashable arguments,
slugify does not transliterate accents, human_bytes uses KB where KiB is
strictly correct.

Writing that section is uncomfortable and it is the most useful part of
the document, because:

  * Every one of those would otherwise be discovered as a BUG REPORT.
  * A limit you have written down is a DECISION. A limit you have not is
    an accident, and you will defend it out of embarrassment.
  * It tells a reader in thirty seconds whether this library is for them,
    which is the actual job of a README.

The test: can you name three things your code does badly? If not, you do
not know your code well enough to have shipped it.""")


# ---------------------------------------------------------------------------
# 5. THE FIVE DESIGN RULES, AND WHY EACH IS CHECKABLE
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("5. RULES YOU CAN CHECK BEAT RULES YOU CAN STATE")
print("=" * WIDTH)
print("""
  RULE                              HOW build.py VERIFIES IT

  1. return, never print            captures stdout during 5 calls and
                                    asserts it is empty
  2. never mutate an argument       passes a list, checks it afterwards
  3. raise on bugs, sentinel on     asserts clamp() raises and
     expected absence               percent(5, 0) returns 'n/a'
  4. docstring on everything        walks __all__ and checks __doc__
  5. no dependencies                PARSES the package with ast and
                                    compares imports to sys.stdlib_module_names

Rule 5's check was wrong the first time it ran: it grepped for lines
starting with "from " and matched the words "from here:" inside a
docstring, reporting a dependency that did not exist. A checker that cries
wolf gets switched off, and then it protects nothing — so it was rewritten
to parse the syntax tree.

THE GENERAL POINT: a README that says "no dependencies" and a check that
parses the imports are different KINDS of statement. Only one of them is
still true in six months.""")


# ---------------------------------------------------------------------------
# 6. VERSIONING IS A PROMISE ABOUT BREAKAGE
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("6. VERSIONING")
print("=" * WIDTH)
print(f"""
  mytoolkit is {mytoolkit.__version__}.

  MAJOR   incompatible change to anything in __all__
  MINOR   new functionality, existing calls unaffected
  PATCH   a fix that changes no documented behaviour

  Reaching 1.0.0 is not a celebration, it is a COMMITMENT: from here,
  changing what truncate() counts is a 2.0.0, not a tidy-up.

  Which is why __all__ matters so much. It is the exact list of things
  that a major version protects. Everything else — mytoolkit.text,
  mytoolkit.decorators.TIMINGS — can change on a patch release, because
  nobody was promised them.

  The version lives in TWO places (pyproject.toml and __init__.py) and
  build.py checks they agree, because they had already drifted once.""")


# ---------------------------------------------------------------------------
# 7. THE ACTUAL TEST OF A LIBRARY
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("""7. THE TEST

  Could somebody who has never met you install this, use it, and hit a
  wall without asking you a question?

    install         pip install -e .              (pyproject.toml)
    discover        python3 -m mytoolkit          (__main__.py)
    learn           README + docstrings           (documentation)
    try             examples/report.py            (a real use)
    trust           pytest, 32 tests + 28 doctests
    predict         Known limits, semantic versioning

  Every one of those is a file, not a virtue. That is the whole milestone:
  "library" is not a quality of the code, it is a set of artefacts sitting
  next to it.""")
print("=" * WIDTH)
