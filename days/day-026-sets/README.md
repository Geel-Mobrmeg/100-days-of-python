# Day 026 — Sets

**Phase 3 · Data structures** · ~70 minutes

> **Today's build:** a duplicate finder that also reports what two tag lists share and where they differ.

**Concepts:** uniqueness · union & intersection · difference · membership speed · `frozenset`

---

## The article

### Why this day exists

A set is an unordered collection of unique, hashable things. That one sentence contains all three
reasons to use one:

1. **Unique** — deduplication is one function call.
2. **Hashable** — so membership is O(1), same as a dict.
3. **Unordered** — so it supports the algebra: union, intersection, difference.

The third is what makes today worth a whole day. Questions like "which customers bought both?",
"which files are in A but not B?", "which permissions did this user lose?" are all one operator
each — and every one of them is a nested loop if you do it with lists.

### 1. Creating

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])       # from any iterable — duplicates vanish
empty = set()               # NOT {} — that is an empty dict
```

`{}` is a dict. This is a genuine wart in the syntax and it catches everybody once.

Elements must be **hashable**, exactly as with dict keys: strings, numbers, tuples — never lists
or dicts. And a set itself is unhashable, so you cannot have a set of sets (see `frozenset`).

### 2. The operators

This is the day's payoff. Each has an operator form and a method form:

```python
a | b        a.union(b)                  # in either
a & b        a.intersection(b)           # in both
a - b        a.difference(b)             # in a, not in b
a ^ b        a.symmetric_difference(b)   # in one but not both
```

```python
a <= b       a.issubset(b)
a >= b       a.issuperset(b)
a.isdisjoint(b)                          # nothing in common
```

The difference between the two forms is not just style: **the operators require both sides to be
sets; the methods accept any iterable.** `{1,2} | [2,3]` is a `TypeError`, while
`{1,2}.union([2,3])` works. Methods when the other side might be a list; operators when both are
sets and you want it to read like maths.

`a - b` is the one you will reach for most, and it is the answer to "what is missing?" — a
question that otherwise needs a loop and a flag.

### 3. Modifying

```python
s.add(x)             # one item
s.update(iterable)   # many
s.discard(x)         # remove if present — no error
s.remove(x)          # remove, KeyError if absent
s.pop()              # remove and return an ARBITRARY item
```

`discard` vs `remove` is a real choice: `remove` tells you when your assumption was wrong,
`discard` does not care. Pick deliberately.

`s.pop()` returns an arbitrary element, not the "first" — there is no first.

### 4. Unordered, and what that costs

```python
s = {3, 1, 2}
print(s)          # {1, 2, 3} — looks sorted; is not a promise
s[0]              # TypeError: 'set' object is not subscriptable
```

Sets have **no order at all**. No indexing, no slicing, no `.sort()`. Small integers often *look*
ordered because of how they hash, and relying on that is a bug waiting for bigger numbers.

Iteration order is arbitrary and can differ between runs (string hashing is randomised per
process). So: **if you need order, `sorted(my_set)` at the point of output.**

That is the price of the deduplication:

```python
list(dict.fromkeys(items))   # deduplicate, KEEPING first-seen order
set(items)                   # deduplicate, order gone
```

The `dict.fromkeys` trick is worth memorising for exactly this reason.

### 5. Membership speed — the big one

```python
if x in big_list:     # O(n) — scans, up to len() comparisons
if x in big_set:      # O(1) — hashes once and jumps
```

Yesterday measured this on dicts and found four orders of magnitude at 100,000 items. Sets are
the same mechanism.

The practical shape is this, and it is the most valuable single refactor available to a beginner:

```python
for item in items:            # 10,000 items
    if item in blacklist:     # a 10,000-item LIST
        ...                   # → 100,000,000 comparisons, ~10 seconds

blacklist = set(blacklist)    # one line
                              # → 10,000 comparisons, instant
```

You have written this nested loop already — Day 22's build contains `if word not in loop`, which
is O(n²) for exactly this reason. One `set()` call fixes it. Day 29 measures the curve.

Building the set costs O(n) once, so it is worth it whenever you will do more than a handful of
lookups.

### 6. `frozenset`

An immutable set. Because it cannot change, it is hashable — so it can be a dict key or an
element of another set:

```python
fs = frozenset([1, 2, 3])
{fs: "a group"}                # works
{frozenset([1, 2]), frozenset([3])}   # a set of sets
```

The typical use is grouping by an unordered collection: "which users have exactly this set of
permissions?"

### 7. Set comprehensions

```python
{w.lower() for w in words}
{len(w) for w in words}
```

Same syntax as Day 22, braces instead of brackets, deduplicated automatically.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Creating, all the operators, order (and its absence), the `set()` speed fix measured, `frozenset`. |
| `build.py`  | The duplicate finder: duplicates with counts, and a full two-way and three-way tag comparison. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`{}` for an empty set.** That is a dict. Use `set()`.

**A list inside a set.** `TypeError: unhashable type: 'list'`. Use a tuple.

**Assuming set order.** There is none. `sorted()` when you print.

**Indexing a set.** Not subscriptable.

**`|` with a list.** Operators need sets on both sides; methods do not.

**`.remove()` on an absent item.** `KeyError`. Use `.discard()` when absence is fine.

**Deduplicating with a set when order matters.** Use `dict.fromkeys`.

**Rebuilding the set inside the loop.** That throws away the entire benefit.

---

## Exercises

1. Deduplicate a list two ways — with and without preserving order.
2. Given two lists of tags, print: in both, in the first only, in the second only, in exactly one.
3. Find the duplicates in a list *and* how many times each appeared. (A set alone cannot do the
   second part — say why.)
4. Time `x in list` against `x in set` at 1,000 / 10,000 / 100,000 items.
5. Use a `frozenset` as a dict key to group people by their exact permission set.
6. Check whether two lists have anything in common, without building the intersection.

---

## Checklist

- [ ] I use `set()` for an empty set
- [ ] I know all four operators and what each answers
- [ ] I know sets have no order and use `sorted()` when printing
- [ ] I convert a list to a set before repeated membership tests
- [ ] I know when to use `dict.fromkeys` instead
- [ ] My finder reports both what is shared and what is missing, in each direction
