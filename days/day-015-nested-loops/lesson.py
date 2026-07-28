"""Day 015 — Nested loops.

    python3 lesson.py
"""

import time

# ---------------------------------------------------------------------------
# 1. The shape
# ---------------------------------------------------------------------------

for row in range(3):
    for col in range(4):
        print(f"({row},{col})", end=" ")
    print()                     # END OF ROW — outer loop's indentation

# The inner loop runs COMPLETELY for each single pass of the outer one.
# 3 rows x 4 columns = 12 passes of the inner body.
#
# The print() is where everyone slips once:
#   * indented one more  -> a newline after every CELL
#   * deleted            -> the whole grid on one line
# It belongs to the OUTER loop: one newline per row, after the columns.

print()

# ---------------------------------------------------------------------------
# 2. Row and column thinking
# ---------------------------------------------------------------------------
#
# For a cell at (row, col): WHAT DECIDES WHAT GOES THERE?
# Answer that first, in words, then write the loop. Do not write the loop and
# fiddle until it looks right — that produces code you cannot modify.

# A chessboard: a square is dark when (row + col) is even. One expression is
# the entire board, and it is why the colours alternate on both axes at once.
for row in range(8):
    for col in range(8):
        print("##" if (row + col) % 2 == 0 else "  ", end="")
    print()

print()

# ---------------------------------------------------------------------------
# 3. When the inner loop is not needed at all
# ---------------------------------------------------------------------------

n = 5

# Row i has i+1 stars. String repetition does the inner loop's job:
for i in range(n):
    print("*" * (i + 1))

print()

# The same shape written with a real inner loop — more code, slower, and no
# clearer. Use the inner loop when the cells DIFFER from each other; use *
# when a row is a simple repeat.
for i in range(n):
    for _ in range(i + 1):
        print("*", end="")
    print()

print()

# A centred pyramid needs TWO things per row. Write the table first:
#
#     row | spaces | stars
#      0  |  n-1   |   1
#      1  |  n-2   |   3
#      2  |  n-3   |   5
#      i  | n-1-i  | 2i+1
#
# Every pyramid bug is a wrong entry in that table, and the table takes
# thirty seconds to write.
for i in range(n):
    print(" " * (n - 1 - i) + "*" * (2 * i + 1))

print()

# ---------------------------------------------------------------------------
# 4. Inner ranges that depend on the outer variable
# ---------------------------------------------------------------------------

letters = "ABCDE"

# Every UNORDERED pair, exactly once. range(i + 1, n) is the idiom, and it
# comes up constantly: comparing all items with all others, finding
# duplicates, computing distances.
pairs = 0
for i in range(len(letters)):
    for j in range(i + 1, len(letters)):
        print(f"{letters[i]}{letters[j]}", end=" ")
        pairs += 1
print(f"\n{pairs} pairs from {len(letters)} letters")

print()

# ---------------------------------------------------------------------------
# 5. break leaves only the INNERMOST loop
# ---------------------------------------------------------------------------

GRID = ["....", ".#..", "...."]
target = "#"

# WRONG — this break leaves the inner loop, and the outer one carries on:
for r, line in enumerate(GRID):
    for c, cell in enumerate(line):
        if cell == target:
            print(f"  naive break: found at ({r},{c})")
            break
    # ... and we are still going round the outer loop

# FIX 1 — a flag. Always works, everybody understands it.
found_at = None
for r, line in enumerate(GRID):
    for c, cell in enumerate(line):
        if cell == target:
            found_at = (r, c)
            break
    if found_at:
        break
print(f"  flag:        found at {found_at}")

# FIX 2 — for...else (Day 14). Neat, and slightly too clever.
for r, line in enumerate(GRID):
    for c, cell in enumerate(line):
        if cell == target:
            break
    else:
        continue        # inner finished with NO break -> go to the next row
    break               # inner DID break -> leave the outer loop too
print(f"  for/else:    found at ({r},{c})")

# FIX 3 — put it in a function and `return` (Day 31). This is the right
# answer, and you should come back and rewrite any two-level search after
# you have met it.

print()

# ---------------------------------------------------------------------------
# 6. The cost — measured, not asserted
# ---------------------------------------------------------------------------

print(f"{'n':>8}{'operations':>14}{'seconds':>10}{'vs previous':>13}")
print("-" * 46)
previous = None
for size in (100, 500, 1000, 2000):
    start = time.perf_counter()
    count = 0
    for i in range(size):
        for j in range(size):
            count += 1
    elapsed = time.perf_counter() - start
    ratio = f"{elapsed / previous:.1f}x" if previous else "-"
    print(f"{size:>8}{count:>14,}{elapsed:>10.3f}{ratio:>13}")
    previous = elapsed

print("-" * 46)
print("Doubling n roughly QUADRUPLES the time. That is O(n^2), and it is why")
print("a nested loop over 100,000 items is 17 minutes rather than 2 seconds.")
print()
print("The dangerous version is the one you cannot see: `if x in some_list`")
print("inside a loop is a nested loop, because `in` on a list scans it.")
print("Day 26's set turns that scan into a single step.")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Move the row-end print() inside the inner loop, then delete it.
#   * Use `for i` inside `for i` and watch the inner one clobber the outer.
#   * Change the pyramid to (n - i) spaces and see which row goes wrong.
#   * Add size 4000 to the timing loop and predict the time before running it.
