"""Day 026 — Sets.

    python3 lesson.py
"""

import timeit

# ---------------------------------------------------------------------------
# 1. Creating — and the empty-set wart
# ---------------------------------------------------------------------------

s = {1, 2, 3}
from_list = set([1, 2, 2, 3, 3, 3])       # duplicates vanish on the way in
empty = set()                             # NOT {} — that is an empty dict

print(f"{s}  {from_list}  {empty}")
print(f"type of {{}} is {type({}).__name__}   <- the wart. Everyone hits it once.")

# Elements must be HASHABLE, exactly as for dict keys:
print(f"\ntuples are fine: {({(0, 0), (1, 1)})}")
try:
    {[1, 2]}
except TypeError as e:
    print(f"lists are not:   TypeError: {e}")

# A set is itself unhashable, so no set of sets — that is what frozenset is
# for (section 6).


# ---------------------------------------------------------------------------
# 2. The operators — today's payoff
# ---------------------------------------------------------------------------

a = {"python", "sql", "git", "linux"}
b = {"python", "javascript", "git", "docker"}

print(f"\na = {sorted(a)}")
print(f"b = {sorted(b)}")
print(f"a | b  union         {sorted(a | b)}")
print(f"a & b  intersection  {sorted(a & b)}")
print(f"a - b  in a only     {sorted(a - b)}")
print(f"b - a  in b only     {sorted(b - a)}")
print(f"a ^ b  in one only   {sorted(a ^ b)}")

print(f"\n{'a <= b  subset':<24}{a <= b}")
print(f"{'{git} <= a':<24}{ {'git'} <= a}")
print(f"{'a.isdisjoint(b)':<24}{a.isdisjoint(b)}")

# THE DIFFERENCE BETWEEN OPERATOR AND METHOD FORM IS NOT JUST STYLE.
# Operators require sets on BOTH sides. Methods take any iterable:
try:
    a | ["docker"]
except TypeError as e:
    print(f"\na | list  -> TypeError: {e}")
print(f"a.union(list) -> works: {sorted(a.union(['docker']))}")

# Each question you actually ask maps to one operator:
#   "who bought both?"            a & b
#   "what is in A but not B?"     a - b
#   "what changed?"               a ^ b
#   "did they lose any?"          old - new
#
# Every one of those is a NESTED LOOP if you do it with lists.


# ---------------------------------------------------------------------------
# 3. Modifying
# ---------------------------------------------------------------------------

s = {1, 2, 3}
s.add(4)
s.update([5, 6])
s.discard(99)              # not there — no error
s.remove(1)                # there — removed
print(f"\nafter add/update/discard/remove: {sorted(s)}")

try:
    s.remove(99)
except KeyError as e:
    print(f"remove() on a missing item: KeyError: {e}")

# discard vs remove is a REAL CHOICE: remove tells you when your assumption
# was wrong; discard does not care. Pick deliberately.

print(f"pop() returns an ARBITRARY item: {s.pop()}  (there is no 'first')")


# ---------------------------------------------------------------------------
# 4. Unordered — and what that costs
# ---------------------------------------------------------------------------

small = {3, 1, 2}
print(f"\n{small}  <- looks sorted. That is NOT a promise.")

big = {100, 3, 57, 1, 999}
print(f"{big}  <- and here the illusion breaks")

try:
    small[0]
except TypeError as e:
    print(f"indexing a set: TypeError: {e}")

# If you need order, sort AT THE POINT OF OUTPUT:
print(f"sorted(big): {sorted(big)}")

# THE PRICE OF DEDUPLICATION. Two different tools:
items = ["b", "a", "c", "a", "b"]
print(f"\noriginal:              {items}")
print(f"set() — order gone:    {set(items)}")
print(f"dict.fromkeys — kept:  {list(dict.fromkeys(items))}")

# Memorise the second one. It is the answer whenever "deduplicate" and
# "keep the order I saw them in" are both requirements.


# ---------------------------------------------------------------------------
# 5. MEMBERSHIP SPEED — the most valuable refactor available to a beginner
# ---------------------------------------------------------------------------

N = 20_000
haystack_list = [f"item{i}" for i in range(N)]
haystack_set = set(haystack_list)
needles = [f"item{i}" for i in range(0, N, 7)]        # ~2,850 lookups

list_time = timeit.timeit(
    lambda: sum(1 for x in needles if x in haystack_list), number=1
)
set_time = timeit.timeit(
    lambda: sum(1 for x in needles if x in haystack_set), number=1
)

print(f"\n{len(needles):,} lookups against {N:,} items:")
print(f"{'  x in list':<16}{list_time:>10.5f}s")
print(f"{'  x in set':<16}{set_time:>10.5f}s")
print(f"{'  ratio':<16}{list_time / set_time:>10.0f}x")

print("""
The practical shape, and you have already written it:

    for item in items:            # 10,000 items
        if item in blacklist:     # a 10,000-item LIST
            ...                   # 100,000,000 comparisons

    blacklist = set(blacklist)    # ONE LINE
                                  # 10,000 comparisons

Day 22's build has `if word not in loop` inside a loop, which is O(n^2) for
exactly this reason. Building the set costs O(n) ONCE, so it pays off the
moment you do more than a handful of lookups. What does NOT pay is building
it inside the loop — that throws the whole benefit away.""")


# ---------------------------------------------------------------------------
# 6. frozenset — immutable, therefore hashable
# ---------------------------------------------------------------------------

fs = frozenset(["read", "write"])
print(f"\nfrozenset: {fs}")
print(f"as a dict key: {({fs: 'editor'})[fs]}")
print(f"a set of sets: {({frozenset([1, 2]), frozenset([3])})}")

# The typical use: grouping by an UNORDERED COLLECTION.
people = {
    "ada": frozenset(["read", "write", "admin"]),
    "alan": frozenset(["read", "write"]),
    "grace": frozenset(["write", "read"]),          # same set, different order
}
by_permissions = {}
for person, perms in people.items():
    by_permissions.setdefault(perms, []).append(person)

print("\ngrouped by exact permission set:")
for perms, names in by_permissions.items():
    print(f"  {sorted(perms)!s:<34}{', '.join(names)}")
print("alan and grace group together — a set does not care about order.")


# ---------------------------------------------------------------------------
# 7. Set comprehensions
# ---------------------------------------------------------------------------

words = ["The", "the", "THE", "quick", "brown"]
print(f"\n{({w.lower() for w in words})}")
print(f"{({len(w) for w in words})}")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write `empty = {}` and then call .add() on it.
#   * Put a list in a set. Then a tuple containing a list.
#   * Print {1, 2, 3} and {"a", "b", "c"} a few times in separate processes
#     and see whether the string one keeps its order between runs.
#   * Take Day 22's O(n^2) dedupe loop, wrap the accumulator in a set, and
#     time both at 20,000 words.
