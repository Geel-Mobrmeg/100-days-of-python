"""Day 013 — for loops and range.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. for iterates over THINGS, not numbers
# ---------------------------------------------------------------------------

for letter in "Ada":
    print(letter, end=" ")
print()

for part in "Ada Augusta Byron".split():
    print(part, end=" | ")
print()

# No index, no counter, no bound. The loop asks the thing for its next item
# until it runs out. Anything that can do that is ITERABLE: strings, lists,
# tuples, dicts, sets, files, ranges.

# Yesterday's version of the same job:
#
#     i = 0
#     while i < len(parts):
#         part = parts[i]
#         print(part)
#         i += 1
#
# Four lines of bookkeeping, three chances for an off-by-one, none of which
# was about the job. If you write that, you have written a `for` loop badly.


# ---------------------------------------------------------------------------
# 2. range() — when you really do want numbers
# ---------------------------------------------------------------------------

print(list(range(5)))            # [0, 1, 2, 3, 4]        stop only
print(list(range(1, 6)))         # [1, 2, 3, 4, 5]        start, stop
print(list(range(0, 10, 2)))     # [0, 2, 4, 6, 8]        start, stop, step
print(list(range(10, 0, -1)))    # [10, 9, ... 1]         counting down
print(list(range(5, 1)))         # []  <- no negative step, so nothing at all

# STOP IS EXCLUDED, exactly as in slicing (Day 3), and for the same payoff:
#   range(n)      produces exactly n values
#   range(a, b)   produces exactly b - a values
print(len(range(0, 10)), "values in range(0, 10)")

# range is LAZY — it computes values as asked, it does not build a list:
print(range(5))                  # range(0, 5), not the numbers
big = range(1_000_000_000)       # instant, and uses no memory
print(f"a billion values, {big[999_999_999]} is the last one")

# "do this three times" — the underscore means "deliberately unused"
for _ in range(3):
    print("tick", end=" ")
print()


# ---------------------------------------------------------------------------
# 3. enumerate() — index AND item
# ---------------------------------------------------------------------------

items = ["flour", "sugar", "eggs"]

# The commonest beginner smell in Python:
#     for i in range(len(items)):
#         print(i, items[i])

for i, item in enumerate(items):
    print(f"  {i}: {item}")

# start=1 whenever a human will read the number. Nobody wants "Question 0".
for n, item in enumerate(items, start=1):
    print(f"  {n}. {item}")

# The `i, item` on the for line is TUPLE UNPACKING — enumerate yields pairs
# and the loop splits each one into two names. Day 23 covers it properly.
print(list(enumerate(items, start=1)))


# ---------------------------------------------------------------------------
# 4. zip() — walk two sequences together
# ---------------------------------------------------------------------------

names = ["Ada", "Charles", "Alan"]
scores = [95, 87, 92]

for name, score in zip(names, scores):
    print(f"  {name:<10}{score:>4}")

# zip STOPS AT THE SHORTEST, silently. Usually what you want; occasionally a
# data-loss bug that nothing reports.
short = ["Ada", "Charles"]
print(list(zip(short, scores)))          # Alan's 92 vanished without a word

# strict=True (3.10+) raises instead, and is the better default when you
# believe the lengths match:
#     list(zip(short, scores, strict=True))    # ValueError

# enumerate and zip compose:
for n, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"  {n}. {name}: {score}")


# ---------------------------------------------------------------------------
# 5. Never modify what you are iterating over
# ---------------------------------------------------------------------------

numbers = [1, 2, 2, 3, 2, 4]

broken = [1, 2, 2, 3, 2, 4]
for value in broken:
    if value == 2:
        broken.remove(value)
print(f"tried to remove every 2, got: {broken}")     # a 2 survives

# No error. Wrong answer. The loop tracks a position; removing an item shifts
# everything after it down, so the next item is skipped.

# Build a new collection instead (Day 22's comprehension):
kept = [value for value in numbers if value != 2]
print(f"the right way:                 {kept}")


# ---------------------------------------------------------------------------
# 6. The loop variable survives the loop
# ---------------------------------------------------------------------------

for n in range(3):
    pass
print(f"after the loop, n is still {n}")

# Occasionally useful, usually a bug — and it does not exist at all if the
# loop ran zero times, which is a NameError far from its cause.


# ---------------------------------------------------------------------------
# 7. Day 10's quiz, collapsed
# ---------------------------------------------------------------------------
#
# This is the payoff. Day 10 spent ~60 lines on ten questions because it had
# no loop. Here is the whole scoring half of it, for any number of questions:

QUIZ = [
    ("What type does input() always return?", "str|string"),
    ("Which operator gives the remainder?", "%|modulo|mod"),
    ("What is 2 ** 3 ** 2?", "512"),
]
ANSWERS = ["str", "mod", "64"]          # pretending these were typed

print()
score = 0
for n, ((question, accepted), given) in enumerate(zip(QUIZ, ANSWERS), start=1):
    ok = given.strip().lower() in accepted.split("|")
    score += ok
    print(f"  {n}. [{'v' if ok else 'x'}] {question}")
    if not ok:
        print(f"        you said {given!r}, accepted: {accepted}")
print(f"  score: {score}/{len(QUIZ)}")

# Ten questions would be ten lines of DATA and not one more line of CODE.
# That is the whole argument for loops, and it is why the quiz is a milestone
# on Day 10 and not on Day 14.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Print range(1, 10, 3) and predict the last value before you look.
#   * Write `for i in range(len(items))` and then convert it to enumerate.
#   * Make `names` and `scores` different lengths and find the lost row.
#     Then add strict=True and read the exception.
#   * Use the loop variable after a loop that ran zero times.
