"""Day 022 — List comprehensions.

    python3 lesson.py
"""

import sys
import timeit

numbers = [3, -1, 4, -1, 5, 9, -2, 6]
words = ["  Ada ", "CHARLES", "alan  ", "hi"]

# ---------------------------------------------------------------------------
# 1. The map form
# ---------------------------------------------------------------------------

# The four-line shape you have written a dozen times:
squares = []
for n in numbers:
    squares.append(n * n)

# The same thing:
squares = [n * n for n in numbers]
print(squares)

# THE MECHANICAL TRANSLATION, worth doing in your head a few times:
#
#     result = []                     result = [EXPR
#     for VAR in ITERABLE:      ->              for VAR in ITERABLE]
#         result.append(EXPR)
#
# Read it as "n times n, FOR EACH n IN numbers". The expression comes first
# because the RESULT is what you care about.

print([w.strip().lower() for w in words])
print([f"{n:+d}" for n in numbers])


# ---------------------------------------------------------------------------
# 2. The filter form — `if` at the END
# ---------------------------------------------------------------------------

positives = [n for n in numbers if n > 0]
print(f"\nfilter:      {positives}")

# Both together. The filter is written LAST but decides first what gets in:
print(f"expr+filter: {[n * n for n in numbers if n > 0]}")
#                      ^expr        ^source    ^filter


# ---------------------------------------------------------------------------
# 3. if/else at the FRONT — a different thing entirely
# ---------------------------------------------------------------------------

# `if` at the end FILTERS: keeps some items.
dropped = [n for n in numbers if n > 0]

# `if/else` at the front TRANSFORMS: keeps all items, changes some.
clamped = [n if n > 0 else 0 for n in numbers]

print(f"\noriginal: {numbers}")
print(f"filtered: {dropped}   <- {len(dropped)} items")
print(f"clamped:  {clamped}   <- {len(clamped)} items")

# THIS IS THE MOST CONFUSING THING ABOUT COMPREHENSIONS. The front form is a
# ternary expression (Day 11) sitting in the VALUE slot; the back form is a
# filter. They are unrelated features that both use the word `if`.
#
# `[n for n in x if n > 0 else 0]` is a SyntaxError, and now you know why.

# Both at once is legal and usually too clever:
print(f"both:     {[n if n > 3 else 0 for n in numbers if n > 0]}")


# ---------------------------------------------------------------------------
# 4. Nesting — clauses read OUTER to INNER, same order as the loops
# ---------------------------------------------------------------------------

grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flat = []
for row in grid:
    for cell in row:
        flat.append(cell)

print(f"\nflattened: {[cell for row in grid for cell in row]}")
#                            ^outer          ^inner

# Producing nested lists is the CORRECT way to build a grid — Day 21's trap:
rows, cols = 3, 4
good = [[0] * cols for _ in range(rows)]
good[0][0] = 9
print(f"grid built with a comprehension: {good}")

bad = [[0] * cols] * rows
bad[0][0] = 9
print(f"grid built with * :              {bad}   <- one row, three times")

# A multiplication grid, nested both ways:
table = [[r * c for c in range(1, 5)] for r in range(1, 5)]
for row in table:
    print("   " + " ".join(f"{v:>3}" for v in row))


# ---------------------------------------------------------------------------
# 5. The brackets decide what you get
# ---------------------------------------------------------------------------

nums = [1, 2, 2, 3]

print(f"\n[list]      {[n * n for n in nums]}")
print(f"{{set}}       {({n * n for n in nums})}        <- deduplicated (Day 26)")
print(f"{{dict}}      {({n: n * n for n in nums})}  <- (Day 25)")

gen = (n * n for n in nums)
print(f"(generator) {gen}")
print(f"            consumed: {list(gen)}")
print(f"            again:    {list(gen)}   <- empty. It is used up.")

# ROUND BRACKETS DO NOT GIVE A TUPLE. They give a generator: values on
# demand, consumable once. tuple(...) if you actually want a tuple.
print(f"tuple()     {tuple(n * n for n in nums)}")

# Inside a function call the extra brackets can be dropped:
print(f"sum():      {sum(n * n for n in nums)}")
print(f"any():      {any(n < 0 for n in nums)}")


# ---------------------------------------------------------------------------
# 6. Memory: where the choice actually matters
# ---------------------------------------------------------------------------

N = 1_000_000
as_list = [n for n in range(N)]
as_gen = (n for n in range(N))

print(f"\nlist of {N:,}:      {sys.getsizeof(as_list):>12,} bytes")
print(f"generator over {N:,}: {sys.getsizeof(as_gen):>12,} bytes")
print("Same values. The generator never holds them all at once, which is")
print("what makes Day 38's 500 MB log file possible.")
del as_list


# ---------------------------------------------------------------------------
# 7. Speed: real, and a poor reason to choose
# ---------------------------------------------------------------------------

setup = "data = list(range(10000))"
loop = """
out = []
for n in data:
    out.append(n * n)
"""
comp = "out = [n * n for n in data]"

loop_time = timeit.timeit(loop, setup, number=200)
comp_time = timeit.timeit(comp, setup, number=200)

print(f"\n{'explicit loop':<20}{loop_time:>10.4f}s")
print(f"{'comprehension':<20}{comp_time:>10.4f}s")
print(f"{'speedup':<20}{loop_time / comp_time:>10.2f}x")
print("Real, because the append happens in C rather than through a method")
print("lookup on every pass. Still choose on READABILITY; take this free.")


# ---------------------------------------------------------------------------
# 8. When a loop reads better
# ---------------------------------------------------------------------------
#
#   * THE BODY DOES MORE THAN ONE THING. A comprehension produces a value.
#     If you also print, log, or update a counter — loop.
#
#   * YOU NEED break. Comprehensions cannot.
#     next(x for x in items if match(x)) is the equivalent for "first match".
#
#   * MORE THAN TWO CLAUSES. [x for a in b for c in d if e if f] is a puzzle.
#
#   * THE EXPRESSION DOES NOT FIT ON A LINE. Two wrapped lines of
#     comprehension are harder than four of loop.
#
#   * YOU WANT THE SIDE EFFECT. This builds a list of Nones and bins it:
#         [print(x) for x in items]      # never do this
#
# THE HONEST TEST: if you had to read it twice, write the loop.

first_negative = next((n for n in numbers if n < 0), None)
print(f"\nfirst negative (the `break` equivalent): {first_negative}")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write [n for n in nums if n > 0 else 0] and read the SyntaxError.
#   * Print a generator, then list() it twice.
#   * Flatten a three-deep list with a comprehension, then with a loop, and
#     decide which you would rather come back to.
#   * Write [print(x) for x in "abc"] and look at what it returns.
