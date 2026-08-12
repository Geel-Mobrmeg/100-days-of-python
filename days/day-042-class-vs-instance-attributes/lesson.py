"""Day 042 — Class vs. instance attributes.

    python3 lesson.py
"""

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. Two places an attribute can live
# ---------------------------------------------------------------------------


class Employee:
    company = "Analytical Engines Ltd"       # CLASS attribute — one, shared
    headcount = 0

    def __init__(self, name):
        self.name = name                     # INSTANCE attribute — one each
        Employee.headcount += 1


ada = Employee("Ada")
alan = Employee("Alan")

print(f"{ada.company}   {alan.company}")
print(f"headcount: {Employee.headcount}")
print(f"\nada.__dict__ = {ada.__dict__}")
print("  ^ `company` is NOT there. Lookup goes INSTANCE FIRST, THEN CLASS.")


# ---------------------------------------------------------------------------
# 2. Assigning through an instance SHADOWS; it does not modify
# ---------------------------------------------------------------------------

ada.company = "Somewhere Else"

print(f"\nada.company   {ada.company}")
print(f"alan.company  {alan.company}      <- unchanged")
print(f"Employee.company {Employee.company}   <- unchanged")
print(f"ada.__dict__ now {ada.__dict__}")
print("  ^ a NEW instance attribute now HIDES the class one")

Employee.company = "New Name Ltd"
print("\nafter Employee.company = 'New Name Ltd':")
print(f"  alan.company  {alan.company}         <- follows the class")
print(f"  ada.company   {ada.company}   <- still shadowed")

del ada.company
print(f"  after `del ada.company`: {ada.company}   <- the shadow is gone")


# ---------------------------------------------------------------------------
# 3. THE MUTABLE CLASS ATTRIBUTE TRAP
# ---------------------------------------------------------------------------


class Team:
    members = []                             # ONE list, for every Team ever


a, b = Team(), Team()
a.members.append("Ada")
b.members.append("Alan")

print(f"\na.members  {a.members}")
print(f"b.members  {b.members}")
print(f"one list:  {a.members is b.members}")

print("""
  a.members.append(...) does not ASSIGN — it MUTATES the one shared list,
  so the shadowing rule never gets a chance to protect you.

  This is Day 32's mutable-default bug with a longer fuse: it survives
  across every instance in the whole program, including between tests.

  RULE: CLASS ATTRIBUTES SHOULD BE IMMUTABLE. Constants, configuration,
  and counters that only ClassName.count += 1 touches. Anything mutable
  and per-instance belongs in __init__.""")


class FixedTeam:
    def __init__(self):
        self.members = []                    # a new list per instance


c, d = FixedTeam(), FixedTeam()
c.members.append("Ada")
print(f"  fixed: c={c.members} d={d.members} shared={c.members is d.members}")


# ---------------------------------------------------------------------------
# 4. THE COUNTER BUG — self.counter += 1
# ---------------------------------------------------------------------------


class BrokenIds:
    _next_id = 1

    def __init__(self):
        self.id = self._next_id
        self._next_id += 1                   # THE BUG


class WorkingIds:
    _next_id = 1

    def __init__(self):
        self.id = WorkingIds._next_id
        WorkingIds._next_id += 1             # assign THROUGH THE CLASS


print(f"\nbroken:  {[BrokenIds().id for _ in range(5)]}")
print(f"working: {[WorkingIds().id for _ in range(5)]}")

print("""
  `self._next_id += 1` expands to `self._next_id = self._next_id + 1`.
  The READ finds the class attribute (1). The WRITE creates an INSTANCE
  attribute. The class counter never moves, so every object gets ID 1.

  Section 2's shadowing rule, doing real damage. `+=` on a class attribute
  through `self` is always this bug.""")


# ---------------------------------------------------------------------------
# 5. @classmethod — the first argument is the CLASS
# ---------------------------------------------------------------------------


class Record:
    _count = 0

    def __init__(self, name, value):
        self.name = name
        self.value = value
        type(self)._count += 1

    @classmethod
    def from_csv(cls, row):
        """An ALTERNATIVE CONSTRUCTOR. Note cls(...), not Record(...)."""
        name, value = row.split(",")
        return cls(name.strip(), int(value))

    @classmethod
    def count(cls):
        return cls._count

    @staticmethod
    def is_valid_row(row):
        """No self, no cls — it needs nothing from the class."""
        return row.count(",") == 1

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.value})"


class Detailed(Record):
    """A subclass, to show why cls(...) matters."""


print(f"\n{Record('direct', 1)}")
print(f"{Record.from_csv('from a row, 42')}")
print(f"{Detailed.from_csv('subclass row, 7')}   <- a Detailed, not a Record")
print("  because from_csv used cls(...), not Record(...)")
print(f"is_valid_row('a,1'):    {Record.is_valid_row('a,1')}")
print(f"records created:        {Record.count()}")


class HardCoded:
    def __init__(self, name):
        self.name = name

    @classmethod
    def make(cls, name):
        return HardCoded(name)               # THE BUG: hard-coded name


class Sub(HardCoded):
    pass


print(f"\nSub.make('x') is a {type(Sub.make('x')).__name__}   "
      f"<- should have been Sub")


# ---------------------------------------------------------------------------
# 6. Which one?
# ---------------------------------------------------------------------------

print("""
  DECORATOR        FIRST ARG   SEES            USE FOR
  (none)           self        this instance   almost everything
  @classmethod     cls         the class       alternative constructors,
                                               class-level state
  @staticmethod    -           nothing         a related helper

  ASK WHAT THE METHOD NEEDS:
    the instance ................ regular method
    the class (to build one, or
    to touch shared state) ...... classmethod
    neither ..................... staticmethod — or, honestly, a plain
                                  module-level function. A staticmethod is
                                  mostly about namespacing.""")


# ---------------------------------------------------------------------------
# 7. Inheritance and shared counters
# ---------------------------------------------------------------------------


class Base:
    _count = 0

    def __init__(self):
        type(self)._count += 1               # per-SUBCLASS counter


class Left(Base):
    pass


class Right(Base):
    pass


Left(); Left(); Right()                      # noqa: E702 - compact demo
print("\nwith type(self)._count += 1:")
print(f"  Base._count  {Base._count}    Left._count  {Left._count}    "
      f"Right._count {Right._count}")
print("""
  Left and Right each got their OWN counter the moment they first assigned,
  because `type(self)._count += 1` reads Base's value and writes to the
  subclass. Sometimes exactly what you want; usually a surprise.

  For ONE counter shared by the whole hierarchy, name the base explicitly:
  `Base._count += 1`. Decide which you mean and write it down.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Give a class `items = []` and append through two instances.
#   * Write an ID counter with self._next_id += 1 and watch every ID be 1.
#   * Hard-code the class name in a classmethod, then subclass it.
#   * Assign to a class attribute through an instance, then check
#     instance.__dict__ and the class attribute.
#   * Create 100 instances in one test and 100 in another. The class counter
#     does not reset — which is why Day 58 needs fixtures.
