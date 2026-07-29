"""Day 043 build — a Vector that prints, compares and lives in a set.

    python3 build.py

The maths is trivial. The exercise is the PROTOCOL: making an object that
works with Python's existing vocabulary — len(), ==, in, [], for, f-strings,
sorted(), set() — instead of inventing its own.

The last section checks the __eq__/__hash__ contract holds under a few
thousand random vectors, because that is the one thing here that fails
silently.
"""

import math
import random

WIDTH = 76


class Vector:
    """An immutable 2D vector.

    IMMUTABLE ON PURPOSE. Hashable means immutable (see the hash contract
    below), and every operation returns a NEW vector rather than mutating
    this one — which is also what makes them safe to share and to put in
    sets.

    __slots__ costs the dynamic __dict__ and buys two things: a typo like
    `v.z = 1` raises instead of silently creating an attribute, and each
    instance is markedly smaller.
    """

    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        # Assign through object.__setattr__ so __setattr__ below can refuse
        # everything else. This is the cheap version of Day 47's @property.
        object.__setattr__(self, "_x", float(x))
        object.__setattr__(self, "_y", float(y))

    # -- immutability ------------------------------------------------------

    def __setattr__(self, name, value):
        raise AttributeError(
            f"Vector is immutable; cannot set {name!r}. "
            f"Use v + Vector(...) or Vector(...) instead."
        )

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    # -- how it PRINTS -----------------------------------------------------

    def __repr__(self):
        """Unambiguous, and eval-able — the gold standard."""
        return f"Vector({self._x:g}, {self._y:g})"

    def __str__(self):
        """Readable."""
        return f"({self._x:g}, {self._y:g})"

    def __format__(self, spec):
        """Makes f'{v:.2f}' work, applying the spec to both components."""
        if not spec:
            return str(self)
        return f"({self._x:{spec}}, {self._y:{spec}})"

    # -- how it COMPARES ---------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented        # let the other type try
        # math.isclose, not ==, because these are floats (Day 5).
        return (math.isclose(self._x, other._x)
                and math.isclose(self._y, other._y))

    def __hash__(self):
        """THE CONTRACT: equal objects MUST hash equally.

        Hashing the same tuple of fields that __eq__ compares is what
        guarantees it. Round first, so that two vectors __eq__ considers
        close also land in the same bucket — otherwise 0.1+0.2 and 0.3
        would be equal but hash apart, and the set would hold both.
        """
        return hash((round(self._x, 9), round(self._y, 9)))

    def __lt__(self, other):
        """Order by magnitude, so sorted() works."""
        if not isinstance(other, Vector):
            return NotImplemented
        return abs(self) < abs(other)

    # -- how it BEHAVES LIKE A CONTAINER -----------------------------------

    def __len__(self):
        return 2                         # a 2D vector has two COMPONENTS

    def __bool__(self):
        """Explicit, because __len__ alone would make (0,0) truthy."""
        return bool(self._x or self._y)

    def __getitem__(self, index):
        return (self._x, self._y)[index]

    def __iter__(self):
        """Makes `x, y = v` work — Day 23's unpacking, on your own type."""
        yield self._x
        yield self._y

    def __contains__(self, value):
        return value in (self._x, self._y)

    # -- arithmetic (Day 44 covers this properly) --------------------------

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self._x + other._x, self._y + other._y)

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self._x - other._x, self._y - other._y)

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self._x * scalar, self._y * scalar)

    __rmul__ = __mul__                   # so 3 * v works as well as v * 3

    def __neg__(self):
        return Vector(-self._x, -self._y)

    def __abs__(self):
        """abs(v) is the magnitude."""
        return math.hypot(self._x, self._y)

    # -- named methods, for things syntax would not make obvious ----------

    def dot(self, other):
        """Dot product. NOT __mul__ — v * w is ambiguous (dot? cross?)."""
        return self._x * other._x + self._y * other._y

    def normalised(self):
        length = abs(self)
        if not length:
            raise ValueError("cannot normalise a zero vector")
        return self * (1 / length)

    def angle_to(self, other):
        """Angle in degrees between two vectors."""
        denominator = abs(self) * abs(other)
        if not denominator:
            raise ValueError("angle undefined for a zero vector")
        cosine = max(-1.0, min(1.0, self.dot(other) / denominator))
        return math.degrees(math.acos(cosine))


# ===========================================================================
# 1. Every protocol, exercised
# ===========================================================================

v = Vector(3, 4)
w = Vector(1, 2)

print("=" * WIDTH)
print(f"{'VECTOR':^{WIDTH}}")
print("=" * WIDTH)

rows = [
    ("repr(v)", repr(v)),
    ("str(v)", str(v)),
    ("f'{v:.3f}'", f"{v:.3f}"),
    ("len(v)", len(v)),
    ("bool(v)", bool(v)),
    ("bool(Vector(0,0))", bool(Vector(0, 0))),
    ("v[0], v[1]", (v[0], v[1])),
    ("x, y = v", tuple(v)),
    ("3.0 in v", 3.0 in v),
    ("v == Vector(3,4)", v == Vector(3, 4)),
    ("v == 'not a vector'", v == "not a vector"),
    ("v + w", v + w),
    ("v - w", v - w),
    ("v * 2", v * 2),
    ("2 * v", 2 * v),
    ("-v", -v),
    ("abs(v)", abs(v)),
    ("v.dot(w)", v.dot(w)),
    ("v.normalised()", f"{v.normalised():.4f}"),
    ("v.angle_to(w)", f"{v.angle_to(w):.2f} degrees"),
]
for label, value in rows:
    print(f"  {label:<24}{str(value):>{WIDTH - 26}}")

