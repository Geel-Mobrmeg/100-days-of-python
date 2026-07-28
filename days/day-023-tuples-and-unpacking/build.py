"""Day 023 build — a geometry helper, points as tuples all the way through.

Every function takes and returns tuples, so results compose: the midpoint of
two points is a point, and can be fed straight back in.

The second half repeats the whole thing with namedtuple and asks you to
compare them. The answers are identical — the difference is entirely in
whether a reader can tell what `a[0]` means.

    python3 build.py
"""

import math
from collections import namedtuple

WIDTH = 68

# ===========================================================================
# PART 1 — plain tuples
# ===========================================================================


def distance(a, b):
    """Straight-line distance between two (x, y) points."""
    ax, ay = a                      # unpack at the top: the rest reads clearly
    bx, by = b
    return math.hypot(bx - ax, by - ay)


def midpoint(a, b):
    """The point halfway between two points. Returns a POINT, so it composes."""
    ax, ay = a
    bx, by = b
    return ((ax + bx) / 2, (ay + by) / 2)


def translate(point, dx, dy):
    """Move a point. Returns a new point — tuples are immutable."""
    x, y = point
    return (x + dx, y + dy)


def perimeter(points):
    """Total length around a closed polygon."""
    # zip(points, points[1:] + points[:1]) pairs each point with the next,
    # wrapping the last back to the first. Day 13's zip doing real work.
    pairs = zip(points, points[1:] + points[:1])
    return sum(distance(a, b) for a, b in pairs)


def polygon_area(points):
    """Area of any simple polygon, by the shoelace formula.

    Sum the cross products of consecutive vertex pairs and halve the
    absolute value. Works for any non-self-intersecting polygon, convex or
    not, which is why it beats splitting things into triangles.
    """
    total = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


def bounding_box(points):
    """Return (bottom_left, top_right) — a tuple OF tuples."""
    xs = [x for x, _ in points]          # `_` discards the y (Day 23)
    ys = [y for _, y in points]
    return ((min(xs), min(ys)), (max(xs), max(ys)))


def centroid(points):
    """The average position of the vertices."""
    n = len(points)
    return (sum(x for x, _ in points) / n, sum(y for _, y in points) / n)


# ---------------------------------------------------------------------------

A = (0, 0)
B = (4, 0)
C = (4, 3)

print("=" * WIDTH)
print(f"{'GEOMETRY WITH TUPLES':^{WIDTH}}")
print("=" * WIDTH)
print(f"A = {A}   B = {B}   C = {C}")
print()

print(f"{'distance(A, B)':<34}{distance(A, B):>32.4f}")
print(f"{'distance(B, C)':<34}{distance(B, C):>32.4f}")
print(f"{'distance(A, C)  [3-4-5]':<34}{distance(A, C):>32.4f}")
print(f"{'midpoint(A, C)':<34}{str(midpoint(A, C)):>32}")
print(f"{'translate(A, 10, 10)':<34}{str(translate(A, 10, 10)):>32}")

# Results compose, because a midpoint IS a point:
m = midpoint(A, C)
print(f"{'distance(A, midpoint(A, C))':<34}{distance(A, m):>32.4f}")
print(f"{'  ... which is half of AC':<34}{distance(A, C) / 2:>32.4f}")

triangle = [A, B, C]
print()
print(f"{'perimeter of ABC':<34}{perimeter(triangle):>32.4f}")
print(f"{'area of ABC (shoelace)':<34}{polygon_area(triangle):>32.4f}")
print(f"{'  ... vs base*height/2':<34}{4 * 3 / 2:>32.4f}")
print(f"{'centroid':<34}{str(tuple(round(v, 3) for v in centroid(triangle))):>32}")
print(f"{'bounding box':<34}{str(bounding_box(triangle)):>32}")

# ---------------------------------------------------------------------------
# Checks against known answers. Floats, so compare with math.isclose (Day 5).
# ---------------------------------------------------------------------------

