"""Day 043 — Dunder methods.

    python3 lesson.py
"""

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. Syntax is delegated to your objects
# ---------------------------------------------------------------------------

print("""  YOU WRITE            PYTHON CALLS
  len(v)               v.__len__()
  v[0]                 v.__getitem__(0)
  x in v               v.__contains__(x)
  a == b               a.__eq__(b)
  repr(v) / str(v)     v.__repr__() / v.__str__()
  bool(v) / if v:      v.__bool__(), else v.__len__()
  for x in v           v.__iter__()
  a + b                a.__add__(b)          (Day 44)

Every piece of syntax you have used for forty-two days has been a dunder
call underneath. Which means YOUR types can support all of it.""")

print(f"\nlen('abc') really calls: {'abc'.__len__()}")
print(f"(2).__add__(3) = {(2).__add__(3)}")


# ---------------------------------------------------------------------------
# 2. Without dunders
# ---------------------------------------------------------------------------


class Bare:
    def __init__(self, x, y):
        self.x, self.y = x, y


a, b = Bare(1, 2), Bare(1, 2)
print(f"\nno dunders:")
print(f"  print(obj)     {a}")
print(f"  a == b         {a == b}       <- identity, not value")
print(f"  in a list      {[a]}")
try:
    len(a)
except TypeError as e:
    print(f"  len(a)         TypeError: {e}")


# ---------------------------------------------------------------------------
# 3. __repr__ and __str__
# ---------------------------------------------------------------------------


class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        # The gold standard: eval(repr(obj)) == obj
        return f"Vector({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"


v = Vector(3, 4)
print(f"\nrepr(v)   {v!r}")
print(f"str(v)    {v}")
print(f"in a list {[v, Vector(1, 1)]}      <- containers use __repr__")
print(f"eval(repr(v)) works: {eval(repr(v)).x == 3}")

# WRITE __repr__ FIRST. It is what you see in a debugger, inside a list,
# and in a failed test's output. __str__ falls back to it.


# ---------------------------------------------------------------------------
# 4. __eq__, and NotImplemented
# ---------------------------------------------------------------------------


class Compared:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Compared({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Compared):
            return NotImplemented          # NOT False. Not an exception.
        return (self.x, self.y) == (other.x, other.y)


print(f"\nequal by value:  {Compared(1, 2) == Compared(1, 2)}")
print(f"different:       {Compared(1, 2) == Compared(9, 9)}")
print(f"vs another type: {Compared(1, 2) == 'a string'}")

print("""
  Returning NotImplemented (THE OBJECT, not the exception) tells Python
  "I do not know how to compare with that", so it tries the OTHER object's
  __eq__ and only then falls back to identity.

  Returning False instead would stop the other type ever getting a chance —
  which breaks interoperability in ways that are very hard to diagnose.""")


# ---------------------------------------------------------------------------
# 5. THE HASH CONTRACT — the real trap of this day
# ---------------------------------------------------------------------------

try:
    {Compared(1, 2)}
except TypeError as e:
    print(f"putting it in a set: TypeError: {e}")

print(f"__hash__ is now: {Compared.__hash__}")

print("""
  DEFINING __eq__ SETS __hash__ TO None. Python does that on purpose,
  because of the contract:

      IF a == b, THEN hash(a) == hash(b)

  Sets and dicts find items BY HASH FIRST and compare second. Two equal
  objects that hash differently land in different buckets, so the set
  contains both and `in` cannot find one of them.

  Rather than let you break that by accident, Python removes the default
  hash the moment you define equality.""")


class Hashable:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Hashable({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Hashable):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))      # THE SAME FIELDS as __eq__


pair = {Hashable(1, 2), Hashable(1, 2), Hashable(3, 4)}
print(f"\nwith __hash__: a set of three gives {len(pair)} — "
      f"the duplicate collapsed")
print(f"as a dict key: {({Hashable(1, 2): 'origin-ish'})[Hashable(1, 2)]}")


