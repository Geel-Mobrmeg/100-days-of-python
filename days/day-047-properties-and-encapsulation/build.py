"""Day 047 build — Temperature: one stored value, three scales, one rule.

    python3 build.py

The rule: nothing below absolute zero, ever, by any route.

There are six ways to set a temperature here (three scales, plus the
constructor, plus arithmetic). All six funnel through ONE setter, so the
rule is written once. The last section tries every route.
"""

WIDTH = 76

ABSOLUTE_ZERO_C = -273.15


class BelowAbsoluteZero(ValueError):
    """Raised when a value would place the temperature below absolute zero."""

    def __init__(self, celsius):
        self.celsius = celsius
        super().__init__(
            f"{celsius:.2f}C is below absolute zero ({ABSOLUTE_ZERO_C}C)"
        )


class Temperature:
    """A temperature. Stored once, in Celsius; readable in three scales.

    ONE SOURCE OF TRUTH: only _celsius exists. fahrenheit and kelvin are
    computed, so they cannot drift out of step with it or with each other.

    ONE RULE, ONE PLACE: every route to changing the value assigns through
    `self.celsius`, so the absolute-zero check is written exactly once.
    """

    __slots__ = ("_celsius",)

    def __init__(self, celsius=0.0):
        # THROUGH THE PROPERTY, not self._celsius — otherwise construction
        # would skip the validation that assignment enforces, and
        # Temperature(-500) would succeed while t.celsius = -500 raised.
        self.celsius = celsius

    # -- the one stored value, and the one rule ---------------------------

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"temperature must be a number, got {value!r}"
            ) from exc
        if value != value:                       # NaN != NaN
            raise ValueError("temperature cannot be NaN")
        if value < ABSOLUTE_ZERO_C:
            raise BelowAbsoluteZero(value)
        object.__setattr__(self, "_celsius", value)

    # -- the other two scales: computed, never stored ---------------------

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        # Convert, then assign through celsius so the rule applies here too.
        self.celsius = (float(value) - 32) * 5 / 9

    @property
    def kelvin(self):
        return self._celsius - ABSOLUTE_ZERO_C

    @kelvin.setter
    def kelvin(self, value):
        self.celsius = float(value) + ABSOLUTE_ZERO_C

    # -- read-only derived values -----------------------------------------

    @property
    def is_freezing(self):
        return self._celsius <= 0

    @property
    def is_boiling(self):
        return self._celsius >= 100

    @property
    def state_of_water(self):
        if self.is_freezing:
            return "ice"
        if self.is_boiling:
            return "steam"
        return "liquid"

    # -- arithmetic, which also goes through the setter --------------------

    def warmed_by(self, degrees):
        """Return a NEW Temperature. Validation happens in its __init__."""
        return Temperature(self._celsius + degrees)

    def cooled_by(self, degrees):
        return Temperature(self._celsius - degrees)

    # -- alternative constructors (Day 42) --------------------------------

    @classmethod
    def from_fahrenheit(cls, value):
        return cls((float(value) - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, value):
        return cls(float(value) + ABSOLUTE_ZERO_C)

    @classmethod
    def absolute_zero(cls):
        return cls(ABSOLUTE_ZERO_C)

    def __repr__(self):
        return f"Temperature({self._celsius:g})"

    def __str__(self):
        return f"{self._celsius:.1f}C / {self.fahrenheit:.1f}F / {self.kelvin:.1f}K"

    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return abs(self._celsius - other._celsius) < 1e-9

    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self._celsius < other._celsius

    def __hash__(self):
        return hash(round(self._celsius, 9))


# ===========================================================================
# 1. Three views, one value
# ===========================================================================

print("=" * WIDTH)
print(f"{'TEMPERATURE':^{WIDTH}}")
print("=" * WIDTH)

known = [
    ("absolute zero", Temperature.absolute_zero()),
    ("water freezes", Temperature(0)),
    ("room", Temperature(21)),
    ("body", Temperature.from_fahrenheit(98.6)),
    ("water boils", Temperature(100)),
    ("the sun's surface", Temperature.from_kelvin(5778)),
]

print(f"{'':<20}{'CELSIUS':>12}{'FAHRENHEIT':>13}{'KELVIN':>12}  {'WATER':<10}")
print("-" * WIDTH)
for label, temperature in known:
    print(f"{label:<20}{temperature.celsius:>12.2f}"
          f"{temperature.fahrenheit:>13.2f}{temperature.kelvin:>12.2f}  "
          f"{temperature.state_of_water:<10}")

# ===========================================================================
# 2. The scales cannot disagree, because two of them do not exist
# ===========================================================================

print()
print("-" * WIDTH)
print("SET ANY SCALE — THE OTHER TWO FOLLOW")
print("-" * WIDTH)

t = Temperature(0)
print(f"  start                 {t}")
t.celsius = 25
print(f"  t.celsius = 25        {t}")
t.fahrenheit = 212
print(f"  t.fahrenheit = 212    {t}")
t.kelvin = 300
print(f"  t.kelvin = 300        {t}")

print(f"""
  Only _celsius is stored: {t.__slots__}
  fahrenheit and kelvin are computed on every read, so there is nothing to
  keep in step and nothing that CAN be stale. Day 19's principle — derive,
  do not accumulate — applied to an object.""")

# ===========================================================================
# 3. EVERY ROUTE HITS THE SAME RULE
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'SIX ROUTES, ONE RULE':^{WIDTH}}")
print("=" * WIDTH)

