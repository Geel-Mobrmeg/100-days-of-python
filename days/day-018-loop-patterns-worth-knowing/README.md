# Day 018 — Loop patterns worth knowing

**Phase 2 · Control flow** · ~80 minutes

> **Today's build:** compute mean, median, mode, min and max over a list — without importing anything.

**Concepts:** accumulator · search-and-flag · running min/max · single-pass thinking

---

## The article

### Why this day exists

There are perhaps eight loop shapes in all of programming. You have been reinventing them for a
week; today they get names. Naming them matters because a named pattern is one you *recognise*
instead of deriving — you stop thinking "how do I do this" and start thinking "oh, that's a
running maximum".

The build is deliberately "no imports". `statistics.median()` exists and you should use it in
real code. Writing it once yourself is how you learn what it costs and where it breaks.

### 1. The accumulator

Collect something across every item.

```python
total = 0
for n in numbers:
    total += n
```

The rule from Day 12 still holds: **start at the value meaning "nothing yet"** — `0` for a sum,
`1` for a product, `""` or `[]` for a collection. And the accumulator lives *outside* the loop.

Variants: counting (`count += 1`), collecting (`result.append(x)`), building a string (collect
into a list, then `"".join()` — never `+=` in a loop).

### 2. Running min / max

An accumulator whose combining step is a comparison.

```python
lowest = numbers[0]                  # start with a REAL value
for n in numbers[1:]:
    if n < lowest:
        lowest = n
```

The initialisation is the whole difficulty:

| Start | Verdict |
|---|---|
| `0` | **wrong** — no positive number ever beats it |
| `float("inf")` | correct, and neat |
| `numbers[0]` | correct, and fails loudly on an empty list |
| `None` | correct, needs an `is None` test in the loop |

`numbers[0]` is usually the best of these because an empty input is genuinely an error for
"minimum", and an `IndexError` says so immediately. `float("inf")` silently returns infinity,
which then travels.

**Track the position, not just the value**, when you need to know *which* item won:

```python
best_i = 0
for i, n in enumerate(numbers):
    if n > numbers[best_i]:
        best_i = i
```

Note `>` rather than `>=`: with `>` you keep the *first* maximum, with `>=` the *last*. That is a
real decision, not a detail, and it matters the moment there are ties.

### 3. Search-and-flag / early exit

```python
found = False
for item in items:
    if matches(item):
        found = True
        break
```

Or `for...else` (Day 14). Or, best of all, `any()` and `all()`, which do exactly this and
short-circuit:

```python
if any(x < 0 for x in numbers): ...
if all(x > 0 for x in numbers): ...
```

If you are writing a search-and-flag loop whose body is one condition, `any`/`all` is shorter and
faster.

### 4. Pairwise

Compare each item with its neighbour — for detecting changes, runs, or sortedness:

```python
for i in range(1, len(items)):
    previous, current = items[i - 1], items[i]
```

Or keep a `previous` variable, initialised to something that cannot occur. `zip(items, items[1:])`
is the neat version and Day 23 makes it read better.

### 5. Single-pass thinking

Here is the idea that separates today from Day 13.

You can compute count, sum, min, max, and mean in **one** pass over the data:

```python
for n in numbers:
    count += 1
    total += n
    if n < lowest: lowest = n
    if n > highest: highest = n
```

Five statistics, one traversal. The alternative — `len(numbers)`, `sum(numbers)`,
`min(numbers)`, `max(numbers)` — is four passes. For a list in memory, four passes over a
million items is fine and the four builtins are clearer, so **use the builtins.**

But single-pass thinking matters enormously in two cases:

- **The data does not fit in memory.** A 500 MB log file (Day 38) can be traversed once but not
  held. Anything needing two passes needs a different design.
- **The data arrives once.** A network stream, a sensor, a generator. There is no "start again".

So the pattern to internalise is: *what can I compute while the data goes past exactly once?*
Mean, yes. Min and max, yes. Median — **no**, because you cannot know the middle value until you
have seen them all. That asymmetry is why the build separates them.

### 6. The three averages, and why there are three

- **Mean** — the total shared out. Sensitive to outliers: one billionaire changes a town's mean
  income and tells you nothing about a typical resident.
- **Median** — the middle value when sorted. Immune to outliers. This is why incomes and house
  prices are always reported as medians.
- **Mode** — the most common value. The only one that works on non-numeric data ("most common
  word"), and the only one that can legitimately not exist or be tied.

Two edge cases the build has to decide about, in writing:

**Median of an even-length list** is conventionally the mean of the two middle values — which
means the median of a list of integers can be a non-integer, and can be a value not present in
the data.

**Mode with a tie** has no single right answer. Return all of them, return the first, or return
nothing. Python's `statistics.mode()` returns the first encountered;
`statistics.multimode()` returns all. Decide, and write it down.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The five patterns, single-pass vs multi-pass, and the first/last-maximum decision. |
| `build.py`  | All five statistics from scratch, with the edge cases enumerated and checked. |

```bash
python3 lesson.py
python3 build.py
python3 build.py 3 1 4 1 5 9 2 6
```

---

## Common mistakes

**`lowest = 0`.** Nothing positive will ever be lower.

**Accumulator inside the loop.** It resets every pass.

**`>=` where you meant `>`** in a running maximum. Changes which tie wins.

**Median without sorting.** The middle *index* is not the middle *value*.

**Median of an even list taking one middle element.** It is the mean of the two.

**Assuming a unique mode.** `[1, 1, 2, 2]` has two.

**Empty input.** Mean divides by zero, min has nothing to return. Decide what happens.

---

## Exercises

1. Compute count, sum, min, max and mean in a single pass. Then with the four builtins. Which is
   clearer, and when does the first one win?
2. Find the position of the maximum. Make it return the first maximum, then the last. Test with
   `[3, 1, 3]`.
3. Detect whether a list is already sorted, in one pass, stopping at the first violation.
4. Find the longest run of identical values in a sequence.
5. Compute the median without `sorted()` — write the sort yourself. Then use `sorted()` and
   compare your answers on 100 random lists.
6. Decide what your functions do for `[]` and for `[5]`. Write the answers down first, then make
   the code agree.

---

## Checklist

- [ ] I can name the accumulator, running-extremum, search-and-flag and pairwise patterns
- [ ] I initialise extrema correctly and know why `0` is wrong
- [ ] I know whether my max returns the first or last tie
- [ ] I can say which statistics are computable in one pass and which are not
- [ ] My median handles even-length lists
- [ ] My code does something defensible with an empty list