# ---------------------------------------------------------------------------
# 6. HASHABLE MEANS IMMUTABLE
# ---------------------------------------------------------------------------

item = Hashable(1, 2)
bucket = {item}
print(f"\nbefore mutating: item in bucket -> {item in bucket}")

item.x = 99                                # the object is in the wrong bucket
print(f"after item.x = 99: item in bucket -> {item in bucket}")
print(f"but it is still in there: {len(bucket)} element, {list(bucket)}")

bucket.add(Hashable(99, 2))
print(f"adding an EQUAL object: now {len(bucket)} elements — {bucket}")

print("""
  Two objects that compare EQUAL are both in the set, and the original
  cannot be found. Nothing raised. The set is simply broken.

  THE CLEAN RULE: HASHABLE MEANS IMMUTABLE. If your type is mutable, leave
  it unhashable — that is exactly why list is unhashable and tuple is not.
  Day 48's frozen dataclasses make this easy to get right.""")


# ---------------------------------------------------------------------------
# 7. __len__, __bool__, __getitem__, __contains__
# ---------------------------------------------------------------------------


class Sized:
    def __init__(self, *values):
        self.values = list(values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]


s = Sized(3, 4, 5)
print(f"\nlen(s)      {len(s)}")
print(f"s[1]        {s[1]}")
print(f"s[-1]       {s[-1]}")
print(f"for x in s  {[x for x in s]}       <- __getitem__ ALONE gives this")
print(f"4 in s      {4 in s}                <- and this")

print("""
  __getitem__ alone gives you iteration AND `in` for free: Python falls
  back to calling it with 0, 1, 2... until IndexError. Defining __iter__
  and __contains__ properly is better, but this fallback is why some very
  old classes work in for loops.""")

# __len__ ALSO SUPPLIES TRUTHINESS, which is sometimes wrong:
zero = Sized(0, 0)
print(f"\nSized(0, 0) is truthy: {bool(zero)}   <- because len() is 2")


class Vector2:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __len__(self):
        return 2                            # a vector has 2 COMPONENTS

    def __bool__(self):
        return bool(self.x or self.y)       # but a ZERO vector is falsy


print(f"Vector2(0, 0) is truthy: {bool(Vector2(0, 0))}   <- __bool__ wins")
print("  __bool__ is checked FIRST; __len__ is only the fallback.")


# ---------------------------------------------------------------------------
# 8. __slots__ — not a method, and it fixes Day 41's typo bug
# ---------------------------------------------------------------------------


class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


slotted = Slotted(1, 2)
try:
    slotted.z = 3
except AttributeError as e:
    print(f"\nwith __slots__, a typo raises: AttributeError: {e}")

loose = Vector(1, 2)
loose.zz = 3
print(f"without __slots__, it silently succeeds: {loose.__dict__}")

import sys                                  # noqa: E402

print(f"\nmemory: slotted has no __dict__ at all "
      f"({not hasattr(slotted, '__dict__')}), saving "
      f"{sys.getsizeof(loose.__dict__)} bytes per instance")


# ---------------------------------------------------------------------------
# 9. Restraint
# ---------------------------------------------------------------------------

print("""
Every dunder you implement is a PROMISE about how your object behaves with
existing syntax, and a surprising one is worse than an absent one.

    __add__ on a Vector      obvious
    __add__ on a User        a puzzle — what would user + user mean?
    __len__ on an Account    what would it count?

THE TEST: WOULD A READER GUESS WHAT IT DOES WITHOUT LOOKING? If not, write
a named method. `account.transactions_count()` beats a mysterious len().""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Define __eq__ without __hash__ and put the object in a set.
#   * Define __hash__ over DIFFERENT fields than __eq__, then make two
#     equal objects and put both in a set. Count them.
#   * Add a mutable object to a set, change it, and try to find it.
#   * Return False instead of NotImplemented from __eq__, then compare with
#     an int both ways round.
#   * Give a class __len__ returning 0 and use it in an `if`.
