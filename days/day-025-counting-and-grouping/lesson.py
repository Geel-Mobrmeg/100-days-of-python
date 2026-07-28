"""Day 025 — Counting and grouping.

    python3 lesson.py
"""

from collections import Counter, defaultdict

WORDS = "the quick brown fox jumps over the lazy dog the fox".split()
NAMES = ["Ada", "Alan", "Grace", "Anita", "Barbara", "Guido", "Bjarne"]

# ---------------------------------------------------------------------------
# 1. Counting by hand — three ways, all correct
# ---------------------------------------------------------------------------

# The obvious way. The `if` exists because you CANNOT += 1 a key that is not
# there yet — that is a KeyError.
counts = {}
for word in WORDS:
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1
print(f"manual:      {counts}")

# With .get() — one line, and the one to remember.
counts = {}
for word in WORDS:
    counts[word] = counts.get(word, 0) + 1
print(f".get():      {counts}")

# With setdefault.
counts = {}
for word in WORDS:
    counts.setdefault(word, 0)
    counts[word] += 1
print(f"setdefault:  {counts}")


# ---------------------------------------------------------------------------
# 2. defaultdict — the missing key creates itself
# ---------------------------------------------------------------------------

counts = defaultdict(int)          # int() is 0
for word in WORDS:
    counts[word] += 1              # no check, no default, no KeyError
print(f"\ndefaultdict: {dict(counts)}")

# defaultdict(factory) calls factory() whenever a MISSING KEY IS ACCESSED.
#   int   -> 0
#   list  -> []
#   set   -> set()

# THE TRAP: merely LOOKING at a missing key creates it.
d = defaultdict(list)
print(f"len before peeking: {len(d)}")
if d["nope"]:                      # this just inserted "nope": []
    pass
print(f"len after peeking:  {len(d)}   <- 'nope' is now a real key")
print(f"contents: {dict(d)}")

# Use .get() or `in` to check WITHOUT creating:
d2 = defaultdict(list)
print(f"d2.get('nope'): {d2.get('nope')}   len still {len(d2)}")


# ---------------------------------------------------------------------------
# 3. Counter — the whole counting loop, as one call
# ---------------------------------------------------------------------------

counts = Counter(WORDS)
print(f"\nCounter:     {counts}")
print(f"most_common(3): {counts.most_common(3)}")
print(f"counts['the']:  {counts['the']}")
print(f"counts['zzz']:  {counts['zzz']}   <- 0, not KeyError")
print(f"and it did NOT insert it: {'zzz' in counts}")

# Counter is a DICT SUBCLASS, so everything you know still works:
print(f"total items: {sum(counts.values())}")
print(f"distinct:    {len(counts)}")

# It counts any iterable, including a string's characters:
print(f"Counter('hello'): {Counter('hello')}")

# Counters do arithmetic, which is occasionally exactly what you want:
a = Counter("aabbc")
b = Counter("abbbd")
print(f"\na       {a}")
print(f"b       {b}")
print(f"a + b   {a + b}      (add counts)")
print(f"a - b   {a - b}      (subtract, dropping <= 0)")
print(f"a & b   {a & b}      (minimum of each — intersection)")
print(f"a | b   {a | b}      (maximum of each — union)")


# ---------------------------------------------------------------------------
# 4. Grouping — the pattern behind SQL's GROUP BY and pandas' groupby
# ---------------------------------------------------------------------------

groups = defaultdict(list)
for name in NAMES:
    groups[name[0]].append(name)            # key function: first letter
print(f"\nby first letter: {dict(groups)}")

by_length = defaultdict(list)
for name in NAMES:
    by_length[len(name)].append(name)
print(f"by length:       {dict(by_length)}")

# THE SHAPE, worth recognising because you will meet it at three sizes:
#
#     groups = defaultdict(list)
#     for item in items:
#         groups[key_of(item)].append(item)
#
#   Day 25  defaultdict           this
#   Day 75  pandas .groupby()     the same idea over a table
#   Day 78  SQL GROUP BY          the same idea in a database

# itertools.groupby is NOT this. It groups only CONSECUTIVE equal items, so
# it needs sorted input, and it surprises everybody once:
from itertools import groupby            # noqa: E402 - imported here to make a point

unsorted = ["a", "b", "a"]
print("\nitertools.groupby on unsorted input:")
for key, group in groupby(unsorted):
    print(f"  {key}: {list(group)}      <- 'a' appears TWICE as a group")
print("Use the defaultdict version unless you specifically want runs.")


# ---------------------------------------------------------------------------
# 5. Inverting — which is grouping in disguise
# ---------------------------------------------------------------------------

roles = {"ada": "maths", "alan": "maths", "grace": "navy"}

naive = {v: k for k, v in roles.items()}
print(f"\nnaive invert: {naive}   <- 'ada' silently lost")

safe = defaultdict(list)
for person, role in roles.items():
    safe[role].append(person)
print(f"safe invert:  {dict(safe)}")

# Inverting a dict IS grouping by value. The one-liner is only correct when
# the values are unique — and nothing warns you when they are not.


# ---------------------------------------------------------------------------
# 6. Finding the biggest — key= is the most useful argument in Python
# ---------------------------------------------------------------------------

counts = Counter(WORDS)

print(f"\nmax by value:      {max(counts, key=counts.get)}")
print(f"max as a pair:     {max(counts.items(), key=lambda kv: kv[1])}")
print(f"sorted by count:   {sorted(counts.items(), key=lambda kv: -kv[1])[:3]}")
print(f"Counter does it:   {counts.most_common(3)}")

# `key=` is Day 27's whole subject. Note that sorted() returns a LIST OF
# PAIRS — the dict itself is not reordered.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Do counts[word] += 1 on a plain {} and read the KeyError.
#   * Print len() of a defaultdict, check three missing keys, print len again.
#   * Invert a dict with repeated values and count what disappeared.
#   * Count bigrams: zip(WORDS, WORDS[1:]) gives consecutive pairs, and
#     Counter takes them directly. The top bigram of most English is "of the".
