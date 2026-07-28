"""Day 018 — Loop patterns worth knowing.

    python3 lesson.py
"""

NUMBERS = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

# ---------------------------------------------------------------------------
# 1. THE ACCUMULATOR — collect something across every item
# ---------------------------------------------------------------------------

total = 0                     # 0 means "nothing yet" for a sum
for n in NUMBERS:
    total += n
print(f"sum:      {total}")

product = 1                   # 1 means "nothing yet" for a product
for n in NUMBERS[:4]:
    product *= n
print(f"product:  {product}")

count = 0                     # counting is an accumulator too
for n in NUMBERS:
    count += 1
print(f"count:    {count}")

# Building a string: collect into a LIST, then join. Never += in a loop —
# each + copies the whole string, so the cost grows quadratically (Day 4).
pieces = []
for n in NUMBERS[:5]:
    pieces.append(str(n))
print(f"joined:   {'-'.join(pieces)}")


# ---------------------------------------------------------------------------
# 2. RUNNING MIN / MAX — an accumulator whose step is a comparison
# ---------------------------------------------------------------------------

# The INITIALISATION is the whole difficulty:
#
#   0               WRONG for min — nothing positive ever beats it
#   float("inf")    correct, neat, and silently returns inf on empty input
#   numbers[0]      correct, and raises IndexError on empty input — usually
#                   what you want, because "the minimum of nothing" is an
#                   error, not a value
#   None            correct, needs an `is None` test inside the loop

lowest = NUMBERS[0]
highest = NUMBERS[0]
for n in NUMBERS[1:]:
    if n < lowest:
        lowest = n
    if n > highest:
        highest = n
print(f"\nlowest {lowest}, highest {highest}")

# Watch the wrong one fail:
wrong = 0
for n in NUMBERS:
    if n < wrong:
        wrong = n
print(f"with lowest = 0 you get {wrong}, which is not in the data at all")

# TRACK THE POSITION when you need to know WHICH item won:
TIES = [3, 1, 3]

first_max = 0
for i, n in enumerate(TIES):
    if n > TIES[first_max]:      # > keeps the FIRST maximum
        first_max = i

last_max = 0
for i, n in enumerate(TIES):
    if n >= TIES[last_max]:      # >= keeps the LAST maximum
        last_max = i

print(f"\n{TIES}: first max at index {first_max}, last max at index {last_max}")
print("> vs >= is a real decision, not a detail. It shows up the moment")
print("there are ties, and it is silent until then.")


# ---------------------------------------------------------------------------
# 3. SEARCH-AND-FLAG / EARLY EXIT
# ---------------------------------------------------------------------------

found = False
for n in NUMBERS:
    if n > 8:
        found = True
        break
print(f"\nflag version:  any value over 8? {found}")

# any() and all() do exactly this, short-circuit exactly the same way, and
# are one line. If your search loop's body is a single condition, use them.
print(f"any():         {any(n > 8 for n in NUMBERS)}")
print(f"all():         {all(n > 0 for n in NUMBERS)}")


# ---------------------------------------------------------------------------
# 4. PAIRWISE — compare each item with its neighbour
# ---------------------------------------------------------------------------

# For changes, runs, and sortedness.
sorted_so_far = True
for i in range(1, len(NUMBERS)):
    if NUMBERS[i] < NUMBERS[i - 1]:
        sorted_so_far = False
        break
print(f"\nis it sorted? {sorted_so_far}")

# The longest run of identical values — pairwise plus two accumulators:
RUNS = [1, 1, 2, 2, 2, 2, 3, 1, 1]
longest = 1
current = 1
for i in range(1, len(RUNS)):
    if RUNS[i] == RUNS[i - 1]:
        current += 1
        if current > longest:
            longest = current
    else:
        current = 1
print(f"longest run in {RUNS}: {longest}")

# zip(items, items[1:]) is the neat version of the same idea:
print(f"neater:       {[(a, b) for a, b in zip(RUNS, RUNS[1:])][:4]} ...")


# ---------------------------------------------------------------------------
# 5. SINGLE-PASS THINKING — the idea that separates today from Day 13
# ---------------------------------------------------------------------------

# FIVE statistics, ONE traversal:
count = 0
total = 0
lowest = NUMBERS[0]
highest = NUMBERS[0]
for n in NUMBERS:
    count += 1
    total += n
    if n < lowest:
        lowest = n
    if n > highest:
        highest = n
mean = total / count
print(f"\none pass:  n={count} sum={total} min={lowest} max={highest} "
      f"mean={mean:.3f}")

# FOUR traversals, and clearer to read:
print(f"four passes: n={len(NUMBERS)} sum={sum(NUMBERS)} "
      f"min={min(NUMBERS)} max={max(NUMBERS)} "
      f"mean={sum(NUMBERS) / len(NUMBERS):.3f}")

# For a list in memory, USE THE BUILTINS. Four passes over a million items
# is nothing, and the builtin version is obviously correct.
#
# Single-pass thinking matters enormously in exactly two situations:
#
#   * THE DATA DOES NOT FIT IN MEMORY. A 500 MB log (Day 38) can be
#     traversed once but not held. Anything needing two passes needs a
#     different design.
#
#   * THE DATA ARRIVES ONCE. A network stream, a sensor, a generator.
#     There is no "start again".
#
# So the question to internalise is: WHAT CAN I COMPUTE WHILE THE DATA GOES
# PAST EXACTLY ONCE?
#
#   mean       yes — running count and running total
#   min, max   yes — running extrema
#   median     NO  — you cannot know the middle value until you have seen
#                    every value. It needs the whole dataset, sorted.
#
# That asymmetry is why today's build separates them, and it is a real
# constraint in real systems, not a puzzle.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Set NUMBERS = [] and run this file. Note which line fails first, and
#     decide what SHOULD happen for each statistic.
#   * Change `if n > TIES[first_max]` to >= and watch the reported index move.
#   * Detect sortedness without break, and count how many extra comparisons
#     you performed on a list that fails at index 1.
#   * Compute a running mean without keeping a total: mean += (n - mean)/count.
#     Compare it to the plain version on a million values and think about why
#     anyone would bother.
