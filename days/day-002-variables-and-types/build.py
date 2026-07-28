"""Day 002 build — a temperature converter, all three scales, both directions.

Six conversions, no branching (that is Day 11) and no input (that is Day 6).
Change the three values under INPUT and run it again.

    python3 build.py
"""

# ---------------------------------------------------------------------------
# INPUT — the only lines to edit
# ---------------------------------------------------------------------------

celsius = 100.0
fahrenheit = 98.6
kelvin = 0.0

# ---------------------------------------------------------------------------
# The constants, named. A bare 273.15 in the middle of an expression is a
# puzzle; ABSOLUTE_ZERO_C is a fact. Naming things IS the lesson today.
# ---------------------------------------------------------------------------

ABSOLUTE_ZERO_C = -273.15     # 0 K expressed in Celsius
F_PER_C = 9 / 5               # degrees Fahrenheit per degree Celsius
F_AT_ZERO_C = 32              # the Fahrenheit reading when Celsius is 0

# ---------------------------------------------------------------------------
# The six conversions. Each is one expression, each is named after what it
# holds, and none of them repeats a magic number.
# ---------------------------------------------------------------------------

# From Celsius
c_to_f = celsius * F_PER_C + F_AT_ZERO_C
c_to_k = celsius - ABSOLUTE_ZERO_C

# From Fahrenheit
f_to_c = (fahrenheit - F_AT_ZERO_C) / F_PER_C
f_to_k = f_to_c - ABSOLUTE_ZERO_C

# From Kelvin
k_to_c = kelvin + ABSOLUTE_ZERO_C
k_to_f = k_to_c * F_PER_C + F_AT_ZERO_C

# ---------------------------------------------------------------------------
# Output. round() is for DISPLAY only — the values above are untouched.
# ---------------------------------------------------------------------------

print("=" * 42)
print("TEMPERATURE CONVERTER")
print("=" * 42)

print()
print(celsius, "degrees Celsius is:")
print("   ", round(c_to_f, 2), "F")
print("   ", round(c_to_k, 2), "K")

print()
print(fahrenheit, "degrees Fahrenheit is:")
print("   ", round(f_to_c, 2), "C")
print("   ", round(f_to_k, 2), "K")

print()
print(kelvin, "Kelvin is:")
print("   ", round(k_to_c, 2), "C")
print("   ", round(k_to_f, 2), "F")

print()
print("=" * 42)

# ---------------------------------------------------------------------------
# Sanity checks — the four conversions everybody knows by heart. If any of
# these prints False, the arithmetic above is wrong, not the physics.
# ---------------------------------------------------------------------------

print("Water freezes:  0 C -> 32 F      ", 0 * F_PER_C + F_AT_ZERO_C == 32)
print("Water boils:  100 C -> 212 F     ", 100 * F_PER_C + F_AT_ZERO_C == 212)
print("The crossover: -40 C -> -40 F    ", -40 * F_PER_C + F_AT_ZERO_C == -40)
print("Absolute zero:  0 K -> -273.15 C ", 0 + ABSOLUTE_ZERO_C == ABSOLUTE_ZERO_C)

# Note that all four of those used == on floats and got away with it, because
# every value involved happens to be exactly representable in binary. Do not
# take the wrong lesson from that: 0.1 + 0.2 == 0.3 is still False.


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add Rankine (R = F + 459.67). Six conversions become twelve — notice how
#     the count grows, and start wondering whether there is a better shape for
#     this. There is: convert everything to one base scale and back. Try it.
#   * Print a temperature below absolute zero and notice the program cheerfully
#     reports nonsense. You cannot fix that yet; you can on Day 11.
#   * Replace every `round(x, 2)` with an f-string format spec once you have
#     done Day 4, and delete a lot of noise.
