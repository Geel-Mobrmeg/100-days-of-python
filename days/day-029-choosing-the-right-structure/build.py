"""Day 029 build — benchmark membership across a list, a set and a dict.

    python3 build.py

Three structures, three sizes, three lookup positions. The numbers are not
the point; THE SHAPE OF THE CURVE is the point, and the program prints the
growth ratios so the shape is visible rather than inferred.

The key question to answer for yourself before reading the output:

    when the data gets 10 times bigger, what happens to each column?
"""

import gc
import sys
import timeit

WIDTH = 76
SIZES = (1_000, 10_000, 100_000)
REPEATS = 2_000


def bench(callable_, number):
    """Time a callable, with the garbage collector out of the way."""
    gc.disable()
    try:
        return timeit.timeit(callable_, number=number)
    finally:
        gc.enable()


print("=" * WIDTH)
print(f"{'MEMBERSHIP BENCHMARK':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'lookups timed per measurement':<44}{REPEATS:>{WIDTH - 44},}")
print(f"{'sizes':<44}{', '.join(f'{s:,}' for s in SIZES):>{WIDTH - 44}}")
print(f"{'python':<44}{sys.version.split()[0]:>{WIDTH - 44}}")

# ===========================================================================
# 1. THE WORST CASE: an item that is NOT THERE.
#
# This is the honest comparison. A missing item forces a list to scan every
# single element before it can say no — there is no early exit. Benchmark
# rule 2: measure the worst case.
# ===========================================================================

print()
print("-" * WIDTH)
print("1. WORST CASE — looking for something that is NOT PRESENT")
print("-" * WIDTH)
print(f"{'SIZE':>9}{'list (s)':>12}{'set (s)':>12}{'dict (s)':>12}"
      f"{'set speedup':>14}{'x10 list':>13}")

previous_list = None
rows = []

for size in SIZES:
    data_list = list(range(size))
    data_set = set(data_list)
    data_dict = dict.fromkeys(data_list)
    missing = -1                      # guaranteed absent from all three

    t_list = bench(lambda: missing in data_list, REPEATS)
    t_set = bench(lambda: missing in data_set, REPEATS)
    t_dict = bench(lambda: missing in data_dict, REPEATS)

    growth = f"{t_list / previous_list:>12.1f}x" if previous_list else f"{'-':>13}"
    previous_list = t_list

    rows.append((size, t_list, t_set, t_dict))
    print(f"{size:>9,}{t_list:>12.5f}{t_set:>12.6f}{t_dict:>12.6f}"
          f"{t_list / t_set:>13.0f}x{growth}")

print("-" * WIDTH)
print("""READ THE LAST TWO COLUMNS.

  x10 list       every 10x more data costs the LIST about 10x more time.
                 That is O(n): the cost is proportional to the size.

  set speedup    grows with the data. It is not a fixed "sets are faster";
                 the GAP ITSELF widens, because the set column barely moves
                 at all. That flat line is O(1).

At 1,000 items the difference is a rounding error. At 100,000 it is the
difference between a program that responds and one that appears to hang.
Which is why "it was fast on my test data" is not evidence.""")

# ===========================================================================
# 2. BEST AND MIDDLE CASE FOR THE LIST — where the average comes from
# ===========================================================================

print()
print("-" * WIDTH)
print("2. WHERE THE ITEM IS, IN A LIST OF 100,000")
print("-" * WIDTH)

size = SIZES[-1]
data_list = list(range(size))
data_set = set(data_list)

