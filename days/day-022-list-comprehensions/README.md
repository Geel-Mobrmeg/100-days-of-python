# Day 022 — List comprehensions

**Phase 3 · Data structures** · ~70 minutes

> **Today's build:** rewrite ten explicit loops as comprehensions, then rewrite two of them back and say why.

**Concepts:** map form · filter form · nested comprehensions · when a loop reads better

---

## The article

### Why this day exists

You have written this shape a dozen times:

```python
result = []
for item in items:
    result.append(transform(item))
```

Four lines, of which one is the idea and three are ceremony. A comprehension is the same thing in
one line — and, importantly, it is the form most Python programmers *expect* to read for this
job, so using a loop signals "something unusual is happening here".

The second half of the day is the harder skill: knowing when **not** to. Comprehensions are the
most over-used feature in Python, and a three-clause nested one with a conditional is genuinely
worse than the loop it replaced.

### 1. The map form

```python
squares = [n * n for n in numbers]
```

Read it as: **"n times n, for each n in numbers"**. The expression comes first, which feels
backwards for about a day and then feels natural, because the *result* is what you care about.

The mechanical translation, which is worth doing in your head the first few times:

```python
result = []                         result = [EXPR
for VAR in ITERABLE:          ->            for VAR in ITERABLE]
    result.append(EXPR)
```

The expression can be anything: `f"{n}!"`, `n.strip().lower()`, `int(x)`, a function call.

### 2. The filter form

Add `if` at the end to keep only some items:

```python
evens = [n for n in numbers if n % 2 == 0]
```

```python
result = []                         result = [EXPR
for VAR in ITERABLE:          ->            for VAR in ITERABLE
    if CONDITION:                           if CONDITION]
        result.append(EXPR)
```

Both together, and the order matters:

```python
[n * n for n in numbers if n > 0]
#  ^expr          ^source    ^filter
```

The filter runs **first** conceptually (it decides what gets in), even though it is written last.

**A conditional `if/else` is different and goes at the front**, because it is a ternary
expression (Day 11) inside the value slot, not a filter:

```python
[n if n > 0 else 0 for n in numbers]     # replaces negatives with 0 — keeps ALL
[n for n in numbers if n > 0]            # drops negatives — keeps SOME
```

That distinction — `if` at the end filters, `if/else` at the front transforms — is the single
most confusing thing about comprehensions, and it is worth saying out loud once.

### 3. Nesting

Two loops, flattening a grid:

```python
flat = [cell for row in grid for cell in row]
```

The clauses read **in the same order as the nested loops**: outer first, inner second. That is
the one rule that makes them decodable:

```python
for row in grid:                    [cell
    for cell in row:          ->     for row in grid
        flat.append(cell)            for cell in row]
```

A comprehension can also *produce* nested lists, which is the correct way to build a grid
(Day 21's trap):

```python
grid = [[0] * cols for _ in range(rows)]        # a NEW row each time
```

### 4. The other comprehensions

The same syntax builds three other things — the brackets decide:

```python
[n * n for n in nums]           # list
{n * n for n in nums}           # set        (Day 26) — deduplicates
{n: n * n for n in nums}        # dict       (Day 25)
(n * n for n in nums)           # GENERATOR  (Day 38) — lazy, not a tuple
```

Note the last one: round brackets do **not** give you a tuple. They give a generator, which
produces values on demand and can only be consumed once. That is enormously useful for large
data (Day 38) and surprising the first time you print one.

Inside a function call you can drop the extra brackets:

```python
sum(n * n for n in nums)
any(x < 0 for x in nums)
```

`sum(... for ...)` over a generator never builds the list at all, so it uses constant memory.
That is why `any()` and `all()` can short-circuit.

### 5. When a loop reads better

Use a loop when:

- **The body does more than one thing.** Comprehensions produce a value; if you also need to
  print, log, or update a counter, use a loop.
- **You need `break`.** Comprehensions cannot. (`next(x for x in ...)` is the equivalent.)
- **There are more than two clauses.** `[x for a in b for c in d if e if f]` is a puzzle.
- **The expression does not fit on a line.** Two wrapped lines of comprehension are harder than
  four of loop.
- **You are doing it for the side effect.** `[print(x) for x in items]` builds a list of `None`s
  and throws it away. Use a loop.

The honest test: **if you had to read it twice, write the loop.** Cleverness in a comprehension
costs the reader more than it saves the writer.

### 6. Performance

Comprehensions are genuinely faster than the equivalent loop — roughly 30–50% — because the
append is done in C rather than by a method lookup on every pass. That is a real difference and a
poor reason to choose one. Choose on readability; take the speed as a bonus.

Where it genuinely matters is memory: a generator expression over a million rows uses a few
hundred bytes, and a list comprehension over the same rows uses hundreds of megabytes.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Both forms, the `if` vs `if/else` distinction, nesting, all four bracket types, and a timing comparison. |
| `build.py`  | Ten loops rewritten as comprehensions — and two rewritten back, with reasons. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`if/else` at the end.** `[n for n in x if n>0 else 0]` is a `SyntaxError`. The conditional form
goes at the front.

**Expecting `(x for x in y)` to be a tuple.** It is a generator. Use `tuple(...)`.

**Consuming a generator twice.** The second pass gets nothing.

**A comprehension for its side effects.** Builds and discards a list.

**Nesting in the wrong order.** Clauses read outer-to-inner, same as the loops.

**`[[0]*3]*3` instead of a comprehension.** Day 21's trap.

**A comprehension nobody can read.** Including you, next week.

---

## Exercises

1. Convert to comprehensions: squares; strings uppercased; strings longer than 3 characters;
   numbers converted from text; `(n, n*n)` pairs.
2. Write both: drop negatives, and clamp negatives to zero. Say which uses `if` and which uses
   `if/else`, and why.
3. Flatten a list of lists. Then flatten one that is three deep, and notice where comprehensions
   stop being the right tool.
4. Build a 4×4 multiplication grid with a nested comprehension.
5. Use `sum(...)` with a generator over a million values and compare memory against the list
   version with `sys.getsizeof`.
6. Take the most complex comprehension you wrote today and expand it back to a loop. Show both to
   someone and ask which they would rather debug.

---

## Checklist

- [ ] I can translate a loop to a comprehension mechanically, and back
- [ ] I know `if` at the end filters and `if/else` at the front transforms
- [ ] I know nested clauses read outer-to-inner
- [ ] I know `(...)` gives a generator, not a tuple
- [ ] I never write a comprehension for its side effects
- [ ] I rewrote two back to loops and can justify both
