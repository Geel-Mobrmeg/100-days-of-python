"""Day 011 — if, elif, else.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. The syntax
# ---------------------------------------------------------------------------

temperature = 24

if temperature > 30:
    print("hot")
elif temperature > 20:
    print("warm")
else:
    print("cold")

# Three things that will be your first three errors:
#   * every if/elif/else ends with a COLON
#   * the INDENT is the block — four spaces, never tabs
#   * `else` takes NO condition. `else x:` is a SyntaxError.

# The condition is tested for TRUTHINESS (Day 7), not just equality:
items = []
if items:
    print("there are items")
else:
    print("no items")          # empty list is falsy

name = ""
if not name:
    print("no name given")


# ---------------------------------------------------------------------------
# 2. Order matters — the chain STOPS at the first match
# ---------------------------------------------------------------------------

score = 95

# WRONG. Every score >= 50 stops at the first branch. Nobody ever gets an A.
if score >= 50:
    wrong_grade = "D"
elif score >= 90:
    wrong_grade = "A"
else:
    wrong_grade = "F"
print(f"wrong order gives {score} the grade {wrong_grade}")

# RIGHT. Most specific first — for numeric bands, highest threshold down.
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"
print(f"right order gives {score} the grade {grade}")

# Because the chain stops at the first match, the second branch ALREADY knows
# the score is under 90. Writing `elif score >= 80 and score < 90:` is not
# just noise — it is a second thing that can be wrong.


# ---------------------------------------------------------------------------
# 3. Boundaries — where every bug in this topic lives
# ---------------------------------------------------------------------------

print()
print("  value   >80    >=80")
print(f"  {79:>5}{str(79 > 80):>7}{str(79 >= 80):>8}")
print(f"  {80:>5}{str(80 > 80):>7}{str(80 >= 80):>8}")
print(f"  {81:>5}{str(81 > 80):>7}{str(81 >= 80):>8}")

# At exactly 80 the two disagree, and that is the whole bug. `>` vs `>=` is
# the most common off-by-one in real software.
#
# The defence is not care. It is TESTING THE BOUNDARY: for every threshold N,
# check N-1, N and N+1. Today's build does this in the file.

# A related trap: GAPS. If one branch is `>= 80` and the next is `< 79`, then
# 79.5 matches nothing at all:
value = 79.5
if value >= 80:
    band = "high"
elif value < 79:
    band = "low"
else:
    band = "FELL THROUGH THE GAP"
print(f"\n79.5 lands in: {band}")

# Without that else, `band` would simply never be assigned, and the NameError
# would surface somewhere else entirely.


# ---------------------------------------------------------------------------
# 4. Nesting, and how to avoid it
# ---------------------------------------------------------------------------

logged_in = True
is_admin = False

# Two levels is about the limit of comfortable:
if logged_in:
    if is_admin:
        print("admin panel")
    else:
        print("user panel")
else:
    print("login page")

# Three or four levels is the "arrow anti-pattern", where the actual work
# sits so far right that the conditions leading to it cannot be read.

# FIX 1: combine with `and` (Day 7).
if logged_in and is_admin:
    print("admin panel")

# FIX 2 — the big one: NAME THE CONDITION. This is usually the largest
# readability win available anywhere in a program, and the name can be
# printed when you are debugging.
can_administer = logged_in and is_admin
if can_administer:
    print("admin panel")
else:
    print("not an admin")

# FIX 3: guard clauses. Handle the exceptional cases first and LEAVE, so the
# main path ends up unindented at the bottom:
#
#     if not logged_in:
#         return                 # Day 31
#     if not is_admin:
#         return
#     show_admin_panel()         # the point of the function, at indent 0
#
# You need something to leave with. `return` is Day 31; `continue` and
# `break` are Day 14. Until then, use FIX 1 and FIX 2.


# ---------------------------------------------------------------------------
# 5. The ternary expression
# ---------------------------------------------------------------------------

age = 20

status = "adult" if age >= 18 else "child"
print(f"\nstatus: {status}")

# Read the MIDDLE first: the condition, then the value if true, then the
# value otherwise. It is an EXPRESSION, so it goes anywhere a value goes:
print(f"You are an {'adult' if age >= 18 else 'child'}")

count = 1
print(f"{count} item{'s' if count != 1 else ''}")

# Use it for two SHORT values. Do not nest it. The moment you read it twice,
# it should have been a normal if:
#
#   BAD:  x = "a" if p else "b" if q else "c" if r else "d"


# ---------------------------------------------------------------------------
# 6. When NOT to use if
# ---------------------------------------------------------------------------

# Yesterday's techniques did not stop being good. If a chain does nothing but
# MAP AN INPUT TO AN OUTPUT, a table is usually clearer:

GRADES = "FFFFFDDCBAA"          # the same table Day 10 used
#         0    5 7 9 10         # index is the score out of 10
print(f"\nlookup table: score 7 -> {GRADES[7]}")

correct = True
print(("WRONG", "RIGHT")[correct])

# Rule of thumb:
#   * mapping input -> output      -> lookup table
#   * branches do different WORK   -> if


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete a colon. Delete an indent. Use a tab. Read all three errors.
#   * Set score = 90 exactly, then 89.999, and confirm you get A then B.
#   * Write `if score == 1 or 2:` and work out why it is always true.
#   * Assign a variable in only two of three branches, then use it after the
#     chain with the third branch taken. Note how far the NameError is from
#     the actual mistake.
