"""Day 015 build — an ASCII art generator.

Ten shapes, one idea: for each cell at (row, col), work out the rule that
decides what goes there, THEN write the loop.

Every shape below states its rule in a comment before the code. If you can
write the rule you can write the loop; if you cannot, no amount of fiddling
with the ranges will save you.

    python3 build.py
    python3 build.py 12
"""

import sys

n = 7
if len(sys.argv) >= 2 and sys.argv[1].isdigit():
    n = max(1, min(int(sys.argv[1]), 30))

WIDTH = max(40, 2 * n + 12)


def title(text):
    """Print a section heading."""
    print()
    print("-" * WIDTH)
    print(text)
    print("-" * WIDTH)


# ===========================================================================
title("1. LEFT TRIANGLE     rule: row i has i+1 stars")
# ===========================================================================

for i in range(n):
    print("*" * (i + 1))

# No inner loop. When a row is a simple repeat, `*` IS the inner loop, and it
# is both faster and easier to read.


# ===========================================================================
title("2. RIGHT-ALIGNED     rule: (n-1-i) spaces, then i+1 stars")
# ===========================================================================

for i in range(n):
    print(" " * (n - 1 - i) + "*" * (i + 1))


# ===========================================================================
title("3. INVERTED          rule: i spaces, then (n-i) stars")
# ===========================================================================

for i in range(n):
    print(" " * i + "*" * (n - i))


# ===========================================================================
title("4. PYRAMID           rule: (n-1-i) spaces, then (2i+1) stars")
# ===========================================================================
#
#     row | spaces | stars
#      0  |  n-1   |   1
#      1  |  n-2   |   3
#      i  | n-1-i  | 2i+1
#
# 2i+1 is always ODD, which is why a pyramid always has a single apex and is
# symmetric about its centre. Write this table before the code, every time.

for i in range(n):
    print(" " * (n - 1 - i) + "*" * (2 * i + 1))


# ===========================================================================
title("5. DIAMOND           rule: a pyramid, then a pyramid upside down")
# ===========================================================================
#
# The join is where diamonds go wrong. The widest row must appear EXACTLY
# ONCE, so the lower half runs from n-2 down to 0, not from n-1.

for i in range(n):
    print(" " * (n - 1 - i) + "*" * (2 * i + 1))
for i in range(n - 2, -1, -1):
    print(" " * (n - 1 - i) + "*" * (2 * i + 1))

print(f"  ^ {2 * n - 1} rows tall and {2 * n - 1} wide — always odd, always square")


# ===========================================================================
title("6. HOLLOW SQUARE     rule: fill if row or col is at an edge")
# ===========================================================================

for row in range(n):
    for col in range(n):
        on_edge = row in (0, n - 1) or col in (0, n - 1)
        print("#" if on_edge else " ", end="")
    print()


# ===========================================================================
title("7. HOLLOW DIAMOND    rule: fill only the first and last star of a row")
# ===========================================================================

for i in range(n):
    inner = 2 * i + 1
    row = "*" + " " * (inner - 2) + "*" if inner > 1 else "*"
    print(" " * (n - 1 - i) + row)
for i in range(n - 2, -1, -1):
    inner = 2 * i + 1
    row = "*" + " " * (inner - 2) + "*" if inner > 1 else "*"
    print(" " * (n - 1 - i) + row)


# ===========================================================================
title("8. CHESSBOARD        rule: dark when (row + col) is even")
# ===========================================================================
#
# One expression is the entire board. That single `% 2` is why the colours
# alternate along BOTH axes at once — which is much harder to get right by
# tracking a "current colour" variable and flipping it.

FILES = "abcdefgh"
SQUARE = 2                       # characters per square, to look roughly square

print("   " + "".join(f"{f:^{SQUARE}}" for f in FILES))
for row in range(8):
    rank = 8 - row
    line = f"{rank:>2} "
    for col in range(8):
        line += "#" * SQUARE if (row + col) % 2 == 0 else " " * SQUARE
    print(line + f" {rank}")
print("   " + "".join(f"{f:^{SQUARE}}" for f in FILES))

# a1 is a dark square on a real board. row=7, col=0 -> (7+0) % 2 == 1 -> light
# here, so this board is inverted. Fixing it is one character; finding it is
# the lesson. Check your output against a real board before you trust a rule.


# ===========================================================================
title("9. MULTIPLICATION GRID  rule: cell (r,c) holds r*c, width from n*n")
# ===========================================================================

cell_w = len(str(n * n)) + 1
for r in range(1, n + 1):
    line = ""
    for c in range(1, n + 1):
        line += f"{r * c:>{cell_w}}"
    print(line)


# ===========================================================================
title("10. EVERY UNORDERED PAIR   rule: inner range starts at i+1")
# ===========================================================================

letters = "ABCDEF"[:min(n, 6)]
pairs = 0
line = ""
for i in range(len(letters)):
    for j in range(i + 1, len(letters)):
        line += f"{letters[i]}{letters[j]} "
        pairs += 1
print(line)
print(f"{pairs} pairs from {len(letters)} letters "
      f"= {len(letters)}*{len(letters) - 1}/2")

print()
print("=" * WIDTH)
print(f"{'ten shapes, one idea: state the rule, then loop':^{WIDTH}}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Shape 8 claims a1 should be dark and admits the board is inverted. Fix
#     it. (Hint: change the parity test, not the loops.) Then check a real
#     chessboard image to be sure — a rule that "looks right" is not a rule
#     that IS right.
#
#   * Run with n = 1 and n = 2. Shape 7's hollow diamond has an `if inner > 1`
#     guard specifically for that; delete it and see the row it breaks.
#
#   * Make the diamond hollow AND bordered by a hollow square, in one pass.
#     You will need to combine two rules per cell, which is where "state the
#     rule first" stops being advice and starts being necessary.
#
#   * Draw a sine wave: for each row, put a `*` at a column computed from
#     math.sin(). Same nested loop, entirely different picture — which is the
#     point of separating the rule from the machinery.

