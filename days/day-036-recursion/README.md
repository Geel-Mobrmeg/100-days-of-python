# Day 036 — Recursion

**Phase 4 · Functions & modular code** · ~85 minutes

> **Today's build:** a directory tree walker that prints an indented listing of any folder you point it at.

**Concepts:** base case · the call stack · recursion limits · memoisation · when to use iteration

---

## The article

### Why this day exists

Recursion is taught early, badly, with factorials — which are better as loops — and so most people
finish believing it is a clever way to do easy things. It is not. It is the *natural* way to do
one specific kind of thing: **problems whose shape contains a smaller copy of themselves.**

A directory contains directories. A comment has replies which have replies. JSON contains JSON.
An expression contains expressions. For all of those, the recursive solution is shorter *and*
clearer than the iterative one, and today's build is deliberately one of them.

### 1. The two parts

Every recursive function has exactly two:

```python
def countdown(n):
    if n <= 0:            # BASE CASE — stop, do not recurse
        print("liftoff")
        return
    print(n)
    countdown(n - 1)      # RECURSIVE CASE — the same problem, SMALLER
```

- **The base case** stops it. Write this first, always.
- **The recursive case** must make the problem *strictly smaller* and must eventually reach the
  base case.

Miss the base case, or fail to shrink the problem, and you get
`RecursionError: maximum recursion depth exceeded` — which is Python's version of a stack
overflow, and is a much friendlier failure than the segfault other languages give you.

The three questions to ask of any recursive function:

1. What is the smallest input, and what do I return for it?
2. Does every recursive call get *strictly* closer to that?
3. If I assume the recursive call is correct, is my answer correct?

Question 3 is the leap. **Trust the recursion.** Do not try to trace three levels down in your
head — assume the inner call works, and check that you combine its result correctly. That is the
whole technique, and people who find recursion hard are almost always trying to simulate the
stack mentally instead.

### 2. The call stack

Each call gets its own frame with its own locals. They stack up, and unwind in reverse:

```
countdown(3)
  countdown(2)
    countdown(1)
      countdown(0)   ← base case, returns
    returns
  returns
returns
```

That is why the traceback on Day 9 said "most recent call last".

Python's default limit is 1000 frames:

```python
import sys
sys.getrecursionlimit()      # 1000
sys.setrecursionlimit(3000)  # possible; usually the wrong fix
```

Raising it is almost always wrong. A depth over 1000 usually means either a missing base case or
a problem that wants iteration. Real C-level stack exhaustion segfaults regardless of the limit.

**Python has no tail-call optimisation**, deliberately — Guido has said so repeatedly. So a
recursion of depth 100,000 will not work no matter how you write it, and the answer is a loop.

### 3. Where recursion genuinely wins

| Problem | Why |
|---|---|
| directory trees | a folder contains folders |
| nested JSON / config | a dict contains dicts (Day 28) |
| comment threads | replies have replies |
| parsing expressions | `(1 + (2 * 3))` |
| divide and conquer | quicksort, mergesort, binary search |
| flood fill, maze solving | the grid branches |

The common shape: **the data is a tree**, and the number of levels is not known in advance.

Where it loses: anything you can express as "for each item in a flat sequence". Factorial,
Fibonacci, summing a list, reversing a string — all clearer and faster as loops. Fibonacci is the
worst example anyone teaches: naive recursion makes over a million calls for `fib(28)` (Day 34
measured it) because it recomputes the same values exponentially often.

### 4. Memoisation

If a recursion recomputes the same arguments, cache them — which is exactly Day 34's build:

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`fib(100)` now returns instantly instead of never. One line turns an exponential algorithm into a
linear one, without changing the algorithm.

`@cache` (3.9+) is `@lru_cache(maxsize=None)`. Both require **hashable arguments** — no lists, no
dicts — for the reason Day 23 gave.

### 5. Converting recursion to iteration

Every recursion can become a loop. Two cases:

**Linear recursion** (one call per level) → a simple loop:

```python
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

**Tree recursion** (several calls per level) → an explicit **stack**:

```python
def walk(root):
    stack = [root]
    while stack:
        current = stack.pop()
        for child in children_of(current):
            stack.append(child)
```

You are doing by hand exactly what the call stack was doing for you. The gain is no depth limit;
the cost is that the code is longer and the traversal order needs thought — `pop()` gives you
depth-first, `pop(0)` (or a `deque`) gives breadth-first.

Today's build implements both, on the same tree, and compares them.

### 6. Practical notes for the build

Walking a real filesystem has three hazards that a textbook tree does not:

- **Symlinks** can point at a parent, giving an infinite tree. Check `path.is_symlink()`.
- **Permissions** — a directory you cannot read raises `PermissionError` mid-walk.
- **Depth** — a deep tree can exhaust the stack, so cap it.

Also: `os.walk()` and `Path.rglob()` already exist and are iterative. Writing the recursive
version once is how you understand what they do; using them afterwards is correct.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Base cases, the stack visualised, `RecursionError`, memoisation measured, tree vs linear. |
| `build.py`  | The tree walker: recursive and iterative, sizes rolled up, depth-limited, symlink-safe. |

```bash
python3 lesson.py
python3 build.py                 # walks this repository
python3 build.py .. 3
python3 build.py --iterative
```

---

## Common mistakes

**No base case.** `RecursionError`.

**A base case that is never reached.** Same error; harder to see.

**Raising the recursion limit to fix a bug.** It is a symptom.

**Recursion where a loop is obvious.** Slower and no clearer.

**Naive Fibonacci.** Exponential. Add `@cache`.

**Returning nothing from the recursive branch.** `return f(n-1)`, not `f(n-1)`.

**Following symlinks while walking a filesystem.** Infinite loop.

**Mutable default as an accumulator.** Day 32's B006, and it now accumulates across whole calls.

---

## Exercises

1. Write `countdown(n)` and remove the base case. Read the error.
2. Sum a nested list of arbitrary depth: `[1, [2, [3, [4]]]]`.
3. Write recursive and iterative factorial. Time both at n=500.
4. Write naive `fib`, add `@cache`, and compare the call counts at n=30.
5. Count files in a directory tree recursively, then with `os.walk`.
6. Convert your recursive walker to an explicit stack, and make it breadth-first by changing one
   line.

---

## Checklist

- [ ] I write the base case first
- [ ] I can state the three questions and answer them for a function I wrote
- [ ] I trust the recursive call instead of tracing it mentally
- [ ] I know Python's limit and why raising it is usually wrong
- [ ] I reach for recursion for trees and loops for sequences
- [ ] My walker handles symlinks, permissions and depth without crashing
