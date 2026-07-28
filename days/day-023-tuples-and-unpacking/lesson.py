"""Day 023 — Tuples and unpacking.

    python3 lesson.py
"""

from collections import namedtuple

# ---------------------------------------------------------------------------
# 1. THE COMMA MAKES THE TUPLE, NOT THE BRACKETS
# ---------------------------------------------------------------------------

point = (3, 4)
empty = ()
one = (3,)                 # the trailing comma is what makes it a tuple
not_a_tuple = (3)          # just the number 3, in brackets

print(f"(3, 4) -> {type(point).__name__}, len {len(point)}")
print(f"(3,)   -> {type(one).__name__}, len {len(one)}")
print(f"(3)    -> {type(not_a_tuple).__name__}")

# Which is why a stray comma creates a tuple you did not want:
oops = 3,
print(f"x = 3, gives {oops!r}  <- a real bug, and it surfaces much later")

# The brackets are usually OPTIONAL, which is why tuples turn up where you
# did not put any:
also_a_tuple = 3, 4
print(f"3, 4 with no brackets: {also_a_tuple}")

# Everything from Day 3 works. The difference is that tuples are IMMUTABLE:
print(point[0], point[-1], point[:1], len(point), 3 in point)
# point[0] = 9        # TypeError: 'tuple' object does not support item assignment
# point.append(5)     # AttributeError: no append


# ---------------------------------------------------------------------------
# 2. List or tuple? A question about MEANING, not about capability
# ---------------------------------------------------------------------------
#
#   LIST    "several of these"        names = ["ada", "alan", "grace"]
#           same kind of thing, count varies, order is data
#
#   TUPLE   "one of these, in parts"  person = ("Ada", 36, "engineer")
#           different parts, fixed count, POSITION IS MEANING
#
# A point is (x, y): always two, and swapping them changes what it means.
# A phone book is a list: any number, order incidental.

# THREE PRACTICAL CONSEQUENCES OF IMMUTABILITY:

# (a) tuples can be dict keys and set members; lists cannot
board = {(0, 0): "rook", (0, 1): "knight"}
print(f"\ntuple as a dict key: {board[(0, 0)]}")
try:
    {[0, 0]: "rook"}
except TypeError as e:
    print(f"list as a dict key:  TypeError: {e}")

# (b) tuples are safe to share — there is no aliasing bug (Day 21), because
#     there is no change to observe.

# (c) they are slightly smaller and faster. Irrelevant until it is not.

# THE TRAP: immutable does not mean the CONTENTS are.
mixed = ([1, 2], 3)
mixed[0].append(99)
print(f"\ntuple holding a list, after appending to it: {mixed}")
print("The tuple fixes WHICH OBJECTS it holds, not that they are frozen.")


# ---------------------------------------------------------------------------
# 3. Unpacking
# ---------------------------------------------------------------------------

x, y = point
print(f"\nx={x} y={y}")

# The counts must MATCH EXACTLY. That strictness fails at the mistake:
try:
    a, b = (1, 2, 3)
except ValueError as e:
    print(f"a, b = (1,2,3) -> ValueError: {e}")

# Unpacking works on ANY iterable, not just tuples:
a, b, c = [1, 2, 3]
first, second = "hi"
year, month, day = "2024-01-15".split("-")
print(f"from a string: {first}{second}   from a split: {year}/{month}/{day}")

# THE SWAP. The right side is evaluated COMPLETELY FIRST into a tuple, then
# unpacked — which is why no temporary is needed and why rotating works too.
a, b = 1, 2
a, b = b, a
print(f"\nswapped: a={a} b={b}")

a, b, c = 1, 2, 3
a, b, c = c, a, b
print(f"rotated: a={a} b={b} c={c}")

# It is also why unpacking in a `for` line reads so well:
people = [("Ada", 36), ("Alan", 41), ("Grace", 85)]
for name, age in people:
    print(f"  {name:<8}{age:>4}")

for i, (name, age) in enumerate(people, start=1):     # nested unpacking
    print(f"  {i}. {name} is {age}")


# ---------------------------------------------------------------------------
# 4. Star unpacking — exactly one starred name, and it is ALWAYS a list
# ---------------------------------------------------------------------------

first, *rest = [1, 2, 3, 4]
*most, last = [1, 2, 3, 4]
head, *middle, tail = [1, 2, 3, 4]

print(f"\nfirst={first} rest={rest}")
print(f"most={most} last={last}")
print(f"head={head} middle={middle} tail={tail}")

# ALWAYS a list, even when unpacking a tuple, and even when it collects
# nothing:
a, *nothing = (1,)
print(f"collected nothing: {nothing!r}  (a list, not a tuple)")

# The clean way to take a verb off its arguments, or a header off a file:
verb, *args = "take brass lamp".split()
print(f"verb={verb!r} args={args}")

lines = ["name,age", "ada,36", "alan,41"]
header, *rows = lines
print(f"header={header!r} rows={rows}")

# `_` is the conventional name for something deliberately discarded:
name, _, role = "Ada,36,engineer".split(",")
print(f"name={name} role={role}   (age discarded on purpose)")


# ---------------------------------------------------------------------------
# 5. Returning several values IS returning one tuple
# ---------------------------------------------------------------------------


def min_max(values):
    """Return the smallest and largest. This is ONE tuple."""
    return min(values), max(values)


lowest, highest = min_max([3, 1, 4, 1, 5])
print(f"\nmin_max -> {min_max([3, 1, 4, 1, 5])}, unpacked to {lowest}, {highest}")

# Python has no special multiple-return feature. It packs a tuple and the
# caller unpacks it. divmod is the built-in example:
q, r = divmod(17, 5)
print(f"divmod(17, 5) = {divmod(17, 5)} -> q={q} r={r}")


# ---------------------------------------------------------------------------
# 6. namedtuple — positions with names
# ---------------------------------------------------------------------------

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)

print(f"\n{p}")                         # Point(x=3, y=4), not (3, 4)
print(f"p.x={p.x}  p[0]={p[0]}")        # names AND indices
px, py = p                              # still unpacks
print(f"unpacked: {px}, {py}")
print(f"still a tuple: {isinstance(p, tuple)}")
print(f"still immutable: ", end="")
try:
    p.x = 9
except AttributeError as e:
    print(f"AttributeError: {e}")

# _replace makes a NEW one with a field changed:
print(f"p._replace(x=10) -> {p._replace(x=10)}, p is still {p}")
print(f"as a dict: {p._asdict()}")

# You get names for free and lose nothing. Compare:
#     distance(a[0], a[1], b[0], b[1])       <- what are these?
#     distance(a.x, a.y, b.x, b.y)           <- obvious
#
# typing.NamedTuple is the modern spelling, with type hints (Day 59):
#
#     class Point(NamedTuple):
#         x: float
#         y: float
#
# And when the record needs BEHAVIOUR as well as fields, that is Day 48's
# @dataclass. The arc tuple -> namedtuple -> dataclass -> class is one of
# the real progressions of this course.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write x = 3, somewhere and then try to do arithmetic with x.
#   * Unpack three values into two names, and read the ValueError.
#   * Put a list inside a tuple, mutate it, and explain to yourself why the
#     tuple did not stop you.
#   * Use a tuple as a dict key, then a list, and compare the errors.
