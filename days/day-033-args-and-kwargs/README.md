# Day 033 — *args and **kwargs

**Phase 4 · Functions & modular code** · ~75 minutes

> **Today's build:** a wrapper that logs every call — its name, its arguments and what it returned.

**Concepts:** packing · unpacking at the call site · forwarding arguments · signature design

---

## The article

### Why this day exists

`*` and `**` are two symbols doing four related jobs, and the confusion comes entirely from the
fact that they mean *opposite things* depending on which side of the function they are on.

They also unlock the single most useful pattern in intermediate Python: a function that wraps
*any other function* without knowing its signature. That is what today's build is, and it is a
decorator with the syntax filed off — which makes Day 37 four days of work easier.

### 1. Packing: `*` in a definition

```python
def total(*numbers):
    return sum(numbers)

total(1, 2, 3)        # numbers is the TUPLE (1, 2, 3)
total()               # numbers is ()
```

`*name` collects **all remaining positional arguments into a tuple**. `**name` collects **all
remaining keyword arguments into a dict**:

```python
def tag(name, **attributes):
    return f"<{name} {attributes}>"

tag("a", href="/x", target="_blank")     # attributes = {"href": "/x", ...}
```

`args` and `kwargs` are conventional names, not keywords — the `*` and `**` do the work. Use
better names when you have them: `*numbers`, `**attributes`.

Order in a signature is fixed: `def f(a, b=1, *args, c, **kwargs)`. Note that anything after
`*args` is automatically **keyword-only** — which is exactly what Day 32's bare `*` was doing.

### 2. Unpacking: `*` at a call site

The same symbols, the opposite direction. Here they **spread** a collection into arguments:

```python
values = [1, 2, 3]
total(*values)               # calls total(1, 2, 3)

options = {"sep": "-", "end": "!\n"}
print("a", "b", **options)   # calls print("a", "b", sep="-", end="!\n")
```

- In a **definition**: collect many arguments into one name.
- At a **call**: spread one collection into many arguments.

Unpacking also works outside function calls, which is often the neatest way to merge:

```python
[*a, *b]              # concatenate lists
{**defaults, **overrides}    # merge dicts, right side wins
first, *rest = items         # Day 23's star unpacking
```

### 3. Forwarding — the pattern everything else is built on

```python
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
```

Those two lines accept **any** call and pass it through **unchanged**. That is the foundation of:

- decorators (Day 37)
- `functools.partial`
- almost every library that wraps another library

Read it in both directions: the `def` line *packs* whatever arrived, and the call line *unpacks*
it again. Nothing is inspected, nothing is assumed, and a function that gains a parameter next
year still passes through.

### 4. Logging a call properly

To print a call the way you would type it, you have to handle both halves:

```python
def format_call(func, args, kwargs):
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func.__name__}({', '.join(parts)})"
```

Use `!r` — `repr` — not `str`. `f(name)` and `f('name')` are different calls, and only `repr`
shows which one happened. This is the same reason Day 4 recommended `!r` for debugging.

Every function object carries metadata you can read:

```python
func.__name__          # "clamp"
func.__doc__           # its docstring
func.__module__        # where it was defined
inspect.signature(func)  # the full signature, as an object
```

`inspect.signature(...).bind(*args, **kwargs)` goes further: it matches the actual arguments to
the parameter *names*, so you can log `clamp(value=15, low=0, high=10)` even when the caller
wrote `clamp(15, 0, 10)`. Today's build uses it.

### 5. When *not* to use them

`*args, **kwargs` costs you everything a signature gives you:

- The reader cannot tell what the function accepts.
- Editors cannot autocomplete.
- Type checkers (Day 59) cannot help.
- A misspelled keyword becomes a silent no-op instead of a `TypeError`.

So use them for **forwarding** (you genuinely do not know the signature) and for **genuinely
variadic** functions (`sum`, `max`, `print`). Do not use them as a shortcut for "several options"
— that is what Day 32's keyword-only parameters are for.

The worst version is a function whose real parameters are hidden in `kwargs` and dug out with
`kwargs.get("timeout", 30)`. Write the parameter.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Packing, unpacking, the forwarding pattern, merging, and what you lose by using them. |
| `build.py`  | The call logger: wraps any function, logs arguments, result, timing and exceptions. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Confusing the two directions.** Definition packs; call unpacks.

**`f(*args)` when you meant `f(args)`.** One passes three arguments, the other passes one tuple.

**Assuming `kwargs` is ordered arbitrarily.** It preserves the caller's order (dicts, since 3.7).

**Mutating `kwargs` and expecting the caller to see it.** It is a fresh dict.

**Using `str` instead of `repr` when logging.** `f(1)` and `f('1')` look identical.

**`**kwargs` as a substitute for real parameters.** You lose every signature benefit.

**Forgetting `functools.wraps` when wrapping.** The wrapper's name and docstring replace the
original's — Day 37.

---

## Exercises

1. Write `total(*numbers)` and call it with 0, 1 and 5 arguments, then with `*a_list`.
2. Write `tag(name, **attributes)` producing `<a href="/x">`.
3. Write a forwarding wrapper and use it on three functions with different signatures.
4. Merge two dicts with `{**a, **b}` and say which side wins.
5. Use `inspect.signature(f).bind(...)` to print a call with parameter names.
6. Take a function with `**kwargs` and rewrite it with explicit keyword-only parameters. Note
   which errors become possible to catch.

---

## Checklist

- [ ] I know `*` packs in a definition and unpacks at a call
- [ ] I can write a wrapper that forwards any call unchanged
- [ ] I use `!r` when logging arguments
- [ ] I can read `func.__name__` and `inspect.signature`
- [ ] I know what a signature buys and what `**kwargs` costs
- [ ] My logger handles positional, keyword, default and failing calls
