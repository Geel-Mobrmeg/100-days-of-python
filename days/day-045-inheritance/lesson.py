"""Day 045 — Inheritance.

    python3 lesson.py
"""

import math

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. Overriding, and why the base class calls self.area()
# ---------------------------------------------------------------------------


class Shape:
    def area(self):
        raise NotImplementedError(f"{type(self).__name__} must implement area()")

    def describe(self):
        # type(self) is the ACTUAL instance's class, never "Shape".
        # self.area() finds the SUBCLASS's version — that indirection is
        # the entire point of inheritance, and it is called POLYMORPHISM.
        return f"{type(self).__name__:<10} area {self.area():>8.2f}"


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


for shape in (Circle(1), Square(2)):
    print(f"  {shape.describe()}")

# describe() was written ONCE and works for every shape, present and future.
# The caller says shape.area() and does not care which class answers.


class Triangle(Shape):
    """Forgot to implement area()."""

    def __init__(self, base, height):
        self.base, self.height = base, height


bad = Triangle(3, 4)                        # instantiates HAPPILY
print("\nTriangle(3, 4) was created with no area() at all")
try:
    bad.describe()
except NotImplementedError as e:
    print(f"  and failed only when USED: NotImplementedError: {e}")
print("  Day 49's abc.ABC fails at INSTANTIATION instead — much earlier.")


# ---------------------------------------------------------------------------
# 2. super()
# ---------------------------------------------------------------------------


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width, self.height = width, height

    def area(self):
        return self.width * self.height


class NamedRectangle(Rectangle):
    def __init__(self, width, height, name):
        super().__init__(width, height)     # run the parent's __init__
        self.name = name

    def describe(self):
        # Extend rather than replace: get the parent's answer, add to it.
        return f"{super().describe()}  ({self.name})"


class Forgetful(Rectangle):
    def __init__(self, width, height, name):
        self.name = name                    # NO super().__init__()


print(f"\n{NamedRectangle(3, 4, 'the big one').describe()}")

try:
    Forgetful(3, 4, "oops").area()
except AttributeError as e:
    print(f"without super().__init__(): AttributeError: {e}")
print("  The parent's attributes never existed. The error surfaces in")
print("  area(), which is nowhere near the __init__ that caused it.")


# ---------------------------------------------------------------------------
# 3. isinstance vs type() vs duck typing
# ---------------------------------------------------------------------------

circle = Circle(1)
print(f"\nisinstance(circle, Circle)  {isinstance(circle, Circle)}")
print(f"isinstance(circle, Shape)   {isinstance(circle, Shape)}   <- subclasses count")
print(f"type(circle) is Shape       {type(circle) is Shape}  <- exact type only")


class Blob:
    """Not a Shape. Has an area(). That is enough."""

    def area(self):
        return 42.0


things = [Circle(1), Square(2), Blob()]
print(f"\nduck typing: {[round(t.area(), 2) for t in things]}")
print("  Blob does not inherit from Shape and works anyway, because the")
print("  only thing the caller needed was .area(). That is DUCK TYPING,")
print("  and it is why Python programmers subclass less than Java ones.")

print(f"\nbut Blob has no describe(): {hasattr(Blob(), 'describe')}")
print("  Inheritance gave the others describe() for free. That is the")
print("  trade: duck typing is looser, inheritance shares implementation.")


# ---------------------------------------------------------------------------
# 4. The MRO
# ---------------------------------------------------------------------------


class A:
    def who(self):
        return "A"


class B(A):
    def who(self):
        return "B -> " + super().who()


class C(A):
    def who(self):
        return "C -> " + super().who()


class D(B, C):
    def who(self):
        return "D -> " + super().who()


print(f"\nD().who()  {D().who()}")
print(f"D.__mro__  {' -> '.join(k.__name__ for k in D.__mro__)}")

print("""
  Note B's super() reached C — a class B has never heard of. super() walks
  THE MRO, not "up to my parent". With single inheritance those are the
  same thing; with multiple inheritance they are not, and that is what
  makes cooperative multiple inheritance both work and confuse people.

  C3 linearisation guarantees: a class comes before its parents, and the
  order you listed the bases is preserved. D.mro() prints it, and reading
  it is how you debug "why did THAT method run".""")

print(f"\neverything inherits from object: {int.__mro__}")


# ---------------------------------------------------------------------------
# 5. THE LISKOV VIOLATION — the textbook one, in code
# ---------------------------------------------------------------------------


class BadSquare(Rectangle):
    """A square IS a rectangle. In geometry. Not in code."""

    def __init__(self, side):
        super().__init__(side, side)

    @property
    def side(self):
        return self.width


def stretch(rectangle):
    """Perfectly reasonable code that works on any Rectangle."""
    rectangle.width = 10
    rectangle.height = 4
    return rectangle.area()


print(f"\nstretch(Rectangle(1, 1))   -> {stretch(Rectangle(1, 1))}   (10 x 4)")
print(f"stretch(BadSquare(1))      -> {stretch(BadSquare(1))}   "
      f"<- still 'a square' with sides 10 and 4?")

print("""
  stretch() is not wrong. Rectangle's contract says width and height are
  independent, and BadSquare cannot honour that — it is now a square with
  unequal sides, or it silently changed both and returned 100. Either way,
  code that worked on the parent breaks on the child.

  THE TEST BEFORE YOU SUBCLASS:
      Is every instance of the child usable EVERYWHERE the parent is
      expected, with no surprises?

  If not, it is not an is-a. Square and Rectangle should both implement a
  Shape interface, and neither should inherit from the other — which is
  tomorrow.""")


# ---------------------------------------------------------------------------
# 6. Inheriting for reuse — the other common mistake
# ---------------------------------------------------------------------------


class Stack(list):
    """Inheriting from list to reuse its code. Looks efficient."""

    def push(self, item):
        self.append(item)


stack = Stack()
stack.push(1)
stack.push(2)
print(f"\nStack: {stack}, pop -> {stack.pop()}")
print(f"...but it also has: {[m for m in ('sort', 'insert', 'reverse', 'remove') if hasattr(stack, m)]}")
stack.insert(0, "not how a stack works")
print(f"and this was allowed: {stack}")

print("""
  You wanted a list INSIDE, not to BE one. Inheriting exposed the entire
  list API, including operations that break the abstraction — and every one
  of them is now part of Stack's public interface forever.

  COMPOSITION fixes this in one line:  self._items = []
  which is tomorrow.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write a subclass __init__ without super() and hunt the AttributeError.
#   * Make a diamond and predict the MRO before printing it.
#   * Write a function that works on Rectangle and breaks on BadSquare.
#   * Subclass dict to "add a feature" and count how many methods you have
#     now promised to support correctly.
