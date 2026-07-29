"""Day 045 build — a shape hierarchy behind one interface.

    python3 build.py

Seven shapes, one base class, and a caller that never asks what anything is.

The test of the design is at the bottom: every function there is written
against `Shape` and works on all seven — including one added at the end that
the report code has never seen.

Every area is checked against a known formula, because a hierarchy that is
elegantly wrong is still wrong.
"""

import math

WIDTH = 78


class Shape:
    """The interface. Subclasses supply area() and perimeter().

    Everything else here is written ONCE and works for every shape, present
    and future, because it calls self.area() and lets the subclass answer.
    """

    def area(self):
        raise NotImplementedError(
            f"{type(self).__name__} must implement area()"
        )

    def perimeter(self):
        raise NotImplementedError(
            f"{type(self).__name__} must implement perimeter()"
        )

    # -- written once, inherited by all -----------------------------------

    @property
    def name(self):
        return type(self).__name__

    def compactness(self):
        """How circle-like the shape is: 1.0 for a circle, less for others.

        4*pi*area / perimeter^2 — the isoperimetric quotient. A genuinely
        useful thing to compute for ANY shape, which is why it belongs in
        the base rather than being repeated seven times.
        """
        p = self.perimeter()
        return (4 * math.pi * self.area()) / (p * p) if p else 0.0

    def scaled(self, factor):
        """Return a new shape `factor` times larger. Subclasses override."""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.name}(area={self.area():.3f})"

    def __lt__(self, other):
        if not isinstance(other, Shape):
            return NotImplemented
        return self.area() < other.area()      # so sorted() works (Day 44)


# ---------------------------------------------------------------------------
# The shapes. Each supplies its own area() and perimeter() and nothing else.
# ---------------------------------------------------------------------------


class Circle(Shape):
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("radius must be positive")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

    def scaled(self, factor):
        return Circle(self.radius * factor)


class Rectangle(Shape):
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("sides must be positive")
        self.width, self.height = width, height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def scaled(self, factor):
        return Rectangle(self.width * factor, self.height * factor)


class Square(Shape):
    """NOT Square(Rectangle).

    A square is a rectangle in geometry and NOT in code: Rectangle's
    contract lets a caller set width and height independently, and a square
    cannot honour that (lesson.py section 5). Both implement Shape; neither
    inherits from the other. That is the Liskov test, applied.
    """

    def __init__(self, side):
        if side <= 0:
            raise ValueError("side must be positive")
        self.side = side

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side

    def scaled(self, factor):
        return Square(self.side * factor)


class Triangle(Shape):
    def __init__(self, a, b, c):
        sides = sorted((a, b, c))
        if sides[0] <= 0:
            raise ValueError("sides must be positive")
        if sides[0] + sides[1] <= sides[2]:
            raise ValueError(f"{a}, {b}, {c} cannot form a triangle")
        self.a, self.b, self.c = a, b, c

    def area(self):
        """Heron's formula — works for any valid triangle."""
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self):
        return self.a + self.b + self.c

    def scaled(self, factor):
        return Triangle(self.a * factor, self.b * factor, self.c * factor)


class RegularPolygon(Shape):
    """Any regular n-sided polygon. One class, infinitely many shapes."""

    def __init__(self, sides, length):
        if sides < 3:
            raise ValueError("a polygon needs at least 3 sides")
        if length <= 0:
            raise ValueError("length must be positive")
        self.sides, self.length = sides, length

    def area(self):
        return (self.sides * self.length ** 2) / (4 * math.tan(math.pi / self.sides))

    def perimeter(self):
        return self.sides * self.length

    def scaled(self, factor):
        return RegularPolygon(self.sides, self.length * factor)

    @property
    def name(self):
        names = {3: "Triangle", 4: "Square", 5: "Pentagon", 6: "Hexagon",
                 8: "Octagon", 10: "Decagon"}
        return names.get(self.sides, f"{self.sides}-gon")


