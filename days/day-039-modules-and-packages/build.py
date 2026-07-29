"""Day 039 build — using the package the way a consumer would.

    python3 build.py
    python3 -m mytoolkit

Day 31 gave you toolkit.py: ten functions in one flat file.
Day 37 added decorators.py next to it.
Today those became a package, and this file is the proof that the
reorganisation cost the CALLER nothing while buying quite a lot.
"""

import mytoolkit
from mytoolkit import cache, chunked, clamp, human_bytes, slugify, timer

WIDTH = 76

print("=" * WIDTH)
print(f"{'USING THE PACKAGE':^{WIDTH}}")
print("=" * WIDTH)

# ===========================================================================
# 1. The import surface
# ===========================================================================

print(f"{'package':<32}{mytoolkit.__name__:>{WIDTH - 32}}")
print(f"{'version':<32}{mytoolkit.__version__:>{WIDTH - 32}}")
print(f"{'public names':<32}{len(mytoolkit.__all__):>{WIDTH - 32}}")
print()
print(f"  {'NAME':<16}{'IMPORTED FROM':<24}{'ACTUALLY DEFINED IN':<28}")
print("  " + "-" * (WIDTH - 4))
for name in ["clamp", "slugify", "chunked", "timer"]:
    function = getattr(mytoolkit, name)
    print(f"  {name:<16}{'mytoolkit':<24}{function.__module__:<28}")

print("""
  Callers write `from mytoolkit import slugify` and never learn that it
  lives in text.py. That file could be split in two tomorrow — or renamed
  strings.py — and not one line of this build would change.

  THAT is what __init__.py buys. The alternative, where every caller writes
  `from mytoolkit.text import slugify`, welds your internal layout into
  everybody else's code.""")

# ===========================================================================
# 2. It all still works
# ===========================================================================

print()
print("-" * WIDTH)
print("2. THE SAME FUNCTIONS, UNCHANGED")
print("-" * WIDTH)

FILES = [
    ("Quarterly Report: Final (2024).pdf", 4_812_004),
    ("notes.txt", 812),
    ("Very Long Presentation About Nothing.pptx", 91_000_000),
]

total = sum(size for _, size in FILES)
for name, size in FILES:
    print(f"  {mytoolkit.truncate(name, 34):<36}"
          f"{human_bytes(size):>12}"
          f"{mytoolkit.percent(size, total):>10}")
    print(f"  {'':<36}{slugify(name)[:38]}")
print(f"  {'TOTAL':<36}{human_bytes(total):>12}")

print()
print(f"  chunked(range(9), 4)   {chunked(range(9), 4)}")
print(f"  clamp(15, 0, 10)       {clamp(15, 0, 10)}")
print(f"  dig(...)               "
      f"{mytoolkit.dig({'a': {'b': [1, 2]}}, 'a', 'b', 1)}")
print(f"  duration(3725)         {mytoolkit.duration(3725)}")

# ===========================================================================
# 3. Decorators and utilities, from ONE import
# ===========================================================================

print()
print("-" * WIDTH)
print("3. DECORATORS AND UTILITIES, FROM ONE PACKAGE")
print("-" * WIDTH)


@cache
@timer(quiet=True)
def expensive_slug(text):
    """Slugify, pretending to be slow."""
    return slugify(text * 40)


TITLES = ["Day 39: Modules", "Day 31: Functions", "Day 39: Modules",
          "Day 39: Modules"]
for title in TITLES:
    expensive_slug(title)

info = expensive_slug.cache_info()
print(f"  {len(TITLES)} calls, {info['misses']} distinct, "
      f"{info['hits']} cache hits ({info['hit_rate']:.0%})")
print(f"  timings recorded: {len(mytoolkit.decorators.TIMINGS)}")
print("""
  Before today these came from two separate files that the caller had to
  know about individually. Now `from mytoolkit import cache, timer,
  slugify` gets all three, and whether they share a file is nobody's
  business but the package's.""")

# ===========================================================================
# 4. What the package structure prevents
# ===========================================================================

print()
print("-" * WIDTH)
print("4. THE NAMING TRAP THIS PACKAGE AVOIDS")
print("-" * WIDTH)

import collections                              # noqa: E402 - the point

print(f"  the STDLIB collections: {collections.__file__.split('/')[-1]}")
print(f"  ours is called:         containers.py")
print(f"  Counter still works:    {collections.Counter('aab')}")
print("""
  chunked/unique/dig are collection helpers, so containers.py is a slightly
  awkward name. It is deliberate: a file called collections.py inside this
  package would shadow the standard library for EVERY module in it, and
  mytoolkit/decorators.py's `import functools` chain would start failing in
  ways that point at the wrong file entirely.

  The rule from lesson.py section 3, applied. Naming is not decoration.""")

# ===========================================================================
# 5. The package as a command
# ===========================================================================

print()
print("-" * WIDTH)
print("5. LIBRARY AND COMMAND, FROM THE SAME CODE")
print("-" * WIDTH)
print("""
  __main__.py makes this work:

      python3 -m mytoolkit

  and it is NOT imported by __init__.py, so none of that code runs when
  somebody does `from mytoolkit import slugify`. The same distinction as
  `if __name__ == "__main__":` in a single file, at package scale.

  It is how `python3 -m pytest`, `python3 -m http.server` and
  `python3 -m pip` all work. Try it now.""")

print()
print("=" * WIDTH)
print(f"""WHAT TODAY ACTUALLY CHANGED

  FOR THE CALLER      nothing. Every function behaves identically, and the
                      import line got SHORTER (one package, not two files).

  FOR THE AUTHOR      submodules can be split, renamed or reorganised
                      freely; __all__ says what is public; __init__.py is
                      the one place that decides the surface; and
                      `python3 -m mytoolkit` works.

  FOR DAY 97          this is already the shape pip expects. Publishing is
                      a pyproject.toml and a src/ directory away.

The reorganisation was worth doing at TWO files. At twelve it would have
been a rewrite.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add `print("init running")` to mytoolkit/__init__.py, then import
#     three different submodules in one script. It prints ONCE — that is
#     sys.modules caching, and it is why __init__.py must stay cheap.
#
#   * Rename text.py to strings.py and update ONLY __init__.py. This file
#     keeps working untouched. Now imagine having done that with forty
#     callers writing `from mytoolkit.text import slugify`.
#
#   * Add a mytoolkit/dates.py with one function, export it from
#     __init__.py, and note the total in `python3 -m mytoolkit` goes up
#     without you editing __main__.py — because it reads __all__.
#
#   * Try `python3 mytoolkit/__main__.py`. It fails with "attempted
#     relative import with no known parent package", because run that way
#     the file is __main__ and has no package to be relative TO. Then run
#     `python3 -m mytoolkit`, which works. Understanding why is
#     understanding packages.
#
#     Note `python3 mytoolkit/text.py` does NOT fail — text.py has no
#     relative imports, so there is nothing to resolve. The error is about
#     relative imports specifically, not about running package files.
#
#   * On Day 40 this gets a README, examples and a version policy. On
#     Day 97 it gets a pyproject.toml and goes to TestPyPI.
