"""Day 007 — Booleans and comparison.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. Comparison
# ---------------------------------------------------------------------------

print(5 == 5, 5 != 4, 5 < 6, 5 <= 5, 5 > 6, 5 >= 6)

# = assigns, == compares. Python makes the confusion a SyntaxError rather than
# a silent bug, which is more than C manages:
#   if x = 5:      <- SyntaxError

# Strings compare by Unicode code point, so ALL uppercase sorts before ALL
# lowercase. This surprises people the first time they sort names:
print("a" < "b")        # True
print("Z" < "a")        # True   <- capital Z is 90, lowercase a is 97
print("apple" < "banana")
print("Apple" < "apple")

# For human-facing comparison, normalise first:
print("ADA".lower() == "ada")     # True

# Different types: == is fine and says False. < is an error.
print(5 == "5")         # False — no exception, just not equal
# print(5 < "6")        # TypeError


# ---------------------------------------------------------------------------
# 2. Chained comparison — Python reads this as maths does
# ---------------------------------------------------------------------------

bmi = 22.4
print(18.5 <= bmi < 25)            # one range test, evaluated once

age = 30
print(0 < age < 150)               # a plausibility check in six characters
print(1 <= 5 <= 10 != 11)          # chains can be as long as you can read

# In C or JavaScript, a < b < c compares (a < b) to c, which is nonsense that
# runs. Python is one of the few languages that does the obvious thing.


# ---------------------------------------------------------------------------
# 3. Truthiness — the whole falsy list, and it is short
# ---------------------------------------------------------------------------

print(bool(False), bool(None))
print(bool(0), bool(0.0))
print(bool(""), bool([]), bool(()), bool({}), bool(set()))
# ^ every one of those is False. Everything else in Python is True.

# Including all of these, which catch people out:
print(bool("0"), bool("False"), bool(" "), bool([0]), bool(-1))
# ^ every one True. A non-empty string is truthy whatever is inside it.

items = ["a", "b"]
print(bool(items))              # True

# Which is why Python conditions read like English. Prefer the first form:
#   if items:              "if there are any items"
#   if len(items) > 0:     same result, more machinery
#   if items != []:        same again, worse

# THE EXCEPTION. When 0 is a real value, truthiness conflates "empty" with
# "absent", and that is a whole family of bugs:
count = 0
print("truthiness says:", bool(count))          # False — but 0 IS the answer
print("explicit says: ", count is not None)     # True  — what you meant


# ---------------------------------------------------------------------------
# 4. and / or DO NOT RETURN BOOLEANS. They return an operand.
# ---------------------------------------------------------------------------

#   a and b  ->  a if a is falsy, else b
#   a or  b  ->  a if a is truthy, else b

print("" or "default")          # 'default'  <- Day 6's fallback, explained
print(0 or 42)                  # 42
print("Ada" or "default")       # 'Ada'
print("Ada" and "Byron")        # 'Byron'
print("" and "Byron")           # ''         <- not False!
print(None or 0 or "" or "last truthy wins")

# In a condition this never matters — the result gets tested for truthiness
# either way. In an assignment it is a feature:
user_supplied = ""
name = user_supplied or "Anonymous"
print(name)

# `not` DOES always return a real bool:
print(not "Ada", not "", not 0, not None)     # False True True True


# ---------------------------------------------------------------------------
# 5. Short-circuiting — a control-flow feature wearing an operator's clothes
# ---------------------------------------------------------------------------

# `False and X` never evaluates X. `True or X` never evaluates X.
# This is a GUARANTEE, not an optimisation, and you are meant to lean on it.

count = 0
total = 100

# The guard and the guarded thing, in one expression. No division happens:
print(count > 0 and total / count > 10)        # False, no ZeroDivisionError

# Reverse it and you get the exception. Uncomment to confirm:
# print(total / count > 10 and count > 0)      # ZeroDivisionError

text = ""
print(text and text[0] == "#")                 # '' — no IndexError
# print(text[0] == "#" and text)               # IndexError

# RULE: put the cheap, protective test on the LEFT.

# Precedence, loosest to tightest: or , and , not , comparisons.
print(True or False and False)      # True  — reads as True or (False and False)
print((True or False) and False)    # False — parenthesise when it matters


# ---------------------------------------------------------------------------
# 6. == vs. is
# ---------------------------------------------------------------------------

a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)     # True  — equal contents
print(a is b)     # False — two separate list objects
print(a is c)     # True  — one object, two names (Day 2's labels)

# Use `is` for EXACTLY three things: None, True, False.
value = None
print(value is None)          # correct
print(value is not None)      # correct

# Why it matters: Python caches small ints and short strings, so `is` can
# appear to work on values and then stop working on bigger ones.
x = 256
y = 256
print("256 is 256:", x is y)          # True  — cached

x = 257
y = 257
print("257 is 257:", x is y)          # usually False — not cached

# A test that passes for 256 and fails for 257 is a horrible bug to find.
# Modern Python emits a SyntaxWarning for `is` against a literal. Listen to it.


# ---------------------------------------------------------------------------
# 7. Bools are ints, and the two builtins that collapse them
# ---------------------------------------------------------------------------

rule_a = True
rule_b = False
rule_c = True

print("passed:", rule_a + rule_b + rule_c)     # 2 — bools add up (Day 2)

print(all([rule_a, rule_b, rule_c]))           # False — every one must be truthy
print(any([rule_a, rule_b, rule_c]))           # True  — at least one is

# Both short-circuit, like `and` and `or`.
# The empty cases look arbitrary and are the only consistent choice:
print(all([]), any([]))                        # True False


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Predict the VALUE, not the truthiness: "" or 0 , 0 or "" , "a" and 0 ,
#     [] or {} or "last". Then check all four.
#   * Write `x == 1 or 2` and work out why it is always True. Then fix it two
#     ways, one of which uses `in`.
#   * Build a condition that safely tests the first character of a possibly
#     empty string. Then write the crashing version and confirm it crashes.
#   * Try `if x == True` where x = "Ada". Explain the result to yourself.
