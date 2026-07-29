"""Day 047 — Properties and encapsulation.

    python3 lesson.py
"""

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. START WITH A PLAIN ATTRIBUTE
# ---------------------------------------------------------------------------


class AccountV1:
    """Version 1. No property. Nothing wrong with this."""

    def __init__(self, balance):
        self.balance = balance


account = AccountV1(100)
account.balance = 250
print(f"v1: {account.balance}")

# Six months later, a rule appears: the balance cannot go negative.


class AccountV2:
    """Version 2. Same public API, now validated."""

    def __init__(self, balance):
        self.balance = balance          # runs the SETTER, not a bare assign

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError(f"balance cannot be negative, got {value}")
        self._balance = value


account = AccountV2(100)
account.balance = 250                   # IDENTICAL calling code
print(f"v2: {account.balance}")
try:
    account.balance = -50
except ValueError as e:
    print(f"    and now: ValueError: {e}")

print("""
  NOT ONE CALL SITE CHANGED. In Java you write getBalance()/setBalance()
  from the start, because promoting a public field to a method later breaks
  every caller. In Python it does not — @property intercepts the SAME
  syntax.

  So the rule is: A PLAIN ATTRIBUTE UNTIL IT NEEDS A RULE. A property that
  only returns self._x is noise.""")


# ---------------------------------------------------------------------------
# 2. THE RECURSION TRAP
# ---------------------------------------------------------------------------


class Recursive:
    @property
    def value(self):
        return self.value               # NOT self._value


try:
    Recursive().value
except RecursionError:
    print("self.value inside property `value`: RecursionError")
print("  The property calls itself forever. It must be self._value.")


# ---------------------------------------------------------------------------
# 3. READ-ONLY: just omit the setter
# ---------------------------------------------------------------------------


class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius             # no setter -> read-only

    @property
    def area(self):
        return 3.14159 * self._radius ** 2      # computed, never stored


circle = Circle(2)
print(f"\nradius {circle.radius}, area {circle.area:.4f}")
try:
    circle.radius = 5
except AttributeError as e:
    print(f"assigning to it: AttributeError: {e}")

# ...but the underlying attribute is still reachable:
circle._radius = 5
print(f"circle._radius = 5 worked. area is now {circle.area:.4f}")
print("  Python has no privacy. `_radius` is a CONVENTION, not a lock.")


# ---------------------------------------------------------------------------
# 4. COMPUTED PROPERTIES — one source of truth
# ---------------------------------------------------------------------------


class Stored:
    """WRONG: both values stored, so they can disagree."""

    def __init__(self, celsius):
        self.celsius = celsius
        self.fahrenheit = celsius * 9 / 5 + 32


class Computed:
    """RIGHT: one stored value, the other derived."""

    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9      # write through the source


stored = Stored(100)
stored.celsius = 0                      # ...and forgot to update fahrenheit
print(f"\nstored:   {stored.celsius}C is apparently {stored.fahrenheit}F")

computed = Computed(100)
computed.celsius = 0
print(f"computed: {computed.celsius}C is {computed.fahrenheit}F")
computed.fahrenheit = 212
print(f"          set F to 212 -> celsius is {computed.celsius}")

print("""
  ONE SOURCE OF TRUTH, SEVERAL VIEWS OF IT. fahrenheit is not stored, so it
  CANNOT drift — Day 19's clock principle, at object level.

  And because the setter assigns through self.celsius, any validation on
  celsius applies to the fahrenheit route too, written once.""")


# ---------------------------------------------------------------------------
# 5. __init__ MUST GO THROUGH THE SETTER
# ---------------------------------------------------------------------------


class Bypassed:
    def __init__(self, value):
        self._value = value             # BYPASSES the setter

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if new < 0:
            raise ValueError("must be positive")
        self._value = new


bad = Bypassed(-500)
print(f"\nBypassed(-500) was allowed: value = {bad.value}")
try:
    bad.value = -500
except ValueError:
    print("...but `bad.value = -500` raises. The two disagree.")
print("  __init__ must say `self.value = value`, not `self._value = value`.")


# ---------------------------------------------------------------------------
# 6. The underscore conventions
# ---------------------------------------------------------------------------


class Conventions:
    def __init__(self):
        self.public = "part of the API"
        self._internal = "do not touch; may change"
        self.__mangled = "name mangling, not privacy"       # noqa

    def reveal(self):
        return self.__mangled


obj = Conventions()
print(f"\n{'obj.public':<28}{obj.public}")
print(f"{'obj._internal':<28}{obj._internal}   <- reachable, by convention only")
try:
    obj.__mangled
except AttributeError as e:
    print(f"{'obj.__mangled':<28}AttributeError: {e}")
print(f"{'obj._Conventions__mangled':<28}{obj._Conventions__mangled}")
print(f"{'the real attribute name:':<28}"
      f"{[k for k in obj.__dict__ if 'mangl' in k][0]}")

print("""
  name        public. Part of your API.
  _name       internal. Linters and `from x import *` respect it; Python
              does not enforce it.
  __name      NAME MANGLING: rewritten to _ClassName__name.

  Mangling is NOT privacy — obj._Conventions__mangled works. Its actual
  purpose is stopping a SUBCLASS from accidentally colliding with a base
  class's attribute. Use it rarely, never as a security measure.""")


# ---------------------------------------------------------------------------
# 7. Properties cost something
# ---------------------------------------------------------------------------

import time                                     # noqa: E402
from functools import cached_property           # noqa: E402


class Expensive:
    def __init__(self):
        self.calls = 0

    @property
    def slow(self):
        self.calls += 1                 # A SIDE EFFECT IN A GETTER. Do not.
        time.sleep(0.01)
        return "computed"

    @cached_property
    def cached(self):
        time.sleep(0.01)
        return "computed once"


e = Expensive()
start = time.perf_counter()
for _ in range(3):
    e.slow
plain_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
for _ in range(3):
    e.cached
cached_ms = (time.perf_counter() - start) * 1000

print(f"\n{'3 reads of a slow @property':<34}{plain_ms:>8.1f} ms")
print(f"{'3 reads of @cached_property':<34}{cached_ms:>8.1f} ms")
print(f"{'the getter counted its own calls':<34}{e.calls:>8}")

print("""
  A PROPERTY LOOKS FREE AND IS NOT. `obj.x` that runs a query surprises
  everyone. Keep them cheap; if it is expensive, name it fetch_x().

  NO SIDE EFFECTS IN A GETTER. Reading an attribute must not change
  anything — the counter above is a bug, not a feature.

  @cached_property computes once and stores the result. Excellent for
  expensive derived values, and WRONG the moment the inputs can change,
  because it will happily return a stale answer forever.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write self.x inside property x.
#   * Put the setter before the getter.
#   * Assign self._x in __init__ and then compare construction with
#     assignment.
#   * Store a derived value AND its source, change one, and print both.
#   * Reach a __mangled attribute from outside.
