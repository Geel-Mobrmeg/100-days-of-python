# Day 024 — Dictionaries

**Phase 3 · Data structures** · ~80 minutes

> **Today's build:** a contact book with lookup by name, partial search and safe handling of missing entries.

**Concepts:** keys & values · `get()` with defaults · iteration order · nesting · `in`

---

## The article

### Why this day exists

This is the most important day in the phase. Dicts are the structure Python is *built out of* —
objects, modules, namespaces and JSON are all dicts underneath — and they are the fix for every
"five parallel lists" problem you have hit since Day 20.

They are also the reason Python feels fast. Looking something up in a dict of ten million items
takes the same time as looking it up in a dict of ten.

### 1. The shape

```python
person = {"name": "Ada", "age": 36, "role": "engineer"}

person["name"]            # "Ada"
person["age"] = 37        # update
person["email"] = "a@b.c" # add — same syntax
del person["role"]
len(person)               # how many pairs
"name" in person          # True — checks KEYS, not values
```

A dict maps **keys** to **values**. Keys must be **hashable**, which in practice means immutable:
strings, numbers, tuples — never lists or dicts. That is why Day 23 mattered.

Values can be anything, including other dicts.

Yesterday's build held a task as `tasks[i]` plus `done[i]`. Today it is one thing:

```python
{"text": "buy milk", "done": False}
```

and the two lists can no longer drift apart, because there is only one.

### 2. `KeyError`, and the three ways to avoid it

`person["phone"]` on a missing key raises `KeyError`. That is often correct — a missing key
frequently *is* a bug. But when absence is normal:

```python
person.get("phone")                 # None if missing
person.get("phone", "unknown")      # your own default
person.setdefault("tags", [])       # get it, or insert it and return it
```

`.get()` is the one you will use constantly. `.setdefault()` is the one people forget exists, and
it is exactly right for "append to a list that might not be there yet":

```python
groups.setdefault(key, []).append(value)
```

Tomorrow's `defaultdict` does that more neatly, but `setdefault` needs no import.

`.pop(key, default)` removes and returns, without raising.

### 3. Iterating

```python
for key in person: ...                    # keys — the default
for key in person.keys(): ...             # same, explicit
for value in person.values(): ...
for key, value in person.items(): ...     # what you want 90% of the time
```

`.items()` yields `(key, value)` tuples, which is why Day 23's unpacking arrives just before
today.

**Order:** since Python 3.7, dicts keep **insertion order**, guaranteed by the language. This is
newer than a lot of advice on the internet, which will tell you dicts are unordered. They were,
until 3.6. They are not now.

Do not mutate a dict while iterating it — same rule as lists, same silent breakage. Iterate over
`list(d.keys())` if you must delete.

### 4. Dicts of dicts

The natural shape for records:

```python
contacts = {
    "ada": {"name": "Ada Lovelace", "phone": "01234", "tags": ["work"]},
    "alan": {"name": "Alan Turing", "phone": "05678", "tags": ["work", "chess"]},
}

contacts["ada"]["phone"]
```

Two levels is comfortable. Three is a smell — at that point you want a class (Day 41).

Safe traversal of nested data is genuinely awkward and Day 28 is dedicated to it. The short
version:

```python
contacts.get("bob", {}).get("phone", "-")     # chained defaults
```

That works because the fallback for a missing person is an empty dict, which then also has no
phone. It is a common idiom and it stops being readable at about three levels.

### 5. Useful methods

```python
d.update(other)            # merge other in, overwriting clashes
d1 | d2                    # a NEW merged dict (3.9+); right side wins
dict.fromkeys(keys, 0)     # build from a list of keys
d.copy()                   # SHALLOW — nested dicts are shared (Day 21)
```

The dict comprehension mirrors Day 22:

```python
{k: v for k, v in pairs}
{name: len(name) for name in names}
{v: k for k, v in d.items()}          # invert — only safe if values are unique
```

### 6. Why dicts are fast

A dict is a **hash table**. Looking up a key computes `hash(key)` once and jumps more or less
straight to the value. It does not search.

| Operation | list | dict |
|---|---|---|
| `x in thing` | O(n) — scans | **O(1)** — one jump |
| lookup by key | O(n) | **O(1)** |
| append / insert | O(1) | O(1) |

**`in` on a list of 100,000 items does up to 100,000 comparisons. On a dict it does about one.**
That is the single biggest performance decision available to a beginner, and Day 29 measures it.

The cost: dicts use more memory, and keys must be hashable.

Two consequences worth knowing:
- A dict is often better than a chain of `if`/`elif` for a lookup — as Day 17 said.
- Hash order for strings is randomised per process for security, but *iteration* order is
  insertion order, so this does not affect you.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every method, `KeyError` vs `.get()`, iteration, nesting, comprehensions, and a measured O(1) vs O(n) demo. |
| `build.py`  | The contact book: exact and partial search, safe missing handling, tags, and the parallel-list version deleted. |

```bash
python3 lesson.py
python3 build.py
printf 'find ada\nsearch tur\nadd bob 555 work\nlist\nquit\n' | python3 build.py
```

---

## Common mistakes

**`KeyError` from `d[k]`.** Use `.get()` when absence is normal — and *not* when it is a bug.

**A list as a key.** `TypeError: unhashable type: 'list'`.

**`.get()` hiding a real bug.** A default that silently papers over a typo'd key is worse than a
crash.

**Mutating while iterating.** `RuntimeError: dictionary changed size during iteration`, or
silence.

**`.copy()` on nested dicts.** Shallow. Inner dicts are shared.

**Believing dicts are unordered.** They have been insertion-ordered since 3.7.

**Inverting a dict with duplicate values.** Silently loses entries.

---

## Exercises

1. Rewrite Day 21's to-do list with one dict per task. Delete the integrity check and explain why
   it is no longer possible to fail.
2. Count word frequencies with `.get(word, 0) + 1`. Then with `.setdefault`. Tomorrow does it
   in one line.
3. Group names by first letter using `setdefault(letter, []).append(name)`.
4. Invert a dict. Then invert one with duplicate values and explain what happened.
5. Time `x in list` vs `x in dict` at 100,000 items. Write down the ratio.
6. Build a nested dict two levels deep and write a safe lookup that never raises.

---

## Checklist

- [ ] I know keys must be hashable and why
- [ ] I choose between `d[k]` and `d.get(k)` deliberately
- [ ] I use `.items()` when I need both
- [ ] I know dicts preserve insertion order
- [ ] I can say why `in` is O(1) on a dict and O(n) on a list
- [ ] My contact book never raises on a missing name
