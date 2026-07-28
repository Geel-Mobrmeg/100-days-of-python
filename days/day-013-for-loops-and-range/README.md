# Day 013 — for loops and range

**Phase 2 · Control flow** · ~70 minutes

> **Today's build:** a multiplication table generator that lines up perfectly for any size you ask for.

**Concepts:** iterating sequences · `range(start, stop, step)` · `enumerate()` · `zip()`

---

## The article

### Why this day exists

Yesterday's loops all had the same three lines of bookkeeping around them: set a counter, test
it, increment it. Every one of those lines is a place to make a mistake, and none of them is
about what you were actually trying to do.

`for` deletes all three. It is the loop you will write nine times out of ten, and today is also
where the repetition in every build you have written so far finally collapses. Day 10's quiz is
about sixty lines expressing three ideas; by tonight you can write it in twelve.

### 1. `for` iterates over things, not numbers

This is the mental shift, and people coming from C or Java find it genuinely strange at first.
Python's `for` does not count. It **takes items out of something, one at a time**:

```python
for letter in "Python":
    print(letter)

for part in "Ada Augusta Byron".split():
    print(part)
```

There is no index, no counter, no bound. The loop asks the thing for its next item until it runs
out. Anything that can hand over items one at a time is **iterable**: strings, lists, tuples,
dicts, sets, files, ranges.

Compare with yesterday:

```python
i = 0                             # for
while i < len(parts):             #     for part in parts:
    part = parts[i]               #         print(part)
    print(part)
    i += 1
```

Four lines of bookkeeping and three chances for an off-by-one, replaced by zero of each. If you
ever write the left-hand version, you have written a `for` loop badly.

### 2. `range()` — when you *do* want numbers

```python
range(5)           # 0, 1, 2, 3, 4          — stop only
range(1, 6)        # 1, 2, 3, 4, 5          — start, stop
range(0, 10, 2)    # 0, 2, 4, 6, 8          — start, stop, step
range(10, 0, -1)   # 10, 9, 8, ... 1        — counting down
```

**`stop` is excluded**, exactly as in slicing (Day 3), and for the same reason: `range(n)`
produces exactly `n` values, and `range(a, b)` produces exactly `b - a` of them. That one
consistency removes a whole class of arithmetic from your head.

Two practical notes:

- `range` is **lazy**. `range(1_000_000_000)` is instant and uses no memory — it computes values
  as they are asked for rather than building a list. `print(range(5))` shows `range(0, 5)`, not
  the numbers; wrap it in `list()` to see them.
- **A `range` is not a list.** You cannot append to it, and it has no `.index()` worth using.

`for _ in range(3)` is the idiom for "do this three times". The underscore is a real variable
name that conventionally means "I am deliberately not using this".

### 3. `enumerate()` — index *and* item

The commonest beginner code smell in Python:

```python
for i in range(len(items)):        # DON'T
    print(i, items[i])
```

The tool for this exists:

```python
for i, item in enumerate(items):         # 0-based
    print(i, item)

for n, item in enumerate(items, start=1):  # 1-based, for humans
    print(n, item)
```

`enumerate` yields pairs, and the `for` line unpacks each pair into two names — that is **tuple
unpacking**, covered properly on Day 23. `start=1` is the right call whenever the number is
being shown to a person; nobody wants to read "Question 0".

Only use `range(len(x))` when you genuinely need the index *and not the item*, which is rare.

### 4. `zip()` — walk two sequences together

```python
names = ["Ada", "Charles", "Alan"]
scores = [95, 87, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

`zip` **stops at the shortest input**, silently. That is usually what you want and occasionally a
data-loss bug — if the two lists should be the same length and are not, `zip` will hide it.
`zip(a, b, strict=True)` (Python 3.10+) raises instead, and is the better default when you
believe the lengths match.

`zip` takes any number of iterables, and pairs with `enumerate` naturally:

```python
for n, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"{n}. {name}: {score}")
```

### 5. Do not modify what you are iterating

```python
for item in items:
    if bad(item):
        items.remove(item)      # BUG — skips elements, silently
```

The loop is tracking a position; removing an item shifts everything after it down, so the next
item gets skipped. No error, wrong answer.

Build a new collection instead — which is Day 22's comprehensions — or iterate over a copy with
`items[:]`. Lists arrive tomorrow; the habit starts today.

### 6. `for` versus `while`

| Use | When |
|---|---|
| `for` | you know what you are iterating over — a sequence, a range, a file |
| `while` | you loop until a condition changes and cannot know how many passes |

Roughly 90% of loops are `for`. If a `while` loop's condition is just a counter you are
maintaining yourself, it wanted to be a `for`.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Iteration, `range`, `enumerate`, `zip`, the modify-while-iterating bug, and Day 10's quiz collapsed to twelve lines. |
| `build.py`  | The multiplication table — sized, aligned and boxed from the data, at any dimension. |

```bash
python3 lesson.py
python3 build.py
python3 build.py 12
python3 build.py 15 7      # 15 rows, 7 columns
```

---

## Common mistakes

**`for i in range(len(items))`** — use `enumerate`.

**Expecting `range(1, 5)` to include 5.** Stop is excluded, always.

**`range(5, 1)`** — produces nothing. Counting down needs a negative step.

**Modifying a list while iterating over it.** Silently skips items.

**`zip` hiding a length mismatch.** Use `strict=True` when they should match.

**Using the loop variable after the loop.** It survives, holding the last value — which is
occasionally useful and usually a bug. It is also undefined if the loop ran zero times.

**Building a string with `+=` in a loop.** Quadratic. Collect and `"".join()` (Day 4).

---

## Exercises

1. Print the 7 times table using `for` and `range`. Then print it backwards, then just the even
   multiples — changing only the `range` arguments.
2. Rewrite yesterday's min/max loop with `for`. Count the lines you deleted.
3. Use `enumerate(..., start=1)` to print a numbered list. Then break it by using `range(len())`
   and note what you had to add.
4. Given names and scores, use `zip` to print them aligned. Now make the lists different lengths
   and observe the silent truncation; then add `strict=True`.
5. Collapse Day 10's quiz to under fifteen lines using a list of questions and one `for`. Diff it
   against the original — that diff is the argument for loops.
6. Print a right triangle of stars of height `n`, then an inverted one, then both. You will need
   nested loops, which is Day 15 — try it anyway.

---

## Checklist

- [ ] I iterate over items directly, not over indices
- [ ] I know `range` excludes its stop and produces `stop - start` values
- [ ] I use `enumerate` instead of `range(len(...))`
- [ ] I know `zip` truncates silently and when to pass `strict=True`
- [ ] I never mutate the thing I am iterating over
- [ ] My table aligns for single- and triple-digit products alike
