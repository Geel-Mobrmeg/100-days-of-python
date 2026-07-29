"""Day 048 build — three earlier classes rewritten, and one left alone.

    python3 build.py

REWRITTEN
  Day 43's Vector        -> frozen, ordered, slotted
  Day 23's Point         -> frozen
  a Config object        -> the case dataclasses were invented for

LEFT ALONE, ON PURPOSE
  Day 41's BankAccount   -> and the file explains, with code, why the
                            generated __eq__ would be a bug rather than a
                            saving

Line counts are measured with inspect, not guessed.
"""

import inspect
import math
from dataclasses import dataclass, field, replace

WIDTH = 78


def loc(obj):
    """Non-blank, non-comment lines of an object's source."""
    return len([
        line for line in inspect.getsource(obj).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ])


# ###########################################################################
# 1. VECTOR — Day 43, by hand
# ###########################################################################

class VectorByHand:
    __slots__ = ("_x", "_y")

    def __init__(self, x, y):
        object.__setattr__(self, "_x", float(x))
        object.__setattr__(self, "_y", float(y))

    def __setattr__(self, name, value):
        raise AttributeError("Vector is immutable")

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self):
        return f"VectorByHand({self._x:g}, {self._y:g})"

    def __eq__(self, other):
        if not isinstance(other, VectorByHand):
            return NotImplemented
        return (self._x, self._y) == (other._x, other._y)

    def __hash__(self):
        return hash((self._x, self._y))

    def __lt__(self, other):
        if not isinstance(other, VectorByHand):
            return NotImplemented
        return abs(self) < abs(other)

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __abs__(self):
        return math.hypot(self._x, self._y)

    def __add__(self, other):
        if not isinstance(other, VectorByHand):
            return NotImplemented
        return VectorByHand(self._x + other._x, self._y + other._y)


# ###########################################################################
#    ...and as a dataclass
# ###########################################################################

@dataclass(frozen=True, slots=True)
class Vector:
    x: float
    y: float

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __lt__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return abs(self) < abs(other)

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)


print("=" * WIDTH)
print(f"{'THREE REWRITES':^{WIDTH}}")
print("=" * WIDTH)

print("\n1. VECTOR")
print(f"   {'by hand':<28}{loc(VectorByHand):>4} lines")
print(f"   {'as a dataclass':<28}{loc(Vector):>4} lines")
print(f"   {'deleted':<28}{loc(VectorByHand) - loc(Vector):>4}")

v, w = Vector(3, 4), Vector(1, 2)
checks = [
    ("repr", repr(v)),
    ("equality", Vector(3, 4) == Vector(3, 4)),
    ("hashable, deduplicates", len({Vector(3, 4), Vector(3, 4), w})),
    ("immutable", "raises"),
    ("__slots__, so typos raise", "raises"),
    ("abs()", abs(v)),
    ("addition", v + w),
    ("sorted by magnitude", sorted([v, w])),
    ("replace()", replace(v, y=99)),
]
for label, value in checks:
    print(f"   {label:<28}{str(value):>{WIDTH - 34}}")

for label, attempt in [("v.x = 9", lambda: setattr(v, "x", 9)),
                       ("v.z = 9", lambda: setattr(v, "z", 9))]:
    try:
        attempt()
        print(f"   {label:<28}{'ALLOWED':>{WIDTH - 34}}")
    except (AttributeError, Exception) as exc:      # noqa: B014
        print(f"   {label:<28}{type(exc).__name__:>{WIDTH - 34}}")

print("""
   frozen=True generated __eq__ AND __hash__ correctly — the contract
   Day 43 spent a page on. slots=True gave the memory saving and the typo
   protection. Only __abs__, __lt__ and __add__ had to be written, because
   only they contain an actual idea.""")

# ###########################################################################
# 2. POINT — Day 23's namedtuple, grown up
# ###########################################################################


@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float

    def distance_to(self, other):
        return math.hypot(other.x - self.x, other.y - self.y)

    def midpoint(self, other):
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)


a, b = Point(0, 0), Point(3, 4)
print("\n2. POINT")
print(f"   {'distance':<28}{a.distance_to(b):>{WIDTH - 34}}")
print(f"   {'midpoint':<28}{str(a.midpoint(b)):>{WIDTH - 34}}")
print(f"   {'ordered':<28}{str(sorted([b, a])):>{WIDTH - 34}}")
print(f"   {'as a dict key':<28}"
      f"{({Point(0, 0): 'origin'})[a]:>{WIDTH - 34}}")
print("""
   Day 23 used a namedtuple for this. The dataclass loses tuple-indexing
   (p[0]) and gains methods, defaults and a clearer repr. Choose on whether
   callers need it to BEHAVE like a tuple.""")

# ###########################################################################
# 3. CONFIG — the case dataclasses were invented for
# ###########################################################################


@dataclass(frozen=True, kw_only=True)
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    timeout: float = 30.0
    retries: int = 3
    allowed_hosts: tuple = ()
    headers: dict = field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self):
        if not 1 <= self.port <= 65535:
            raise ValueError(f"port {self.port} is out of range")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


default = Config()
production = replace(default, host="api.example.com", port=443, debug=False)

