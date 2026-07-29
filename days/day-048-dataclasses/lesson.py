"""Day 048 — Dataclasses.

    python3 lesson.py
"""

from dataclasses import (
    FrozenInstanceError, asdict, astuple, dataclass, field, fields, replace,
)
from datetime import datetime

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. What it generates
# ---------------------------------------------------------------------------


class PointByHand:
    """Fifteen lines to say "a point has an x and a y"."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"PointByHand(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, PointByHand):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)


@dataclass
class Point:
    x: float
    y: float


print(f"by hand:   {PointByHand(1, 2)}")
print(f"dataclass: {Point(1, 2)}")
print(f"equality:  {Point(1, 2) == Point(1, 2)}")
print(f"generated: {[m for m in ('__init__', '__repr__', '__eq__') if m in Point.__dict__]}")

# THE ANNOTATIONS ARE REQUIRED — that is how the decorator finds the fields.


@dataclass
class Partial:
    counted: int
    ignored = "no annotation, so NOT a field"


print(f"\nfields of Partial: {[f.name for f in fields(Partial)]}")
print(f"'ignored' is a plain class attribute: {Partial(1).ignored}")

# ...but they are NOT enforced at runtime:
print(f"Point('a', 'b') = {Point('a', 'b')}   <- annotations are not checks")
print("  They are documentation, and input for mypy (Day 59).")


# ---------------------------------------------------------------------------
# 2. frozen=True — Day 43's whole hash contract, in one word
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenPoint:
    x: float
    y: float


p = FrozenPoint(1, 2)
try:
    p.x = 99
except FrozenInstanceError as e:
    print(f"\nfrozen assignment: FrozenInstanceError: {e}")

print(f"hashable:   {hash(p) == hash(FrozenPoint(1, 2))}")
print(f"in a set:   {len({FrozenPoint(1, 2), FrozenPoint(1, 2), FrozenPoint(3, 4)})}")
print("unfrozen is unhashable: ", end="")
try:
    {Point(1, 2)}
except TypeError as e:
    print(f"{e}")

print("""
  Day 43 spent a page on "defining __eq__ removes __hash__" and "hashable
  means immutable". frozen=True gives you BOTH, correctly, in one word —
  and it is the right default for anything that is a VALUE rather than a
  THING.""")


# ---------------------------------------------------------------------------
# 3. order=True — and why field order becomes API
# ---------------------------------------------------------------------------


@dataclass(order=True)
class Version:
    major: int
    minor: int


@dataclass(order=True)
class Reversed:
    minor: int
    major: int


print(f"\nsorted by (major, minor): "
      f"{sorted([Version(1, 10), Version(2, 0), Version(1, 2)])}")
print(f"sorted by (minor, major): "
      f"{sorted([Reversed(10, 1), Reversed(0, 2), Reversed(2, 1)])}")
print("  Same data, different declaration order, different sort. ORDER IS API.")


@dataclass(order=True)
class Task:
    priority: int
    name: str = field(compare=False)        # excluded from ordering AND ==


print(f"\nname excluded: {Task(1, 'a') == Task(1, 'b')}")


# ---------------------------------------------------------------------------
# 4. field() — and the mutable default, REJECTED
# ---------------------------------------------------------------------------

try:
    @dataclass
    class Broken:
        items: list = []
except ValueError as e:
    print(f"\n`items: list = []` -> ValueError: {e}")

print("""  Day 32's bug, caught AT CLASS-DEFINITION TIME rather than shipped.
  A hand-written __init__ would have let it through silently. That alone
  is a reason to reach for @dataclass.""")


@dataclass
class Order:
    id: int
    items: list = field(default_factory=list)          # a NEW list each time
    created: datetime = field(default_factory=datetime.now)
    _cache: dict = field(default_factory=dict, repr=False, compare=False)
    total: float = field(init=False, default=0.0)      # not a parameter

    def __post_init__(self):
        self.total = len(self.items) * 10.0


a, b = Order(1), Order(2)
a.items.append("x")
print(f"\nseparate lists: a={a.items} b={b.items} shared={a.items is b.items}")

order = Order(3, ["pen", "pad"])
print(f"repr hides _cache: {order}")
print(f"total was computed in __post_init__: {order.total}")


# ---------------------------------------------------------------------------
# 5. __post_init__, including on a frozen class
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Temperature:
    celsius: float
    kelvin: float = field(init=False)

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError(f"{self.celsius} is below absolute zero")
        # FROZEN means you cannot assign — even here. This is exactly what
        # the generated __init__ does internally.
        object.__setattr__(self, "kelvin", self.celsius + 273.15)


print(f"\n{Temperature(100)}")
try:
    Temperature(-500)
except ValueError as e:
    print(f"validated: ValueError: {e}")


# ---------------------------------------------------------------------------
# 6. The free functions
# ---------------------------------------------------------------------------

point = Point(1, 2)
print(f"\nasdict:   {asdict(point)}")
print(f"astuple:  {astuple(point)}")
print(f"replace:  {replace(point, y=99)}   <- a NEW object")
print(f"fields:   {[(f.name, f.type) for f in fields(Point)]}")
print("  asdict() is how a dataclass becomes JSON on Day 55.")
print("  replace() is the frozen-object equivalent of assignment.")


# ---------------------------------------------------------------------------
# 7. Field order and defaults
# ---------------------------------------------------------------------------

try:
    @dataclass
    class BadOrder:
        with_default: int = 0
        without_default: str
except (TypeError, NameError) as e:
    print(f"\nnon-default after default: {type(e).__name__}: {e}")

print("  Same rule as Day 32's function signatures, same reason.")
print("  kw_only=True (3.10+) removes the constraint entirely.")


# ---------------------------------------------------------------------------
# 8. WHEN NOT TO USE ONE
# ---------------------------------------------------------------------------

print("""
DO NOT USE @dataclass WHEN...

  THE CLASS IS MOSTLY BEHAVIOUR
    Day 41's BankAccount has five methods and one invariant. The generated
    __init__ saves two lines, and the generated __eq__ is ACTIVELY WRONG:
    two accounts with the same balance are not the same account.

  IT NEEDS CLASS-LEVEL STATE
    Day 42's Employee issues sequential IDs from a class counter. There is
    no field-list way to say that.

  YOU NEED SETTABLE COMPUTED PROPERTIES
    Day 47's Temperature lets you assign .fahrenheit. A frozen dataclass
    cannot; an unfrozen one loses the hash.

  IDENTITY MATTERS MORE THAN VALUE
    Generated __eq__ compares fields. For a User, an Account, a Session or
    a Connection, that is the wrong question.

THE RULE OF THUMB:
    @dataclass FOR VALUES        Point, Money, Config, Event
    a plain class FOR THINGS     Account, Session, Parser, Connection

THE ALTERNATIVES
    NamedTuple           immutable AND tuple-compatible (Day 23)
    TypedDict            a dict with a declared shape (Day 66)
    pydantic.BaseModel   VALIDATES AND COERCES at runtime — the right
                         choice for data from outside your program, and
                         the foundation of FastAPI (Day 85)
    attrs                the library dataclasses were based on""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write `items: list = []` and read the error.
#   * Remove an annotation and check fields().
#   * Put a non-default field after a defaulted one.
#   * Make a frozen dataclass and assign in __post_init__ without
#     object.__setattr__.
#   * Reorder the fields of an order=True class and re-sort.