square = [(0, 0), (4, 0), (4, 4), (0, 4)]
concave = [(0, 0), (4, 0), (4, 4), (2, 2), (0, 4)]      # an arrowhead

checks = [
    ("3-4-5 triangle hypotenuse", distance(A, C), 5.0),
    ("right triangle area", polygon_area(triangle), 6.0),
    ("4x4 square area", polygon_area(square), 16.0),
    ("4x4 square perimeter", perimeter(square), 16.0),
    ("concave polygon area", polygon_area(concave), 12.0),
    ("distance to self is zero", distance(A, A), 0.0),
    ("midpoint of a point is itself", midpoint(B, B)[0], 4.0),
]

print()
print("-" * WIDTH)
print(f"{'CHECK':<40}{'GOT':>12}{'WANT':>8}{'OK':>7}")
print("-" * WIDTH)
all_ok = True
for label, got, want in checks:
    ok = math.isclose(got, want)
    all_ok = all_ok and ok
    print(f"{label:<40}{got:>12.4f}{want:>8.2f}{str(ok):>7}")
print("-" * WIDTH)
print(f"{'all checks passed':<40}{str(all_ok):>27}")

print()
print("The concave case matters: a naive 'split into triangles' area would")
print("get it wrong. The shoelace formula handles any simple polygon.")

# ===========================================================================
# PART 2 — the same thing with namedtuple
# ===========================================================================

Point = namedtuple("Point", ["x", "y"])


def distance_named(a, b):
    """Same maths. Read it and compare with distance() above."""
    return math.hypot(b.x - a.x, b.y - a.y)


def midpoint_named(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)


pA, pB, pC = Point(0, 0), Point(4, 0), Point(4, 3)

print()
print("=" * WIDTH)
print(f"{'THE SAME GEOMETRY WITH namedtuple':^{WIDTH}}")
print("=" * WIDTH)
print(f"A = {pA}")
print(f"C = {pC}")
print()
print(f"{'distance_named(A, C)':<34}{distance_named(pA, pC):>32.4f}")
print(f"{'midpoint_named(A, C)':<34}{str(midpoint_named(pA, pC)):>32}")
print(f"{'identical to the tuple version?':<34}"
      f"{str(math.isclose(distance_named(pA, pC), distance(A, C))):>32}")

print()
print("A namedtuple IS a tuple, so everything still works:")
print(f"{'  indexable':<34}{pC[0]:>32}")
print(f"{'  unpackable':<34}{str(tuple(v for v in pC)):>32}")
print(f"{'  usable as a dict key':<34}{str({pC: 'corner'}[pC]):>32}")
print(f"{'  works in the tuple functions':<34}{distance(pA, pC):>32.4f}")

print()
print("=" * WIDTH)
print("""COMPARE THE TWO SIGNATURES

    ax, ay = a                    return math.hypot(b.x - a.x,
    bx, by = b                                      b.y - a.y)
    return math.hypot(bx - ax, by - ay)

Same answer, same speed, same type. The difference is that the second one
cannot be got the wrong way round by a reader, and a typo in `.x` raises
AttributeError immediately where `[0]` would silently use the wrong number.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a point to a set and use it as a dict key. Then try the same with
#     [x, y] lists and read the TypeError. That is why grids and caches are
#     keyed by tuples.
#
#   * polygon_area returns abs(...). Remove the abs() and run the square
#     with its vertices reversed. The sign tells you the WINDING DIRECTION,
#     which is genuinely useful — decide whether to expose it.
#
#   * Add `def scale(point, factor)` and `def rotate(point, degrees)`. Both
#     take a point and return a point, so they compose:
#         rotate(scale(translate(p, 1, 1), 2), 90)
#     That composability is what "return the same type you take" buys you.
#
#   * Write bounding_box to return a namedtuple Box(left, bottom, right, top)
#     and see how much clearer the call site gets.
#
#   * On Day 48, rewrite Point as a frozen @dataclass and add __add__ so
#     that a + b works (Day 44). The arc tuple -> namedtuple -> dataclass ->
#     class is the same object growing up.