class Ellipse(Shape):
    def __init__(self, a, b):
        if a <= 0 or b <= 0:
            raise ValueError("semi-axes must be positive")
        self.a, self.b = a, b

    def area(self):
        return math.pi * self.a * self.b

    def perimeter(self):
        """Ramanujan's approximation — there is no closed form."""
        a, b = self.a, self.b
        h = ((a - b) ** 2) / ((a + b) ** 2)
        return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

    def scaled(self, factor):
        return Ellipse(self.a * factor, self.b * factor)


# ===========================================================================
# CODE THAT KNOWS NOTHING ABOUT THE SUBCLASSES
# ===========================================================================

def report(shapes):
    """Written against Shape. Works on anything with area() and perimeter()."""
    print(f"{'SHAPE':<14}{'AREA':>12}{'PERIMETER':>12}"
          f"{'COMPACTNESS':>13}  {'':<22}")
    print("-" * WIDTH)
    peak = max(s.area() for s in shapes)
    for shape in sorted(shapes, reverse=True):
        bar = "#" * int(shape.area() / peak * 20)
        print(f"{shape.name:<14}{shape.area():>12.3f}{shape.perimeter():>12.3f}"
              f"{shape.compactness():>13.4f}  {bar:<22}")
    print("-" * WIDTH)
    print(f"{'TOTAL':<14}{sum(s.area() for s in shapes):>12.3f}"
          f"{sum(s.perimeter() for s in shapes):>12.3f}")


def largest(shapes):
    return max(shapes)                     # uses __lt__ from the base


def total_area(shapes):
    return sum(s.area() for s in shapes)


shapes = [
    Circle(3),
    Rectangle(4, 6),
    Square(5),
    Triangle(3, 4, 5),
    RegularPolygon(6, 3),
    Ellipse(4, 2),
]

print("=" * WIDTH)
print(f"{'SHAPES':^{WIDTH}}")
print("=" * WIDTH)
report(shapes)

print()
print(f"{'largest':<30}{largest(shapes)!r:>{WIDTH - 30}}")
print(f"{'total area':<30}{total_area(shapes):>{WIDTH - 30}.3f}")
print(f"{'most circle-like':<30}"
      f"{max(shapes, key=lambda s: s.compactness()).name:>{WIDTH - 30}}")
print(f"{'all doubled, total area':<30}"
      f"{total_area([s.scaled(2) for s in shapes]):>{WIDTH - 30}.3f}")
print(f"{'  ...which is 4x the original':<30}"
      f"{str(math.isclose(total_area([s.scaled(2) for s in shapes]), 4 * total_area(shapes))):>{WIDTH - 30}}")

# ===========================================================================
# THE ACTUAL TEST: add a shape without touching anything above
# ===========================================================================


class Annulus(Shape):
    """A ring. Written AFTER report() and largest() and total_area()."""

    def __init__(self, outer, inner):
        if inner >= outer:
            raise ValueError("the hole must be smaller than the shape")
        self.outer, self.inner = outer, inner

    def area(self):
        return math.pi * (self.outer ** 2 - self.inner ** 2)

    def perimeter(self):
        return 2 * math.pi * (self.outer + self.inner)

    def scaled(self, factor):
        return Annulus(self.outer * factor, self.inner * factor)


print()
print("-" * WIDTH)
print("A SEVENTH SHAPE, ADDED AFTER report() WAS WRITTEN")
print("-" * WIDTH)
report(shapes + [Annulus(5, 3)])
print("""
  Not one line of report(), largest(), total_area() or Shape changed. That
  is what the hierarchy bought: the CALLER depends on the interface, not on
  the list of implementations.""")

# ===========================================================================
# THE AREAS, CHECKED
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'AGAINST KNOWN FORMULAS':^{WIDTH}}")
print("=" * WIDTH)

