# Day 035 — Lambdas and functional tools

**Phase 4 · Functions & modular code** · ~75 minutes

> **Today's build:** the same data pipeline written three ways — loop, comprehension, functional — then judged.

**Concepts:** `lambda` · `map` & `filter` · `functools.reduce` · readability limits

---

## The article

### Why this day exists

Python has functional tools, and Python is not a functional language. Both halves matter.

`lambda` and `key=` you will use constantly. `map` and `filter` you will read in other people's
code and rarely write. `reduce` you should be able to recognise and almost never use. Today is
about knowing which is which, and the build is deliberately a *judgement* exercise rather than a
technique one.

### 1. `lambda`

An expression that makes a function, without a name:

```python
double = lambda n: n * 2          # don't do this
def double(n): return n * 2       # do this
```

Assigning a lambda to a name is pointless — you have written a worse `def` that loses the name in
tracebacks. Ruff flags it (E731).

`lambda` earns its place when the function is **an argument to something else** and is too small
to deserve a name:

```python
sorted(people, key=lambda p: p["age"])
max(items, key=lambda i: i.score)
sorted(counts.items(), key=lambda kv: -kv[1])
```

Restrictions, which are the design: one expression, no statements, no assignment, no `return`, no
type hints. If you want any of those, you want a `def`.

### 2. `map` and `filter`

```python
map(str.upper, words)            # apply to each
filter(str.isalpha, words)       # keep where true
```

Both are **lazy** — they return iterators, not lists. `print(map(...))` shows
`<map object at 0x...>`, and consuming one twice gives nothing the second time. Wrap in `list()`
when you need a list.

The comparison that matters:

```python
map(lambda n: n * 2, numbers)      # a lambda AND a map
[n * 2 for n in numbers]           # just the expression
```

**When the transform needs a lambda, the comprehension is clearer.** When you already have a
named function, `map` is fine and arguably neater:

```python
map(str.strip, lines)              # good
[line.strip() for line in lines]   # equally good
```

`filter(None, items)` is a genuinely useful idiom: it drops every falsy value.

### 3. `reduce`

```python
from functools import reduce
reduce(lambda a, b: a + b, [1, 2, 3, 4])       # 10
```

`reduce` collapses a sequence to one value by applying a two-argument function cumulatively. It
was a builtin in Python 2; Guido moved it to `functools` deliberately, arguing that almost every
real use is clearer as a loop or as an existing builtin.

He was right. Before reaching for `reduce`, check whether one of these already exists:

| Instead of `reduce(...)` | Use |
|---|---|
| `lambda a, b: a + b` | `sum()` |
| `lambda a, b: a if a > b else b` | `max()` |
| `lambda a, b: a * b` | `math.prod()` |
| string concatenation | `"".join()` |
| `lambda a, b: a and b` | `all()` |

That leaves genuinely custom accumulations — merging dicts, composing functions, running a state
machine — where `reduce` is legitimate and a loop is usually still clearer to the next reader.

Always pass the **initial value**: `reduce(f, items, 0)`. Without it, an empty sequence raises
`TypeError`.

### 4. The other `functools` tools

```python
from functools import partial
int_from_binary = partial(int, base=2)
int_from_binary("1010")            # 10
```

`partial` fixes some arguments and returns a new function. It is a closure (Day 34) with a
standard name, and it is genuinely useful for callbacks.

`operator` replaces the most common trivial lambdas, and is faster:

```python
from operator import itemgetter, attrgetter, add
sorted(rows, key=itemgetter("age"))       # rather than lambda r: r["age"]
```

### 5. Which to use

The honest ranking for Python, in order of preference:

1. **A comprehension** — for map/filter work. This is the Pythonic default.
2. **A generator expression** — when the data is large or you only need one pass.
3. **A `for` loop** — when there are side effects, early exit, or more than one output.
4. **`map`/`filter` with a *named* function** — neat, and reads well.
5. **`map`/`filter` with a lambda** — almost always worse than a comprehension.
6. **`reduce`** — only when no builtin fits.

The reason is not taste. A comprehension puts the transformation, the source and the filter in
**reading order**; `map(lambda x: f(x), filter(lambda x: g(x), items))` puts them inside out, and
you read it right to left.

### 6. Where functional thinking genuinely wins

Setting the style question aside, three ideas from this world are worth keeping:

- **Pure functions** — same input, same output, no side effects. Trivial to test (Day 57) and to
  reason about.
- **Immutability** — return new values rather than mutating (Day 21's aliasing bugs).
- **Functions as values** — passing behaviour as an argument, which is `key=`, decorators, and
  callbacks.

Those three make code better in any style. `reduce` does not.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `lambda` and its limits, laziness, `map`/`filter`/`reduce`, `partial`, `operator`. |
| `build.py`  | One pipeline, four implementations, verified identical, timed, and judged on readability. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`f = lambda x: ...`** — just use `def`. Ruff E731.

**Printing a `map` object.** It is lazy. `list()` it.

**Consuming an iterator twice.** The second pass is empty.

**`reduce` where `sum` exists.**

**`reduce` with no initial value on a possibly-empty sequence.** `TypeError`.

**A lambda with a conditional and two calls in it.** Write a `def`.

**Nesting `map` inside `filter` inside `map`.** Unreadable. Comprehension.

---

## Exercises

1. Write the same transform as a comprehension, a `map` with a lambda, and a `map` with a named
   function. Rank them.
2. Show that a `map` object is consumed after one pass.
3. Replace three `reduce` calls with builtins.
4. Use `filter(None, ...)` to drop falsy values, then write the comprehension equivalent.
5. Use `partial` to make `int_from_hex`, then do the same with a closure and compare.
6. Take the most functional-looking line you can write, then rewrite it as a loop and show both to
   someone.

---

## Checklist

- [ ] I never assign a lambda to a name
- [ ] I know `map` and `filter` are lazy
- [ ] I prefer comprehensions to `map` + `lambda`
- [ ] I check for a builtin before using `reduce`
- [ ] I can use `partial` and `itemgetter`
- [ ] I judged my four pipeline versions and can defend the ranking
