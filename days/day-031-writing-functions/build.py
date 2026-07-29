"""Day 031 build — exercising the toolkit.

    python3 build.py

The library itself is toolkit.py. This file is its first CONSUMER, and that
is the point: writing the caller is how you find out whether the API is any
good. Two things about toolkit.py were changed after writing this file, and
both are noted at the bottom.
"""

import doctest

import toolkit

WIDTH = 74


def demo(title, rows):
    print()
    print("-" * WIDTH)
    print(title)
    print("-" * WIDTH)
    for call, result in rows:
        print(f"  {call:<44}{result!r:>26}")


print("=" * WIDTH)
print(f"{'TOOLKIT — TEN UTILITIES':^{WIDTH}}")
print("=" * WIDTH)

# ---------------------------------------------------------------------------

demo("clamp(value, low, high) — keep a number inside a range", [
    ("clamp(15, 0, 10)", toolkit.clamp(15, 0, 10)),
    ("clamp(-3, 0, 10)", toolkit.clamp(-3, 0, 10)),
    ("clamp(0.5, 0, 1)", toolkit.clamp(0.5, 0, 1)),
])
print("  Used for: progress bars, percentages, anything with a valid range.")

demo("percent(part, whole) — a share, safe when whole is zero", [
    ("percent(1, 4)", toolkit.percent(1, 4)),
    ("percent(1, 3, places=2)", toolkit.percent(1, 3, places=2)),
    ("percent(5, 0)", toolkit.percent(5, 0)),
])
print("  Note it returns 'n/a' rather than raising: an empty dataset is a")
print("  normal state for a report, not a programmer error.")

demo("human_bytes(count) — file sizes people can read", [
    ("human_bytes(512)", toolkit.human_bytes(512)),
    ("human_bytes(2048)", toolkit.human_bytes(2048)),
    ("human_bytes(1_500_000_000)", toolkit.human_bytes(1_500_000_000)),
    ("human_bytes(0)", toolkit.human_bytes(0)),
])

demo("duration(seconds) — h:mm:ss, dropping the hours when they are zero", [
    ("duration(75)", toolkit.duration(75)),
    ("duration(3725)", toolkit.duration(3725)),
    ("duration(0)", toolkit.duration(0)),
    ("duration(86399)", toolkit.duration(86399)),
])

demo("truncate(text, limit) — limit INCLUDES the suffix", [
    ("truncate('Hello, world', 8)", toolkit.truncate("Hello, world", 8)),
    ("truncate('Hi', 8)", toolkit.truncate("Hi", 8)),
    ("truncate('abcdefghij', 5)", toolkit.truncate("abcdefghij", 5)),
    ("truncate('abc', 2)", toolkit.truncate("abc", 2)),
])
print("  'limit includes the suffix' is the decision that makes this usable")
print("  in a fixed-width column. The docstring says so, because the other")
print("  choice is equally defensible and the caller cannot guess.")

demo("slugify(text) — URL-safe identifiers", [
    ("slugify('Hello, World!')", toolkit.slugify("Hello, World!")),
    ("slugify('  Day 31: Functions  ')", toolkit.slugify("  Day 31: Functions  ")),
    ("slugify('!!!')", toolkit.slugify("!!!")),
])

demo("initials(name) — Day 3's build, finally reusable", [
    ("initials('Ada Augusta Byron King')", toolkit.initials("Ada Augusta Byron King")),
    ("initials('prince')", toolkit.initials("prince")),
    ("initials('   ')", toolkit.initials("   ")),
])
print("  Day 3 needed 60 lines and could not handle a one-word name. The")
print("  difference is not cleverness — it is .split() plus a function.")

demo("chunked(items, size) — batching", [
    ("chunked([1,2,3,4,5], 2)", toolkit.chunked([1, 2, 3, 4, 5], 2)),
    ("chunked([], 3)", toolkit.chunked([], 3)),
    ("chunked(range(7), 3)", toolkit.chunked(range(7), 3)),
])
print("  Takes any iterable, not just a list — because it calls list()")
print("  first. That one line is why range() works here.")

demo("unique(items) — dedupe, keeping order", [
    ("unique([3,1,3,2,1])", toolkit.unique([3, 1, 3, 2, 1])),
    ("unique('abracadabra')", toolkit.unique("abracadabra")),
])

