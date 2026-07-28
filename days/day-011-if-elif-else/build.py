"""Day 011 build — a grade calculator, with the boundaries actually tested.

Two implementations of the same policy:

    grade_from_chain     an if/elif chain      — the obvious way
    grade_from_table     a threshold table     — the way that scales

and then the part that matters: a boundary check that runs BOTH against
N-1, N and N+1 for every threshold, and reports any disagreement.

Getting a grade calculator roughly right is easy. Getting it right AT THE
EDGES, and knowing you have, is the actual exercise.

    python3 build.py
"""

WIDTH = 64

# ---------------------------------------------------------------------------
# The policy, in one place. Everything below reads from these.
# ---------------------------------------------------------------------------
#
# Each entry is "minimum percentage, grade". A score belongs to the first
# band whose minimum it reaches, scanning from the top.

BANDS = (
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
)

PASS_MARK = 60


# ===========================================================================
# 1. The if/elif chain
# ===========================================================================
#
# Note what is NOT here: no upper bounds. `elif score >= 80` already knows
# the score is below 90, because the chain stopped at the first match. An
# `and score < 90` would be a second thing that could be wrong.

def grade_from_chain(score):
    """Return the letter grade for a percentage, using an if/elif chain."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


# ===========================================================================
# 2. The table
# ===========================================================================
#
# Same policy, driven by BANDS. Adding a band is a one-line data change
# rather than an edit to control flow — which is the argument for it.

def grade_from_table(score):
    """Return the letter grade for a percentage, using the BANDS table."""
    for minimum, letter in BANDS:
        if score >= minimum:
            return letter
    return "F"


# (Functions are Day 31 and the `for` is Day 13. They are used here because
#  the alternative — pasting the chain three times to test three values — is
#  exactly the duplication this build is about avoiding. Read them as "a
#  named piece of code you can run more than once".)


# ===========================================================================
# 3. The report
# ===========================================================================

print("=" * WIDTH)
print(f"{'GRADE CALCULATOR':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'MIN':>6}{'GRADE':>8}   {'MEANING':<40}")
print("-" * WIDTH)
print(f"{90:>6}{'A':>8}   {'excellent':<40}")
print(f"{80:>6}{'B':>8}   {'good':<40}")
print(f"{70:>6}{'C':>8}   {'satisfactory':<40}")
print(f"{60:>6}{'D':>8}   {'pass':<40}")
print(f"{0:>6}{'F':>8}   {'fail':<40}")
print("=" * WIDTH)
print()

SCORES = (100, 95, 90, 89.9, 85, 80, 79.5, 72, 70, 65, 60, 59.9, 30, 0)

print(f"{'SCORE':>8}{'GRADE':>8}{'PASSED':>9}  {'BAR':<30}")
print("-" * WIDTH)
for score in SCORES:
    letter = grade_from_chain(score)
    passed = score >= PASS_MARK
    bar = "#" * int(score / 100 * 25)
    print(f"{score:>8}{letter:>8}{str(passed):>9}  {bar:<30}")

print()

# ===========================================================================
# 4. THE BOUNDARY TEST — the point of the day
# ===========================================================================
#
# For every threshold N, check N-1, N and N+1. If a `>` had been written
# where a `>=` belonged, exactly one of these rows would be wrong, and it
# would be the middle one.

print("=" * WIDTH)
print(f"{'BOUNDARY CHECK':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'SCORE':>8}{'CHAIN':>8}{'TABLE':>8}{'AGREE':>8}   {'NOTE':<28}")
print("-" * WIDTH)

disagreements = 0
for minimum, expected in BANDS:
    for offset in (-1, 0, 1):
        probe = minimum + offset
        if probe < 0 or probe > 100:
            continue
        from_chain = grade_from_chain(probe)
        from_table = grade_from_table(probe)
        agree = from_chain == from_table
        disagreements += not agree
        note = "<- the threshold itself" * (offset == 0)
        print(
            f"{probe:>8}{from_chain:>8}{from_table:>8}"
            f"{str(agree):>8}   {note:<28}"
        )
    print("-" * WIDTH)

print(f"{'disagreements':<44}{disagreements:>20}")
print()

# The middle row of each group is the one that matters. At exactly 90 the
# grade must be A, not B. Change `>=` to `>` in grade_from_chain and run
# this again: four rows flip, and they are all threshold rows.

# ===========================================================================
# 5. Interactive
# ===========================================================================

print("=" * WIDTH)
raw = input("Enter a percentage (or press Enter to skip): ").strip()

# Day 6's safe conversion: validate, then convert something guaranteed valid.
is_numeric = raw.replace(".", "", 1).isdigit()

if not raw:
    print("Skipped.")
elif not is_numeric:
    print(f"{raw!r} is not a number. Percentages only, 0 to 100.")
else:
    value = float(raw)
    if value < 0 or value > 100:
        print(f"{value} is outside 0-100. Nothing sensible to report.")
    else:
        letter = grade_from_chain(value)
        print(f"{value}% is a {letter} "
              f"({'pass' if value >= PASS_MARK else 'fail'})")

print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change one `>=` to `>` in grade_from_chain. The boundary check should
#     immediately report disagreements, and only on threshold rows. That is
#     what a test is: a thing that notices before your students do.
#
#   * Add plus/minus grades (A-, B+, ...). In the chain that is twelve
#     branches; in BANDS it is twelve lines of data and no logic change.
#     Do both, then decide which you would rather maintain.
#
#   * The interactive section at the bottom is three levels of nesting deep.
#     Rewrite it with guard clauses once you have `continue` (Day 14) or
#     `return` (Day 31), and compare.
#
#   * What should 100.0 return? What about -0.0? An empty string? Write the
#     answer down BEFORE you check what your code does. That written answer
#     is a specification, and the gap between it and the code is a bug.
