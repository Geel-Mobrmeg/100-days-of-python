"""Day 005 — Numbers and operators.

    python3 lesson.py
"""

import math
from decimal import Decimal, ROUND_HALF_UP

# ---------------------------------------------------------------------------
# 1. The seven arithmetic operators
# ---------------------------------------------------------------------------

print(7 + 3, 7 - 3, 7 * 3)        # 10 4 21
print(7 / 3)                      # 2.3333333333333335  — true division
print(7 // 3)                     # 2                   — floor division
print(7 % 3)                      # 1                   — remainder
print(7 ** 3)                     # 343                 — power

# / ALWAYS returns a float, even when it divides exactly. This is the one
# that bites: an index or a count computed with / is the wrong type.
print(10 / 5, type(10 / 5))       # 5.0 <class 'float'>
print(10 // 5, type(10 // 5))     # 5 <class 'int'>

# // FLOORS, it does not truncate. Python rounds toward negative infinity;
# C and Java round toward zero. Note the difference on negatives:
print(7 // 2)                     # 3
print(-7 // 2)                    # -4   <- not -3
print(int(-7 / 2))                # -3   <- truncation, if that is what you want
print(7.0 // 2)                   # 3.0  — floor division of a float stays float


# ---------------------------------------------------------------------------
# 2. % — the operator that earns its keep
# ---------------------------------------------------------------------------

n = 17

print(n % 2 == 0)          # is n even?
print(n % 5 == 0)          # does 5 divide n?  (Day 14 builds a prime finder on this)
print(n % 10)              # last decimal digit

# // and % are two halves of ONE operation: how many whole ones fit, and what
# is left over. Splitting a total into units is always this pair.
total_seconds = 3725
print(total_seconds // 60, "minutes and", total_seconds % 60, "seconds")

# divmod() gives you both at once:
print(divmod(3725, 60))    # (62, 5)

# Nested, for hours/minutes/seconds:
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60
print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

# On negatives, % takes the SIGN OF THE DIVISOR. That is what makes wrapping
# work correctly for negative values:
print(-7 % 3)              # 2   (not -1)
print(-90 % 360)           # 270 — the useful consequence


# ---------------------------------------------------------------------------
# 3. Precedence — the errors here are SILENT, which is what makes them bad
# ---------------------------------------------------------------------------

# ** binds tighter than unary minus:
print(-2 ** 2)             # -4   — this is -(2 ** 2)
print((-2) ** 2)           # 4    — this is what you probably meant

# ** is RIGHT-associative; everything else is left-associative:
print(2 ** 3 ** 2)         # 512  — 2 ** (3 ** 2)
print((2 ** 3) ** 2)       # 64

# The classic wrong average. It runs. It raises nothing. It is wrong.
a = 10
b = 20
c = 30
print(a + b + c / 3)       # 40.0  <- only c was divided
print((a + b + c) / 3)     # 20.0  <- correct

# Roots are fractional powers:
print(9 ** 0.5)            # 3.0
print(27 ** (1 / 3))       # 3.0000000000000004 — floats, again


# ---------------------------------------------------------------------------
# 4. Augmented assignment
# ---------------------------------------------------------------------------

total = 0
total += 10       # total = total + 10
total -= 3
total *= 2
total //= 4
print("total:", total)     # 3


# ---------------------------------------------------------------------------
# 5. The math module — your first import
# ---------------------------------------------------------------------------

print(math.sqrt(16))       # 4.0  — always a float
print(math.floor(3.7), math.ceil(3.2))     # 3 4
print(math.pi, math.e)
print(math.inf > 10 ** 100)                # True

# THREE ways to make 3.7 whole, and they disagree on negatives. Know which
# one you are asking for:
print(int(-3.7), math.floor(-3.7), math.ceil(-3.7), round(-3.7))
#     -3         -4                -3               -4
#     truncate   down              up               nearest

# The correct way to compare floats. Day 2 said never use == ; this is why
# that advice was actionable.
print(0.1 + 0.2 == 0.3)                    # False
print(math.isclose(0.1 + 0.2, 0.3))        # True


# ---------------------------------------------------------------------------
# 6. round() does not do what you think
# ---------------------------------------------------------------------------

# Banker's rounding: exact halves go to the nearest EVEN number.
print(round(0.5), round(1.5), round(2.5), round(3.5))   # 0 2 2 4

# This is deliberate — always-round-up biases a long sum upward — but it is
# not what a shopkeeper does.

# And floats cannot hold most decimals exactly, so this looks broken:
print(round(2.675, 2))     # 2.67, because 2.675 is really 2.67499999999999982


# ---------------------------------------------------------------------------
# 7. Decimal — what money is actually made of
# ---------------------------------------------------------------------------

# Decimal stores decimal digits exactly. Build it from a STRING; building it
# from a float just inherits the float's error.
print(Decimal("0.1") + Decimal("0.2"))     # 0.3 exactly
print(Decimal(0.1))                        # 0.1000000000000000055511151231257827
                                           #  ^ do not do this

PENNY = Decimal("0.01")
print(Decimal("2.675").quantize(PENNY, rounding=ROUND_HALF_UP))   # 2.68

# quantize() is "round to this many places, with the rule I name". It is the
# operation you want every time you turn a computed amount into money.
bill = Decimal("100.00")
share = (bill / 3).quantize(PENNY, rounding=ROUND_HALF_UP)
print(share, share * 3)     # 33.33 99.99  <- the missing penny. Today's build.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Compute 10_000 seconds as h:mm:ss. Then do it with two divmod() calls.
#   * Predict then check: 7 % -2, -7 % -2, -7 // -2.
#   * Write a leap-year test with % , and , or and not. 2000 is one; 1900 is not.
#   * Add 0.1 to itself ten times and compare to 1.0. Then with Decimal("0.1").
#   * Divide by zero on purpose, with / and then with %. Same exception?
