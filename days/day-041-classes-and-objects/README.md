# Day 041 — Classes and objects

**Phase 5 · Object-oriented Python** · ~80 minutes

> **Today's build:** a `BankAccount` class that deposits, withdraws, refuses overdrafts and keeps a history.

**Concepts:** the `class` statement · `__init__` · `self` · instance attributes · methods

---

## The article

### Why this day exists

You have already built objects. Day 34's counter closure held private state and exposed one
behaviour; Day 24's contact records were data with no behaviour attached. A class is what you get
when you want **both**, and more than one operation on the same state.

The syntax is small. The genuinely hard part — *when* to use one — is Day 46, and it is worth
knowing from the start that "always" is the wrong answer.

### 1. The shape

```python
class BankAccount:
    """A single account."""

    def __init__(self, owner, balance=0):
        self.owner = owner            # instance attributes
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        self.balance += amount
        self.history.append(("deposit", amount))
        return self.balance
```

```python
account = BankAccount("Ada", 100)     # calls __init__
account.deposit(50)
account.balance                       # 150
```

- **`class`** defines a type. `CapWords` by convention (Day 8).
- **`__init__`** is not a constructor — the object already exists when it runs. It is the
  *initialiser*: its job is to set up attributes and nothing else.
- **`self`** is the instance, passed automatically. `account.deposit(50)` becomes
  `BankAccount.deposit(account, 50)`.
- **Instance attributes** are created by assigning to `self.something`. There is no declaration
  list; if `__init__` does not set it, it does not exist.

### 2. `self` is a convention, not a keyword

You could call it `this` or `banana` and Python would not object. **Call it `self`.** Every reader
of Python expects it, and linters flag anything else.

Two consequences worth internalising:

- **Every method needs it.** Forgetting it gives
  `TypeError: deposit() takes 1 positional argument but 2 were given` — because the instance was
  passed and there was nowhere to put it.
- **`self.x` and `x` are different things.** A bare `x` inside a method is a local variable that
  vanishes when the method returns. Only `self.x` persists.

### 3. Objects are dictionaries with a nicer face

```python
account.__dict__      # {'owner': 'Ada', 'balance': 150, 'history': [...]}
```

Instance attributes are literally stored in a dict. That is why you can add one at any time:

```python
account.nickname = "savings"     # legal, and usually a mistake
```

Python will not stop you, and a typo becomes a silent new attribute rather than an error:

```python
account.balence = 500            # creates a NEW attribute. balance unchanged.
```

That is the single most annoying bug in this topic. Defences: set every attribute in `__init__`
(so the real one exists), use `__slots__` (Day 43), or run a type checker (Day 59), which catches
it.

### 4. Methods, and returning things

A method is a function whose first parameter is the instance. Everything from Days 31–33 applies:
defaults, keyword-only arguments, docstrings.

The design question specific to methods is **what to return**:

- **Mutating methods** conventionally return `None` — the same rule as `list.append` (Day 21).
- **Query methods** return a value and change nothing.
- **Returning `self`** enables chaining (`account.deposit(50).withdraw(20)`), which reads nicely
  and hides that the object changed. Use it deliberately or not at all.

Keep the two kinds separate. A method that both changes the object *and* returns something
interesting is one that cannot be safely called twice.

### 5. `__str__` and `__repr__`

Without them you get `<__main__.BankAccount object at 0x7f8b1c0>`, which tells you nothing.

```python
def __repr__(self):
    return f"BankAccount(owner={self.owner!r}, balance={self.balance})"
```

- **`__repr__`** is for *developers*: unambiguous, ideally valid Python. Used by the REPL, by
  containers, by debuggers.
- **`__str__`** is for *users*: readable. Falls back to `__repr__` if absent.

**If you write only one, write `__repr__`** — it is the one you see when debugging, and it is the
one used when your object is inside a list. Day 43 covers the rest of the dunder family.

### 6. When a class is the right answer

| Use a | When |
|---|---|
| function | one operation, no state |
| closure | one behaviour with a little private state (Day 34) |
| dict / dataclass | data with no behaviour (Day 48) |
| **class** | **several operations on shared state, with rules about that state** |

`BankAccount` qualifies on all three counts: several operations (deposit, withdraw, statement),
shared state (the balance), and rules (you cannot withdraw more than you have). That last one is
the strongest signal — **a class is where invariants live.**

A class with one method and no state should be a function. A class that is only `__init__` should
be a dataclass. Day 46 goes further.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `class`, `__init__`, `self`, the typo trap, `__dict__`, `__repr__`, and closure-vs-class. |
| `build.py`  | `BankAccount`: deposits, withdrawals, overdraft refusal, transfers, statement, and its invariants checked. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Forgetting `self` in a method signature.** `TypeError` about argument counts.

**Forgetting `self.` on an attribute.** You made a local that vanishes.

**A typo creating a new attribute.** `account.balence = 500` is legal.

**Doing work in `__init__`.** It should set attributes, not open files or call APIs.

**Mutable default in `__init__`.** Day 32's B006, now shared by every instance.

**Returning something from a mutating method by accident.**

**No `__repr__`.** Debugging is guesswork.

---

## Exercises

1. Write a `Counter` class with `increment`, `reset` and `value`. Compare with Day 34's closure.
2. Create two instances and prove their attributes are independent.
3. Print `obj.__dict__`. Add an attribute from outside. Explain why Python allowed it.
4. Write `__repr__` for a class and put three instances in a list.
5. Give a class a mutable default via `__init__(self, items=[])` and show all instances sharing it.
6. Write a class whose method forgets `self.` and find the bug from the symptom alone.

---

## Checklist

- [ ] I can write a class with `__init__` and methods
- [ ] I know `self` is the instance and is passed automatically
- [ ] I know attributes live in `__dict__` and can be added at any time
- [ ] I write `__repr__` on anything I will debug
- [ ] Mutating methods of mine return `None`
- [ ] My account cannot be made to go negative by any sequence of calls