positions = [
    ("first item", 0),
    ("1% in", size // 100),
    ("middle", size // 2),
    ("last item", size - 1),
    ("not present", -1),
]

print(f"{'POSITION':<16}{'list (s)':>12}{'set (s)':>12}{'ratio':>12}")
for label, target in positions:
    t_list = bench(lambda: target in data_list, REPEATS)
    t_set = bench(lambda: target in data_set, REPEATS)
    print(f"{label:<16}{t_list:>12.6f}{t_set:>12.6f}{t_list / t_set:>11.0f}x")

print("""
A list scans from the front and STOPS at a match, so "first item" is fast
and tells you nothing. "Last item" and "not present" are the same cost, and
that cost is the honest one. The set does not care where the item is,
because it never looks — it computes a hash and jumps.

This is also why a benchmark that happens to query popular items reports
numbers a production system will never see.""")

# ===========================================================================
# 3. THE COST OF BUILDING THE SET — because it is not free
# ===========================================================================

print()
print("-" * WIDTH)
print("3. IS BUILDING THE SET WORTH IT? — the break-even point")
print("-" * WIDTH)

size = 50_000
data_list = list(range(size))
build_time = bench(lambda: set(data_list), 20) / 20
one_list_lookup = bench(lambda: -1 in data_list, 200) / 200
one_set_lookup = bench(lambda: -1 in set([1]), 200) / 200

break_even = build_time / max(one_list_lookup - one_set_lookup, 1e-12)

print(f"{'building a set of ' + f'{size:,}':<40}{build_time * 1000:>10.3f} ms")
print(f"{'one failed lookup in the list':<40}{one_list_lookup * 1000:>10.4f} ms")
print(f"{'one failed lookup in a set':<40}{one_set_lookup * 1000:>10.6f} ms")
print(f"{'break-even, in lookups':<40}{break_even:>10.1f}")
print(f"""
Build it once and it pays for itself after about {break_even:.0f} lookups. Below
that, the list is fine. This is why "always use a set" is bad advice and
"use a set when you will look things up repeatedly" is good advice.

It is also exactly why rebuilding the set INSIDE the loop is a bug: you pay
the build cost on every single iteration and never reach break-even.""")

# ===========================================================================
# 4. WHAT IT COSTS IN MEMORY
# ===========================================================================

print()
print("-" * WIDTH)
print("4. WHAT YOU PAY FOR IT")
print("-" * WIDTH)

size = 100_000
data_list = list(range(size))
data_set = set(data_list)
data_dict = dict.fromkeys(data_list)
data_tuple = tuple(data_list)

print(f"{'STRUCTURE':<14}{'BYTES':>16}{'RELATIVE':>12}")
base = sys.getsizeof(data_list)
for label, obj in [
    ("tuple", data_tuple), ("list", data_list),
    ("set", data_set), ("dict", data_dict),
]:
    n = sys.getsizeof(obj)
    print(f"{label:<14}{n:>16,}{n / base:>11.1f}x")

print("""
(getsizeof measures the container, not the integers inside it, which are
shared. The ratio is the useful part.)

A set costs roughly 3-4x the memory of a list to make lookups constant.
That is a trade, and it is usually an obviously good one — but on data that
does not fit in memory it is the wrong way round, and then you want a
database index (Day 78) rather than a bigger set.""")

# ===========================================================================
# 5. THE ACCIDENTAL O(n^2), AND ITS ONE-LINE FIX
# ===========================================================================

print()
print("-" * WIDTH)
print("5. THE SAME PROGRAM, TWICE")
print("-" * WIDTH)

print(f"{'n':>8}{'nested (s)':>14}{'with set (s)':>14}"
      f"{'speedup':>12}{'x2 nested':>12}")

previous = None
for n in (1_000, 2_000, 4_000, 8_000):
    a = [f"id{i}" for i in range(n)]
    b = [f"id{i}" for i in range(n // 2, n + n // 2)]

    def nested():
        return sum(1 for x in a if x in b)

    def with_set():
        seen = set(b)
        return sum(1 for x in a if x in seen)

    t_nested = bench(nested, 1)
    t_set = bench(with_set, 1)
    doubling = f"{t_nested / previous:>10.1f}x" if previous else f"{'-':>11}"
    previous = t_nested

    print(f"{n:>8,}{t_nested:>14.5f}{t_set:>14.5f}"
          f"{t_nested / t_set:>11.0f}x{doubling}")

print("-" * WIDTH)
print("""DOUBLE n AND THE NESTED VERSION TAKES ABOUT FOUR TIMES AS LONG.

That is the signature of O(n^2), and it is the single most useful thing to
be able to recognise in a timing table. The set version roughly doubles,
which is O(n).

The fix was one line:

    seen = set(b)

and the answer is identical. No cleverness, no algorithm — just knowing
that `in` on a list scans and `in` on a set does not.""")

print()
print("=" * WIDTH)
print(f"{'SUMMARY':^{WIDTH}}")
print("=" * WIDTH)
print("""  looking things up repeatedly? .................. set or dict
  need order, duplicates, or position? ........... list
  a fixed record, or a key? ...................... tuple
  n under a few hundred? ......................... it does not matter
  unsure? ........................................ measure it""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add 1,000,000 to SIZES. The list column grows another 10x; the set
#     column does not move. Expect it to take a minute.
#
#   * Replace the integers with strings. Hashing a string costs more than
#     hashing a small int, so the set column rises a little — and the
#     conclusion does not change at all.
#
#   * Section 3 computes a break-even in lookups. Verify it: run the loop
#     with exactly that many lookups both ways and confirm the times meet.
#
#   * Section 5 uses lists of strings. Try it with lists of DICTS, which are
#     unhashable, and work out what you would do instead. (Key on one field.)
#
#   * Take the O(n^2) dedupe from Day 22's build and fix it here. Then go
#     back and fix it there.
