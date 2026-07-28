"""Day 014 — break, continue and loop-else.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. break — leave the loop immediately
# ---------------------------------------------------------------------------

for n in range(2, 1000):
    if 1000 % n == 0:
        print(f"smallest factor of 1000: {n}")
        break

# Without the break that loop performs 998 divisions to answer a question
# settled after one. Nothing after `break` in the body runs, the condition is
# not re-checked, and execution continues after the loop.

# BREAK LEAVES ONLY THE INNERMOST LOOP. This is the one thing about it that
# surprises people, and it matters from tomorrow onwards.


# ---------------------------------------------------------------------------
# 2. continue — skip the rest of THIS pass
# ---------------------------------------------------------------------------

CONFIG = """
# comment line
name = Ada

  # indented comment
role = engineer
"""

for line in CONFIG.splitlines():
    if not line.strip():
        continue                       # blank
    if line.strip().startswith("#"):
        continue                       # comment
    print(f"  setting: {line.strip()}")

# That is Day 11's GUARD CLAUSE, finally with something to leave with.
# Compare the nested version, which does the same job:

print()
for line in CONFIG.splitlines():
    if line.strip():
        if not line.strip().startswith("#"):
            print(f"  nested: {line.strip()}")

# The guard version keeps the real work at ONE level of indentation, and puts
# each rejection reason on its own line where it can be read, changed or
# deleted independently. Past one condition, prefer it.

# THE CLASSIC continue BUG, in a while loop. Do not run this:
#
#     i = 0
#     while i < len(items):
#         if bad(items[i]):
#             continue          # i never increments -> infinite loop
#         i += 1
#
# One more reason to use `for`.


# ---------------------------------------------------------------------------
# 3. for...else — the feature nobody knows
# ---------------------------------------------------------------------------

# The `else` runs ONLY IF THE LOOP FINISHED WITHOUT A BREAK.
# Read it as "nobreak". If it had been spelled that way nobody would ever
# have been confused by it.

print()
for number in (7, 9, 2, 1):
    for divisor in range(2, number):
        if number % divisor == 0:
            print(f"  {number} is divisible by {divisor}")
            break
    else:
        print(f"  {number} is prime (nothing divided it)")

# Note 2: range(2, 2) is EMPTY, so the inner loop runs zero times and goes
# straight to else. For a primality test that is exactly right.
# Note 1: it does the same, and says 1 is prime — which is WRONG, and is
# why the build guards the small cases before it starts looping.


# ---------------------------------------------------------------------------
# 4. The flag variable — the same job, one more moving part
# ---------------------------------------------------------------------------

number = 9

found_factor = False
for divisor in range(2, number):
    if number % divisor == 0:
        found_factor = True
        break

print()
print(f"flag version: {number} prime? {not found_factor}")

# Both are correct. The trade:
#   for...else   one fewer variable, but a reader may not know the feature
#   flag         universally understood, one more thing to keep in sync
#
# Use else when the loop is unmistakably a search. Use a flag when the loop
# also does other work. Comment either one.

# THE CLASSIC FLAG BUG: not resetting it inside an outer loop.
print()
found = False                       # declared too far out
for candidate in (4, 7):
    for divisor in range(2, candidate):
        if candidate % divisor == 0:
            found = True
            break
    print(f"  {candidate}: composite? {found}   <- 7 inherits 4's answer")


# ---------------------------------------------------------------------------
# 5. while...else works the same way
# ---------------------------------------------------------------------------

print()
attempts = 0
MAX = 3
while attempts < MAX:
    attempts += 1
    succeeded = attempts == 5          # never, in three tries
    if succeeded:
        print("  worked")
        break
else:
    print(f"  all {MAX} attempts failed")

# That is a retry loop, and it is the shape you will meet again on Day 66.


# ---------------------------------------------------------------------------
# 6. Why sqrt(n) is the right bound
# ---------------------------------------------------------------------------
#
# If n = a * b, then one of a and b is at most sqrt(n). So any factor ABOVE
# the square root implies a matching factor BELOW it — which the loop would
# already have found. Checking past sqrt(n) can never discover anything new.

n = 36
print()
print(f"factor pairs of {n}:")
for a in range(1, n + 1):
    if n % a == 0:
        b = n // a
        marker = "  <- sqrt is here" * (a == b)
        print(f"  {a:>3} x {b:<3}{marker}")

# Read that list: the pairs mirror around 6. Everything after the middle is
# the first half again, reversed. Stopping at sqrt(n) turns ~1,000,000
# divisions into ~1,000 for a seven-digit number.
#
# THE GENERAL LESSON: the big speedups come from DOING LESS WORK, not from
# doing the same work faster. Day 95 makes this formal.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete the `break` in section 1 and print n each pass. Count the lines.
#   * Move `found = False` inside the outer loop in section 4 and watch the
#     bug disappear.
#   * Change the for...else in section 3 to test 25. Then 49. Perfect squares
#     are where a wrong sqrt bound shows up.
#   * Write a loop with `else` that you EXPECT to break, then make the data
#     such that it does not. Confirm you understand which branch you get.
