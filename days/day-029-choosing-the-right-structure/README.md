# Day 029 — Choosing the right structure

**Phase 3 · Data structures** · ~75 minutes

> **Today's build:** benchmark membership tests across a list, a set and a dict at three sizes; explain the curve.

**Concepts:** list vs. set vs. dict · lookup cost · when order matters · measuring it

---

## The article

### Why this day exists

You now have four containers. This day is about picking, and about the one number that decides it
more often than anything else: **how the cost grows as the data grows.**

The build measures it rather than asserting it, because the difference between "sets are faster"
and "sets were 3,000 times faster at 100,000 items and 30 times faster at 1,000" is the
difference between a slogan and knowledge you can act on.

### 1. Big-O, briefly

Big-O describes **how the cost grows with the size of the input**, ignoring constants:

| Notation | Name | 10× the data means | Example |
|---|---|---|---|
| O(1) | constant | same cost | `d[key]`, `len(x)`, `list.append` |
| O(log n) | logarithmic | +1 step or so | binary search (Day 12) |
| O(n) | linear | 10× cost | `x in list`, `sum()`, one loop |
| O(n log n) | linearithmic | ~10× cost | `sorted()` |
| O(n²) | quadratic | **100× cost** | nested loop, `in` inside a loop |

It says nothing about small inputs. An O(n²) algorithm on 10 items beats an O(n) one with a big
constant. It is a statement about **the shape of the curve**, and it only starts mattering when
the data grows — which it always does, later, in production, on a Friday.

The one that ruins programs is O(n²), and it usually arrives disguised, as `if x in some_list`
inside a loop over another list.

### 2. The four containers

| | list | tuple | dict | set |
|---|---|---|---|---|
| ordered | yes | yes | insertion | **no** |
| mutable | yes | **no** | yes | yes |
| duplicates | yes | yes | keys unique | **no** |
| index by position | yes | yes | no | no |
| `x in c` | **O(n)** | **O(n)** | O(1) | O(1) |
| lookup by key | O(n) | O(n) | O(1) | — |
| append / add | O(1) | — | O(1) | O(1) |
| insert / delete at front | O(n) | — | — | — |
| can be a dict key | no | **yes** | no | no (`frozenset` yes) |

### 3. Choosing

Ask three questions in order:

**1. Do I need to look things up?**
Yes, by identity → **set**. Yes, by key with a value attached → **dict**. This question alone
decides most cases, and getting it wrong is what makes programs slow.

**2. Does order matter?**
Position matters, or duplicates matter → **list**. Otherwise the set/dict answer stands.

**3. Is it a fixed record, or will it be a key?**
→ **tuple**.

A short decision list:

- "Is this in my collection?", asked more than a few times → **set**
- "What is the value for this name?" → **dict**
- "The third item" / "in the order they arrived" / duplicates matter → **list**
- "A point, a row, a return value" → **tuple**
- "Unique, and I need to compare collections" → **set**

### 4. The refactor that matters

```python
# before: O(n × m)
for item in items:              # 10,000
    if item in blocklist:       # a 10,000-item LIST → 10,000 comparisons
        ...                     # = 100,000,000 operations

# after: O(n + m)
blocked = set(blocklist)        # one line, O(m) once
for item in items:
    if item in blocked:         # O(1)
        ...                     # = 20,000 operations
```

**One line, 5,000× less work.** This is the highest-value performance change available to
someone at your stage, and it needs no cleverness — only noticing that `in` on a list scans.

Building the set costs one pass, so it pays off from about three lookups onward. What does *not*
pay is rebuilding it inside the loop, which throws the entire benefit away.

### 5. When the "slow" structure is right

- **Small n.** At 10 items, everything is instant. Do not contort code for a list of five.
- **You need order or duplicates.** Correctness first, always.
- **You iterate rather than look up.** A `for` over a list is the same speed as over a set.
- **Memory matters.** A set uses roughly 3–4× the memory of a list of the same items.
- **The items are unhashable.** Lists of dicts cannot go in a set at all.

### 6. How to measure

```python
import timeit
timeit.timeit(lambda: target in data, number=1000)
```

Rules that make a benchmark mean something — and today's build breaks the first one on purpose to
show what happens:

1. **Use realistic data.** Yesterday's `sorted()` demo reported the *opposite* of the truth
   because the input was already sorted and Timsort detects that. Benchmark on data shaped like
   your real data.
2. **Measure the worst case.** For `x in list`, that is the last element or a missing one.
3. **Repeat.** One run measures noise.
4. **Compare ratios, not seconds.** Seconds depend on the machine; the ratio and its *growth*
   are the finding.
5. **Do not include setup in the timing.**

Day 95 does this properly with `cProfile`. Today is about the habit: **measure, do not assume.**

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The comparison table live, the three questions, and the O(n²) refactor measured. |
| `build.py`  | The benchmark: three structures, three sizes, best and worst case, and the curve explained. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`in` on a list inside a loop.** The commonest accidental O(n²) there is.

**Rebuilding the set inside the loop.** Benefit gone.

**Optimising a list of ten.** Wasted effort and worse code.

**Benchmarking on unrealistic data.** Sorted input, all-identical values, best-case lookups.

**Timing one run.** Noise.

**Using a set and then needing the order.** Correctness first.

**Assuming `list.append` is slow.** It is O(1) amortised. `insert(0, x)` is the slow one.

---

## Exercises

1. Time `x in list` and `x in set` at 1,000 / 10,000 / 100,000. Tabulate the ratios and describe
   how the ratio itself grows.
2. Time looking up a *missing* item vs the *first* item in a list. Explain the difference.
3. Write an O(n²) duplicate finder, time it at 5,000, then rewrite with a set and time again.
4. Compare `sys.getsizeof` for a list, set and dict of 100,000 ints.
5. Time `list.insert(0, x)` against `deque.appendleft` for 50,000 items.
6. Find one place in your earlier builds with `in` on a list inside a loop. Fix it and measure.

---

## Checklist

- [ ] I can state what O(1), O(n) and O(n²) mean for 10× the data
- [ ] I ask "will I look things up?" before choosing a container
- [ ] I convert to a set before repeated membership tests
- [ ] I know the memory cost of that choice
- [ ] I benchmark on realistic data, worst case, repeated
- [ ] I can explain my benchmark's curve, not just quote its numbers
