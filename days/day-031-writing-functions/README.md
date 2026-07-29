# Day 031 — Writing functions

**Phase 4 · Functions & modular code** · ~75 minutes

> **Today's build:** a personal library of ten small utilities you will actually reuse later in the course.

**Concepts:** `def` & `return` · parameters vs. arguments · local scope · implicit `None` · docstrings

---

## The article

### Why this day exists

Every build so far has been one long script that runs top to bottom. That works up to about a
hundred lines and then stops working, for a reason that is not really about length: **a script
has no boundaries.** Any line can touch any variable, so understanding line 200 means having read
lines 1 to 199.

A function draws a boundary. It says: *these are my inputs, this is my output, and nothing else
is my business.* That is the whole idea, and everything else today is mechanics.

Today's build is deliberately practical. You will import it on Day 37, package it on Day 39, and
publish it on Day 97 — so write utilities you actually want.

### 1. The mechanics

```python
def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"

message = greet("Ada")
```

- `def` **defines**; it does not run anything. The body executes only when called.
- **Parameters** are the names in the definition (`name`). **Arguments** are the values passed at
  the call (`"Ada"`). People use the words interchangeably; knowing the difference makes error
  messages readable.
- The parentheses are the call. `greet` is the function object; `greet()` runs it. Passing
  `greet` without parentheses is how you hand a function to `sorted(key=...)` — and forgetting
  them is a common bug that produces no error until much later.

### 2. `return`, and the implicit `None`

`return` sends a value back **and exits immediately.**

```python
def classify(n):
    if n < 0:
        return "negative"       # leaves here
    if n == 0:
        return "zero"
    return "positive"
```

That is the **guard clause** shape from Day 11, finally with something to return with. Handle the
special cases first and leave; the main path ends up unindented at the bottom.

**A function with no `return` returns `None`.** Not nothing — `None`. This is the single biggest
beginner bug in this topic:

```python
def add(a, b):
    print(a + b)         # prints, returns None

total = add(2, 3)        # prints 5; total is None
total + 1                # TypeError, five lines away from the cause
```

**Print or return, and know which you are doing.** A function that prints can only ever be used
one way. A function that returns can be printed, stored, tested (Day 57), summed, or fed to
another function. Return by default; print at the edges of your program.

`return` with several values returns one tuple (Day 23):

```python
return minimum, maximum
lo, hi = min_max(data)
```

### 3. Local scope

Names created inside a function are **local**: they exist during the call and then vanish.

```python
def f():
    x = 10          # local to f
    return x

f()
print(x)            # NameError
```

That is the boundary doing its job. Two functions can both use `i` without any chance of
collision, which is what makes them composable.

A function *can read* names from outside, which is how it sees constants and imports. It **cannot
assign** to them without `global` (Day 34) — and you should not want to.

The rule that matters: **pass what you need in, return what you produce out.** A function that
reads a global is a function that cannot be moved, reused, or tested without dragging its
environment along.

### 4. Mutable arguments

Arguments are passed by **assignment**, which behaves differently depending on mutability
(Day 21):

```python
def rebind(items):
    items = [1, 2, 3]       # rebinds the LOCAL name — caller unaffected

def mutate(items):
    items.append(4)         # mutates the SHARED object — caller sees it
```

Both are legitimate. What is not legitimate is doing the second one by accident. If a function
modifies its arguments, **say so in the name** (`sort_in_place`) and in the docstring. Otherwise
copy first:

```python
def sorted_copy(items):
    items = list(items)     # now it is mine
    items.sort()
    return items
```

### 5. Docstrings

A string literal as the first statement of a function. It is not a comment — it is stored on the
object and shown by `help()`:

```python
def clamp(value, low, high):
    """Return value limited to the range low..high.

    >>> clamp(15, 0, 10)
    10
    """
```

The convention: one imperative line saying what it *returns* ("Return the..."), a blank line, then
detail if needed. If you cannot write that one line, the function is doing more than one thing.

Examples in a docstring that look like a REPL session are **doctests** and can be run:
`python -m doctest -v yourfile.py`. Today's build uses them, so the library tests itself.

### 6. What makes a good function

- **One job.** If the docstring needs "and", split it.
- **A name that says what it returns.** `total_price`, `is_valid`, `parse_date`. Verbs for
  actions, `is_`/`has_` for booleans.
- **Few parameters.** More than about four is a sign that some of them belong together.
- **No surprises.** Do not print, write files or mutate globals from something called
  `calculate_total`.
- **Same input, same output** where possible. Such functions are trivial to test and to reason
  about.
- **Short.** Not a rule, but a long function is usually several short ones that have not been
  separated yet.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `def`/`return`, the implicit `None` bug, scope, mutable arguments, docstrings and doctests. |
| `toolkit.py` | **The library.** Ten utilities with docstrings and doctests. You will reuse this file for the rest of the course. |
| `build.py` | Demonstrates every utility and runs the doctests. |

```bash
python3 lesson.py
python3 build.py
python3 -m doctest -v toolkit.py | tail -3
```

---

## Common mistakes

**Printing instead of returning.** The result is unusable.

**Forgetting `return`.** The function returns `None` and the error appears elsewhere.

**Calling without parentheses.** `sorted(key=len)` is right; `total = my_func` stores the
function, not its result.

**Assigning to a global inside a function.** `UnboundLocalError`, or Day 34's `global`.

**Mutating an argument by accident.** Copy first, or name it honestly.

**A function that needs six arguments.** Some of them are one object (Day 23, Day 41).

**Code after `return`.** Unreachable. Ruff will tell you.

---

## Exercises

1. Write `add` twice — printing and returning. Show that only one can be used in `add(1,2) + 3`.
2. Write a function with three `return`s as guard clauses, then the same logic with nested `if`.
3. Prove a local name does not exist after the call.
4. Write `append_item(items)` that mutates and `with_item(items)` that does not. Prove the
   difference with `is`.
5. Add a doctest to each of your utilities and run `python -m doctest`.
6. Take the longest build you have written and extract three functions from it. Note what each
   needed passed in — that list is what was previously implicit.

---

## Checklist

- [ ] I know a function without `return` returns `None`
- [ ] I return by default and print only at the edges
- [ ] I use guard clauses instead of nesting
- [ ] I know when I am mutating an argument
- [ ] Every function I wrote has a one-line docstring saying what it returns
- [ ] My ten utilities pass their doctests
