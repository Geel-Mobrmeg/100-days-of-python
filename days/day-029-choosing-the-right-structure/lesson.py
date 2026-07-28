"""Day 029 — Choosing the right structure.

    python3 lesson.py
"""

import sys
import timeit
from collections import deque

WIDTH = 72

# ---------------------------------------------------------------------------
# 1. The four containers, side by side
# ---------------------------------------------------------------------------

print("""
                list      tuple     dict        set
  ordered       yes       yes       insertion   NO
  mutable       yes       NO        yes         yes
  duplicates    yes       yes       keys unique NO
  by position   yes       yes       no          no
  x in c        O(n)      O(n)      O(1)        O(1)
  by key        O(n)      O(n)      O(1)        -
  append/add    O(1)      -         O(1)        O(1)
  insert front  O(n)      -         -           -
  dict key      no        YES       no          frozenset
""")

# ---------------------------------------------------------------------------
# 2. Big-O: how the cost GROWS. It says nothing about small inputs.
# ---------------------------------------------------------------------------

print(f"{'notation':<14}{'10x the data means':<26}{'example'}")
print("-" * WIDTH)
for notation, growth, example in [
    ("O(1)", "same cost", "d[key], len(x), append"),
    ("O(log n)", "one more step", "binary search (Day 12)"),
    ("O(n)", "10x the cost", "x in list, sum(), one loop"),
    ("O(n log n)", "about 10x", "sorted()"),
    ("O(n^2)", "100x THE COST", "nested loop; `in` inside a loop"),
]:
    print(f"{notation:<14}{growth:<26}{example}")

print("""
The one that ruins programs is O(n^2), and it almost always arrives
DISGUISED — as `if x in some_list` inside a loop over another list.""")

# ---------------------------------------------------------------------------
# 3. THE REFACTOR THAT MATTERS — measured
# ---------------------------------------------------------------------------

N = 5_000
items = [f"item{i}" for i in range(N)]
blocklist = [f"item{i}" for i in range(N // 2, N + N // 2)]


def with_list():
    return sum(1 for x in items if x in blocklist)       # O(n * m)


def with_set():
    blocked = set(blocklist)                             # O(m), ONCE
    return sum(1 for x in items if x in blocked)         # O(n)


def rebuilt_inside():
    return sum(1 for x in items if x in set(blocklist))  # O(n * m) again!


slow = timeit.timeit(with_list, number=1)
fast = timeit.timeit(with_set, number=1)
wasted = timeit.timeit(rebuilt_inside, number=1)

print(f"\n{N:,} items against a {len(blocklist):,}-item blocklist:")
print(f"{'  `in` a list':<34}{slow:>10.4f}s")
print(f"{'  set() built ONCE, outside':<34}{fast:>10.4f}s"
      f"   {slow / fast:>8.0f}x faster")
print(f"{'  set() rebuilt INSIDE the loop':<34}{wasted:>10.4f}s"
      f"   {slow / wasted:>8.1f}x")
print(f"{'  same answer?':<34}"
      f"{str(with_list() == with_set() == rebuilt_inside()):>10}")

print("""
  ONE LINE moved the set() call out of the loop. Building it costs one pass,
  so it pays off from about three lookups onward — and rebuilding it inside
  throws the entire benefit away while looking almost identical.""")

# ---------------------------------------------------------------------------
# 4. The three questions
# ---------------------------------------------------------------------------

print("""
ASK THESE IN ORDER:

  1. DO I NEED TO LOOK THINGS UP?
       by identity ................ set
       by key, with a value ....... dict
     This question alone decides most cases, and getting it wrong is what
     makes programs slow.

  2. DOES ORDER OR DUPLICATION MATTER?
       yes ........................ list
       no ......................... the answer from question 1 stands

  3. IS IT A FIXED RECORD, OR WILL IT BE A KEY?
       yes ........................ tuple
""")

# ---------------------------------------------------------------------------
# 5. When the "slow" structure is the right one
# ---------------------------------------------------------------------------

M = 100_000
as_list = list(range(M))
as_set = set(as_list)
as_dict = dict.fromkeys(as_list)

print(f"memory for {M:,} integers:")
print(f"{'  list':<12}{sys.getsizeof(as_list):>14,} bytes")
print(f"{'  set':<12}{sys.getsizeof(as_set):>14,} bytes"
      f"   {sys.getsizeof(as_set) / sys.getsizeof(as_list):>5.1f}x")
print(f"{'  dict':<12}{sys.getsizeof(as_dict):>14,} bytes"
      f"   {sys.getsizeof(as_dict) / sys.getsizeof(as_list):>5.1f}x")

# ITERATION is the same speed for all of them — the O(1) advantage is for
# LOOKUP, not for walking through:
it_list = timeit.timeit(lambda: sum(1 for _ in as_list), number=3)
it_set = timeit.timeit(lambda: sum(1 for _ in as_set), number=3)
print(f"\niterating all {M:,}, 3 times:")
print(f"{'  list':<12}{it_list:>10.4f}s")
print(f"{'  set':<12}{it_set:>10.4f}s   <- no advantage; you are not looking up")

print("""
KEEP THE LIST WHEN:
  * n is small — at ten items everything is instant
  * you need order or duplicates — CORRECTNESS FIRST
  * you iterate rather than look up
  * memory is tight
  * the items are unhashable (a list of dicts cannot go in a set at all)""")

# ---------------------------------------------------------------------------
# 6. The one list operation that really is slow
# ---------------------------------------------------------------------------

K = 30_000


def list_front():
    q = []
    for i in range(K):
        q.insert(0, i)          # O(n) each time — everything shifts along
    return len(q)


def deque_front():
    q = deque()
    for i in range(K):
        q.appendleft(i)         # O(1)
    return len(q)


t_list = timeit.timeit(list_front, number=1)
t_deque = timeit.timeit(deque_front, number=1)
print(f"\n{K:,} inserts at the FRONT:")
print(f"{'  list.insert(0, x)':<26}{t_list:>10.4f}s")
print(f"{'  deque.appendleft(x)':<26}{t_deque:>10.4f}s   "
      f"{t_list / t_deque:>6.0f}x faster")
print("  list.append() is O(1) and perfectly fine. It is the FRONT that is")
print("  expensive, because every other element has to move up one.")

# ---------------------------------------------------------------------------
# 7. How to measure honestly
# ---------------------------------------------------------------------------

print("""
FIVE RULES FOR A BENCHMARK THAT MEANS SOMETHING

  1. USE REALISTIC DATA. Day 27's first draft reported that sorted() beat
     heapq by 10x — the opposite of the truth — because the input was
     already sorted and Timsort detects that. The data was the bug.
  2. MEASURE THE WORST CASE. For `x in list` that is the LAST item, or one
     that is not there at all.
  3. REPEAT. One run measures noise.
  4. COMPARE RATIOS, NOT SECONDS. Seconds are about the machine; the ratio
     and how it GROWS is the finding.
  5. KEEP SETUP OUT OF THE TIMED SECTION.

Day 95 does this properly with cProfile. Today is the habit: MEASURE, DO
NOT ASSUME — including when the thing you assumed was written in a book.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Time `x in list` for the FIRST item and the LAST item. Explain the gap.
#   * Set N = 20_000 in section 3 and watch the ratio grow. It is not a
#     constant — that is what O(n^2) versus O(n) means.
#   * Find `if x in some_list` inside a loop in one of your earlier builds
#     (Day 22's dedupe has one). Fix it and measure before and after.
