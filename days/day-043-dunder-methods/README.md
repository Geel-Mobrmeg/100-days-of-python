# Day 043 — Dunder methods

**Phase 5 · Object-oriented Python** · ~85 minutes

> **Today's build:** a `Vector` class that prints usefully, compares correctly and works inside a set.

**Concepts:** `__str__` vs. `__repr__` · `__len__` · `__eq__` · `__hash__` · `__contains__`

---

## The article

### Why this day exists

Python's syntax is not built into the language so much as *delegated to your objects*. `len(x)`
calls `x.__len__()`. `a == b` calls `a.__eq__(b)`. `for i in x` calls `x.__iter__()`. Every piece
of syntax you have used for forty-two days has been a dunder call underneath.

Which means your own types can support all of it. That is what "Pythonic" actually means: an
object that works with the language's existing vocabulary instead of inventing its own
(`v.add(w)`, `v.get_length()`, `v.equals(w)`).

There is also one genuine correctness trap here — the `__eq__`/`__hash__` contract — which
silently breaks sets and dicts if you get it wrong.

### 1. The protocol idea

**Dunder** = "double underscore". You almost never call them directly; you use the syntax and
Python calls them:

| You write | Python calls |
|---|---|
| `len(v)` | `v.__len__()` |
| `v[0]` | `v.__getitem__(0)` |
| `x in v` | `v.__contains__(x)` |
| `a == b` | `a.__eq__(b)` |
| `repr(v)` / `str(v)` | `v.__repr__()` / `v.__str__()` |
| `bool(v)` / `if v:` | `v.__bool__()`, else `v.__len__()` |
| `for x in v` | `v.__iter__()` |
| `a + b` | `a.__add__(b)` (Day 44) |

Implement the ones that make sense for your type and skip the rest. A `Vector` should support
`len` and `==`; it should not support `keys()`.

### 2. `__repr__` and `__str__`

```python
def __repr__(self):
    return f"Vector({self.x}, {self.y})"     # unambiguous, ideally eval-able

def __str__(self):
    return f"({self.x}, {self.y})"           # readable
```

`repr` is for developers, `str` is for users, and `str` falls back to `repr`. **Write `__repr__`
first**; it is what you see in a debugger, in a list, and in a failed test's output.

The gold standard for `__repr__`: `eval(repr(obj)) == obj`. Not always achievable, always worth
aiming at.

### 3. `__eq__` — and the `__hash__` contract

By default, `==` on your objects means `is` — identity. Two vectors with the same numbers are not
equal, which is almost never what you want.

```python
def __eq__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented              # NOT False, and not an error
    return self.x == other.x and self.y == other.y
```

Returning **`NotImplemented`** (the object, not the exception) tells Python "I do not know how to
compare with that" — so it tries the *other* object's `__eq__`, and only then falls back to
identity. Returning `False` instead would prevent the other type from ever getting a chance, which
breaks interoperability in ways that are hard to diagnose.

Now the trap. **Defining `__eq__` sets `__hash__` to `None`**, making your object unhashable:

```python
{Vector(1, 2)}       # TypeError: unhashable type: 'Vector'
```

Python does this deliberately, because of the contract:

> **If `a == b`, then `hash(a) == hash(b)`.**

Sets and dicts find items by hash first and compare second. If two equal objects hash differently
they land in different buckets and the set contains both. Rather than let you break that
accidentally, Python removes the default hash the moment you define equality.

The fix is to define `__hash__` over **the same fields** as `__eq__`:

```python
def __hash__(self):
    return hash((self.x, self.y))          # a tuple of the same fields
```

**And those fields must not change while the object is in a set.** Mutate `v.x` after adding `v`
to a set and it is in the wrong bucket — you can no longer find it, and it may appear twice.

The clean rule: **hashable means immutable.** If your type is mutable, leave it unhashable. That is
why `list` is unhashable and `tuple` is not.

### 4. `__len__`, `__bool__`, `__getitem__`, `__contains__`

```python
def __len__(self):  return 2                      # must be a non-negative int
def __bool__(self): return bool(self.x or self.y) # else falls back to __len__
def __getitem__(self, index): ...                 # v[0]
def __contains__(self, value): ...                # x in v
```

Two useful consequences:

- **`__len__` also provides truthiness.** Without `__bool__`, `if v:` uses `len(v) != 0`. For a
  `Vector` that is wrong — a 2D zero vector has length 2 and should be falsy — so define
  `__bool__` explicitly.
- **`__getitem__` alone gives you iteration and `in` for free.** Python falls back to calling it
  with 0, 1, 2… until `IndexError`. Defining `__iter__` and `__contains__` properly is better, but
  the fallback is why some very old classes work in `for` loops.

### 5. What else is out there

```python
__iter__, __next__          # for loops, comprehensions (Day 38)
__call__                    # makes the instance callable (Day 37)
__enter__, __exit__         # `with` blocks (Day 53)
__getattr__, __setattr__    # attribute access — powerful, easy to abuse
__format__                  # f"{v:.2f}" on your own type
__slots__                   # not a method: fixes the attribute list
```

`__slots__` is worth knowing now. It replaces the instance `__dict__` with a fixed set of fields:

```python
class Vector:
    __slots__ = ("x", "y")
```

Which means `v.z = 1` raises `AttributeError` — catching Day 41's typo bug — and each instance
uses noticeably less memory. The cost: no dynamic attributes, and some interaction with
inheritance.

### 6. Restraint

Every dunder you implement is a promise about how your object behaves with existing syntax, and a
surprising one is worse than an absent one. `__add__` on a `Vector` is obvious. `__add__` on a
`User` is a puzzle.

The test: **would a reader guess what it does without looking?** If not, write a named method.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Each dunder, the `NotImplemented` rule, the hash contract broken and fixed, `__slots__`. |
| `build.py`  | `Vector`: repr, equality, hashing, indexing, iteration, formatting — and a set that behaves. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`__eq__` without `__hash__`.** The object becomes unhashable.

**`__hash__` over different fields than `__eq__`.** Sets and dicts silently misbehave.

**A hashable, mutable object.** Change a field after adding it to a set and it is lost.

**Returning `False` from `__eq__` for an unknown type.** Return `NotImplemented`.

**Only `__str__`.** Debugging shows `<object at 0x...>`.

**`__len__` on something with no length**, then being surprised by its truthiness.

**Implementing dunders because they exist.** Restraint is the skill.

---

## Exercises

1. Write a class with `__eq__` and put two equal instances in a set. Read the error, then fix it.
2. Make a hashable class, add an instance to a set, mutate the field, then try to find it.
3. Write `__repr__` such that `eval(repr(obj)) == obj`.
4. Write `__len__` on a type where 0 is meaningful, then explain why you also need `__bool__`.
5. Add `__slots__` and try to set an attribute that is not listed.
6. Implement `__getitem__` only, and confirm `for` and `in` still work.

---

## Checklist

- [ ] I write `__repr__` on everything I will debug
- [ ] My `__eq__` returns `NotImplemented` for unknown types
- [ ] My `__hash__` uses exactly the fields `__eq__` uses
- [ ] I keep hashable types immutable
- [ ] I know `__len__` supplies truthiness unless `__bool__` exists
- [ ] My vectors deduplicate correctly in a set
