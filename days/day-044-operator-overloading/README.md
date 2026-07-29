# Day 044 — Operator overloading

**Phase 5 · Object-oriented Python** · ~85 minutes

> **Today's build:** a `Money` type that adds, compares and sorts — and refuses to mix currencies silently.

**Concepts:** `__add__` & `__sub__` · `__lt__` · `__getitem__` · `total_ordering` · `NotImplemented`

---

## The article

### Why this day exists

Yesterday's dunders made an object *behave* like a Python value. Today's make it *compute* like
one — and introduce the two mechanisms that make operator overloading actually work in a language
where you do not control the other operand: **reflected operations** and **`NotImplemented`**.

`Money` is the right build because it has a rule that operators alone cannot express: 10 GBP plus
10 USD is not 20 of anything. A type that silently returns 20 is worse than one that raises.

### 1. The arithmetic dunders

| Operator | Method | Reflected |
|---|---|---|
| `a + b` | `__add__` | `__radd__` |
| `a - b` | `__sub__` | `__rsub__` |
| `a * b` | `__mul__` | `__rmul__` |
| `a / b` | `__truediv__` | `__rtruediv__` |
| `a // b` | `__floordiv__` | `__rfloordiv__` |
| `a % b` | `__mod__` | `__rmod__` |
| `a ** b` | `__pow__` | `__rpow__` |
| `-a` | `__neg__` | — |
| `abs(a)` | `__abs__` | — |
| `a @ b` | `__matmul__` | `__rmatmul__` |

### 2. Reflected operations — the half people miss

`3 * money` cannot work by calling `int.__mul__(3, money)` — `int` has never heard of your class.
So Python tries the **reflected** method on the right operand:

```
a * b   →   a.__mul__(b)
            if that returns NotImplemented, try  b.__rmul__(a)
            if that also does, raise TypeError
```

That is why `__rmul__ = __mul__` (for a commutative operation) makes `3 * money` work. For
non-commutative ones the arguments are the other way round:

```python
def __rsub__(self, other):
    return Money(other) - self       # other - self, note the order
```

`__radd__` also needs care for `sum()`, which starts from the integer `0`:

```python
def __radd__(self, other):
    if other == 0:          # sum()'s starting value
        return self
    return self.__add__(other)
```

Without that, `sum(list_of_money)` raises.

### 3. `NotImplemented` is the whole protocol

```python
def __add__(self, other):
    if not isinstance(other, Money):
        return NotImplemented        # "I don't know how" — not an error
    ...
```

**Return `NotImplemented`, do not raise `TypeError`.** Raising kills the reflected attempt and
means no other type can ever interoperate with yours. Returning it lets Python try the other side
and raise a good error itself:

```
TypeError: unsupported operand type(s) for +: 'Money' and 'str'
```

That message is better than anything you would have written, and you get it for free.

The exception: when the types *are* compatible but the **values** are not — `Money(10, "GBP") +
Money(10, "USD")` — that is a `ValueError` you should raise. `NotImplemented` would produce a
confusing "unsupported operand type Money and Money".

**Wrong type → `NotImplemented`. Wrong value → raise.**

### 4. Comparison, and `total_ordering`

Six methods: `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`. You rarely need all six:

- `__ne__` is derived from `__eq__` automatically.
- The reflected comparisons are each other: `a < b` falls back to `b > a`.

`functools.total_ordering` fills in the rest from `__eq__` plus **one** of the ordering methods:

```python
@total_ordering
class Money:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
    # __le__, __gt__, __ge__ generated
```

It costs a little speed (the generated methods call yours) and saves four methods' worth of places
to make a mistake. Use it unless you are in a hot loop.

Defining `__lt__` also makes `sorted()`, `min()` and `max()` work — which is what Day 27's `key=`
was working around.

### 5. In-place operators

`a += b` tries `__iadd__` first, and falls back to `a = a + b`. So `+=` works without you doing
anything.

Define `__iadd__` only for **mutable** types where in-place is genuinely cheaper (a big buffer, a
growing collection), and **return `self`**. For an immutable type like `Money`, leave it out — the
fallback is correct and prevents the aliasing surprise where `a += b` changes something another
name is pointing at.

### 6. Restraint, again

The rule from Day 43 applies harder here. An operator must mean **the obvious thing**:

- `Money + Money` → obvious.
- `Money * 3` → obvious (three times the amount).
- `Money * Money` → **meaningless**. What unit is GBP²? Do not define it.
- `Vector * Vector` → ambiguous (dot? cross? element-wise?) — name it instead.

If a reader would have to check, use a named method. `account.merge(other)` beats `account + other`
every time.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every operator, the reflected mechanism traced, `NotImplemented` vs raising, `total_ordering`. |
| `build.py`  | `Money`: exact arithmetic, currency safety, sorting, `sum()`, allocation without losing pennies. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Raising `TypeError` from `__add__`.** Kills reflected operations. Return `NotImplemented`.

**No `__radd__`.** `sum()` fails on the initial `0`.

**`__rsub__` with the operands the right way round.** They are reversed.

**Defining `__lt__` without `__eq__`.** `sorted()` works, `==` does not.

**`__iadd__` that does not return `self`.** The variable becomes `None`.

**Overloading `*` for something non-obvious.**

**Floats for money.** Day 5. `Decimal`.

---

## Exercises

1. Write `__add__` returning `NotImplemented` for unknown types, then try `money + "x"` and read
   the error Python generates.
2. Make `3 * money` work. Explain which method ran.
3. Use `sum()` on a list of your type. Fix the failure with `__radd__`.
4. Add `@total_ordering` and count the methods you deleted.
5. Try to add two different currencies. Decide between `ValueError` and `NotImplemented`, and
   defend it.
6. Split £100 three ways using your type so the parts sum back to exactly £100.

---

## Checklist

- [ ] I return `NotImplemented` for unknown types and raise for bad values
- [ ] I know how reflected operations work and when they fire
- [ ] `sum()` works on my type
- [ ] I use `total_ordering` rather than writing six comparisons
- [ ] I only overload operators whose meaning is obvious
- [ ] My currency mixing raises, and my allocation loses no pennies
