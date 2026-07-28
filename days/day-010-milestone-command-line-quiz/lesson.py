"""Day 010 — Milestone techniques: program structure and branchless selection.

Today's build is a scored quiz, and you still do not have `if`. That sounds
like a crippling limitation. It is actually the best possible preparation for
tomorrow, because it forces you to learn the two techniques that experienced
programmers reach for INSTEAD of a conditional, long after they have one.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. The shape of a program
# ---------------------------------------------------------------------------
#
# Every program you have written for nine days, and most of the ones you will
# write for ninety more, has the same four-part shape:
#
#     CONFIGURE   constants at the top, named, in one place
#     INPUT       gather everything from the outside world
#     COMPUTE     pure arithmetic on what you gathered — no printing
#     REPORT      print. Nothing here calculates anything.
#
# The discipline is keeping COMPUTE and REPORT apart. When a program computes
# a value inside a print() call, that value cannot be checked, reused, or
# tested (Day 57). Every build in this course from here on separates them.

WIDTH = 60


# ---------------------------------------------------------------------------
# 2. A bool is an index
# ---------------------------------------------------------------------------

# Day 2: True is 1 and False is 0. Day 3: sequences are indexed by integers.
# Put those together and a two-element sequence becomes a branch:

VERDICT = ("WRONG", "RIGHT")

correct = True
print(VERDICT[correct])          # RIGHT
print(VERDICT[False])            # WRONG

# That is `if correct: "RIGHT" else: "WRONG"` with no `if` in sight. It reads
# well, it is one line, and it stays one line for any number of cases — which
# a chain of `if`/`elif` does not.

MARK = ("x", "v")
print(f"[{MARK[True]}] [{MARK[False]}]")


# ---------------------------------------------------------------------------
# 3. A number is an index — the lookup table
# ---------------------------------------------------------------------------

# The generalisation. Instead of ten comparisons deciding a grade, ONE string
# where position N holds the grade for a score of N:

GRADES = "FFFFFDDCBAA"
#         01234567890
#         |    |  ||`--- 9 and 10 -> A
#         |    |  |`---- 8        -> B
#         |    |  `----- 7        -> C
#         |    `-------- 5, 6     -> D
#         `------------- 0 to 4   -> F

for score in range(11):
    print(f"  score {score:>2}  ->  grade {GRADES[score]}")

# Compare that to the `if score >= 9: ... elif score >= 8: ...` you would
# write tomorrow. The table version puts the whole policy in one line where
# it can be read, checked and changed. This is a real technique, not a
# workaround: lookup tables outlive the branches they replace.
#
# (The `for` above is Day 13 and is only here to print eleven rows.)


# ---------------------------------------------------------------------------
# 4. Multiplying by a bool selects a string
# ---------------------------------------------------------------------------

# Day 3: "ab" * 2 is "abab". So "ab" * True is "ab", and "ab" * False is "".
# That makes a whole message appear or vanish on a condition:

hint = "  Hint: it is the capital, not the largest city."
was_wrong = True
print("Your answer was marked" + " incorrect" * was_wrong)
print(hint * was_wrong)          # shown

# Careful: print("") still prints a BLANK LINE, because print adds the
# newline itself. To emit truly nothing, put the newline inside the string
# being multiplied and turn print's own off:
print((hint + "\n") * (not was_wrong), end="")     # no output at all
print((hint + "\n") * was_wrong, end="")           # the hint, once

# Use this sparingly once you have `if`. It is perfect for suffixes and
# optional fragments, and unreadable for anything longer.

# The plural-s trick is the version you will keep using forever:
for n in (0, 1, 5):
    print(f"  {n} question{'s' * (n != 1)}")


# ---------------------------------------------------------------------------
# 5. Comparing what a human typed
# ---------------------------------------------------------------------------

# Never compare raw input. Normalise BOTH sides the same way, every time.

expected = "Cairo"
typed = "  cairo  "

print(typed == expected)                                  # False — useless
print(typed.strip().lower() == expected.lower())          # True  — correct

# For numbers, compare with a tolerance rather than for equality, because
# floats (Day 5) and because "3.0" and "3" are the same answer:
answer_text = " 3.0 "
target = 3
clean = answer_text.strip()
is_numeric = clean.replace(".", "", 1).replace("-", "", 1).isdigit()
value = float(clean * is_numeric or "nan")
print(abs(value - target) < 0.001)                        # True

# `clean * is_numeric or "nan"` is Day 6's safe-conversion trick: a string
# times False is "", "" is falsy, so float() sees "nan" and never raises.
# nan compares False against everything, so a non-numeric answer is simply
# marked wrong instead of crashing the quiz.


# ---------------------------------------------------------------------------
# 6. Accepting more than one right answer
# ---------------------------------------------------------------------------

# `in` against a string of delimited options is enough today, and it is the
# pattern the build uses. (Day 26's sets are the proper tool.)

ACCEPTED = "true|t|yes|y|1"
given = "Yes"
print(given.strip().lower() in ACCEPTED.split("|"))       # True

# Careful: `given in ACCEPTED` without the split would also match "ru",
# because that is a substring. Splitting into whole options is the fix, and
# the bug it avoids is a genuinely common one.
print("ru" in ACCEPTED)                                   # True  <- wrong
print("ru" in ACCEPTED.split("|"))                        # False <- right


# ---------------------------------------------------------------------------
# 7. Scoring
# ---------------------------------------------------------------------------

results = (True, True, False, True, False)

print()
print("=" * WIDTH)
print(f"{'score':<20}{sum(results):>10}")
print(f"{'out of':<20}{len(results):>10}")
print(f"{'percent':<20}{sum(results) / len(results):>10.0%}")
print(f"{'all correct':<20}{str(all(results)):>10}")
print(f"{'any correct':<20}{str(any(results)):>10}")
print("=" * WIDTH)

# sum() over bools is the count of Trues (Day 7). all() and any() collapse
# them to a single verdict. Between them you rarely need to count by hand.


# ---------------------------------------------------------------------------
# What tomorrow changes
# ---------------------------------------------------------------------------
#
# On Day 11 you get `if`, and you should go back and rewrite today's build
# with it. Then compare the two honestly. You will find:
#
#   * The per-answer feedback is much better with `if` — messages can differ
#     in structure, not just in content.
#   * The grade lookup is STILL better as a table. Do not replace it.
#
# Knowing which of those is which is the actual skill.
