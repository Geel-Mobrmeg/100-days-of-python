"""Day 042 build — Employee: sequential IDs and alternative constructors.

    python3 build.py

Two jobs that both need class-level state:

  SEQUENTIAL IDS        a counter shared by every employee ever created,
                        no matter WHICH constructor made them

  ALTERNATIVE           __init__ takes named arguments; real data arrives as
  CONSTRUCTORS          CSV rows, dicts and JSON. @classmethod gives each
                        its own front door without duplicating validation.

The last section proves the ID counter is genuinely shared by running every
constructor and checking no ID repeats.
"""

import json
from datetime import date

WIDTH = 78


class Employee:
    """One employee. IDs are issued sequentially across ALL constructors."""

    # ---- CLASS attributes: one each, shared by every instance -----------
    company = "Analytical Engines Ltd"
    _next_id = 1000                      # the shared counter
    _registry = {}                       # id -> employee, for lookups

    VALID_ROLES = ("engineer", "analyst", "manager", "director")
    PAY_BANDS = {
        "engineer": (45_000, 85_000),
        "analyst": (38_000, 68_000),
        "manager": (60_000, 110_000),
        "director": (95_000, 200_000),
    }
    # Those three are safe as class attributes because they are IMMUTABLE
    # (a tuple, and a dict nobody mutates). _registry is mutable and IS
    # mutated — deliberately, because it is genuinely shared state, not
    # per-instance data that leaked upward.

    def __init__(self, name, role, salary, started=None):
        role = role.strip().lower()
        if role not in self.VALID_ROLES:
            raise ValueError(
                f"{role!r} is not one of {', '.join(self.VALID_ROLES)}"
            )
        low, high = self.PAY_BANDS[role]
        if not low <= salary <= high:
            raise ValueError(
                f"{salary:,} is outside the {role} band ({low:,}-{high:,})"
            )

        # THE COUNTER. Assign THROUGH THE CLASS, never through self —
        # `self._next_id += 1` would create an instance attribute and leave
        # the class counter at 1000 forever. See lesson.py section 4.
        self.id = Employee._next_id
        Employee._next_id += 1

        self.name = name.strip()
        self.role = role
        self.salary = salary
        self.started = started or date.today()

        Employee._registry[self.id] = self

    # -- ALTERNATIVE CONSTRUCTORS -----------------------------------------
    #
    # Every one of these ends in `cls(...)`, so all the validation in
    # __init__ runs exactly once and a subclass gets its own type back.

    @classmethod
    def from_csv(cls, row, delimiter=","):
        """Build from 'name,role,salary[,started]'."""
        parts = [p.strip() for p in row.split(delimiter)]
        if len(parts) < 3:
            raise ValueError(f"need at least 3 fields, got {len(parts)}: {row!r}")
        started = date.fromisoformat(parts[3]) if len(parts) > 3 else None
        return cls(parts[0], parts[1], int(parts[2]), started)

    @classmethod
    def from_dict(cls, data):
        """Build from a mapping, as a database row or API payload arrives."""
        started = data.get("started")
        return cls(
            data["name"], data["role"], int(data["salary"]),
            date.fromisoformat(started) if started else None,
        )

    @classmethod
    def from_json(cls, text):
        """Build one, or a list, from JSON (Day 55)."""
        payload = json.loads(text)
        if isinstance(payload, list):
            return [cls.from_dict(item) for item in payload]
        return cls.from_dict(payload)

    @classmethod
    def graduate(cls, name):
        """A trainee: the role and salary are policy, not caller input."""
        return cls(name, "analyst", cls.PAY_BANDS["analyst"][0])

    # -- CLASS-LEVEL QUERIES ----------------------------------------------

    @classmethod
    def count(cls):
        return len(cls._registry)

    @classmethod
    def find(cls, employee_id):
        return cls._registry.get(employee_id)

    @classmethod
    def payroll(cls):
        return sum(e.salary for e in cls._registry.values())

    @classmethod
    def by_role(cls):
        out = {}
        for employee in cls._registry.values():
            out.setdefault(employee.role, []).append(employee)
        return out

    @classmethod
    def reset(cls):
        """Clear all shared state. Tests need this (Day 58)."""
        cls._next_id = 1000
        cls._registry = {}

    # -- STATICMETHOD: needs nothing from the class ------------------------

    @staticmethod
    def is_valid_row(row, delimiter=","):
        """True if a CSV row has enough fields and a numeric salary."""
        parts = [p.strip() for p in row.split(delimiter)]
        return len(parts) >= 3 and parts[2].isdigit()

    # -- instance methods --------------------------------------------------

    def years_served(self, today=None):
        today = today or date.today()
        return (today - self.started).days / 365.25

    def band_position(self):
        """Where in the pay band this salary sits, 0.0 to 1.0."""
        low, high = self.PAY_BANDS[self.role]
        return (self.salary - low) / (high - low)

    def __repr__(self):
        return (f"{type(self).__name__}(id={self.id}, name={self.name!r}, "
                f"role={self.role!r}, salary={self.salary:,})")


