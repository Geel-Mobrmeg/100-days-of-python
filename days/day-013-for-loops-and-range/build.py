"""Day 013 build — a multiplication table that lines up at any size.

    python3 build.py            # 12 x 12
    python3 build.py 20         # 20 x 20
    python3 build.py 15 7       # 15 rows, 7 columns

The requirement is "lines up PERFECTLY for any size you ask for", and that
one word is the whole exercise. A table hard-coded to width 4 looks fine at
12x12 and falls apart at 25x25, where products reach 625 and the header
still reserves three characters.

So: measure the widest thing that will be printed, and derive every width
from that. Never type a column width. This is Day 1's frame-that-fits idea,
at the size where getting it wrong actually shows.
"""

import sys

# ---------------------------------------------------------------------------
# Arguments. sys.argv is the list of words after `python3` — argv[0] is the
# script name. Day 63 replaces this with argparse; this is the crude version.
# ---------------------------------------------------------------------------

rows = 12
cols = 12

if len(sys.argv) >= 2 and sys.argv[1].isdigit():
    rows = int(sys.argv[1])
    cols = rows
if len(sys.argv) >= 3 and sys.argv[2].isdigit():
    cols = int(sys.argv[2])

rows = max(1, min(rows, 40))
cols = max(1, min(cols, 40))

# ---------------------------------------------------------------------------
# THE MEASUREMENT. Everything below is derived from these two numbers, so
# nothing can drift out of alignment.
# ---------------------------------------------------------------------------

largest_product = rows * cols
cell_w = len(str(largest_product)) + 1        # +1 for one space of gutter
label_w = len(str(max(rows, cols))) + 1       # the row-header column

grid_w = label_w + 2 + cell_w * cols          # 2 for the " |" separator

title = f"{rows} x {cols} MULTIPLICATION TABLE"

# The title is a thing that gets printed, so it counts. At 3x3 the grid is
# ten characters wide and the title is twenty-six, and a rule measured only
# from the grid would be shorter than the heading it underlines. Format specs
# pad, they never truncate — so the widest item has to win.
table_w = max(grid_w, len(title))

# When the title is the wider of the two, the grid gets indented so it sits
# centred under it rather than hugging the left edge of a much longer rule.
pad = " " * ((table_w - grid_w) // 2)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

print()
print(f"{title:^{table_w}}")
print("=" * table_w)

header = pad + f"{'x':>{label_w}} |"
for c in range(1, cols + 1):
    header += f"{c:>{cell_w}}"
print(header)

print(pad + "-" * label_w + "-+" + "-" * (cell_w * cols))

# ---------------------------------------------------------------------------
# Body. One row per multiplicand; one cell per multiplier.
# ---------------------------------------------------------------------------

for r in range(1, rows + 1):
    line = pad + f"{r:>{label_w}} |"
    for c in range(1, cols + 1):
        line += f"{r * c:>{cell_w}}"
    print(line)

print("=" * table_w)
print(f"widest product {largest_product}, so every cell is {cell_w} wide")
print()

# ===========================================================================
# The same data, three other shapes — each one is a different loop, and the
# table above is only one way to look at the numbers.
# ===========================================================================

# --- 1. A single row, the classic "n times table" -------------------------

n = min(7, rows)
print(f"THE {n} TIMES TABLE")
print("-" * 34)
for c in range(1, min(cols, 12) + 1):
    print(f"  {n:>2} x {c:>2} = {n * c:>4}")
print()

# --- 2. Only the even multiples, by changing the range and nothing else ----

print(f"THE {n} TIMES TABLE, EVENS ONLY")
print("-" * 34)
for c in range(2, min(cols, 12) + 1, 2):
    print(f"  {n:>2} x {c:>2} = {n * c:>4}")
print()

# --- 3. Backwards, by using a negative step -------------------------------

print(f"THE {n} TIMES TABLE, BACKWARDS")
print("-" * 34)
for c in range(min(cols, 12), 0, -1):
    print(f"  {n:>2} x {c:>2} = {n * c:>4}")
print()

# --- 4. The triangle: skip the duplicates ---------------------------------
#
# 3 x 7 and 7 x 3 are the same fact. Starting the inner range at the outer
# index prints each fact once — 78 cells instead of 144 for a 12x12 table.

print("EACH FACT ONCE (upper triangle)")
print("=" * table_w)
shown = 0
for r in range(1, rows + 1):
    line = f"{r:>{label_w}} |"
    line += " " * (cell_w * (r - 1))
    for c in range(r, cols + 1):
        line += f"{r * c:>{cell_w}}"
        shown += 1
    print(line)
print("=" * table_w)
print(f"{shown} facts instead of {rows * cols} — the rest are the same ones twice")
print()

# --- 5. Squares, using zip to walk two sequences together -----------------

print("SQUARES AND THEIR DIFFERENCES")
print("-" * 46)
sides = range(1, min(rows, 12) + 1)
squares = [s * s for s in sides]
print(f"{'n':>4}{'n^2':>8}{'gap':>8}   {'':<20}")
previous = 0
for side, square in zip(sides, squares):
    gap = square - previous
    bar = "#" * side
    print(f"{side:>4}{square:>8}{gap:>8}   {bar:<20}")
    previous = square
print("-" * 46)
print("the gaps are the odd numbers — that is why squares are what they are")
print()


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 build.py 25`. Every column must still line up: products
#     reach 625 and cell_w becomes 4 on its own. Then hard-code cell_w = 4
#     and run it at 40 to see what the requirement was protecting you from.
#
#   * Run `python3 build.py 1` and `python3 build.py 1 1`. Degenerate sizes
#     should produce a degenerate table, not a crash and not a blank.
#
#   * Add a blank line every 5 rows to make the table easier to scan. You
#     have % from Day 5, and `if r % 5 == 0` from Day 11.
#
#   * Highlight the perfect squares down the diagonal — they are the cells
#     where r == c.
#
#   * The nested loop building each line with += is the string-concatenation
#     pattern Day 4 warned about. Rewrite the body using a list and
#     "".join(), and measure whether it matters at this size. (It does not.
#     Knowing WHEN a rule stops mattering is as useful as the rule.)
