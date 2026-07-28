"""Day 001 build — a name in an ASCII frame that draws itself to fit.

The point of this build is one idea: never type a length you can compute.
Change NAME to anything — one letter or forty — and the frame still closes.

    python3 build.py
"""

# The only thing you should ever need to edit in this file.
NAME = "Ada Lovelace"

# One space of breathing room on each side of the text.
PADDING = 1

# ---------------------------------------------------------------------------
# Work out the geometry once, then reuse it.
# ---------------------------------------------------------------------------
#
#   +--------------+
#   |  Ada Lovelace  |
#   +--------------+
#    ^^            ^^
#    ||            |+-- corner
#    ||            +--- padding
#    |+----------------- inner width = len(NAME) + PADDING * 2
#    +------------------ corner
#
inner_width = len(NAME) + PADDING * 2

top_and_bottom = "+" + "-" * inner_width + "+"
middle = "|" + " " * PADDING + NAME + " " * PADDING + "|"

print(top_and_bottom)
print(middle)
print(top_and_bottom)

print()

# ---------------------------------------------------------------------------
# The same idea, three more ways. Every one of these is just "compute the
# width, then repeat a character that many times".
# ---------------------------------------------------------------------------

# A double-ruled box.
print("=" * (len(NAME) + 4))
print("|", NAME, "|")
print("=" * (len(NAME) + 4))

print()

# A banner: the name centred in a row of stars. Day 4 does this properly with
# format specs; today the arithmetic is the lesson.
banner_width = len(NAME) + 20
side = (banner_width - len(NAME) - 2) // 2   # // is whole-number division
print("*" * banner_width)
print("*" * side + " " + NAME + " " + "*" * side)
print("*" * banner_width)

print()

# An underline that always matches, which is the smallest useful version of
# the whole idea — and the one you will actually keep using.
print(NAME)
print("~" * len(NAME))


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Set PADDING = 3 and confirm every frame still closes.
#   * Set NAME = "Bo" and then to your full legal name. No line should be
#     ragged. If one is, you typed a number somewhere you should have
#     computed one — find it.
#   * Add a second line under the name (a title, a date) and make the frame
#     size itself to whichever of the two lines is longer. You do not know
#     max() yet; try it anyway and look it up if you get stuck.
