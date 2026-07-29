# Day 048 — Dataclasses

**Phase 5 · Object-oriented Python** · ~75 minutes

> **Today's build:** rewrite three of your earlier classes as dataclasses and count the lines you deleted.

**Concepts:** `@dataclass` · field defaults · `frozen=True` · `order=True` · `__post_init__`

---

## The article

### Why this day exists

Most classes are mostly boilerplate. `__init__` assigns five arguments to five attributes,
`__repr__` lists them, `__eq__` compares them — and all three are mechanical restatements of the
same five names.

`@dataclass` generates them from the field list. It is not a new concept; it is the same class you
were already writing, with the typing removed.

The interesting part of today is knowing **which of your classes it should not replace.**

### 1. The basics

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

That generates `__init__`, `__repr__` and `__eq__`. The equivalent by hand is about fifteen lines.

The **annotations are required** — that is how the decorator finds the fields. But they are not
enforced at runtime: `Point("a", "b")` works fine. They are documentation, and input for mypy
(Day 59). A field with no annotation is simply not a field.

### 2. The options

```python
@dataclass(frozen=True, order=True, slots=True, kw_only=True)
```

| Option | Does |
|---|---|
| `frozen=True` | assignment raises `FrozenInstanceError`; also generates `__hash__` |
| `order=True` | generates `<`, `<=`, `>`, `>=` comparing fields **in declaration order** |
| `slots=True` | adds `__slots__` (3.10+) — smaller, and typos raise |
| `kw_only=True` | every field must be passed by name (3.10+) |
| `eq=False` | do not generate `__eq__` (keeps the inherited identity hash) |

**`frozen=True` is the big one.** Day 43 spent a page on the `__eq__`/`__hash__` contract and
"hashable means immutable"; `frozen=True` gives you both correctly in one word, and it is the right
default for anything that is a *value* rather than a *thing*.

`order=True` compares the **tuple of fields in declaration order**, so field order becomes part of
your API. Put the field you want to sort by first, or use `field(compare=False)` to exclude the
rest.

### 3. `field()`

For anything a bare default cannot express:

```python
from dataclasses import field

@dataclass
class Order:
    id: int
    items: list = field(default_factory=list)      # NOT items: list = []
    created: datetime = field(default_factory=datetime.now)
    _cache: dict = field(default_factory=dict, repr=False, compare=False)
    tag: str = field(default="", metadata={"help": "optional label"})
```

**`default_factory` is the fix for Day 32's mutable default.** And dataclasses are strict about it
— `items: list = []` raises `ValueError` at class-definition time rather than letting you ship the
shared-list bug. That is a genuine improvement over a hand-written `__init__`.

Useful `field()` arguments: `repr=False` (hide it), `compare=False` (exclude from `__eq__`/order),
`init=False` (not a constructor parameter — set it in `__post_init__`).

### 4. `__post_init__`

Runs after the generated `__init__`. It is where validation and derived fields go:

```python
@dataclass
class Temperature:
    celsius: float

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError("below absolute zero")
```

On a **frozen** dataclass you cannot assign in `__post_init__` either — use
`object.__setattr__(self, "name", value)`, which is exactly what the generated `__init__` does.

### 5. When *not* to use one

This is the part worth taking away.

- **When the class is mostly behaviour.** Day 41's `BankAccount` has five methods and one rule; the
  generated `__init__` would save two lines and the `__eq__` would be actively wrong (two accounts
  with the same balance are not the same account).
- **When it needs a class-level counter.** Day 42's `Employee` issues sequential IDs; a dataclass
  cannot express that in its field list.
- **When you need computed properties as *settable*.** Day 47's `Temperature` lets you assign
  `fahrenheit`. A frozen dataclass cannot.
- **When identity matters more than value.** Generated `__eq__` compares fields. For anything with
  an identity — a user, an account, a connection — that is wrong.

The rule of thumb: **`@dataclass` for values, a plain class for things.** A `Point`, a `Money`, a
`Config` are values. An `Account`, a `Session`, a `Parser` are things.

### 6. The alternatives

- **`NamedTuple`** (Day 23) — immutable, indexable, tuple-compatible. Use when it must behave like
  a tuple.
- **`TypedDict`** — a plain dict with a declared shape. For JSON that must stay a dict (Day 66).
- **`pydantic.BaseModel`** — dataclass-like, but it *validates and coerces at runtime*. Third
  party, and the foundation of FastAPI (Day 85).
- **`attrs`** — the library dataclasses were based on. More features, still worth knowing about.

Ordinary `@dataclass` covers most cases. Reach for pydantic when the data comes from outside your
program and must be checked.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Generation, every option, `field()`, `__post_init__`, and the mutable-default rejection. |
| `build.py`  | Three earlier classes rewritten, line counts compared, and one deliberately left alone. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**No annotation.** The attribute is not a field at all.

**`items: list = []`.** `ValueError` at definition. Use `default_factory=list`.

**Believing annotations are enforced.** They are not, without mypy.

**Non-default field after a defaulted one.** `TypeError`. Or use `kw_only=True`.

**`order=True` and forgetting field order is the sort order.**

**Assigning in `__post_init__` on a frozen class.** Use `object.__setattr__`.

**Using a dataclass where identity matters.** Two users with the same name become equal.

---

## Exercises

1. Write a class by hand with `__init__`, `__repr__` and `__eq__`, then as a dataclass. Count.
2. Try `items: list = []` and read the error.
3. Make a frozen dataclass, put it in a set, and try to mutate it.
4. Use `order=True`, then reorder the fields and watch the sort change.
5. Add `__post_init__` validation to a frozen dataclass — you will need `object.__setattr__`.
6. Take a class of yours that should **not** be a dataclass and write down why.

---

## Checklist

- [ ] I annotate every field
- [ ] I use `default_factory` for mutable defaults
- [ ] I use `frozen=True` for value types
- [ ] I know `order=True` sorts by declaration order
- [ ] I put validation in `__post_init__`
- [ ] I can name a class of mine that should stay a plain class, and say why
