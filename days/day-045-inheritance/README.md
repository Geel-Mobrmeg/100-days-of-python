# Day 045 — Inheritance

**Phase 5 · Object-oriented Python** · ~80 minutes

> **Today's build:** a shape hierarchy where every subclass computes its own area behind one shared interface.

**Concepts:** subclassing · `super()` · overriding · `isinstance` · the MRO

---

## The article

### Why this day exists

Inheritance is the most over-taught and most over-used idea in object-oriented programming. It is
genuinely useful for one thing — **several types that are interchangeable to the caller** — and it
is reached for constantly to mean "these things share some code", which it does badly.

Today is the mechanics, done properly. **Tomorrow is when not to use it**, and tomorrow is the more
important day.

### 1. Subclassing and overriding

```python
class Shape:
    def area(self):
        raise NotImplementedError("subclasses must implement area()")

    def describe(self):
        return f"{type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2
```

`Circle` gets `describe()` for free, and `describe()` calls `self.area()` — which finds the
*subclass's* version. That indirection is the whole point of inheritance, and it has a name:
**polymorphism**. The caller says `shape.area()` and does not care which class answers.

Note `type(self).__name__` rather than `"Shape"`. Inside a base class, `self` is always the actual
instance, so this is how a base method reports the real type.

### 2. `super()`

Call the parent's version of a method:

```python
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)      # run Rectangle's __init__
        self.side = side
```

Two rules worth internalising:

- **Always call `super().__init__()`** when a subclass defines `__init__`. Skip it and the parent's
  attributes never exist, producing an `AttributeError` somewhere far away.
- **`super()` follows the MRO, not "the parent".** With single inheritance those are the same
  thing. With multiple inheritance they are not, and that is section 4.

`super()` with no arguments only works inside a class body. `super(Square, self)` is the explicit
Python 2 form; you will see it in old code.

### 3. `isinstance` and duck typing

```python
isinstance(circle, Circle)      # True
isinstance(circle, Shape)       # True — subclasses count
type(circle) is Shape           # False — exact type only
```

Use `isinstance`, not `type(x) == Y`. The first respects subclasses; the second refuses them, which
defeats the point of having a hierarchy.

But the more Pythonic instinct is to **not check at all**:

```python
for shape in shapes:
    print(shape.area())        # works for anything with .area()
```

This is **duck typing** — "if it walks like a duck". The object does not have to inherit from
`Shape`; it just has to have the method. That is why Day 49's `Protocol` exists, and why Python
programmers reach for inheritance less than Java programmers do.

Reasonable uses of `isinstance`: returning `NotImplemented` in dunders (Day 44), validating at a
boundary, and handling genuinely different input types.

### 4. The MRO

With multiple inheritance, Python needs an order to search:

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

D.__mro__      # D, B, C, A, object
```

That is **C3 linearisation**, and its guarantees are: a class comes before its parents, and the
order you listed bases is preserved. `D.mro()` prints it, and reading it is how you debug "why did
that method run".

`super()` walks the *MRO*, not "up". So inside `B`, `super()` may reach `C` — a class `B` has never
heard of — depending on what the instance actually is. That is what makes cooperative multiple
inheritance work, and what makes it confusing.

**Every class inherits from `object`.** That is where the default `__init__`, `__eq__`, `__repr__`
and friends come from.

### 5. Abstract-ish base classes

Raising `NotImplementedError` documents intent but only fails **when the method is called**:

```python
class Shape:
    def area(self):
        raise NotImplementedError
```

An incomplete subclass instantiates happily and blows up later. Day 49's `abc.ABC` fails at
*instantiation* instead, which is much earlier and much better. Today uses the manual version so
the difference is visible.

### 6. Where inheritance goes wrong

Four failure modes, all of which tomorrow addresses:

- **Deep chains.** Four levels means a reader opens four files to understand one method.
- **Inheriting for reuse.** `class Stack(list)` gives `Stack` `.sort()`, `.insert()` and everything
  else — including operations that make no sense on a stack. You wanted a list *inside*, not to
  *be* one.
- **The fragile base class.** Changing a base method silently changes every subclass, including
  ones you have never read.
- **Liskov violations.** The classic: `Square(Rectangle)`. A rectangle lets you set width and
  height independently; a square cannot. Any code that works on rectangles breaks on squares — so
  square *is not* a rectangle, in the substitutability sense, however true it is in geometry.

The test before you subclass: **is every instance of the child usable everywhere the parent is
expected?** If not, it is not an `is-a`, and you want composition.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Overriding, `super()`, `isinstance` vs duck typing, the MRO, and the Square/Rectangle violation. |
| `build.py`  | The shape hierarchy: one interface, seven shapes, verified against known formulas. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Forgetting `super().__init__()`.** The parent's attributes never exist.

**`type(x) == Shape`.** Rejects every subclass.

**Deep hierarchies.** Four levels to read one method.

**Inheriting to reuse code.** Use composition (Day 46).

**Overriding with a different signature.** Callers break unpredictably.

**`Square(Rectangle)`.** The textbook Liskov violation.

**Mutable class attributes in a base.** Day 42, now shared across the whole hierarchy.

---

## Exercises

1. Write a base with a method that raises `NotImplementedError` and a subclass that forgets it.
   Note *when* it fails.
2. Write a subclass `__init__` without `super()` and find the resulting `AttributeError`.
3. Build a diamond (`D(B, C)`) and print `D.__mro__`. Predict which method runs.
4. Write `Square(Rectangle)` and a function that sets width and height independently. Watch it
   break.
5. Replace an `isinstance` chain with duck typing and say what you gained and lost.
6. Add a shape to your hierarchy without touching any other file.

---

## Checklist

- [ ] I always call `super().__init__()`
- [ ] I use `isinstance`, not `type() ==`
- [ ] I can read an MRO and predict which method runs
- [ ] I know `super()` follows the MRO, not "the parent"
- [ ] I ask "is-a, substitutably?" before subclassing
- [ ] My shapes are interchangeable to every function that uses them
