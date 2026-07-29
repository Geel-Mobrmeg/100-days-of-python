# Day 047 — Properties and encapsulation

**Phase 5 · Object-oriented Python** · ~80 minutes

> **Today's build:** a `Temperature` class where setting an impossible value raises instead of quietly storing it.

**Concepts:** `@property` · setters · validation on assign · the underscore convention

---

## The article

### Why this day exists

Day 41 built an account with an invariant and then admitted it could be broken from outside:
`account.balance = -1000` succeeded. Today closes that hole.

The Python answer is not the Java one. Python has **no private attributes** and does not want any.
Instead it has a convention (`_name`) and a mechanism (`@property`) that lets you add validation
*later*, without changing a single line of calling code. That last part is why Python programmers
do not write getters and setters up front.

### 1. Do not write getters and setters

In Java you write `getBalance()` / `setBalance()` from the start, because switching a public field
to a method later breaks every caller. In Python it does not:

```python
class Account:
    def __init__(self, balance):
        self.balance = balance          # start here. A plain attribute.
```

If you later need validation, `@property` intercepts the *same syntax*:

```python
class Account:
    def __init__(self, balance):
        self.balance = balance          # this now runs the setter

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value
```

**`account.balance = 5` is unchanged at every call site.** That is the whole argument: start
simple, add the property when you need it, break nothing.

So the rule is: **a plain attribute until it needs a rule.** A property that only returns
`self._x` is noise.

### 2. The mechanics

```python
@property
def celsius(self):              # the GETTER — the method name is the
    return self._celsius        # attribute name

@celsius.setter
def celsius(self, value):       # note: @<name>.setter, not @property
    self._celsius = value

@celsius.deleter
def celsius(self):
    del self._celsius
```

Three things that catch people:

- **The getter must come first.** `@celsius.setter` needs `celsius` to already be a property.
- **`self._celsius`, not `self.celsius`,** inside the property. The second is infinite recursion.
- **Omit the setter and the attribute is read-only** — assignment raises `AttributeError`. That is
  the neatest way to make something immutable-ish.

### 3. Computed properties

A property does not need a stored value at all:

```python
@property
def fahrenheit(self):
    return self._celsius * 9 / 5 + 32

@fahrenheit.setter
def fahrenheit(self, value):
    self.celsius = (value - 32) * 5 / 9      # goes through celsius's validation
```

**One source of truth, several views of it.** `fahrenheit` and `kelvin` are not stored, so they
cannot drift out of step with `celsius` — Day 19's principle, at object level. And because the
setter assigns through `self.celsius`, the validation is written once and every route obeys it.

This is the strongest reason to use properties: **derived values that cannot go stale.**

### 4. Validation belongs in the setter, and `__init__` should use it

```python
def __init__(self, celsius):
    self.celsius = celsius        # NOT self._celsius
```

Assigning to `self.celsius` runs the setter, so construction is validated by the same code as
every later assignment. Writing `self._celsius = celsius` bypasses it — and then
`Temperature(-500)` succeeds while `t.celsius = -500` raises, which is an infuriating bug to
diagnose.

### 5. The underscore convention

- **`name`** — public. Part of your API.
- **`_name`** — internal. "Do not touch; may change without notice." Python does not enforce it,
  linters and tooling respect it, and `from x import *` skips it.
- **`__name`** (two leading, at most one trailing) — **name mangling**. Python rewrites it to
  `_ClassName__name`.

Name mangling is **not** privacy — `obj._Account__balance` still works. Its actual purpose is to
stop a subclass accidentally colliding with a base class's attribute. Use it rarely, and never as
a security measure.

**Nothing here is enforced.** `obj._balance = -1000` always works. Python's position is that
consenting adults can read a docstring, and that the cost of real privacy (in a language this
dynamic) exceeds the benefit. Day 48's `frozen=True` is the closest thing to genuine
immutability.

### 6. Costs and cautions

- **A property looks free and is not.** `obj.x` that runs a database query surprises everyone.
  Keep them cheap; if it is expensive, name it `fetch_x()`.
- **No side effects in a getter.** Reading an attribute should not change anything.
- **Properties are per-class, not per-instance.** They live on the class.
- **`functools.cached_property`** computes once and stores the result — good for expensive derived
  values, and *wrong* the moment the inputs can change.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Plain → property with no caller change, recursion trap, read-only, computed, mangling. |
| `build.py`  | `Temperature`: one stored value, three scales, validated once, and every route tested. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`self.celsius` inside the `celsius` property.** Infinite recursion.

**Setter before getter.** `NameError`.

**`self._x = x` in `__init__`.** Skips validation; construction and assignment then disagree.

**Storing what you could compute.** Two sources of truth, guaranteed drift.

**A property that does real work.** Callers assume attribute access is cheap.

**Trivial getters and setters.** Use a plain attribute until there is a rule.

**Believing `__name` is private.** It is `_Class__name`.

---

## Exercises

1. Start with a plain attribute, add a property, and show no caller changed.
2. Write `self.x` inside property `x` and read the `RecursionError`.
3. Make an attribute read-only and try to assign to it.
4. Write `Temperature` with computed `fahrenheit`, and prove the two cannot disagree.
5. Bypass validation with `obj._value = -500`, then say what Python offers instead.
6. Use `__name` and reach it from outside via `_Class__name`.

---

## Checklist

- [ ] I use a plain attribute until it needs a rule
- [ ] My `__init__` assigns through the property
- [ ] I compute derived values rather than storing them
- [ ] I know how to make an attribute read-only
- [ ] I know `_name` is a convention and `__name` is mangling, not privacy
- [ ] No sequence of assignments can put my `Temperature` below absolute zero
