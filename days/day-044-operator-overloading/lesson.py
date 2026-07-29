"""Day 044 — Operator overloading.

    python3 lesson.py
"""

from functools import total_ordering

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. REFLECTED OPERATIONS — traced, so the mechanism is visible
# ---------------------------------------------------------------------------


class Traced:
    """Prints which dunder Python reached for."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Traced({self.value})"

    def __mul__(self, other):
        print(f"    Traced.__mul__({self!r}, {other!r})")
        if not isinstance(other, (int, float)):
            print("      -> NotImplemented")
            return NotImplemented
        return Traced(self.value * other)

    def __rmul__(self, other):
        print(f"    Traced.__rmul__({self!r}, {other!r})  <- the REFLECTED one")
        return self.__mul__(other)


print("traced * 3:")
print(f"  = {Traced(5) * 3}")

print("\n3 * traced:")
print(f"  = {3 * Traced(5)}")

print("""
  `3 * traced` cannot work by calling int.__mul__(3, traced) — int has
  never heard of Traced. So Python does this:

      a * b   ->  a.__mul__(b)
                  if that returns NotImplemented, try b.__rmul__(a)
                  if that also does, raise TypeError

  The int returned NotImplemented, Python tried the RIGHT operand's
  __rmul__, and it worked. That is the whole mechanism.""")


# ---------------------------------------------------------------------------
# 2. NotImplemented vs raising TypeError
# ---------------------------------------------------------------------------


class Polite:
    def __add__(self, other):
        if not isinstance(other, Polite):
            return NotImplemented          # "I do not know how"
        return Polite()


class Rude:
    def __add__(self, other):
        if not isinstance(other, Rude):
            raise TypeError("Rude cannot add that")     # kills the protocol
        return Rude()


try:
    Polite() + "a string"
except TypeError as e:
    print(f"Polite + str  -> TypeError: {e}")

try:
    Rude() + "a string"
except TypeError as e:
    print(f"Rude   + str  -> TypeError: {e}")

print("""
  The FIRST message names both types and the operator. Python generated it
  for free, from NotImplemented. The second is whatever the author typed,
  and it is less useful.

  Worse: raising means no other type can EVER interoperate. A hypothetical
  MoreRude class with __radd__ never gets a chance, because Rude threw
  before Python could try it.

  RETURN NotImplemented FOR THE WRONG TYPE. RAISE FOR A WRONG VALUE.""")


# ---------------------------------------------------------------------------
# 3. sum() and the __radd__ trap
# ---------------------------------------------------------------------------


class NoRadd:
    def __init__(self, n):
        self.n = n

    def __add__(self, other):
        if not isinstance(other, NoRadd):
            return NotImplemented
        return NoRadd(self.n + other.n)


class WithRadd(NoRadd):
    def __radd__(self, other):
        if other == 0:                     # sum() starts from the INT 0
            return self
        return self.__add__(other)


try:
    sum([NoRadd(1), NoRadd(2)])
except TypeError as e:
    print(f"sum() without __radd__: TypeError: {e}")

print(f"sum() with __radd__:    {sum([WithRadd(1), WithRadd(2)]).n}")
print(f"or give sum a start:    {sum([NoRadd(1), NoRadd(2)], NoRadd(0)).n}")

print("""
  sum() begins with the integer 0 and does 0 + first_item. That calls
  int.__add__(0, item), which returns NotImplemented, so Python tries
  item.__radd__(0) — and if there is not one, it fails.

  Two fixes: define __radd__ to handle 0, or always call
  sum(items, start_value). The first makes your type work with code you
  did not write, so prefer it.""")


# ---------------------------------------------------------------------------
# 4. Non-commutative operators reverse their arguments
# ---------------------------------------------------------------------------


class Number:
    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return f"Number({self.n})"

    def __sub__(self, other):
        value = other.n if isinstance(other, Number) else other
        return Number(self.n - value)

    def __rsub__(self, other):
        # `10 - number` arrives here as (self=number, other=10).
        # The answer is other - self, NOT self - other.
        return Number(other - self.n)


print(f"Number(3) - 1  = {Number(3) - 1}")
print(f"10 - Number(3) = {10 - Number(3)}   <- 7, not -7")
print("  If __rsub__ had said `self.n - other`, that would read -7.")


# ---------------------------------------------------------------------------
# 5. Comparison and total_ordering
# ---------------------------------------------------------------------------


@total_ordering
class Version:
    """Six comparison operators from two methods."""

    def __init__(self, major, minor):
        self.major, self.minor = major, minor

    def __repr__(self):
        return f"v{self.major}.{self.minor}"

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)

    def __hash__(self):
        return hash((self.major, self.minor))


a, b = Version(1, 2), Version(1, 10)
print(f"\n{a} <  {b}  {a < b}")
print(f"{a} <= {b}  {a <= b}    <- generated")
print(f"{a} >  {b}  {a > b}   <- generated")
print(f"{a} >= {b}  {a >= b}   <- generated")
print(f"{a} != {b}  {a != b}    <- always free, from __eq__")

versions = [Version(2, 0), Version(1, 10), Version(1, 2)]
print(f"\nsorted:  {sorted(versions)}")
print(f"max:     {max(versions)}")
print(f"in a set: {len({Version(1, 2), Version(1, 2)})}")

print("""
  @total_ordering fills in __le__, __gt__ and __ge__ from __eq__ plus ONE
  ordering method. It costs a little speed (the generated ones call yours)
  and saves four methods' worth of places to make a mistake.

  Note __lt__ also makes sorted(), min() and max() work with no key= —
  which is what Day 27 was working around.""")


# ---------------------------------------------------------------------------
# 6. In-place operators
# ---------------------------------------------------------------------------


class Immutable:
    def __init__(self, n):
        self.n = n

    def __add__(self, other):
        return Immutable(self.n + other.n)


x = Immutable(1)
original = x
x += Immutable(2)                          # falls back to x = x + Immutable(2)
print(f"\nimmutable += : x.n = {x.n}, original.n = {original.n}, "
      f"same object = {x is original}")


class Mutable:
    def __init__(self, items):
        self.items = list(items)

    def __iadd__(self, other):
        self.items.extend(other.items)
        return self                        # MUST return self


y = Mutable([1, 2])
alias = y
y += Mutable([3])
print(f"mutable +=   : y.items = {y.items}, alias.items = {alias.items}, "
      f"same object = {y is alias}")

print("""
  `a += b` tries __iadd__ first and falls back to `a = a + b`. So += works
  without you doing anything.

  Define __iadd__ ONLY for mutable types where in place is genuinely
  cheaper, and RETURN self — forget that and the variable becomes None.

  Note the alias above saw the change. That is exactly the Day 21 surprise,
  and it is why immutable types should NOT define __iadd__.""")


# ---------------------------------------------------------------------------
# 7. Restraint
# ---------------------------------------------------------------------------

print("""
AN OPERATOR MUST MEAN THE OBVIOUS THING.

  Money + Money      obvious
  Money * 3          obvious — three times the amount
  Money * Money      MEANINGLESS. What unit is GBP squared?
  Vector * Vector    AMBIGUOUS — dot? cross? element-wise? Name it.
  User + User        a puzzle
  Account + Account  a puzzle with a plausible-looking answer, which is
                     worse

IF A READER WOULD HAVE TO CHECK, USE A NAMED METHOD.
`account.merge(other)` beats `account + other` every time.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Raise TypeError from __add__ instead of returning NotImplemented, and
#     compare the two error messages.
#   * sum() a list of your type without __radd__.
#   * Write __rsub__ with the operands the wrong way round and test 10 - x.
#   * Define __iadd__ without returning self.
#   * Remove @total_ordering and try `a <= b`.