print("\n3. CONFIG")
print(f"   {'defaults':<20}{str(default)[:52]:>{WIDTH - 26}}")
print(f"   {'one override':<20}{str(production)[:52]:>{WIDTH - 26}}")
print(f"   {'immutable':<20}", end="")
try:
    default.port = 99
    print(f"{'ALLOWED':>{WIDTH - 26}}")
except Exception as exc:                            # noqa: BLE001
    print(f"{type(exc).__name__:>{WIDTH - 26}}")

for label, attempt in [("port 99999", lambda: Config(port=99999)),
                       ("timeout 0", lambda: Config(timeout=0)),
                       ("positional args", lambda: Config("host"))]:
    try:
        attempt()
        print(f"   {label:<20}{'ALLOWED':>{WIDTH - 26}}")
    except (ValueError, TypeError) as exc:
        print(f"   {label:<20}{type(exc).__name__:>{WIDTH - 26}}")

print("""
   kw_only=True means Config("api.example.com") is a TypeError — nobody can
   pass seven positional arguments in the wrong order. frozen=True means a
   config cannot be edited halfway through a run. __post_init__ validates
   once, at construction.

   Seven fields, seven defaults, full validation, immutable, comparable,
   printable, in about fifteen lines. THIS is what dataclasses are for.""")

# ###########################################################################
# 4. THE ONE LEFT ALONE
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'AND THE ONE THAT SHOULD NOT BE A DATACLASS':^{WIDTH}}")
print("=" * WIDTH)


@dataclass
class AccountAsDataclass:
    """Day 41's BankAccount, naively converted. This is a BUG."""

    owner: str
    balance: float = 0.0
    history: list = field(default_factory=list)

    def deposit(self, amount):
        self.balance += amount
        self.history.append(amount)


ada_1 = AccountAsDataclass("Ada", 100.0)
ada_2 = AccountAsDataclass("Ada", 100.0)

print("  two DIFFERENT accounts, same owner and balance:")
print(f"  {'ada_1 == ada_2':<38}{str(ada_1 == ada_2):>{WIDTH - 42}}")
print(f"  {'same object?':<38}{str(ada_1 is ada_2):>{WIDTH - 42}}")

ada_1.deposit(50)
print(f"  {'after ada_1.deposit(50)':<38}"
      f"{str(ada_1 == ada_2):>{WIDTH - 42}}")

print("""
  Two people opened accounts with the same name and the same opening
  balance, and the system says they are THE SAME ACCOUNT. Deposit into one
  and they become different again.

  That is not a rough edge, it is a wrong answer to an important question.
  An account has an IDENTITY: two accounts are the same account if they are
  the same account, not if their fields match. Generated __eq__ cannot
  express that, and the default (identity) was already correct.

  THE OTHER THREE REASONS IT STAYS A PLAIN CLASS:

    * it is mostly BEHAVIOUR — deposit, withdraw, transfer, statement,
      check_invariants. The generated __init__ saves two lines out of a
      hundred.
    * it has an INVARIANT (balance >= 0) that must be enforced on every
      route, which is Day 47's property, not a field list.
    * `history` must never be replaced wholesale, and a dataclass hands
      callers a public mutable attribute by default.

  THE RULE:  @dataclass FOR VALUES,  a plain class FOR THINGS.
             Point, Money, Config, Event  ->  values
             Account, Session, Parser     ->  things""")

# ###########################################################################
# SUMMARY
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT WAS DELETED':^{WIDTH}}")
print("=" * WIDTH)
print(f"  {'CLASS':<22}{'BY HAND':>10}{'DATACLASS':>12}{'SAVED':>10}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'Vector':<22}{loc(VectorByHand):>10}{loc(Vector):>12}"
      f"{loc(VectorByHand) - loc(Vector):>10}")
print(f"  {'Point':<22}{'~25':>10}{loc(Point):>12}"
      f"{25 - loc(Point):>10}")
print(f"  {'Config':<22}{'~45':>10}{loc(Config):>12}"
      f"{45 - loc(Config):>10}")
print(f"  {'BankAccount':<22}{'100':>10}{'-':>12}{'0':>10}")
print("  " + "-" * (WIDTH - 4))
print("""
  The saving is real and it is not the point. What @dataclass actually buys
  is that the generated __eq__, __hash__ and __repr__ are CORRECT — Day 43
  showed how easy the hash contract is to get subtly wrong by hand, and
  frozen=True gets it right every time.

  The judgement is knowing which of your classes it should not touch.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add eq=False to AccountAsDataclass. The identity problem disappears —
#     so a dataclass CAN model an account, if you turn off the feature that
#     made it attractive. Decide whether that is worth it.
#
#   * Convert Day 44's Money. frozen=True and order=True generate most of
#     it, and the CURRENCY CHECK in __add__ is the part that cannot be
#     generated — which is exactly the part that made it interesting.
#
#   * Convert Day 47's Temperature. You will find you can have validation
#     (__post_init__) or a settable .fahrenheit, but not both. Say which
#     you would give up.
#
#   * Give Config a `from_env()` classmethod and a `to_json()` using
#     asdict(). That combination — frozen, validated, serialisable — is
#     what every real application's settings object looks like.