checks = [
    ("Circle(1) area = pi", Circle(1).area(), math.pi),
    ("Circle(1) perimeter = 2pi", Circle(1).perimeter(), 2 * math.pi),
    ("Rectangle(3,4) area = 12", Rectangle(3, 4).area(), 12),
    ("Square(5) area = 25", Square(5).area(), 25),
    ("Triangle(3,4,5) area = 6", Triangle(3, 4, 5).area(), 6),
    ("Triangle(3,4,5) is right-angled", 3 ** 2 + 4 ** 2, 5 ** 2),
    ("RegularPolygon(4,5) == Square(5)",
     RegularPolygon(4, 5).area(), Square(5).area()),
    ("RegularPolygon(3,4) == Triangle(4,4,4)",
     RegularPolygon(3, 4).area(), Triangle(4, 4, 4).area()),
    ("Ellipse(3,3) == Circle(3)", Ellipse(3, 3).area(), Circle(3).area()),
    ("Annulus(2,1) = 3pi", Annulus(2, 1).area(), 3 * math.pi),
    ("a circle's compactness is 1", Circle(7).compactness(), 1.0),
    ("a square's compactness is pi/4", Square(3).compactness(), math.pi / 4),
]

all_ok = True
for label, got, want in checks:
    ok = math.isclose(got, want, rel_tol=1e-9)
    all_ok = all_ok and ok
    print(f"  {label:<44}{got:>14.6f}{str(ok):>10}")

print("-" * WIDTH)
print(f"  {'every formula correct':<44}{str(all_ok):>24}")
print("""
  Two of those checks are the interesting ones: RegularPolygon(4, 5) and
  Square(5) are separate classes computing the same number by different
  formulas, and they agree. So do RegularPolygon(3,4) and an equilateral
  Triangle, and Ellipse(3,3) and Circle(3).

  Independent implementations agreeing is the strongest evidence you can
  get without a proof — and it is exactly what makes a hierarchy testable.""")

# ===========================================================================
# WHAT THE HIERARCHY REFUSES
# ===========================================================================

print()
print("-" * WIDTH)
print("VALIDATION LIVES IN EACH SUBCLASS, WHERE THE RULES DIFFER")
print("-" * WIDTH)
for label, attempt in [
    ("Circle(-1)", lambda: Circle(-1)),
    ("Triangle(1, 2, 10)  — cannot close", lambda: Triangle(1, 2, 10)),
    ("RegularPolygon(2, 5) — not a polygon", lambda: RegularPolygon(2, 5)),
    ("Annulus(3, 5) — hole bigger than ring", lambda: Annulus(3, 5)),
    ("Shape().area() — no implementation", lambda: Shape().area()),
]:
    try:
        attempt()
        print(f"  {label:<44}ALLOWED — should it be?")
    except (ValueError, NotImplementedError) as exc:
        print(f"  {label:<44}{type(exc).__name__}")

print("""
  Shape().area() raises only WHEN CALLED. Shape() itself was created
  happily, and an incomplete subclass would be too. Day 49's abc.ABC moves
  that failure to instantiation — much earlier, and much easier to fix.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a Trapezoid. If you had to change any existing line, the
#     interface was wrong.
#
#   * Try making Square inherit from Rectangle, then write a function that
#     sets width and height independently. lesson.py section 5 shows what
#     happens. Then explain why THIS file has them as siblings.
#
#   * RegularPolygon(4, 5) and Square(5) compute the same area two ways.
#     Should Square just be RegularPolygon(4, side)? Argue both sides —
#     the answer involves how often you construct each and how the name
#     reads at the call site.
#
#   * Add a Composite shape holding a list of shapes, whose area is the
#     sum. It is a Shape AND it contains Shapes — the Composite pattern,
#     and the first place inheritance and composition genuinely combine.
#
#   * On Day 49 make Shape an abc.ABC with @abstractmethod and confirm
#     Shape() itself becomes impossible to instantiate.
