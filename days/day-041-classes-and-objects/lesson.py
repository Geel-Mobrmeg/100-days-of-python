"""Day 041 — Classes and objects.

    python3 lesson.py
"""

WIDTH = 72

# ---------------------------------------------------------------------------
# 1. The shape
# ---------------------------------------------------------------------------


class BankAccount:
    """A single account, with a balance and a history."""

    def __init__(self, owner, balance=0):
        # __init__ is NOT a constructor. The object already exists when this
        # runs; its job is to set up attributes and nothing else.
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        """Add to the balance. Returns None — it mutates."""
        self.balance += amount
        self.history.append(("deposit", amount))

    def statement(self):
        """Return a summary. Changes nothing."""
        return f"{self.owner}: {self.balance} ({len(self.history)} entries)"

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"


ada = BankAccount("Ada", 100)
ada.deposit(50)

print(ada)                      # uses __repr__
print(ada.statement())
print(f"balance: {ada.balance}")


# ---------------------------------------------------------------------------
# 2. self is the instance, passed automatically
# ---------------------------------------------------------------------------

# These two lines are the SAME CALL:
ada.deposit(10)
BankAccount.deposit(ada, 10)
print(f"\nboth forms worked: {ada.balance}")

# `self` is a CONVENTION, not a keyword — but call it self. Every reader of
# Python expects it and every linter flags anything else.


class Forgetful:
    def no_self():              # noqa: N805 - deliberately wrong
        return "this will fail"

    def loses_it(self):
        total = 99              # a LOCAL. Vanishes when the method returns.
        self.kept = 99          # an ATTRIBUTE. Persists.
        return total


try:
    Forgetful().no_self()
except TypeError as e:
    print(f"method without self: TypeError: {e}")

obj = Forgetful()
obj.loses_it()
print(f"self.kept survived: {obj.kept}")
print(f"the local did not:  {'total' in obj.__dict__}")


# ---------------------------------------------------------------------------
# 3. Instances are independent
# ---------------------------------------------------------------------------

alan = BankAccount("Alan", 500)
print(f"\n{ada}")
print(f"{alan}")
print(f"separate objects: {ada is not alan}")
print(f"separate histories: {ada.history is not alan.history}")


# ---------------------------------------------------------------------------
# 4. Objects are dictionaries with a nicer face
# ---------------------------------------------------------------------------

print(f"\nada.__dict__ = {ada.__dict__}")

# Which is why you can add an attribute at any time...
ada.nickname = "savings"
print(f"after adding one: {list(ada.__dict__)}")

# ...and why A TYPO SILENTLY CREATES A NEW ATTRIBUTE:
before = ada.balance
ada.balence = 500               # noqa - the exhibit. Note the spelling.
print(f"\nafter `ada.balence = 500`, ada.balance is still {before}")
print(f"and there is now a stray attribute: "
      f"{[k for k in ada.__dict__ if 'bal' in k]}")

print("""
  That is the most annoying bug in this topic: no error, no warning, and
  the real balance is untouched. THREE DEFENCES:

    * set every attribute in __init__, so the real one always exists
    * __slots__ (Day 43), which makes new attributes an AttributeError
    * a type checker (Day 59), which catches it without running anything""")

del ada.balence, ada.nickname


# ---------------------------------------------------------------------------
# 5. THE MUTABLE DEFAULT, now shared by every instance
# ---------------------------------------------------------------------------


class Broken:
    def __init__(self, items=[]):       # noqa: B006 - the exhibit
        self.items = items


a, b = Broken(), Broken()
a.items.append("x")
print(f"\ntwo separate Broken() objects, but: b.items = {b.items}")
print(f"they share one list: {a.items is b.items}")


class Fixed:
    def __init__(self, items=None):
        self.items = list(items) if items else []


c, d = Fixed(), Fixed()
c.items.append("x")
print(f"Fixed: d.items = {d.items}, shared = {c.items is d.items}")

# Day 32's B006, with a longer fuse: the default is created ONCE when the
# class body runs, so EVERY instance that omits the argument shares it.


# ---------------------------------------------------------------------------
# 6. __str__ vs __repr__
# ---------------------------------------------------------------------------


class Bare:
    pass


class Both:
    def __repr__(self):
        return "Both(the developer view)"

    def __str__(self):
        return "the user view"


print(f"\nno __repr__:  {Bare()}")
print(f"str(Both()):  {Both()}")
print(f"repr(Both()): {Both()!r}")
print(f"in a list:    {[Both()]}       <- containers always use __repr__")

print("""
  __repr__   for DEVELOPERS: unambiguous, ideally valid Python. Used by the
             REPL, by containers, by debuggers.
  __str__    for USERS: readable. Falls back to __repr__ if absent.

  IF YOU WRITE ONLY ONE, WRITE __repr__. It is what you see when debugging
  and what appears when your object is inside a list.""")


# ---------------------------------------------------------------------------
# 7. Closure or class? Day 34's question, answered
# ---------------------------------------------------------------------------


def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

    def reset(self):
        self.count = 0

    def __repr__(self):
        return f"Counter(count={self.count})"


closure = make_counter()
obj = Counter()
print(f"\nclosure: {[closure() for _ in range(3)]}")
print(f"class:   {[obj.increment() for _ in range(3)]}")

obj.reset()
print(f"and the class can also reset: {obj}")
print("""
  THE CLOSURE WINS when there is ONE behaviour and the state should be
  genuinely unreachable.

  THE CLASS WINS the moment you want a SECOND operation on that state —
  reset(), a __repr__, a way to inspect it. Adding reset() to the closure
  means returning two functions, and a third means a tuple of three, at
  which point you have written a class without the syntax.

  USE A CLASS WHEN: several operations, shared state, AND rules about that
  state. That last one is the strongest signal — A CLASS IS WHERE
  INVARIANTS LIVE. `BankAccount` has one: the balance never goes negative.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write a method without self and read the TypeError.
#   * Assign to `balance` instead of `self.balance` inside a method.
#   * Misspell an attribute from outside the class and hunt the symptom.
#   * Give __init__ a mutable default and make two instances.
#   * Delete __repr__ and put three instances in a list.
