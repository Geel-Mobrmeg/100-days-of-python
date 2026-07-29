"""Day 049 — Abstract bases and protocols.

    python3 lesson.py
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence, Sized
from typing import Protocol, runtime_checkable

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. Day 45's problem: NotImplementedError fails LATE
# ---------------------------------------------------------------------------


class OldStyleShape:
    def area(self):
        raise NotImplementedError


class OldSquare(OldStyleShape):
    """Forgot area()."""

    def __init__(self, side):
        self.side = side


shape = OldSquare(3)                     # created HAPPILY
print("OldSquare(3) was constructed with no area() at all")
try:
    shape.area()
except NotImplementedError:
    print("  ...and failed only when area() was finally called")


# ---------------------------------------------------------------------------
# 2. ABC fails at CONSTRUCTION, naming the missing method
# ---------------------------------------------------------------------------


class Shape(ABC):
    @abstractmethod
    def area(self):
        """Return the area."""

    @abstractmethod
    def perimeter(self):
        """Return the perimeter."""

    def describe(self):
        """CONCRETE. Written once, inherited by every implementation."""
        return f"{type(self).__name__}: area {self.area():.2f}"


class Incomplete(Shape):
    def area(self):
        return 1.0                       # perimeter is still missing


try:
    Incomplete()
except TypeError as e:
    print(f"\nIncomplete(): TypeError: {e}")

try:
    Shape()
except TypeError as e:
    print(f"Shape():      TypeError: {e}")


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side


print(f"complete:     {Square(3).describe()}")

print("""
  The failure moved from "when somebody calls the method" to "when somebody
  tries to build the object", and the message NAMES what is missing. That
  is the guarantee Day 45 wanted and could not get.

  Note describe() is concrete: ABCs can mix contract and shared code, which
  is real reuse and not just a promise.""")


# ---------------------------------------------------------------------------
# 3. Protocol — structural, not nominal
# ---------------------------------------------------------------------------


@runtime_checkable
class Drawable(Protocol):
    """Anything with these methods satisfies this. No inheritance needed."""

    def draw(self) -> str: ...
    def bounds(self) -> tuple: ...


class Sprite:
    """Does NOT inherit from Drawable. Satisfies it anyway."""

    def draw(self):
        return "a sprite"

    def bounds(self):
        return (0, 0, 32, 32)


class Label:
    def __init__(self, text):
        self.text = text

    def draw(self):
        return f"label {self.text!r}"

    def bounds(self):
        return (0, 0, len(self.text) * 8, 16)


def render(items):
    """Takes anything Drawable. In a type hint: items: Iterable[Drawable]."""
    return [item.draw() for item in items]


print(f"\nrender: {render([Sprite(), Label('hi')])}")
print(f"isinstance(Sprite(), Drawable): {isinstance(Sprite(), Drawable)}")
print(f"Sprite inherits Drawable:       {issubclass(Sprite, Drawable) and 'declared' or 'no'}")
print(f"Sprite.__mro__:                 "
      f"{[c.__name__ for c in Sprite.__mro__]}")

print("""
  STRUCTURAL TYPING: the SHAPE counts, not the ancestry. Sprite never
  mentions Drawable and satisfies it. That is duck typing, written down and
  checkable by mypy (Day 59).

  THE DECISIVE ADVANTAGE: it works on classes you DO NOT OWN. You can
  declare that pathlib.Path satisfies your FileLike protocol without
  touching pathlib.""")

# ...but the runtime check is WEAK:


class Liar:
    def draw(self, canvas, x, y, scale):     # totally different signature
        return "wrong"

    def bounds(self):
        return None


print(f"\nisinstance(Liar(), Drawable): {isinstance(Liar(), Drawable)}   "
      f"<- it only checked the NAMES")
try:
    render([Liar()])
except TypeError as e:
    print(f"and calling it: TypeError: {e}")
print("  @runtime_checkable checks method NAMES, not signatures. mypy is")
print("  the real check; isinstance here is a smoke alarm, not a lock.")


# ---------------------------------------------------------------------------
# 4. register() — claiming a third-party class satisfies an ABC
# ---------------------------------------------------------------------------


class Serialiser(ABC):
    @abstractmethod
    def dumps(self, obj): ...


import json                                       # noqa: E402

Serialiser.register(json.JSONEncoder)

print(f"\nafter register(): "
      f"{issubclass(json.JSONEncoder, Serialiser)}")
print("  ...and Python checked NOTHING. register() is a promise you make,")
print("  not a verification. Protocol at least lets mypy check it.")


# ---------------------------------------------------------------------------
# 5. collections.abc — the best-designed ABCs in the language
# ---------------------------------------------------------------------------


class Playlist(Sequence):
    """Only __len__ and __getitem__ are written. Look what arrives."""

    def __init__(self, *tracks):
        self._tracks = list(tracks)

    def __len__(self):
        return len(self._tracks)

    def __getitem__(self, index):
        return self._tracks[index]


playlist = Playlist("a", "b", "c")
print("\nwritten by hand:  __len__, __getitem__")
print(f"  len()           {len(playlist)}")
print(f"  indexing        {playlist[1]}")
print(f"  slicing         {playlist[0:2]}")
print(f"  iteration       {[t for t in playlist]}")
print(f"  `in`            {'b' in playlist}")
print(f"  reversed()      {list(reversed(playlist))}")
print(f"  .index('c')     {playlist.index('c')}")
print(f"  .count('a')     {playlist.count('a')}")

free = [m for m in ("__contains__", "__iter__", "__reversed__", "index", "count")
        if m not in Playlist.__dict__]
print(f"  inherited free: {free}")

print("""
  Two methods in, eight capabilities out. That is what a well-designed
  abstract base looks like, and collections.abc is worth reading.

  FOR TYPE HINTS, PREFER THESE TO CONCRETE TYPES:
    def f(items: Iterable[str])   accepts list, tuple, set, generator
    def f(items: list[str])       accepts one thing""")

print(f"\n  isinstance([1,2], Sequence)  {isinstance([1, 2], Sequence)}")
print(f"  isinstance('ab', Sequence)   {isinstance('ab', Sequence)}")
print(f"  isinstance({{1,2}}, Sequence)  {isinstance({1, 2}, Sequence)}"
      f"   <- a set is not ordered")
print(f"  isinstance({{1,2}}, Iterable)  {isinstance({1, 2}, Iterable)}")
print(f"  isinstance({{1,2}}, Sized)     {isinstance({1, 2}, Sized)}")


# ---------------------------------------------------------------------------
# 6. Which to use
# ---------------------------------------------------------------------------

print("""
  USE ABC WHEN                        USE Protocol WHEN
  you own all the implementations     they are third-party or unknown
  you want to share concrete code     you only need the contract
  you want a runtime guarantee        static checking is enough
  the relationship is genuinely is-a  anything with the shape will do
  plugins registering with you        a function's parameter type

  A FRAMEWORK EXTENSION POINT -> ABC. Loud early failure, shared code.
  A FUNCTION PARAMETER        -> Protocol. Accept anything that works.
  SMALL INTERNAL CODE         -> neither. Plain duck typing is fine.

DESIGNING THE INTERFACE IS THE ACTUAL WORK

  * KEEP IT SMALL. Five methods x three implementations = fifteen
    obligations.
  * DEPEND ON BEHAVIOUR, NOT DATA. save(record), not get_connection().
  * DO NOT LEAK THE IMPLEMENTATION. An interface with execute_sql() can
    only be implemented by databases — you have abstracted nothing.
  * SEGREGATE. Two interfaces of two methods beat one of four when some
    implementers only need half.

  THE TEST: CAN YOU WRITE A SECOND, GENUINELY DIFFERENT IMPLEMENTATION?
  If the only one you can imagine is the one you have, the interface is a
  description of your class, not an abstraction.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write an ABC subclass missing one method and read the TypeError.
#   * Use @abstractmethod WITHOUT inheriting ABC. It does nothing.
#   * Satisfy a Protocol with the right names and wrong signatures.
#   * Inherit collections.abc.Mapping with only __getitem__, __len__ and
#     __iter__, and count what you got.
#   * Write Day 46's channel/formatter/logger/retry protocols.
