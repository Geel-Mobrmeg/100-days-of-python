# Day 014 — break, continue and loop-else

**Phase 2 · Control flow** · ~70 minutes

> **Today's build:** a prime number finder that stops checking the moment it knows the answer.

**Concepts:** early exit · skipping iterations · `for...else` · flag variables

---

## The article

### Why this day exists

A loop that always runs to completion is doing work it does not need to do. Once you have found
what you were looking for, every further pass is wasted — and in a search over a million items,
"wasted" can mean minutes.

Today is about leaving early, skipping the uninteresting, and — the part almost nobody knows —
Python's answer to the question "how do I tell whether the loop found anything?"

### 1. `break`

`break` leaves the loop immediately. Nothing after it in the body runs, the condition is not
re-checked, execution continues after the loop.

```python
for n in range(2, 1000):
    if 1000 % n == 0:
        print(f"smallest factor: {n}")
        break                       # found it. Stop.
```

Without the `break` that loop does 998 divisions to answer a question settled after one.

**`break` only leaves the innermost loop.** In nested loops (tomorrow) it does not leave both,
which is the single most common surprise about it.

### 2. `continue`

`continue` skips the rest of *this* pass and goes to the next one.

```python
for line in lines:
    if not line.strip():
        continue                    # blank line, nothing to do
    if line.startswith("#"):
        continue                    # comment
    process(line)
```

That is the **guard clause** shape from Day 11, finally with something to leave with. Compare:

```python
for line in lines:                        for line in lines:
    if line.strip():                          if not line.strip():
        if not line.startswith("#"):              continue
            process(line)                     if line.startswith("#"):
                                                  continue
                                              process(line)
```

The right-hand version has the real work at one level of indentation instead of three, and each
rejection reason sits on its own line where it can be read, changed or deleted independently.
For more than one condition, prefer it.

The classic `continue` bug is in a `while` loop: if the progress step is *after* the `continue`,
you skip it and hang forever.

```python
while i < len(items):
    if bad(items[i]):
        continue           # i never increments. Infinite loop.
    i += 1
```

This is one more reason to use `for`.

### 3. `for...else` — the one nobody knows

A loop can have an `else` clause. It runs **only if the loop finished without a `break`**:

```python
for n in range(2, number):
    if number % n == 0:
        print(f"{number} is divisible by {n}")
        break
else:
    print(f"{number} is prime")
```

The name is genuinely bad. Read `else` here as **"no break"** — if it had been spelled
`nobreak` nobody would ever have been confused. It means *the search ran to completion and found
nothing.*

It works on `while` too, and it is exactly the tool for a search loop. The alternative is a flag
variable:

```python
found = False
for n in range(2, number):
    if number % n == 0:
        found = True
        break
if not found:
    print("prime")
```

Both are correct. The flag version is more familiar to more readers; the `else` version has one
fewer variable to keep in sync. Use `else` when the loop is unmistakably a search, and a flag
when the loop also does something else — and always add a comment, because the reader may not
know the feature exists.

Note: `else` runs when the loop ends naturally, **including when it ran zero times**. `for n in
range(2, 2)` executes no passes and goes straight to `else`. For the prime test that is exactly
right — 2 has nothing to check and is prime — and it is the kind of edge case worth confirming
rather than assuming.

### 4. Knowing when to stop: the prime example

The naive primality test checks every number from 2 up to *n−1*. Three improvements, each one a
line:

1. **Stop at the first factor** (`break`) — a composite number usually exits almost immediately.
2. **Stop at √n.** If *n = a × b*, one of *a* and *b* is at most √n. So a factor above √n implies
   a matching factor below it, which you would already have found. This turns 999,983 divisions
   into 999.
3. **Skip the evens.** Check 2 once, then only odd divisors. Halves the remaining work.

Together these take the test on 999,983 from about a million operations to about 500. Today's
build measures all four versions so you can see it rather than take it on faith.

The general lesson is the one worth keeping: **the biggest speedups come from doing less work,
not from doing the same work faster.** Day 95 makes this formal.

### 5. `break` and `else` in `while`

Everything above applies to `while` too:

```python
while attempts < 3:
    if try_it():
        break
else:
    print("all three attempts failed")
```

That is a genuinely elegant retry, and it is the shape you will meet again on Day 66.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `break`, `continue`, `for...else`, flags, and the guard-clause rewrite side by side. |
| `build.py`  | The prime finder — four versions, with the operation counts that justify each one. |

```bash
python3 lesson.py
python3 build.py
python3 build.py 999983
```

---

## Common mistakes

**Expecting `break` to leave both loops.** It leaves one. Tomorrow covers the fix.

**`continue` before the increment in a `while`.** Infinite loop.

**Reading `else` as "otherwise".** It means "no break".

**Forgetting `else` runs when the loop ran zero times.** Usually correct, occasionally not.

**A flag that is never reset** inside an outer loop. It stays `True` from a previous pass.

**Checking divisors up to `n`.** Up to `int(n ** 0.5) + 1` is enough, and it is not a rounding
detail — get the `+ 1` wrong and you will misclassify perfect squares.

---

## Exercises

1. Find the first number over 1000 divisible by both 7 and 13. Stop as soon as you find it.
2. Sum only the positive numbers in a mixed list, using `continue` to skip the rest.
3. Write a search with `for...else` and then the same search with a flag. Show both to someone
   and ask which they find clearer.
4. Confirm your prime test says: 2 prime, 3 prime, 4 not, 9 not, 25 not, 1 not, 0 not, −7 not.
   Perfect squares and 1 are where naive versions break.
5. Count how many divisions your test performs for 97 versus 96. Explain the difference.
6. Print the first 20 primes. Then all primes under 100 using a sieve, and compare the counts.

---

## Checklist

- [ ] I know `break` exits only the innermost loop
- [ ] I use `continue` to flatten nested conditions in loops
- [ ] I can read `for...else` as "no break"
- [ ] I know why √n is the right upper bound for a factor search
- [ ] My prime test is correct for 0, 1, 2 and perfect squares
- [ ] I can say how many operations my finder saved, with a number
