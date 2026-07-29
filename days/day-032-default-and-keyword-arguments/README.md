# Day 032 — Default and keyword arguments

**Phase 4 · Functions & modular code** · ~75 minutes

> **Today's build:** a report generator whose defaults make the common call one argument long.

**Concepts:** default values · keyword-only args · argument order rules · the mutable default trap

---

## The article

### Why this day exists

A function with eight required parameters is technically usable and practically not. Defaults are
what turn a flexible function into a *pleasant* one: the common case becomes one argument, and
every unusual case is still reachable.

There is also one genuine Python landmine in here — the mutable default — which is unlike
anything else in the language, produces a bug that looks supernatural, and catches everybody
exactly once.

### 1. Defaults

```python
def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

greet("Ada")                              # Hello, Ada!
greet("Ada", "Hi")                        # positionally
greet("Ada", punctuation="?")             # by keyword, skipping the middle
```

**Parameters with defaults must come after those without.** `def f(a=1, b)` is a `SyntaxError` —
there would be no way to tell what a single argument meant.

Choose defaults so the **common case needs no arguments at all**. If callers always pass the same
value, that value is the default.

### 2. Keyword arguments

At the call site you can pass by position or by name:

```python
make_report(data, "wide", True, False, 20)          # unreadable
make_report(data, layout="wide", totals=True, top=20)   # obvious
```

Keywords can be in any order and may be mixed with positional arguments — but **all positional
arguments must come first**.

The rule worth adopting: **any boolean argument should be passed by keyword.** `send(msg, True)`
tells the reader nothing; `send(msg, urgent=True)` tells them everything.

### 3. Keyword-only parameters

A bare `*` in the signature means *everything after me must be passed by name*:

```python
def report(rows, *, layout="table", totals=True, width=80):
    ...

report(data, layout="csv")      # fine
report(data, "csv")             # TypeError
```

This is the tool for **options**. It stops callers writing `report(data, "csv", False, 100)` — a
line nobody can read and which breaks silently the day you reorder the parameters.

The mirror image is `/`, which marks parameters as **positional-only**:

```python
def clamp(value, low, high, /):
    ...
```

You will use it rarely. Its purpose is to keep parameter *names* out of your public API, so you
can rename them later without breaking anyone.

The full signature grammar, in order:

```python
def f(pos_only, /, standard, *args, kw_only, **kwargs):
```

### 4. THE MUTABLE DEFAULT TRAP

```python
def add_item(item, basket=[]):        # LOOKS reasonable. Is a bug.
    basket.append(item)
    return basket

add_item("apple")      # ['apple']
add_item("pear")       # ['apple', 'pear']   ← where did the apple come from?
```

**Default values are evaluated once, when the `def` statement runs — not on each call.** So every
call that does not supply `basket` shares *the same list object*, and mutations accumulate across
calls, across the whole program, forever.

The fix is always the same:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []               # a NEW list, per call
    basket.append(item)
    return basket
```

This applies to every mutable default: `[]`, `{}`, `set()`, and any object of your own. Ruff flags
it as **B006**, and that alone justifies running a linter.

The same evaluate-once rule bites with computed defaults:

```python
def log(message, when=datetime.now()):    # frozen at import time, forever
def log(message, when=None):              # right; compute inside
```

### 5. Designing a signature

Order parameters by how often they change:

```python
def report(rows, *, layout="table", width=80, totals=True, top=None):
```

- **Required, positional:** the thing being operated on. Usually one.
- **Keyword-only with defaults:** everything else.

Test the design by writing the calls first:

```python
report(rows)                          # the common case: one argument
report(rows, top=10)                  # one thing different
report(rows, layout="csv", top=10)    # still readable at any length
```

If the common call needs four arguments, the defaults are wrong.

**Never use a mutable object as a default.** **Never make a boolean positional.** **Never reorder
parameters after release** — that is why keyword-only exists.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Defaults, keyword-only, `/`, and the mutable-default trap demonstrated with `is`. |
| `build.py`  | The report generator: one required argument, eight keyword-only options, four output formats. |

```bash
python3 lesson.py
python3 build.py
ruff check --isolated --select B build.py     # B006 catches the trap
```

---

## Common mistakes

**`def f(a=1, b)`** — `SyntaxError`.

**A mutable default.** State leaks between calls. `None` plus a check.

**A computed default.** Evaluated once at import.

**Positional booleans.** `f(x, True, False)` is unreadable.

**Reordering parameters.** Breaks every positional caller silently.

**Too many required arguments.** Give the rare ones defaults.

**Mutating a default that came from the caller.** Copy it if you will change it.

---

## Exercises

1. Write `add_item(item, basket=[])` and call it three times. Explain the output using the word
   "once".
2. Fix it with `None`, and prove with `is` that each call gets a different list.
3. Write a function with a keyword-only parameter and call it positionally. Read the `TypeError`.
4. Take a function of yours with four positional parameters and redesign it so the common call
   needs one.
5. Show that `def f(when=time.time())` freezes at import.
6. Run `ruff check --select B` over a file with a mutable default.

---

## Checklist

- [ ] I know defaults are evaluated once, at definition
- [ ] I never use a mutable default
- [ ] I make options keyword-only with `*`
- [ ] I never pass a boolean positionally
- [ ] I order parameters by how often they change
- [ ] My report's common call is one argument long
