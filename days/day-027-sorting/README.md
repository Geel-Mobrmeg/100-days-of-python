# Day 027 — Sorting

**Phase 3 · Data structures** · ~75 minutes

> **Today's build:** a leaderboard sorted by score descending, then by time ascending, then alphabetically.

**Concepts:** `sorted()` vs. `.sort()` · key functions · `reverse` · stability · multi-key sorts

---

## The article

### Why this day exists

Sorting is solved. You will never write a sorting algorithm in production, and Python's is better
than anything you would write. What you *will* do, constantly, is tell it **what to sort by** —
and the two ideas that make that work, key functions and stability, are the actual content of
today.

The multi-key sort in the build is the thing worth taking away: "score descending, then time
ascending, then alphabetically" is a real requirement that appears in every leaderboard, report
and table you will ever produce, and there are two ways to do it — one obvious and one that
handles mixed directions.

### 1. `sorted()` vs. `.sort()`

```python
new = sorted(items)      # returns a NEW list; the original is untouched
items.sort()             # sorts IN PLACE; returns None
```

The Day 16/21 rule again: **in-place methods return `None`**. `x = items.sort()` gives `None`.

`.sort()` only exists on lists. `sorted()` takes **any iterable** and always returns a list —
which is how you sort a dict, a set, or a generator:

```python
sorted(my_dict)                 # the keys
sorted(my_dict.items())         # (key, value) pairs
sorted(my_set)                  # the only way to get a set in order
```

Use `sorted()` by default. Use `.sort()` when the list is large and you genuinely do not need the
original — it saves a copy.

### 2. Key functions

`key=` takes a function applied to each element; the *results* are compared, and the *original
elements* are returned.

```python
sorted(words, key=len)                    # by length
sorted(words, key=str.lower)              # case-insensitively
sorted(people, key=lambda p: p["age"])    # by a dict field
sorted(records, key=lambda r: r[2])       # by a tuple position
```

The key function is called **once per element** (not once per comparison), so an expensive key is
fine.

`operator.itemgetter` and `attrgetter` are the faster, tidier forms of the common lambdas:

```python
from operator import itemgetter
sorted(people, key=itemgetter("age"))
sorted(records, key=itemgetter(2))
sorted(people, key=itemgetter("last", "first"))   # a tuple key, for free
```

Without `key=`, Python compares the elements directly, so a list of tuples sorts by first
element, then second — which is often exactly what you want, and is the basis of section 4.

### 3. Stability — the property that makes multi-key sorts work

**Python's sort is stable: elements that compare equal keep their original relative order.**

That is a guarantee, not an implementation detail, and it has a direct consequence:

> To sort by A then B, sort by B **first**, then by A.

```python
people.sort(key=itemgetter("first"))     # least significant first
people.sort(key=itemgetter("last"))      # most significant last
# now sorted by last name, and within each surname by first name
```

This reads backwards and is correct. Each sort preserves the order the previous one established
among ties.

Stability also means "sort by score" leaves equal scores in whatever order they arrived in —
which is *not* random, and is why an unstable-looking result is usually a stability question.

### 4. Multi-key: two techniques

**Technique 1 — a tuple key.** One pass, and the natural choice when all keys go the same
direction:

```python
sorted(rows, key=lambda r: (r["last"], r["first"]))
```

Tuples compare element by element, so this is "by last name; ties broken by first name".

**The problem:** `reverse=True` reverses *everything*. For "score descending, then name
ascending" a tuple key alone will not do — reversing gives you names descending too.

**Two fixes.** For numbers, negate:

```python
key=lambda r: (-r["score"], r["name"])       # score DESC, name ASC
```

For anything not negatable (strings, dates), use **successive stable sorts**, in reverse order of
importance:

```python
rows.sort(key=itemgetter("name"))                    # least significant
rows.sort(key=itemgetter("score"), reverse=True)     # most significant
```

That second technique always works, for any mix of directions and types. The negation trick is
shorter and only works on numbers. Know both.

### 5. What can and cannot be compared

```python
sorted([3, "1"])       # TypeError: '<' not supported between 'str' and 'int'
sorted([None, 1])      # TypeError
```

Python refuses to guess across types. A column of "mostly numbers" with one `None` in it will
raise, and that is the correct behaviour — but it means real data needs a key that normalises:

```python
sorted(rows, key=lambda r: (r["score"] is None, r["score"]))
```

That puts `None`s last: `False` sorts before `True`, so present values come first, and the second
element only gets compared among values of the same presence.

Strings sort by **code point**, so all uppercase precedes all lowercase, and accented characters
land after `z`. For human-facing order use `key=str.lower`, and for correct language-aware
ordering you need `locale.strxfrm` or a proper collation library — a genuinely hard problem that
this course does not solve.

### 6. When not to sort the whole thing

```python
max(items, key=...)              # the single largest
min(items, key=...)              # the single smallest
heapq.nlargest(10, items, key=...)   # the top 10 of a million
```

Sorting is O(n log n); `max` is O(n). For "the top 3 of a million rows", `heapq.nlargest` is the
right tool. `Counter.most_common(n)` (Day 25) uses it internally.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Both functions, key functions, stability proved, both multi-key techniques, mixed-type failures. |
| `build.py`  | The leaderboard: score desc, time asc, name asc — done both ways and verified identical. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`x = items.sort()`** — `None`.

**`sorted()` on a dict expecting pairs.** You get the keys. Use `.items()`.

**`reverse=True` with a tuple key.** Reverses every level.

**Sorting mixed types.** `TypeError`, correctly.

**`key=len()` instead of `key=len`.** Pass the function, do not call it.

**Multi-key sorts in the wrong order.** Least significant first.

**Sorting a million rows for the top 10.** Use `heapq.nlargest`.

**Expecting case-insensitive order by default.** `"Z" < "a"`.

---

## Exercises

1. Sort words by length, then alphabetically among equal lengths — both ways.
2. Prove stability: sort by one field twice with different second fields and show the tie order.
3. Sort a dict by value descending, then by key ascending.
4. Sort records with some `None` scores so the `None`s land last, without crashing.
5. Sort `["banana", "Apple", "cherry"]` case-sensitively and case-insensitively.
6. Time `sorted(million)[:10]` against `heapq.nlargest(10, million)`.

---

## Checklist

- [ ] I know which of `sorted`/`.sort` returns `None`
- [ ] I can write a key function for a dict field or tuple position
- [ ] I can state what stability guarantees
- [ ] I can do a mixed-direction multi-key sort, two ways
- [ ] I know why sorting mixed types raises
- [ ] My leaderboard's tie-breaks are correct and I can prove it