print(f"\n  {'sorted by magnitude':<24}"
      f"{str(sorted([Vector(5, 5), Vector(1, 0), v])):>{WIDTH - 26}}")
print(f"  {'max()':<24}{str(max([Vector(1, 0), v, w])):>{WIDTH - 26}}")
print(f"  {'sum of a list':<24}"
      f"{str(sum([v, w, Vector(1, 1)], Vector(0, 0))):>{WIDTH - 26}}")

# ===========================================================================
# 2. Immutability
# ===========================================================================

print()
print("-" * WIDTH)
print("IMMUTABILITY")
print("-" * WIDTH)

for label, attempt in [
    ("v.x = 99", lambda: setattr(v, "x", 99)),
    ("v._x = 99", lambda: setattr(v, "_x", 99)),
    ("v.z = 99  (a typo)", lambda: setattr(v, "z", 99)),
]:
    try:
        attempt()
        print(f"  {label:<28}ALLOWED — should it be?")
    except AttributeError as exc:
        print(f"  {label:<28}AttributeError: {str(exc)[:38]}")

print(f"  {'v is unchanged':<28}{v!r}")
print("""
  __slots__ stops NEW attributes; __setattr__ stops assignment to the real
  ones. Together they make the object genuinely immutable, which is what
  lets it be hashed safely. Day 48's @dataclass(frozen=True) does all of
  this in one line.""")

# ===========================================================================
# 3. THE HASH CONTRACT, under attack
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE __eq__ / __hash__ CONTRACT':^{WIDTH}}")
print("=" * WIDTH)

random.seed(11)
sample = [
    Vector(random.randint(-4, 4), random.randint(-4, 4))
    for _ in range(4000)
]

violations = 0
for first in sample[:400]:
    for second in sample[:400]:
        if first == second and hash(first) != hash(second):
            violations += 1

unique_by_set = len(set(sample))
unique_by_eq = 0
seen = []
for candidate in sample:
    if not any(candidate == other for other in seen):
        seen.append(candidate)
        unique_by_eq += 1

print(f"{'vectors generated':<44}{len(sample):>{WIDTH - 44},}")
print(f"{'pairs checked for equal-but-different-hash':<44}"
      f"{400 * 400:>{WIDTH - 44},}")
print(f"{'contract violations':<44}{violations:>{WIDTH - 44}}")
print(f"{'distinct according to set()':<44}{unique_by_set:>{WIDTH - 44}}")
print(f"{'distinct according to == alone':<44}{unique_by_eq:>{WIDTH - 44}}")
print(f"{'set() and == agree':<44}"
      f"{str(unique_by_set == unique_by_eq):>{WIDTH - 44}}")

print("""
  That last line is the whole test. If __hash__ used different fields from
  __eq__, set() would find MORE distinct vectors than == does — equal
  objects landing in different buckets, both kept, and nothing raised.

  Sets and dicts find by HASH first and compare second. Get the contract
  wrong and they are quietly, permanently wrong.""")

# What a broken version does, for contrast:


class BadVector:
    """__hash__ over the WRONG fields. Deliberately broken."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash(self.x)              # ignores y!


bad_sample = [BadVector(x, y) for x in range(3) for y in range(3)] * 2
bad_set = set(bad_sample)
bad_eq = 0
seen = []
for candidate in bad_sample:
    if not any(candidate == other for other in seen):
        seen.append(candidate)
        bad_eq += 1

print(f"  {'BadVector: distinct by set()':<44}{len(bad_set):>{WIDTH - 46}}")
print(f"  {'BadVector: distinct by ==':<44}{bad_eq:>{WIDTH - 46}}")
print(f"  {'they agree':<44}{str(len(bad_set) == bad_eq):>{WIDTH - 46}}")
print("""
  BadVector hashes only x, so (1,0) and (1,5) collide into one bucket —
  where __eq__ then separates them, so the set is actually still CORRECT,
  just slow. Collisions are legal.

  The fatal direction is the other one: EQUAL OBJECTS THAT HASH
  DIFFERENTLY. Change BadVector.__eq__ to compare only x and leave the
  hash alone, and the numbers above diverge.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Delete __hash__ and put a Vector in a set. Read the TypeError, then
#     check what Vector.__hash__ has become.
#
#   * Make Vector mutable (drop __setattr__), add one to a set, change x,
#     and try `v in bucket`. It is False, and the vector is still in there.
#     That is the bug the immutability exists to prevent.
#
#   * dot() is a named method, not __mul__, because v * w is ambiguous —
#     dot product? cross product? element-wise? Decide what YOU think *
#     should mean, then read what numpy chose and why.
#
#   * Add __matmul__ so `v @ w` is the dot product. That operator was added
#     to Python in 3.5 for exactly this reason.
#
#   * On Day 44 add __truediv__, __lt__ for a total ordering, and see what
#     functools.total_ordering saves. On Day 48 rewrite the whole class as
#     @dataclass(frozen=True, order=True) and count the lines you delete.