class Contractor(Employee):
    """A subclass, to show that cls(...) returns the right type."""

    company = "Contracted In"


# ===========================================================================
# 1. Every constructor, one shared counter
# ===========================================================================

print("=" * WIDTH)
print(f"{'EMPLOYEE':^{WIDTH}}")
print("=" * WIDTH)

people = [
    Employee("Ada Lovelace", "director", 165_000, date(2019, 3, 1)),
    Employee.from_csv("Alan Turing, engineer, 78000, 2020-06-15"),
    Employee.from_csv("Grace Hopper|manager|98000", delimiter="|"),
    Employee.from_dict({"name": "Katherine Johnson", "role": "analyst",
                        "salary": 61000, "started": "2021-01-11"}),
    Employee.graduate("Barbara Liskov"),
    Contractor.from_csv("Bjarne Stroustrup, engineer, 82000"),
]
people += Employee.from_json(json.dumps([
    {"name": "Margaret Hamilton", "role": "manager", "salary": 104000},
    {"name": "Radia Perlman", "role": "engineer", "salary": 71000},
]))

print(f"{'ID':<7}{'NAME':<22}{'ROLE':<12}{'SALARY':>11}{'BAND':>8}  {'TYPE':<12}")
print("-" * WIDTH)
for person in people:
    print(f"{person.id:<7}{person.name:<22}{person.role:<12}"
          f"{person.salary:>11,}{person.band_position():>8.0%}  "
          f"{type(person).__name__:<12}")

ids = [p.id for p in people]
print("-" * WIDTH)
print(f"{'employees created':<38}{len(people):>{WIDTH - 38}}")
print(f"{'constructors used':<38}{5:>{WIDTH - 38}}")
print(f"{'IDs issued':<38}{f'{min(ids)}-{max(ids)}':>{WIDTH - 38}}")
print(f"{'every ID unique':<38}"
      f"{str(len(set(ids)) == len(ids)):>{WIDTH - 38}}")
print(f"{'IDs strictly sequential':<38}"
      f"{str(ids == list(range(min(ids), min(ids) + len(ids)))):>{WIDTH - 38}}")
print(f"{'total payroll':<38}{f'{Employee.payroll():,}':>{WIDTH - 38}}")
print("""
  Five different constructors, one counter, no collisions — because every
  one of them ends in `cls(...)`, so they all funnel through __init__.
  Duplicating the ID logic in each would have been five places to get it
  wrong, and the bug would only appear when two constructors were used in
  the same run.""")

# ===========================================================================
# 2. cls(...) gives subclasses the right type
# ===========================================================================

contractor = [p for p in people if isinstance(p, Contractor)][0]
print("-" * WIDTH)
print(f"{'Contractor.from_csv returned a':<38}"
      f"{type(contractor).__name__:>{WIDTH - 38}}")
print(f"{'its company (overridden)':<38}"
      f"{contractor.company:>{WIDTH - 38}}")
print(f"{'but it shares the ID counter':<38}"
      f"{contractor.id:>{WIDTH - 38}}")
print(f"{'and appears in the registry':<38}"
      f"{str(Employee.find(contractor.id) is contractor):>{WIDTH - 38}}")
print("""
  from_csv says `cls(...)`, so calling it on Contractor built a Contractor.
  Hard-coding `Employee(...)` would have returned an Employee and the bug
  would be invisible until somebody checked the type.""")

