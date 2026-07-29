# Day 042 — Class vs. instance attributes

**Phase 5 · Object-oriented Python** · ~80 minutes

> **Today's build:** an `Employee` class that issues sequential IDs and can be built from a CSV row.

**Concepts:** shared state · `@classmethod` · `@staticmethod` · alternative constructors

---

## The article

### Why this day exists

Yesterday every attribute belonged to one instance. Today: attributes that belong to the *class*,
shared by every instance — which is how you count instances, issue sequential IDs, hold
configuration, and define constants.

It also contains one of Python's genuine gotchas, where a shared mutable attribute quietly links
every object you create.

### 1. Two places an attribute can live

```python
class Employee:
    company = "Analytical Engines Ltd"     # CLASS attribute — one, shared
    count = 0

    def __init__(self, name):
        self.name = name                   # INSTANCE attribute — one each
```

Lookup goes **instance first, then class**. So `employee.company` finds nothing on the instance
and falls back to the class.

The asymmetry that catches everyone:

```python
employee.company = "Somewhere Else"    # creates an INSTANCE attribute,
                                       # SHADOWING the class one
Employee.company = "New Name"          # changes it for everyone who has
                                       # not shadowed it
```

**Assigning through an instance never modifies the class attribute.** It creates a new instance
attribute that hides it. You can see this in `employee.__dict__` — before the assignment,
`company` is not there.

### 2. THE MUTABLE CLASS ATTRIBUTE TRAP

```python
class Team:
    members = []              # ONE list, shared by every Team ever made

a, b = Team(), Team()
a.members.append("Ada")
b.members                     # ['Ada']   ← !
```

`a.members.append(...)` does not assign — it *mutates* the one shared list. This is Day 32's
mutable-default bug with an even longer fuse, because it survives across every instance in the
whole program.

**Rule: class attributes should be immutable.** Constants, configuration, counters that only
`ClassName.count += 1` touches. Anything mutable and per-instance belongs in `__init__`.

### 3. `@classmethod`

A method whose first argument is the **class**, not the instance:

```python
@classmethod
def from_csv(cls, row):
    name, role, salary = row.split(",")
    return cls(name, role, int(salary))
```

Two uses, and both matter:

**Alternative constructors.** `__init__` takes one set of arguments; a classmethod can offer
others. `dict.fromkeys`, `datetime.fromtimestamp` and `Path.cwd` are all this pattern. The naming
convention is `from_something`.

**Class-level operations.** Reading or resetting shared state: `Employee.reset_ids()`,
`Employee.count()`.

**Use `cls(...)`, not `Employee(...)`.** With `cls`, a subclass calling `Manager.from_csv(row)`
gets a `Manager`; hard-coding the name gives an `Employee` and the bug is subtle.

### 4. `@staticmethod`

A function that happens to live in the class. No `self`, no `cls`, no access to any state:

```python
@staticmethod
def is_valid_email(text):
    return "@" in text and "." in text
```

Use it for a helper that is *conceptually* part of the class but needs nothing from it. If you
find yourself wanting one, ask honestly whether it should be a module-level function instead —
usually it should. A staticmethod is mostly about namespacing.

### 5. Which one?

| Decorator | First arg | Sees | Use for |
|---|---|---|---|
| (none) | `self` | this instance | almost everything |
| `@classmethod` | `cls` | the class | alternative constructors, class state |
| `@staticmethod` | — | nothing | a related helper |

Ask what the method needs. Needs the instance → regular. Needs the class (to construct one, or to
touch shared state) → `classmethod`. Needs neither → `staticmethod`, or a plain function.

### 6. Sequential IDs

The build's real job. The naive version:

```python
class Employee:
    _next_id = 1

    def __init__(self, name):
        self.id = Employee._next_id
        Employee._next_id += 1
```

Three things to notice:

- `Employee._next_id += 1` and not `self._next_id += 1`. The second **reads** the class attribute
  and then **creates an instance attribute** with the new value — leaving the class counter at 1
  forever, so every employee gets ID 1. This is the same shadowing rule as section 1, and it is
  the classic bug of this pattern.
- The leading underscore says "internal".
- It is **not thread-safe** (Day 92): two threads can read the same value before either writes.
  A `threading.Lock` fixes it, and knowing the limitation now is worth more than the fix.

Under inheritance, `cls._next_id += 1` gives each subclass its own counter from the moment it
first assigns — sometimes what you want, usually a surprise. The build shows both.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Lookup order, shadowing, the mutable trap, all three method kinds, `cls` vs the class name. |
| `build.py`  | `Employee`: sequential IDs, three alternative constructors, class-level stats, and the counter bug shown. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**A mutable class attribute.** Every instance shares it.

**`self.counter += 1` for a class counter.** Creates an instance attribute; the class one never
moves.

**Assigning through an instance and expecting the class to change.** It shadows.

**`Employee(...)` inside a classmethod.** Breaks subclasses. Use `cls(...)`.

**A `staticmethod` that should be a function.** Ask what it gains from the class.

**Forgetting class attributes are shared across a whole process.** Including between tests
(Day 58).

---

## Exercises

1. Give a class `items = []` and append through two instances. Explain using the word "one".
2. Print `instance.__dict__` before and after assigning to a class attribute through it.
3. Write `Employee.from_csv` with `cls(...)`, then hard-code the class name and subclass it.
4. Write a counter with `self._count += 1` and find why every object gets 1.
5. Write a `@staticmethod` validator, then move it to module level. Which is better?
6. Add a `@classmethod` that resets shared state, and say why tests need it.

---

## Checklist

- [ ] I know lookup is instance-then-class
- [ ] I never put a mutable object in a class attribute
- [ ] I use `ClassName.counter += 1`, not `self.counter += 1`
- [ ] I use `cls(...)` in alternative constructors
- [ ] I can say when a `staticmethod` should be a plain function
- [ ] My employee IDs are unique and sequential across every constructor
