"""Day 024 — Dictionaries.

    python3 lesson.py
"""

import timeit

# ---------------------------------------------------------------------------
# 1. The shape
# ---------------------------------------------------------------------------

person = {"name": "Ada", "age": 36, "role": "engineer"}

print(person["name"])
person["age"] = 37                  # update
person["email"] = "ada@example.com" # add — same syntax
del person["role"]
print(person)
print(len(person), "name" in person, "Ada" in person)
#                   ^ True          ^ False — `in` checks KEYS, not values

# KEYS MUST BE HASHABLE, which in practice means immutable: strings,
# numbers, tuples. Never lists or dicts. That is why Day 23 came first.
grid = {(0, 0): "origin", (1, 2): "somewhere"}
print(f"\ntuple key: {grid[(0, 0)]}")
try:
    {[0, 0]: "nope"}
except TypeError as e:
    print(f"list key:  TypeError: {e}")

# Day 21's to-do list held tasks[i] AND done[i], two lists that had to stay
# in step forever. One dict per task, and drifting apart stops being
# possible — there is only one thing:
task = {"text": "buy milk", "done": False}
print(f"\none task, one object: {task}")


# ---------------------------------------------------------------------------
# 2. KeyError, and the three ways round it
# ---------------------------------------------------------------------------

try:
    person["phone"]
except KeyError as e:
    print(f"\nmissing key raises KeyError: {e}")

# That is often CORRECT — a missing key is frequently a bug, and you want to
# hear about it. When absence is genuinely normal:
print(f".get('phone')            -> {person.get('phone')}")
print(f".get('phone', 'unknown') -> {person.get('phone', 'unknown')}")

# setdefault: get it, or insert it and return it. Exactly right for
# "append to a list that might not exist yet":
person.setdefault("tags", []).append("pioneer")
person.setdefault("tags", []).append("mathematician")
print(f"setdefault built:        {person['tags']}")

# .pop with a default removes without raising:
print(f".pop('nope', '-')        -> {person.pop('nope', '-')}")

# WARNING: a .get() default that papers over a TYPO'd key is worse than a
# crash. Use it when absence is expected, not to silence errors.


# ---------------------------------------------------------------------------
# 3. Iterating
# ---------------------------------------------------------------------------

scores = {"ada": 95, "alan": 87, "grace": 92}

print()
for key in scores:                       # keys, the default
    print(f"  key {key}")
for value in scores.values():
    print(f"  value {value}")
for name, score in scores.items():       # what you want 90% of the time
    print(f"  {name:<8}{score:>4}")

# .items() yields (key, value) TUPLES — which is why Day 23's unpacking
# lands the day before today.
print(list(scores.items())[:2])

# ORDER: since Python 3.7 dicts keep INSERTION ORDER, guaranteed by the
# language. Much advice online predates this and says they are unordered.
ordered = {}
for name in ("zoe", "adam", "mia"):
    ordered[name] = 1
print(f"insertion order preserved: {list(ordered)}")

# Do not mutate while iterating — same rule as lists:
try:
    for name in scores:
        if scores[name] < 90:
            del scores[name]
except RuntimeError as e:
    print(f"mutating while iterating: RuntimeError: {e}")

# Iterate over a snapshot of the keys instead:
scores = {"ada": 95, "alan": 87, "grace": 92}
for name in list(scores):
    if scores[name] < 90:
        del scores[name]
print(f"deleting via list(scores): {scores}")


# ---------------------------------------------------------------------------
# 4. Dicts of dicts — the natural shape for records
# ---------------------------------------------------------------------------

contacts = {
    "ada": {"name": "Ada Lovelace", "phone": "01234", "tags": ["work"]},
    "alan": {"name": "Alan Turing", "phone": "05678", "tags": ["work", "chess"]},
}

print(f"\n{contacts['ada']['phone']}")

# Safe traversal of the nested case. The fallback for a missing person is an
# EMPTY DICT, which then also has no phone:
print(f"missing person: {contacts.get('bob', {}).get('phone', '-')}")

# Two levels is comfortable. Three is a smell — at that point you want a
# class (Day 41). Day 28 is entirely about surviving deeper nesting.


# ---------------------------------------------------------------------------
# 5. Merging, building, comprehensions
# ---------------------------------------------------------------------------

defaults = {"colour": "black", "size": "M"}
chosen = {"size": "L"}

merged = defaults | chosen              # 3.9+, a NEW dict, right side wins
print(f"\nmerged: {merged}")

combined = defaults.copy()
combined.update(chosen)                 # in place, same result
print(f"update: {combined}")

print(f"fromkeys: {dict.fromkeys(['a', 'b', 'c'], 0)}")

# Dict comprehensions mirror Day 22:
names = ["Ada", "Alan", "Grace"]
print(f"comprehension: {({n: len(n) for n in names})}")

d = {"a": 1, "b": 2}
print(f"inverted:      {({v: k for k, v in d.items()})}")

# Inverting is only safe when the VALUES ARE UNIQUE — otherwise entries are
# silently lost:
dupes = {"a": 1, "b": 1}
print(f"inverting duplicates: {({v: k for k, v in dupes.items()})}  <- 'a' gone")

# .copy() is SHALLOW, exactly as for lists (Day 21):
nested = {"inner": [1, 2]}
shallow = nested.copy()
shallow["inner"].append(3)
print(f"shallow copy shares the inner list: {nested}")


# ---------------------------------------------------------------------------
# 6. WHY DICTS ARE FAST — the biggest performance decision a beginner makes
# ---------------------------------------------------------------------------

N = 100_000
big_list = list(range(N))
big_dict = dict.fromkeys(range(N))
big_set = set(range(N))

target = N - 1            # the worst case for a list: the very last item

list_time = timeit.timeit(lambda: target in big_list, number=200)
dict_time = timeit.timeit(lambda: target in big_dict, number=200)
set_time = timeit.timeit(lambda: target in big_set, number=200)

print(f"\n`x in thing` over {N:,} items, 200 times:")
print(f"{'  list':<12}{list_time:>10.5f}s   scans, up to {N:,} comparisons")
print(f"{'  dict':<12}{dict_time:>10.5f}s   hashes once and jumps")
print(f"{'  set':<12}{set_time:>10.5f}s   same (Day 26)")
print(f"{'  ratio':<12}{list_time / dict_time:>10.0f}x faster")

# A dict is a HASH TABLE. Looking up a key computes hash(key) once and goes
# more or less straight to the value. It does not search.
#
#                       list        dict
#   x in thing          O(n)        O(1)
#   lookup by key       O(n)        O(1)
#
# The cost: more memory, and keys must be hashable. Day 29 measures how the
# gap grows with size.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Look up a key that does not exist, with [] and then with .get().
#   * Use a list as a key. Then a tuple containing a list. Read both errors.
#   * Invert a dict whose values repeat, and count what you lost.
#   * Delete from a dict while iterating it, and read the RuntimeError.
#   * Change N to 1,000,000 above and run it again. The ratio grows.
