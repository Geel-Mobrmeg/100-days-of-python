# Day 037 — Decorators

**Phase 4 · Functions & modular code** · ~90 minutes

> **Today's build:** write `@timer`, `@retry` and `@cache`, then apply them to your Day 31 utilities.

**Concepts:** functions as objects · wrapper functions · `@` syntax · `functools.wraps` · arguments

---

## The article

### Why this day exists

You have already written a decorator. Day 33's call logger *was* one, and Day 34 explained the
closure that makes it work. Today is mostly the notation — plus the one genuinely fiddly part
(decorators that take arguments), which trips people up because it needs three nested functions.

Decorators matter because they are everywhere in the Python you will read: Flask's `@app.route`,
pytest's `@fixture`, FastAPI's `@app.get`, `@property`, `@dataclass`, `@staticmethod`. Knowing
they are just function calls demystifies most frameworks at once.

### 1. `@` is notation

```python
@logged
def add(a, b):
    return a + b
```

means exactly, and only:

```python
def add(a, b):
    return a + b
add = logged(add)
```

That is the entire feature. A decorator is **a function that takes a function and returns a
function**, and `@` is sugar for the reassignment.

The standard shape:

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"got {result!r}")
        return result
    return wrapper
```

Three things are doing work, and you have met all of them:

- `*args, **kwargs` (Day 33) — accept and forward any signature.
- The closure over `func` (Day 34) — the wrapper remembers what it wraps.
- `functools.wraps` — see below.

**Return the result.** A wrapper that calls `func(...)` without returning turns every decorated
function into one that returns `None`. It is the commonest decorator bug and it is silent.

### 2. `functools.wraps`

Without it, the wrapper replaces the original's identity:

```python
add.__name__     # "wrapper"
add.__doc__      # None
help(add)        # useless
```

`@functools.wraps(func)` copies `__name__`, `__doc__`, `__module__`, `__qualname__` and
`__wrapped__` across. It costs one line and it is not optional — debuggers, `help()`, pytest and
`inspect.signature` all rely on that metadata.

`__wrapped__` lets you get back to the original: `add.__wrapped__` is the undecorated function.

### 3. Decorators with arguments

This is the fiddly bit. `@retry(times=3)` is **called first**, and the *result* is used as the
decorator:

```python
@retry(times=3)
def fetch(): ...
```

means:

```python
fetch = retry(times=3)(fetch)
```

Note the two sets of parentheses. So `retry(times=3)` must return a decorator, which means
**three** nested functions:

```python
def retry(times=3):              # 1. takes the ARGUMENTS
    def decorator(func):         # 2. takes the FUNCTION
        @functools.wraps(func)
        def wrapper(*a, **kw):   # 3. takes the CALL
            ...
        return wrapper
    return decorator
```

Read it outside-in: arguments, function, call. Every decorator-with-arguments has this shape, and
once you have written one the pattern never changes.

To support both `@retry` and `@retry(times=3)`, check whether the first argument is callable —
today's build does that, and it is the reason some library decorators feel magical.

### 4. Stacking

```python
@timer
@retry(times=3)
def fetch(): ...
```

applies **bottom-up**: `fetch = timer(retry(times=3)(fetch))`.

So `timer` is the outermost and measures *all* the retries together. Reverse them and you time
each attempt separately. **The order changes the meaning**, and it is worth writing a comment
saying which you meant.

### 5. Where they earn their keep

The test: **is this concern orthogonal to what the function does?**

Timing, retrying, caching, logging, access control, rate limiting, validation, registration — none
of those are part of "compute a slug", and all of them apply identically to fifty functions. That
is exactly what a decorator is for.

Where they do not: anything that needs to change the function's *logic*, anything that makes the
signature unclear, or a one-off. A decorator used once is a function call wearing a hat.

The real cost is **debuggability**. A traceback through three decorators has three extra frames,
and `inspect.signature` can lie. Use them for genuinely cross-cutting concerns and not for
cleverness.

### 6. The three you will actually write

- **`@timer`** — measure and report. The simplest useful one.
- **`@retry(times, delay)`** — for anything touching a network (Day 66). Needs exponential
  backoff and a specific exception type, not a bare `except`.
- **`@cache`** — `functools.cache` already exists; writing it (Day 34) is how you understand its
  limits: hashable arguments only, and unbounded memory unless you set `maxsize`.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `@` desugared, `wraps` proved, arguments, stacking order, class-based decorators. |
| `build.py`  | `@timer`, `@retry`, `@cache` and `@validated`, applied to the Day 31 toolkit and measured. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Forgetting to return the result.** Every decorated function returns `None`.

**Forgetting `functools.wraps`.** Names, docs and signatures are lost.

**Forgetting the extra parentheses.** `@retry` where `@retry()` was needed, or vice versa.

**Assuming stacking order.** Bottom-up. It changes the meaning.

**Decorating with mutable shared state.** All calls share it — sometimes wanted, usually not.

**`@cache` on a function taking a list.** `TypeError: unhashable type`.

**`@cache` on something with side effects or fresh data.** It will return a stale answer forever.

---

## Exercises

1. Write `@logged` without `functools.wraps`, print `__name__`, then add it.
2. Write `@timer` and apply it to something slow.
3. Write `@repeat(n)` that calls the function n times. Note the three levels.
4. Stack two decorators, then swap them, and explain the difference in output.
5. Write `@retry` with exponential backoff that only catches one exception type.
6. Add `@cache` to a function that reads a file, then change the file. Explain what you see.

---

## Checklist

- [ ] I can desugar `@d` and `@d(arg)` into plain assignments
- [ ] My wrappers return the result
- [ ] I always use `functools.wraps`
- [ ] I can write a decorator that takes arguments
- [ ] I know stacking applies bottom-up
- [ ] My three decorators work on the toolkit without changing any of it
