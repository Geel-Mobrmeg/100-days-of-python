"""Day 006 build — a BMI calculator that will not crash, whatever you type.

Two halves to "refuses nonsense input instead of crashing":

  NOT CRASHING  is achievable today. Clean the input down to something that is
                always convertible, with a fallback when nothing survives.

  REFUSING      as in "stop, complain, ask again" needs `if` (Day 11) and
                `while` (Day 12). You do not have them.

So this program does the part that comes first and that most people skip: it
decides, precisely, whether the input is acceptable, and prints a verdict for
every rule. Day 11 acts on the verdict. Day 12 re-asks. Day 51 replaces the
whole approach with try/except.

    python3 build.py
    printf '1.75\\n70\\n' | python3 build.py
    printf '  175 cm \\n70,5 KG\\n' | python3 build.py
"""

WIDTH = 52

print("=" * WIDTH)
print(f"{'BMI CALCULATOR':^{WIDTH}}")
print("=" * WIDTH)
print("Height accepts: 1.75, 175cm, '1,75'. Weight accepts kg or lb.")
print()

# ---------------------------------------------------------------------------
# 1. Read. Everything arrives as a string; nothing is trusted yet.
# ---------------------------------------------------------------------------

raw_height = input("Height  : ")
raw_weight = input("Weight  : ")

# ---------------------------------------------------------------------------
# 2. Clean. Strip, lowercase, drop units, normalise the decimal mark, strip
#    again — because removing a unit leaves the space it was sitting next to.
# ---------------------------------------------------------------------------

h = raw_height.strip().lower()
had_cm = h.endswith("cm")
h = h.replace("cm", "").replace("m", "").replace(",", ".").strip()

w = raw_weight.strip().lower()
had_lb = w.endswith("lb") or w.endswith("lbs")
w = w.replace("lbs", "").replace("lb", "").replace("kg", "")
w = w.replace(",", ".").strip()

# ---------------------------------------------------------------------------
# 3. Validate. Each rule is a bool. Printing bools is how a program reports a
#    verdict when it cannot yet act on one.
# ---------------------------------------------------------------------------

h_not_empty = len(h) > 0
h_one_dot = h.count(".") <= 1
h_numeric = h.replace(".", "", 1).isdigit()
h_ok = h_not_empty and h_one_dot and h_numeric

w_not_empty = len(w) > 0
w_one_dot = w.count(".") <= 1
w_numeric = w.replace(".", "", 1).isdigit()
w_ok = w_not_empty and w_one_dot and w_numeric

print()
print("-" * WIDTH)
print(f"{'VALIDATION':^{WIDTH}}")
print("-" * WIDTH)
print(f"{'rule':<34}{'height':>9}{'weight':>9}")
print(f"{'not empty':<34}{str(h_not_empty):>9}{str(w_not_empty):>9}")
print(f"{'at most one decimal point':<34}{str(h_one_dot):>9}{str(w_one_dot):>9}")
print(f"{'digits only once cleaned':<34}{str(h_numeric):>9}{str(w_numeric):>9}")
print("-" * WIDTH)
print(f"{'ACCEPTED':<34}{str(h_ok):>9}{str(w_ok):>9}")
print()

print(f"raw height {raw_height!r} cleaned to {h!r}")
print(f"raw weight {raw_weight!r} cleaned to {w!r}")
print()

# ---------------------------------------------------------------------------
# 4. Convert — safely, with no conditional available.
#
#    `h * h_ok` is the trick. A bool is an int (Day 2), so multiplying a
#    string by it keeps the string when the verdict was True and produces ""
#    when it was False. `or "0"` then supplies the default for that empty
#    string. Together they guarantee float() only ever sees something it can
#    parse, so it cannot raise. That is the "does not crash" half, and it is
#    the whole reason validation had to come before conversion.
#
#    A rejected input becomes 0, and 0 propagates visibly through everything
#    below rather than silently poisoning one number. That is a design choice,
#    and it is only defensible because the verdict was printed above.
# ---------------------------------------------------------------------------

height_value = float(h * h_ok or "0")
weight_value = float(w * w_ok or "0")

# Units. Multiplying by a bool is multiplying by 1 or 0 (Day 2), which is how
# you pick between two numbers with no `if` available.
height_m = height_value / 100 * had_cm + height_value * (not had_cm)
weight_kg = weight_value * 0.45359237 * had_lb + weight_value * (not had_lb)

# A height of 0 would be a ZeroDivisionError, so keep the divisor away from
# zero and let the "usable" flag below carry the truth.
safe_height = height_m or 1.0

bmi = weight_kg / (safe_height ** 2)
usable = h_ok and w_ok and height_m > 0 and weight_kg > 0

# ---------------------------------------------------------------------------
# 5. Report
# ---------------------------------------------------------------------------

print("-" * WIDTH)
print(f"{'RESULT':^{WIDTH}}")
print("-" * WIDTH)
print(f"{'Height (m)':<34}{height_m:>18.3f}")
print(f"{'Weight (kg)':<34}{weight_kg:>18.3f}")
print(f"{'BMI':<34}{bmi:>18.1f}")
print(f"{'Is this number meaningful?':<34}{str(usable):>18}")
print()

# The category, as five booleans. Exactly one is True for any real BMI.
print(f"{'Underweight  (under 18.5)':<34}{str(usable and bmi < 18.5):>18}")
print(f"{'Healthy      (18.5 - 24.9)':<34}{str(usable and 18.5 <= bmi < 25):>18}")
print(f"{'Overweight   (25.0 - 29.9)':<34}{str(usable and 25 <= bmi < 30):>18}")
print(f"{'Obese        (30.0 and over)':<34}{str(usable and bmi >= 30):>18}")
print("=" * WIDTH)

# `18.5 <= bmi < 25` is a chained comparison — Python reads it as one range
# test, exactly as the maths notation does. Tomorrow explains why that works.


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Feed it every awful thing you can think of: an empty line, "abc",
#     "1.2.3", "-70", "0", "  175 CM  ", "154lbs". It must never traceback.
#     If it does, you have found the gap — fix it.
#   * "-70" currently fails the digits gate, so it is rejected. Is rejecting a
#     negative weight the right call, or should it be a separate rule with its
#     own line in the table? Decide and implement it.
#   * Note that `usable` is computed and then only PRINTED. On Day 11, that
#     one bool becomes the condition of an `if` and this file gets shorter.
#   * On Day 12, wrap the whole thing in a while loop that re-asks until
#     h_ok and w_ok. On Day 51, delete the validation and use try/except
#     instead — then argue with yourself about which version you prefer.
