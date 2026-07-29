# Day 046 — Composition over inheritance

**Phase 5 · Object-oriented Python** · ~85 minutes

> **Today's build:** take a four-level inheritance chain and rebuild it from small collaborating objects.

**Concepts:** is-a vs. has-a · delegation · fragile base classes · mixins

---

## The article

### Why this day exists

Yesterday taught inheritance. Today is the more useful day, because the default answer to "should
this be a subclass?" is **no**, and knowing why will improve your designs more than any syntax in
this phase.

The industry slogan is *"favour composition over inheritance"*. It comes from the Gang of Four
book, it is thirty years old, and it is right. This day is about understanding it rather than
repeating it.

### 1. is-a versus has-a

- **Inheritance is `is-a`.** A `Circle` **is a** `Shape`. Anywhere a `Shape` is expected, a
  `Circle` works.
- **Composition is `has-a`.** A `Car` **has an** `Engine`. The car holds one and asks it to do
  things.

The mistake is using inheritance for `has-a`, because it happens to give you the methods:

```python
class Stack(list):          # WRONG — a stack is not a list
    def push(self, item):
        self.append(item)

class Stack:                # RIGHT — a stack HAS a list
    def __init__(self):
        self._items = []
    def push(self, item):
        self._items.append(item)
```

The first `Stack` inherits `sort()`, `insert()`, `reverse()` and `__getitem__` — every one of which
breaks the abstraction, and every one of which is now part of `Stack`'s public API forever. You
wanted a list *inside*, not to *be* one.

### 2. The four costs of inheritance

**You inherit everything.** Including the methods that make no sense and the ones added to the
base next year.

**The base class becomes fragile.** Change one method and every subclass changes — including
subclasses in other people's code that you have never read. This is the *fragile base class
problem*, and it is why library authors are so reluctant to change base classes.

**It is fixed at class-definition time.** A `Circle` cannot stop being a `Shape` at runtime. A car
can be given a different engine.

**Deep chains are unreadable.** Four levels means opening four files to understand one method call,
and `super()` in a diamond can reach a class you have never heard of.

### 3. What composition gives you

**Delegation:** hold an object, forward to it.

```python
class Stack:
    def __init__(self):
        self._items = []
    def push(self, item): self._items.append(item)
    def pop(self):        return self._items.pop()
    def __len__(self):    return len(self._items)
```

You expose exactly three operations. Adding a fourth is deliberate. This is the whole technique.

**Runtime configuration:** the pieces are arguments.

```python
service = Service(storage=S3Storage(), notifier=EmailNotifier())
service = Service(storage=MemoryStorage(), notifier=NullNotifier())   # in tests
```

That second line is the biggest practical win. **Composition makes things testable**, because you
can substitute a component. With inheritance you would need a whole parallel subclass hierarchy —
and Day 58's `monkeypatch` exists largely to work around designs that did not do this.

**Combinations without an explosion.** Three storage backends × three notifiers × two formatters is
8 classes composed, or 18 subclasses.

### 4. Mixins — the reasonable middle

A **mixin** is a small class providing one capability, designed to be combined:

```python
class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__)

class User(JsonMixin, TimestampMixin):
    ...
```

Rules that keep them sane: no `__init__`, no state of their own, one capability each, named
`...Mixin`, and always listed *before* the real base class (MRO order — Day 45).

Mixins are inheritance used for `can-do` rather than `is-a`, and they are genuinely useful.
Django and DRF are built on them. They are also the easiest thing in this article to overdo: five
mixins on one class and nobody can find where a method comes from.

### 5. When inheritance *is* right

Not never. Use it when **all** of these hold:

1. It is a genuine `is-a`, substitutably (the Liskov test from Day 45).
2. The subclasses are interchangeable to the caller.
3. The base is stable, and ideally you control it.
4. The hierarchy is one or two levels deep.

Yesterday's shapes qualify on all four. A framework asking you to subclass `Model` or `TestCase`
also qualifies — that is the framework's chosen extension point.

Day 49's abstract base classes and protocols are the version of inheritance that is *only* an
interface, with no implementation to inherit — which sidesteps most of today's problems.

### 6. The practical test

Before subclassing, ask three questions:

1. **Is every child usable everywhere the parent is expected?** No → composition.
2. **Am I doing this to reuse code, or to be substitutable?** Reuse → composition.
3. **Would I be happy inheriting every future method the base gains?** No → composition.

And one more, which catches most of it: **would this read better as a constructor argument?**

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `is-a` vs `has-a`, the `Stack(list)` failure, delegation, runtime swapping, mixins, `__getattr__`. |
| `build.py`  | A four-level chain rebuilt from components — with both versions runnable and compared. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Inheriting to reuse code.** The commonest one.

**Subclassing `list`/`dict`.** You promise the entire API. Use `UserList`/`UserDict` if you must.

**Deep hierarchies.** Two levels is plenty.

**Mixins with state or `__init__`.** They stop composing.

**Mixins after the base class.** MRO order matters.

**Composition with no interface.** If the components have no agreed shape, you cannot swap them.

**Forwarding forty methods by hand.** If you need that, inheritance may be right after all.

---

## Exercises

1. Write `Stack(list)` and `insert(0, x)` into it. Then write the composed version.
2. Take a three-level chain of yours and redraw it as components.
3. Write a service that takes its storage as an argument, and test it with a fake.
4. Write two mixins and combine them. Print the MRO and find where each method comes from.
5. Use `__getattr__` to forward everything to a wrapped object. Then say why that is dangerous.
6. Find a class you wrote that inherits for reuse, and rewrite it.

---

## Checklist

- [ ] I ask `is-a` or `has-a` before subclassing
- [ ] I never inherit purely to reuse code
- [ ] I can write delegation without thinking about it
- [ ] I pass components in as arguments so they can be swapped in tests
- [ ] My mixins have no state and one capability each
- [ ] My rebuilt version supports combinations the chain could not
