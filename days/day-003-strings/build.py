"""Day 003 build — an initials extractor.

Turn a full name into its initials, using only what Day 3 gave you: indexing,
slicing, searching and concatenation.

The interesting part of this build is where it FAILS. A two-part name is easy.
A three-part name needs a second search. A four-part name needs a third. There
is no version of this that handles "any" name without a loop, and that is the
point: you are meant to finish today wanting .split(), which arrives tomorrow.

    python3 build.py
"""

# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

full_name = "Ada Augusta Byron King"

print("Name:", repr(full_name))
print("-" * 46)


# ---------------------------------------------------------------------------
# 1. About cleaning the input
# ---------------------------------------------------------------------------
#
# A leading or trailing space would put "" where an initial belongs. Handling
# that needs either a conditional (Day 11) or .strip() (Day 4), and you have
# neither. So today the input is assumed clean, and this comment is the
# honest record of a corner that is being cut.

cleaned = full_name


# ---------------------------------------------------------------------------
# 2. The first initial is free
# ---------------------------------------------------------------------------

first_initial = cleaned[0]
print("First initial:      ", first_initial)


# ---------------------------------------------------------------------------
# 3. Every other initial is "the character after a space"
# ---------------------------------------------------------------------------
#
# .index(" ") finds the FIRST space. To find the next one, search the part of
# the string that comes after it — then add back the offset you sliced away.

space_1 = cleaned.index(" ")
second_initial = cleaned[space_1 + 1]

rest = cleaned[space_1 + 1:]
space_2 = rest.index(" ")
third_initial = rest[space_2 + 1]

rest_2 = rest[space_2 + 1:]
space_3 = rest_2.index(" ")
fourth_initial = rest_2[space_3 + 1]

print("Second initial:     ", second_initial)
print("Third initial:      ", third_initial)
print("Fourth initial:     ", fourth_initial)


# ---------------------------------------------------------------------------
# 4. Assemble them
# ---------------------------------------------------------------------------

initials = first_initial + second_initial + third_initial + fourth_initial
print("Initials:           ", initials)

# Dotted, the way they appear on an envelope:
dotted = (
    first_initial + "." + second_initial + "." + third_initial + "." + fourth_initial + "."
)
print("Dotted:             ", dotted)

# Spaced out:
spaced = (
    first_initial + ". " + second_initial + ". " + third_initial + ". " + fourth_initial + "."
)
print("Spaced:             ", spaced)

print("-" * 46)


# ---------------------------------------------------------------------------
# 5. A monogram: first initial + last initial, which needs no counting at all
# ---------------------------------------------------------------------------
#
# Searching from the RIGHT with .rindex() finds the LAST space, so this one
# works for any number of middle names. It is the only part of this file that
# genuinely generalises — and it does so precisely because it never had to
# know how many pieces there were.

last_space = cleaned.rindex(" ")
monogram = cleaned[0] + cleaned[last_space + 1]
print("Monogram (F + L):   ", monogram)

surname = cleaned[last_space + 1:]
print("Surname:            ", surname)
print("Sort key:           ", surname + ", " + cleaned[:cleaned.index(" ")])

print("-" * 46)


# ---------------------------------------------------------------------------
# 6. Tomorrow, in one line
# ---------------------------------------------------------------------------
#
# Everything above, for ANY number of name parts, with no index arithmetic and
# no crash on a name with the wrong number of pieces. Do not use this today —
# just read it, and notice how much of this file it deletes.

preview = "".join(part[0] for part in full_name.split())
print("Day 4 does it thus: ", preview)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Set full_name = "Ada Lovelace" and run it. Read the ValueError, and note
#     exactly which line failed and why. This is the lesson of the build.
#   * Make the monogram section work on a single-word name. (Hint: .rindex()
#     raises; .rfind() returns -1, and -1 + 1 is 0. Is that a fix or a bug?)
#   * Handle a hyphenated surname: "Ada Lovelace-Byron" should still monogram
#     as "AL", but what should the full initials be? Decide, then implement.