# ===========================================================================
# 3. Class-level queries
# ===========================================================================

print()
print("-" * WIDTH)
print("BY ROLE")
print("-" * WIDTH)
for role, group in sorted(Employee.by_role().items()):
    total = sum(e.salary for e in group)
    names = ", ".join(e.name.split()[0] for e in group)
    print(f"  {role:<12}{len(group):>3}{total:>12,}   {names[:36]}")

# ===========================================================================
# 4. What it refuses
# ===========================================================================

print()
print("-" * WIDTH)
print("VALIDATION HAPPENS ONCE, IN __init__, SO EVERY CONSTRUCTOR GETS IT")
print("-" * WIDTH)

count_before = Employee.count()
id_before = Employee._next_id

bad = [
    ("an unknown role", lambda: Employee("X", "wizard", 50_000)),
    ("salary below the band", lambda: Employee("X", "engineer", 10_000)),
    ("salary above the band", lambda: Employee("X", "analyst", 500_000)),
    ("a CSV row with too few fields", lambda: Employee.from_csv("X,engineer")),
    ("a bad role via from_dict",
     lambda: Employee.from_dict({"name": "X", "role": "wizard", "salary": 1})),
    ("a bad salary via from_json",
     lambda: Employee.from_json('{"name":"X","role":"analyst","salary":1}')),
]

for label, attempt in bad:
    try:
        attempt()
        print(f"  {label:<44}ALLOWED — should it be?")
    except (ValueError, KeyError) as exc:
        print(f"  {label:<44}{type(exc).__name__}")

print()
print(f"  {'employees created by those six':<44}"
      f"{Employee.count() - count_before:>10}")
print(f"  {'IDs consumed by those six':<44}"
      f"{Employee._next_id - id_before:>10}")
print("""
  Zero, and zero. The validation runs BEFORE the counter is touched, so a
  rejected employee does not burn an ID or leave a half-built object in the
  registry. Check first, mutate second — Day 41's rule, at class level.""")

# ===========================================================================
# 5. The bug this design avoids
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE COUNTER BUG':^{WIDTH}}")
print("=" * WIDTH)


class BrokenEmployee:
    _next_id = 1

    def __init__(self, name):
        self.id = self._next_id
        self._next_id += 1                   # THE BUG


broken = [BrokenEmployee(f"person {n}") for n in range(5)]
print(f"  with `self._next_id += 1`:  ids = {[e.id for e in broken]}")
print(f"  the class counter is still: {BrokenEmployee._next_id}")
print(f"  and each instance grew its own: "
      f"{[e.__dict__.get('_next_id') for e in broken]}")
print("""
  `self._next_id += 1` READS the class attribute and WRITES an instance
  attribute. The class counter never moves; every employee gets ID 1; and
  each object quietly carries a private copy.

  Employee above says `Employee._next_id += 1`. One word's difference, and
  the difference between unique IDs and a database with five primary-key
  collisions.""")

Employee.reset()
print(f"\n  after Employee.reset(): {Employee.count()} in the registry, "
      f"next id {Employee._next_id}")
print("""  reset() exists because CLASS STATE SURVIVES BETWEEN TESTS. Two test
  files creating employees will see each other's counter unless something
  clears it — which is exactly what Day 58's fixtures are for.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change `Employee._next_id += 1` to `type(self)._next_id += 1` and
#     create employees and contractors alternately. Each class now gets its
#     OWN counter from its first assignment, so IDs repeat across types.
#     Decide which behaviour you want and write down why.
#
#   * PAY_BANDS is a mutable dict as a class attribute. Nothing mutates it,
#     so it is safe — but prove that to yourself, then have one method do
#     `self.PAY_BANDS[role] = ...` and watch it change for every employee
#     in the process.
#
#   * The counter is not thread-safe (Day 92): two threads can read 1000
#     before either writes 1001. Reproduce it with ThreadPoolExecutor, then
#     fix it with threading.Lock.
#
#   * _registry holds a strong reference to every employee ever made, so
#     none is ever garbage collected. That is a memory leak in a long-lived
#     process. Look up weakref.WeakValueDictionary.
#
#   * On Day 48, see how much of __init__ @dataclass removes — and notice
#     it cannot express the ID counter, which is why this class stays a
#     class.
