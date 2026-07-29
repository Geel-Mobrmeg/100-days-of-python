# Day 049 — Abstract bases and protocols

**Phase 5 · Object-oriented Python** · ~85 minutes

> **Today's build:** a plugin interface with two working implementations that the caller can't tell apart.

**Concepts:** `ABC` · `@abstractmethod` · duck typing · `typing.Protocol` · interface design

---

## The article

### Why this day exists

Day 45's `Shape` said "subclasses must implement `area()`" by raising `NotImplementedError` — and
then let you instantiate an incomplete subclass anyway, failing only when the method was called.
Day 46 built a `NotificationService` whose components had no declared shape at all; it simply
hoped every channel had `.deliver()`.

Both are *interfaces* that are not written down. Today writes them down, two different ways, and
the choice between the two is the actual content.

### 1. `ABC` — the explicit interface

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, record): ...

    @abstractmethod
    def load(self, key): ...

    def save_all(self, records):        # a concrete method, inherited
        return [self.save(r) for r in records]
```

The payoff: **an incomplete subclass cannot be instantiated.**

```python
class Broken(Storage):
    def save(self, record): ...

Broken()      # TypeError: Can't instantiate abstract class Broken
              # with abstract method load
```

That failure happens at construction, naming the missing method — not somewhere downstream when
`load()` is finally called. It is the same guarantee Day 45 wanted and could not get.

`ABC` also lets you mix abstract and concrete: `save_all` is written once and inherited by every
implementation. That is real code reuse, not just a contract.

`@abstractmethod` combines with `@property`, `@classmethod` and `@staticmethod` — the order
matters, `@abstractmethod` goes innermost.

### 2. `Protocol` — the implicit interface

```python
from typing import Protocol, runtime_checkable

class Storage(Protocol):
    def save(self, record) -> int: ...
    def load(self, key) -> object: ...
```

Nothing inherits from this. A class satisfies it by **having the right methods** — which is duck
typing, written down and checkable by mypy (Day 59).

This is **structural typing**: the shape is what counts, not the ancestry. Java and `ABC` use
*nominal* typing — you must declare the relationship.

The decisive advantage: **it works on classes you do not own.** You can declare that `pathlib.Path`
satisfies your `FileLike` protocol without touching `pathlib`. With `ABC` you would have to
`register()` it, or wrap it.

`@runtime_checkable` allows `isinstance(x, Storage)` — but only checks *method names*, not
signatures. It is a weak check and mypy is the real one.

### 3. Which to use

| Use `ABC` when | Use `Protocol` when |
|---|---|
| you own all the implementations | implementations are third-party or unknown |
| you want to share concrete code | you only need the contract |
| you want a runtime guarantee at construction | static checking is enough |
| the relationship is genuinely `is-a` | anything with the shape will do |
| plugins registering with your framework | a function's parameter type |

Rough guidance:

- **A framework extension point** — `ABC`. You want the loud early failure and the shared code.
- **A function parameter** — `Protocol`. `def process(store: Storage)` should accept anything that
  works.
- **Neither, for small internal code.** Plain duck typing is fine; a protocol you never check is
  documentation, which is not nothing but is not a guarantee either.

### 4. The interface is a design decision

Both mechanisms only *record* an interface. Choosing what goes in it is the work:

- **Keep it small.** Every method is a promise every implementer must keep. Five methods on an
  interface with three implementations is fifteen obligations.
- **Depend on behaviour, not data.** `save(record)` not `get_connection()`.
- **Do not leak the implementation.** If your interface has `execute_sql()`, only databases can
  implement it, and you have not abstracted anything.
- **Segregate.** Better two interfaces of two methods than one of four, if some implementers only
  need half. (This is the "I" in SOLID.)

The test: **can you write a second, genuinely different implementation?** If the only one you can
imagine is the one you have, the interface is a description of your class, not an abstraction.
Today's build has two, and one of them is deliberately unlike the other.

### 5. What the standard library already gives you

`collections.abc` defines the interfaces Python itself uses: `Iterable`, `Sized`, `Container`,
`Sequence`, `Mapping`, `Hashable`, `Callable`.

```python
from collections.abc import Sequence
isinstance([1, 2], Sequence)     # True
isinstance("ab", Sequence)       # True
```

Inheriting from `collections.abc.Sequence` gets you `__contains__`, `__iter__`, `__reversed__`,
`index` and `count` **for free**, from just `__len__` and `__getitem__`. That is the best
demonstration of a well-designed abstract base there is, and it is worth reading its source.

For type hints, prefer these over concrete types: `def f(items: Iterable[str])` accepts a list, a
tuple, a set or a generator. `def f(items: list[str])` accepts one thing.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `ABC` failing at construction, `Protocol` structural matching, `register()`, `collections.abc`. |
| `build.py`  | A plugin system: one interface, four unlike implementations, and a runner that cannot tell them apart. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`NotImplementedError` instead of `@abstractmethod`.** Fails late, at call time.

**Forgetting to inherit `ABC`.** `@abstractmethod` alone does nothing.

**Expecting `Protocol` to be enforced at runtime.** It is a static check.

**`isinstance` against a `runtime_checkable` Protocol and trusting it.** Names only, no signatures.

**A fat interface.** Every method is an obligation for every implementer.

**An interface with one implementation.** That is a class, not an abstraction.

**`list[str]` in a signature where `Iterable[str]` would do.**

---

## Exercises

1. Write an `ABC` with two abstract methods, implement one, and read the `TypeError`.
2. Write the same interface as a `Protocol` and satisfy it without inheriting.
3. Use `@runtime_checkable` and pass something with the right names but wrong signatures.
4. Inherit from `collections.abc.Sequence` with only `__len__` and `__getitem__`, then count what
   you got free.
5. Take Day 46's `NotificationService` components and write the protocol they were implying.
6. Design an interface, then write a second implementation genuinely unlike the first. If you
   cannot, the interface is wrong.

---

## Checklist

- [ ] I know `ABC` fails at instantiation and `NotImplementedError` fails at call time
- [ ] I can write a `Protocol` and satisfy it without inheritance
- [ ] I can say when to choose each
- [ ] I keep interfaces small
- [ ] I use `collections.abc` types in signatures
- [ ] My two implementations are genuinely different and interchangeable
