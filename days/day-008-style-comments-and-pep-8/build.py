"""Parse one delimited user record and report it.

This is `ugly.py` after the refactor. It is byte-for-byte identical in output
and silent under `ruff check`. That combination is the whole exercise:

    python3 ugly.py  > /tmp/before.txt
    python3 build.py > /tmp/after.txt
    diff /tmp/before.txt /tmp/after.txt && echo "behaviour unchanged"

If the diff is empty, the refactor was honest. If it is not, you changed the
program while claiming to tidy it — which is the single most common way a
"cleanup" commit breaks production.
"""

# ---------------------------------------------------------------------------
# Constants. Every magic number from the original now has a name, and the
# names are the documentation.
# ---------------------------------------------------------------------------

RULE_WIDTH = 60

BMI_UNDERWEIGHT_MAX = 18.5
BMI_HEALTHY_MAX = 25
BMI_OVERWEIGHT_MAX = 30

MAX_PLAUSIBLE_AGE = 150
MAX_PLAUSIBLE_HEIGHT_M = 3
MAX_PLAUSIBLE_WEIGHT_KG = 500

MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = 365
CM_PER_M = 100
LB_PER_KG = 2.20462

RECORD = "  Ada Lovelace,  ada@example.com , 36 , 1.75 , 70.5  "

# ---------------------------------------------------------------------------
# Parse. Every field is stripped at the point it is read, once, so that
# nothing downstream has to wonder whether it was.
# ---------------------------------------------------------------------------

fields = RECORD.strip().split(",")

name = fields[0].strip().title()
email = fields[1].strip().lower()
age = int(fields[2].strip())
height_m = float(fields[3].strip())
weight_kg = float(fields[4].strip())

# ---------------------------------------------------------------------------
# Derive
# ---------------------------------------------------------------------------

bmi = weight_kg / (height_m**2)

is_underweight = bmi < BMI_UNDERWEIGHT_MAX
is_healthy = BMI_UNDERWEIGHT_MAX <= bmi < BMI_HEALTHY_MAX
is_overweight = BMI_HEALTHY_MAX <= bmi < BMI_OVERWEIGHT_MAX
is_obese = bmi >= BMI_OVERWEIGHT_MAX

is_plausible = (
    0 < age < MAX_PLAUSIBLE_AGE
    and 0 < height_m < MAX_PLAUSIBLE_HEIGHT_M
    and 0 < weight_kg < MAX_PLAUSIBLE_WEIGHT_KG
)

email_looks_valid = "@" in email and "." in email

name_parts = name.split()
initials = name_parts[0][0] + name_parts[1][0]

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

rule = "=" * RULE_WIDTH

print(rule)
print("USER RECORD")
print(rule)
print(f"Name:  {name}")
print(f"Email: {email}")
print(f"Age:   {age}")
print(f"Height:{height_m}m")
print(f"Weight:{weight_kg}kg")
print(
    f"BMI:   {round(bmi, 1)}   "
    f"(underweight={is_underweight} healthy={is_healthy} "
    f"overweight={is_overweight} obese={is_obese})"
)
print(f"Valid: {is_plausible}")
print(rule)
print(f"Email looks ok: {email_looks_valid}")
print(f"Initials: {initials}")
print(f"Age in months: {age * MONTHS_PER_YEAR}")
print(f"Age in days:   {age * DAYS_PER_YEAR}")
print(f"Height in cm:  {height_m * CM_PER_M}")
print(f"Weight in lb:  {round(weight_kg * LB_PER_KG, 1)}")


# ---------------------------------------------------------------------------
# What actually changed, and why
# ---------------------------------------------------------------------------
#
#  1. Dead imports deleted.        os, sys, math, json were never used, and
#                                  `from decimal import *` imported ~40 names
#                                  into the file to use none of them.
#  2. `l`, `O`, `I` renamed.       Those three are banned by PEP 8 because in
#                                  most fonts they are indistinguishable from
#                                  1, 0 and 1.
#  3. Names made consistent.       NAME, Email, age, h, W became one scheme:
#                                  lower_snake_case, spelled out.
#  4. Units put in the names.      `h` became `height_m`, `W` became
#                                  `weight_kg`. A unit in the name is a bug
#                                  that never happens.
#  5. Magic numbers named.         18.5, 25, 30, 150, 2.20462 were facts with
#                                  no explanation. Now they are constants.
#  6. Chained comparisons.         `bmi>=18.5 and bmi<25` became
#                                  `18.5 <= bmi < 25` (Day 7).
#  7. `== True` deleted.           `has_at == True` is just `has_at`.
#  8. Concatenation to f-strings.  No more str() calls, no more + chains, and
#                                  the 130-character BMI line now fits.
#  9. Commented-out code deleted.  Git remembers it. Nobody else needs to.
# 10. `if_valid` renamed.          A name starting with `if_` that is not a
#                                  condition is actively misleading.
#
# Notice what did NOT change: the arithmetic, the parsing, the output. A
# refactor that changes behaviour is not a refactor, it is a rewrite with a
# misleading commit message.
