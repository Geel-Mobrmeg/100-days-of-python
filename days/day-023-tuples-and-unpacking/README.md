# Day 023 — Tuples and unpacking

**Phase 3 · Data structures** · ~70 minutes

> **Today's build:** a geometry helper: distance, midpoint and area, all passing points around as tuples.

**Concepts:** immutability · tuple unpacking · swapping · star unpacking · `namedtuple`

---

## The article

### Why this day exists

You have been using tuples since Day 13 without being told: `enumerate` yields them, `zip` yields
them, `divmod` returns one. Today they get explained, along with the syntax that makes them
pleasant — unpacking — which is one of the features people miss most when they go back to other
languages.

The deeper point is a design one. A list and a tuple can hold the same things, so the choice
between them is not technical, it is about **meaning**.

### 1. Tuples

```python
point = (3, 4)
empty = ()
one = (3,)          # the comma makes it — NOT the brackets
```

`(3)` is just the number 3 in brackets. `(3,)` is a one-element tuple. That trailing comma is the
classic tuple gotcha, and it also means `x = 3,` quietly creates a tuple.

The brackets are usually optional, which is why tuples turn up where you did not put any:

```python
point = 3, 4                 # a tuple
return x, y                  # returns ONE tuple (Day 31)
for i, item in enumerate(x)  # unpacking a tuple
```

Everything from Day 3 works — indexing, slicing, `len`, `in`, iteration. The difference is that
tuples are **immutable**: no `append`, no `sort`, no item assignment.

### 2. List or tuple?

Both hold a sequence, so the technical answer is unhelpful. The useful rule is about *what the
positions mean*:

| Use a **list** when | Use a **tuple** when |
|---|---|
| items are the same kind of thing | items are different parts of one thing |
| the count varies | the count is fixed by meaning |
| order is data | position is meaning |
| you will add or remove | it is a fixed record |
| `["ada", "alan", "grace"]` | `("Ada", 36, "engineer")` |

A list is *"several of these"*. A tuple is *"one of these, made of parts"*. A point is
`(x, y)` — always two, and swapping them changes what it means. Names in a phone book are a
list — any number, order is incidental.

Three practical consequences of immutability:

- **Tuples can be dict keys and set members** (Day 24, 26); lists cannot, because hashing
  something that can change is unsound. `{(0, 0): "origin"}` works.
- **Tuples are safe to share.** There is no aliasing bug (Day 21), because there is no change to
  see.
- **Tuples are slightly smaller and faster.** Irrelevant until it is not.

One trap: **immutable does not mean the contents are.** A tuple holding a list still lets you
change the list. `([1,2], 3)` — you can append to that first element. The tuple guarantees which
objects it holds, not that they are frozen.

### 3. Unpacking

```python
point = (3, 4)
x, y = point               # x = 3, y = 4
```

The number of names must match exactly, or you get
`ValueError: too many values to unpack`. That strictness is a feature — it fails at the mistake.

Unpacking works on **any iterable**, not just tuples:

```python
a, b, c = [1, 2, 3]
first, second = "hi"
```

The famous consequence, and the one everyone shows off first:

```python
a, b = b, a           # swap, no temporary variable
```

The right side is evaluated *completely first* into a tuple, then unpacked, which is why it works
and why `a, b, c = c, a, b` also does exactly what it looks like.

Multiple assignment is the same feature:

```python
x, y, z = 1, 2, 3
```

And it is why unpacking in a `for` line reads so well:

```python
for name, age in people:
for i, (name, age) in enumerate(people):     # nested unpacking
```

### 4. Star unpacking

`*` collects "everything else", and there can be exactly one:

```python
first, *rest = [1, 2, 3, 4]        # first=1, rest=[2, 3, 4]
*most, last = [1, 2, 3, 4]         # most=[1, 2, 3], last=4
first, *middle, last = [1, 2, 3, 4]  # middle=[2, 3]
```

**The starred name always gets a list**, even when it collects nothing (then it is `[]`) and even
when unpacking a tuple. That surprises people.

This is the clean way to take a header off a file, or a command off its arguments:

```python
verb, *args = command.split()
header, *rows = lines
```

`_` is the conventional name for a value you are deliberately discarding:

```python
name, _, role = record.split(",")
x, *_ = point            # just the first
```

### 5. Returning several values

A function returning "two things" returns one tuple, and the caller unpacks it. That is the whole
mechanism — Python has no special multiple-return feature:

```python
def min_max(values):
    return min(values), max(values)      # one tuple

lowest, highest = min_max(data)          # unpacked
```

`divmod(17, 5)` → `(3, 2)` is the built-in example, and `q, r = divmod(17, 5)` is how you use it.

### 6. `namedtuple` — positions with names

`point[0]` is unreadable in a way `point.x` is not.

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)

p.x          # 3
p[0]         # 3 — still a tuple, still indexable
x, y = p     # still unpacks
```

You get names for free and lose nothing: it *is* a tuple, so it works everywhere a tuple works,
and it prints as `Point(x=3, y=4)` instead of `(3, 4)`.

`typing.NamedTuple` is the modern spelling with type hints (Day 59):

```python
class Point(NamedTuple):
    x: float
    y: float
```

When your record grows behaviour as well as fields, that is what Day 48's `@dataclass` is for.
The progression `tuple → namedtuple → dataclass → class` is one of the real arcs of this course.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Tuples, the one-element comma, unpacking, swapping, star forms, and `namedtuple` in place. |
| `build.py`  | The geometry helper — points as tuples throughout, then the same code with `namedtuple`. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`(3)` is not a tuple.** You need `(3,)`.

**Accidental tuple from a stray comma.** `x = 3,` makes `(3,)`, and the bug appears later.

**`ValueError: too many values to unpack`.** The counts must match. Use `*rest` if they vary.

**Expecting `*rest` to be a tuple.** It is always a list.

**Mutating a list inside a tuple and being surprised it worked.** The tuple fixes which objects,
not their contents.

**A list as a dict key.** `TypeError: unhashable type`. Use a tuple.

**`point[0]` and `point[1]` everywhere.** Use `namedtuple`.

---

## Exercises

1. Make a one-element tuple. Prove it with `len` and `type`.
2. Swap two variables, then rotate three, with no temporaries.
3. Split `"2024-01-15"` into three ints in one line.
4. Take a header row off a list of lines with star unpacking.
5. Use a `(row, col)` tuple as a dict key. Then try a list and read the error.
6. Rewrite your geometry helper with `namedtuple` and count the `[0]`s you deleted.

---

## Checklist

- [ ] I know the comma makes the tuple, not the brackets
- [ ] I can say when I would choose a tuple over a list, in terms of meaning
- [ ] I unpack in `for` lines rather than indexing
- [ ] I know `*rest` is always a list
- [ ] I know why a tuple can be a dict key and a list cannot
- [ ] My geometry functions return unpackable results
