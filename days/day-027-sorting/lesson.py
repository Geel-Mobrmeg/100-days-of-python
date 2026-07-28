"""Day 027 — Sorting.

    python3 lesson.py
"""

import heapq
import random
import timeit
from operator import itemgetter

WORDS = ["banana", "Apple", "cherry", "date", "elderberry", "fig"]

PEOPLE = [
    {"first": "Ada", "last": "Lovelace", "age": 36},
    {"first": "Alan", "last": "Turing", "age": 41},
    {"first": "Grace", "last": "Hopper", "age": 85},
    {"first": "Anita", "last": "Borg", "age": 55},
    {"first": "Barbara", "last": "Liskov", "age": 85},
]

# ---------------------------------------------------------------------------
# 1. sorted() vs .sort()
# ---------------------------------------------------------------------------

nums = [3, 1, 4, 1, 5]

new = sorted(nums)                  # a NEW list
print(f"sorted(nums) -> {new}, nums unchanged -> {nums}")

returned = nums.sort()              # IN PLACE, returns None
print(f"nums.sort() returned {returned}, nums is now {nums}")

# .sort() only exists on LISTS. sorted() takes any iterable and always
# returns a list — which is the only way to get a set or dict in order:
print(f"\nsorted(a set):   {sorted({3, 1, 2})}")
scores = {"ada": 95, "alan": 87}
print(f"sorted(a dict):  {sorted(scores)}          <- the KEYS")
print(f"sorted(.items()): {sorted(scores.items())}")


# ---------------------------------------------------------------------------
# 2. Key functions
# ---------------------------------------------------------------------------

print(f"\ndefault:          {sorted(WORDS)}")
print(f"key=len:          {sorted(WORDS, key=len)}")
print(f"key=str.lower:    {sorted(WORDS, key=str.lower)}")

# Strings sort by CODE POINT, so all uppercase comes before all lowercase.
# That is why "Apple" leads the default sort and not the lowercased one.
print(f'"Z" < "a" is {"Z" < "a"}')

# key= is applied ONCE PER ELEMENT (not per comparison), so an expensive key
# function is fine.
print(f"\nby age:           {[p['first'] for p in sorted(PEOPLE, key=lambda p: p['age'])]}")

# itemgetter is the faster, tidier form of the common lambda:
print(f"itemgetter('age'): {[p['first'] for p in sorted(PEOPLE, key=itemgetter('age'))]}")

# ...and it takes several fields, giving a tuple key for free:
by_name = sorted(PEOPLE, key=itemgetter("last", "first"))
print(f"by last, first:   {[p['last'] for p in by_name]}")

# key=len, not key=len(). Pass the FUNCTION, do not call it.


# ---------------------------------------------------------------------------
# 3. STABILITY — the property that makes multi-key sorts work
# ---------------------------------------------------------------------------
#
# Python's sort is STABLE: elements that compare equal keep their original
# relative order. That is a language GUARANTEE, not an implementation detail.

pairs = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]
print(f"\noriginal:         {pairs}")
print(f"sorted by number: {sorted(pairs, key=itemgetter(1))}")
print("                   ^ b before c, a before d — the original order")
print("                     survived among the ties. That is stability.")

# THE CONSEQUENCE:
#     To sort by A then B, sort by B FIRST, then by A.
#
# It reads backwards and it is correct, because each pass preserves the
# order the previous pass established among ties.

people = PEOPLE.copy()
people.sort(key=itemgetter("first"))     # LEAST significant first
people.sort(key=itemgetter("age"))       # MOST significant last
print(f"\nage, then first name (two passes):")
for p in people:
    print(f"  {p['age']:>4}  {p['first']}")
print("  ^ 85s are Barbara then Grace — alphabetical, from the first pass")


# ---------------------------------------------------------------------------
# 4. Multi-key, and the mixed-direction problem
# ---------------------------------------------------------------------------

# TECHNIQUE 1: a tuple key. One pass. Tuples compare element by element.
by_tuple = sorted(PEOPLE, key=lambda p: (p["age"], p["first"]))
print(f"\ntuple key:        {[(p['age'], p['first']) for p in by_tuple]}")

