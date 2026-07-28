"""Day 008 — Style, comments and PEP 8.

Every convention as a before/after pair. The "before" lines are all in
comments, because several of them would fail the linter this file is meant to
pass — which is itself the point.

    python3 lesson.py
    ruff check --isolated --select E,F,W,N,UP,C4,SIM,B lesson.py
"""

# ---------------------------------------------------------------------------
# 1. Naming
# ---------------------------------------------------------------------------

# BEFORE:  l = 70.5        <- l, O and I are BANNED by PEP 8: in most fonts
#          O = 0              they are indistinguishable from 1, 0 and 1.
#          I = 1
# AFTER:
weight_kg = 70.5

# BEFORE:  h = 1.75        <- what unit? metres? feet? hands?
# AFTER:   the unit lives in the name, and a whole class of bug disappears
height_m = 1.75

# BEFORE:  NAME = "Ada"    <- SHOUTING means "constant", and this is not one
#          Email = "..."   <- CapWords means "class"
# AFTER:   one scheme, lower_snake_case, spelled out
name = "Ada"
email = "ada@example.com"

# Constants really are SHOUTED, and that is how a reader tells them apart:
MAX_RETRIES = 3
LB_PER_KG = 2.20462

print(f"{name} <{email}>  {weight_kg}kg  {height_m}m")


# ---------------------------------------------------------------------------
# 2. Whitespace
# ---------------------------------------------------------------------------

a = 10
b = 3

# BEFORE:  x=a+b
# AFTER:   spaces around binary operators
x = a + b

# BEFORE:  print( "hi" , x )
# AFTER:   no space inside brackets, one after each comma
print("hi", x)

# The one exception, which black does and which looks wrong for a day:
# around a HIGHER-priority operator you may drop the spaces to show grouping.
bmi = weight_kg / height_m**2
print(f"{bmi:.1f}")


# ---------------------------------------------------------------------------
# 3. Line length, and how to break a long line
# ---------------------------------------------------------------------------

# BEFORE (scrolls off the screen, and hides its own structure while doing it).
# The line below is deliberately over the limit, so it carries the suppression
# that section 8 talks about — with the rule named and a reason given:
#   print("BMI: "+str(round(bmi,1))+"  (under="+str(bmi<18.5)+" healthy="+str(bmi>=18.5 and bmi<25)+")")  # noqa: E501 - the exhibit

# AFTER: adjacent string literals are concatenated by the parser, so wrapping
# an f-string across lines costs nothing and needs no + at all.
print(
    f"BMI: {bmi:.1f}  "
    f"(under={bmi < 18.5} "
    f"healthy={18.5 <= bmi < 25} "
    f"over={bmi >= 25})"
)

# For a long boolean, put the operators at the START of each line — a reader
# scanning the left edge can see the structure without reading the values.
is_plausible = (
    0 < weight_kg < 500
    and 0 < height_m < 3
    and 10 < bmi < 60
)
print("plausible:", is_plausible)


# ---------------------------------------------------------------------------
# 4. Comments: why, not what
# ---------------------------------------------------------------------------

# BEFORE:  bmi_rounded = round(bmi, 1)   # round bmi to 1 place
#          ^ worthless. It restates the code, and it is now a second thing to
#            keep in sync when the code changes.

# AFTER: either say something the code cannot, or say nothing.
# WHO recommends one decimal place; two implies a precision scales do not have.
bmi_rounded = round(bmi, 1)
print(bmi_rounded)

# Best of all, replace the comment with a name. This needs no comment:
is_underweight = bmi < 18.5
print(is_underweight)

# Commented-out code should be DELETED, not left. Git remembers it (Day 69);
# a reader cannot tell whether it is a spare part or a landmine.


# ---------------------------------------------------------------------------
# 5. Docstrings are not comments
# ---------------------------------------------------------------------------

# A docstring is the first STATEMENT in a module, function or class. It is
# stored on the object; a comment is discarded by the parser. This file has
# one at the top — that is why help() and __doc__ can find it:

print(__doc__.splitlines()[0])

# Triple quotes even for one line, imperative mood, ends with a full stop.
# Day 31 covers function docstrings, where they earn their keep.


# ---------------------------------------------------------------------------
# 6. Imports
# ---------------------------------------------------------------------------

# BEFORE:  import math, json          <- one line, two modules
#          from decimal import *      <- ~40 unknown names into your namespace
#          import os                  <- never used
#
# AFTER:   one per line, at the top of the file, grouped
#            1. standard library
#            2. third party
#            3. your own
#          with a blank line between the groups, and NOTHING imported that is
#          not used. `ruff` catches all four of those mistakes.


# ---------------------------------------------------------------------------
# 7. Comparisons — the ones the linter flags
# ---------------------------------------------------------------------------

has_at = "@" in email

# BEFORE:  if has_at == True        <- E712
# AFTER:
print(has_at)

# BEFORE:  if bmi >= 18.5 and bmi < 25
# AFTER:   Day 7's chained comparison
print(18.5 <= bmi < 25)

# BEFORE:  if len(name) > 0
# AFTER:   Day 7's truthiness
print(bool(name))


# ---------------------------------------------------------------------------
# 8. Silencing the linter honestly
# ---------------------------------------------------------------------------

# When the linter is wrong, silence THAT RULE on THAT LINE, with a reason:
#
#     import config    <hash> noqa: F401  — imported for its side effect
#
# Always name the rule code. A bare suppression with no code and no reason
# switches off EVERY rule on that line, forever, and is how a codebase goes
# quiet and stays broken.
#
# (Written as <hash> above so that ruff does not read this comment as a real
#  directive — which it did, the first time this file was written.)


# ---------------------------------------------------------------------------
# Now do it
# ---------------------------------------------------------------------------
#
#   * Run:  ruff check --isolated --select E,F,W,N,UP,C4,SIM,B ugly.py
#     Thirteen errors. Fix them by hand, keeping the output identical.
#   * Run `ruff check --fix` on a COPY of ugly.py. Count how many it fixes
#     alone, then work out why it will not touch the rest. (Hint: renaming a
#     variable can change behaviour; deleting a space cannot.)
#   * Run `black --diff ugly.py` and note everything it changes that ruff
#     never mentioned. Formatting and linting are different jobs.