demo("dig(data, *keys) — Day 28, kept", [
    ("dig({'a': {'b': [10, 20]}}, 'a', 'b', 1)",
     toolkit.dig({"a": {"b": [10, 20]}}, "a", "b", 1)),
    ("dig({'a': 1}, 'a', 'b', default='-')",
     toolkit.dig({"a": 1}, "a", "b", default="-")),
    ("dig(None, 'a', default=0)", toolkit.dig(None, "a", default=0)),
])

# ---------------------------------------------------------------------------
# They compose — which is the whole reason they return instead of printing
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'THEY COMPOSE':^{WIDTH}}")
print("=" * WIDTH)

FILES = [
    {"name": "Quarterly Report: Final Version (2024).pdf", "bytes": 4_812_004,
     "seconds": 3725},
    {"name": "notes.txt", "bytes": 812, "seconds": 12},
    {"name": "Very Long Presentation About Nothing.pptx", "bytes": 91_000_000,
     "seconds": 604},
]

total_bytes = sum(f["bytes"] for f in FILES)

print(f"  {'FILE':<34}{'SIZE':>12}{'SHARE':>10}{'TIME':>10}  {'SLUG':<0}")
print("  " + "-" * (WIDTH - 4))
for f in FILES:
    print(f"  {toolkit.truncate(f['name'], 32):<34}"
          f"{toolkit.human_bytes(f['bytes']):>12}"
          f"{toolkit.percent(f['bytes'], total_bytes):>10}"
          f"{toolkit.duration(f['seconds']):>10}")
    print(f"  {'':<34}{toolkit.slugify(f['name'])[:38]}")

print("  " + "-" * (WIDTH - 4))
print(f"  {'TOTAL':<34}{toolkit.human_bytes(total_bytes):>12}")

print(f"""
  Four utilities in one f-string, each returning a string that the next
  thing can use. None of them printed anything. That is the difference
  between a library and a script.""")

# ---------------------------------------------------------------------------
# The library tests itself
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
result = doctest.testmod(toolkit, verbose=False)
print(f"{'doctests run':<40}{result.attempted:>{WIDTH - 40}}")
print(f"{'failed':<40}{result.failed:>{WIDTH - 40}}")
print(f"{'library is self-verifying':<40}"
      f"{str(result.failed == 0 and result.attempted > 0):>{WIDTH - 40}}")
print("=" * WIDTH)

# ---------------------------------------------------------------------------
# The errors it raises ON PURPOSE
# ---------------------------------------------------------------------------

print()
print("WHAT IT REFUSES TO DO")
print("-" * WIDTH)
for label, call in [
    ("clamp(5, 10, 0)  — range is inside out", lambda: toolkit.clamp(5, 10, 0)),
    ("chunked([1,2], 0) — size below 1", lambda: toolkit.chunked([1, 2], 0)),
]:
    try:
        call()
        print(f"  {label:<44}(no error — should there be?)")
    except ValueError as e:
        print(f"  {label:<44}ValueError: {e}")

print("""
  Both of those are PROGRAMMER errors, not user input, so they raise rather
  than returning something plausible. percent(5, 0) does the opposite and
  returns 'n/a', because an empty dataset is a normal state for a report.

  Deciding which of those two a given failure is — bug or expected state —
  is most of API design, and Day 52 gives it a proper vocabulary.""")


# ---------------------------------------------------------------------------
# What writing this file changed about the library
# ---------------------------------------------------------------------------
#
#   1. truncate() originally counted the limit WITHOUT the suffix, so
#      truncate(name, 32) could return 35 characters and break the column
#      above. Using it in a table is what exposed that; reading the
#      function never would have.
#
#   2. chunked() originally indexed `items` directly, so chunked(range(7), 3)
#      worked but chunked(generator, 3) silently returned []. Adding
#      list(items) fixed it.
#
#   THE LESSON: WRITE THE CALLER TO FIND OUT WHETHER THE API IS ANY GOOD.
#   On Day 57 pytest replaces this file, and it will find a third one.
#
# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add two utilities of your own that you have already hand-written twice
#     in this course. Give each a docstring and at least two doctests.
#
#   * `dig` has a signature the others do not: *keys and a keyword-only
#     default. Day 32 and 33 explain why, and you will come back and make
#     the whole library's signatures deliberate.
#
#   * Break one doctest on purpose and run `python3 -m doctest toolkit.py`.
#     Read the failure format — it is the ancestor of everything on Day 57.