# THE PROBLEM: reverse=True reverses EVERYTHING.
wrong = sorted(PEOPLE, key=lambda p: (p["age"], p["first"]), reverse=True)
print(f"reverse=True:     {[(p['age'], p['first']) for p in wrong]}")
print("                   ^ age descending, but the NAMES are descending too")

# FIX A — negate the number. Short, and only works on numbers.
fix_a = sorted(PEOPLE, key=lambda p: (-p["age"], p["first"]))
print(f"negate the age:   {[(p['age'], p['first']) for p in fix_a]}")

# FIX B — successive stable sorts, least significant first. Works for ANY
# mix of directions and types, including strings and dates you cannot negate.
fix_b = PEOPLE.copy()
fix_b.sort(key=itemgetter("first"))                    # ascending
fix_b.sort(key=itemgetter("age"), reverse=True)        # descending
print(f"two passes:       {[(p['age'], p['first']) for p in fix_b]}")

print(f"\nthe two fixes agree: {fix_a == fix_b}")


# ---------------------------------------------------------------------------
# 5. What cannot be compared
# ---------------------------------------------------------------------------

try:
    sorted([3, "1"])
except TypeError as e:
    print(f"\nmixed types: TypeError: {e}")

try:
    sorted([1, None, 2])
except TypeError as e:
    print(f"with None:   TypeError: {e}")

# Python refuses to guess, which is right — but real data HAS holes. The fix
# is a key that normalises. `x is None` is a bool, and False sorts before
# True, so present values come first:
rows = [{"n": 3}, {"n": None}, {"n": 1}, {"n": None}, {"n": 2}]
safe = sorted(rows, key=lambda r: (r["n"] is None, r["n"] if r["n"] is not None else 0))
print(f"Nones last:  {[r['n'] for r in safe]}")


# ---------------------------------------------------------------------------
# 6. When NOT to sort
# ---------------------------------------------------------------------------

print(f"\nmax by age:  {max(PEOPLE, key=itemgetter('age'))['first']}")
print(f"min by age:  {min(PEOPLE, key=itemgetter('age'))['first']}")

# Sorting is O(n log n). max() is O(n). For "the top 10 of a million",
# heapq.nlargest is the right tool — and it is what Counter.most_common
# uses internally (Day 25).
#
# MEASURE THIS ON REALISTIC DATA. The first version of this demo used
# list(range(1_000_000, 0, -1)) and reported that sorted() was TEN TIMES
# FASTER than heapq — the opposite of the claim. The data was the problem:
# Python's Timsort detects an already-sorted or reverse-sorted run and
# finishes in O(n). A benchmark on sorted input measures the wrong thing.
random.seed(42)
million = list(range(1_000_000))
random.shuffle(million)

full = timeit.timeit(lambda: sorted(million)[:10], number=3)
partial = timeit.timeit(lambda: heapq.nsmallest(10, million), number=3)

print(f"\ntop 10 of {len(million):,} SHUFFLED values, 3 times:")
print(f"{'  sorted(...)[:10]':<24}{full:>10.4f}s")
print(f"{'  heapq.nsmallest(10)':<24}{partial:>10.4f}s")
print(f"{'  ratio':<24}{full / partial:>10.1f}x")

# And the cautionary version, on the data that misled the first draft:
already = list(range(1_000_000, 0, -1))
sorted_input = timeit.timeit(lambda: sorted(already)[:10], number=3)
print(f"\n{'  sorted() on REVERSE-SORTED input':<34}{sorted_input:>10.4f}s")
print(f"{'  ...vs on shuffled input':<34}{full:>10.4f}s")
print("  Same length, same call, ~an order of magnitude apart. Timsort is")
print("  adaptive. Benchmark on data shaped like your real data, or you")
print("  will draw a confident conclusion about the wrong thing.")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write x = my_list.sort() and use x.
#   * Sort by (score, name) with reverse=True and find the wrong names.
#   * Sort a list of dicts where one score is None, then fix it.
#   * Prove stability yourself: sort by a field where several rows tie, and
#     check the tied rows kept their input order.
#   * Sort ["e", "E", "é"] and explain the order. Then try key=str.lower.