t = Temperature(20)
routes = [
    ("Temperature(-500)",
     lambda: Temperature(-500)),
    ("t.celsius = -500",
     lambda: setattr(t, "celsius", -500)),
    ("t.fahrenheit = -1000",
     lambda: setattr(t, "fahrenheit", -1000)),
    ("t.kelvin = -1",
     lambda: setattr(t, "kelvin", -1)),
    ("Temperature.from_kelvin(-5)",
     lambda: Temperature.from_kelvin(-5)),
    ("Temperature.from_fahrenheit(-500)",
     lambda: Temperature.from_fahrenheit(-500)),
    ("t.cooled_by(1000)",
     lambda: t.cooled_by(1000)),
]

for label, attempt in routes:
    try:
        attempt()
        print(f"  {label:<38}ALLOWED — the rule has a hole")
    except BelowAbsoluteZero as exc:
        print(f"  {label:<38}{type(exc).__name__}: {exc.celsius:.2f}C")

print(f"\n  {'t is unchanged after all seven':<38}{t!r:>{WIDTH - 42}}")

print("""
  Seven routes, one check. Every setter and every constructor assigns
  through `self.celsius`, so the rule lives in exactly one place — and
  adding an eighth route cannot forget it, as long as it does the same.

  Compare with validating in each method: seven copies of one comparison,
  and the bug arrives the day somebody adds the eighth.""")

# ===========================================================================
# 4. Bad types and read-only values
# ===========================================================================

print()
print("-" * WIDTH)
print("OTHER THINGS IT REFUSES")
print("-" * WIDTH)

for label, attempt in [
    ("t.celsius = 'warm'", lambda: setattr(t, "celsius", "warm")),
    ("t.celsius = None", lambda: setattr(t, "celsius", None)),
    ("t.celsius = float('nan')", lambda: setattr(t, "celsius", float("nan"))),
    ("t.state_of_water = 'ice'", lambda: setattr(t, "state_of_water", "ice")),
    ("t.is_freezing = True", lambda: setattr(t, "is_freezing", True)),
    ("t.colour = 'red'  (a typo)", lambda: setattr(t, "colour", "red")),
]:
    try:
        attempt()
        print(f"  {label:<38}ALLOWED — should it be?")
    except (TypeError, ValueError, AttributeError) as exc:
        print(f"  {label:<38}{type(exc).__name__}")

print("""
  state_of_water and is_freezing have GETTERS ONLY, so assigning to them
  raises — they are conclusions, not settings.

  And `t.colour = 'red'` raises because of __slots__ (Day 43), which closes
  Day 41's typo hole: an attribute that was never declared cannot be
  created by accident.""")

# ===========================================================================
# 5. WHAT IT STILL CANNOT STOP
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE LIMIT OF ENCAPSULATION IN PYTHON':^{WIDTH}}")
print("=" * WIDTH)

t = Temperature(20)
object.__setattr__(t, "_celsius", -9999.0)
print("  object.__setattr__(t, '_celsius', -9999.0)")
print(f"  t is now: {t}")
print(f"  below absolute zero: {t.celsius < ABSOLUTE_ZERO_C}")

print("""
  Python has no private attributes and does not want any. The property
  protects against MISUSE OF THE API, not against somebody deliberately
  going around it — and that is the language's considered position, not an
  oversight.

  WHAT YOU ACTUALLY GET:
    _celsius      a convention every Python reader understands
    @property     validation on every NORMAL route, written once
    __slots__     typos become errors
    frozen=True   Day 48 — assignment raises, including through the
                  attribute name

  What you do NOT get is a lock. If somebody reaches past the interface,
  the bug is theirs — and the docstring above says so, which is the most
  enforcement Python offers and, in practice, enough.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change __init__ to `self._celsius = celsius` and re-run section 3.
#     Temperature(-500) starts succeeding while t.celsius = -500 still
#     raises — construction and assignment disagreeing is a genuinely
#     horrible bug to diagnose.
#
#   * Store fahrenheit as well as celsius, set one, and print both. Then
#     delete the stored version and confirm the problem is gone rather than
#     fixed.
#
#   * Add a Rankine scale. It should be about six lines and require no
#     change to the validation, because there is only one place it lives.
#
#   * Add @cached_property for something genuinely expensive, then change
#     celsius and read it again. It is stale — which is why cached_property
#     is wrong for anything derived from mutable state.
#
#   * On Day 48, rewrite this as @dataclass(frozen=True) with a
#     __post_init__ validator and compare. The dataclass wins on lines and
#     loses the ability to set fahrenheit — decide which you want.
