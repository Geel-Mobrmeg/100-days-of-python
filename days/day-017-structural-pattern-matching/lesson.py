"""Day 017 — Structural pattern matching.

Needs Python 3.10 or newer.

    python3 lesson.py
"""

import sys

if sys.version_info < (3, 10):
    sys.exit("match/case needs Python 3.10+. You have " + sys.version)

# ---------------------------------------------------------------------------
# 1. The basic form — looks like switch, is not switch
# ---------------------------------------------------------------------------

for command in ("north", "south", "sideways"):
    match command:
        case "north":
            print(f"  {command:<10} -> You go north.")
        case "south":
            print(f"  {command:<10} -> You go south.")
        case _:
            print(f"  {command:<10} -> I don't understand.")

# `case _` is the WILDCARD and plays the role of else. With no wildcard and
# no match, the whole statement does NOTHING, silently:
match "sideways":
    case "north":
        print("never")
print("  (an unmatched match with no wildcard does nothing at all)")

# No fall-through. The first matching case runs and the match is over.
# Several literals in one case use | , read as "or":
for command in ("n", "up", "north"):
    match command:
        case "north" | "n" | "up":
            print(f"  {command:<10} -> north (three spellings, one case)")


# ---------------------------------------------------------------------------
# 2. Sequence patterns — where match stops being switch
# ---------------------------------------------------------------------------

print()
COMMANDS = (
    "look",
    "go north",
    "take brass lamp",
    "put lamp in bag",
    "",
)

for raw in COMMANDS:
    words = raw.split()
    match words:
        case []:
            print(f"  {raw!r:<20} -> (nothing typed)")
        case [action]:
            print(f"  {raw!r:<20} -> one word: action={action!r}")
        case ["go", direction]:
            print(f"  {raw!r:<20} -> movement: direction={direction!r}")
        case ["take", *items]:
            print(f"  {raw!r:<20} -> take: items={items}")
        case [verb, *rest]:
            print(f"  {raw!r:<20} -> verb={verb!r}, rest={rest}")

# TWO THINGS AT ONCE: matching a SHAPE and CAPTURING parts of it into names.
# ["go", direction] means "a two-element sequence whose first item is the
# string 'go'" — and if it matches, `direction` now holds the second item.
#
# The `if`-based equivalent needs a length check, an index check and an
# assignment, per case, and gets unreadable by the fourth one.

# `*rest` captures everything else and may appear once per pattern.

# A sequence pattern matches lists and tuples but NOT strings — deliberately,
# or `case [a, b]` would match every two-character string:
match "hi":
    case [a, b]:
        print("  never happens")
    case str():
        print("  'hi' is matched by str(), not by [a, b]")


# ---------------------------------------------------------------------------
# 3. Guards
# ---------------------------------------------------------------------------

print()
inventory = ["lamp"]

for raw in ("take lamp", "take sword"):
    match raw.split():
        case ["take", item] if item in inventory:
            print(f"  {raw!r:<14} -> you already have the {item}")
        case ["take", item]:
            print(f"  {raw!r:<14} -> you take the {item}")

# The guard runs AFTER the pattern matches. Specific case first, as always.


# ---------------------------------------------------------------------------
# 4. THE TRAP — a bare name CAPTURES, it does not compare
# ---------------------------------------------------------------------------

print()
EXIT = "quit"
print(f"  before: EXIT = {EXIT!r}")

command = "dance"
match command:
    case EXIT:                     # does NOT compare with EXIT
        print(f"  matched 'EXIT' even though command was {command!r}")

print(f"  after:  EXIT = {EXIT!r}   <- silently overwritten")

# A bare name in a pattern position is a CAPTURE PATTERN. It matches anything
# and binds the value to that name. No error. No warning. Always matches.

# THE FIX: a dotted name is a VALUE pattern, and is compared.


class Direction:
    NORTH = "north"
    SOUTH = "south"


for command in ("north", "dance"):
    match command:
        case Direction.NORTH:      # dotted -> compared. Correct.
            print(f"  {command!r:<10} -> matched Direction.NORTH properly")
        case _:
            print(f"  {command!r:<10} -> no match (as it should be)")

# So: use literals directly, or put constants in a class/module and use the
# dotted form. `_` is the one name specially defined never to bind.


# ---------------------------------------------------------------------------
# 5. Mapping and class patterns
# ---------------------------------------------------------------------------

print()
EVENTS = (
    {"type": "move", "dir": "north"},
    {"type": "say", "text": "hello", "volume": 11},
    {"type": "quit"},
)

for event in EVENTS:
    match event:
        case {"type": "move", "dir": direction}:
            print(f"  move -> {direction}")
        case {"type": "say", "text": text}:
            print(f"  say  -> {text!r}  (extra keys are ignored)")
        case {"type": kind}:
            print(f"  {kind}")

# Mapping patterns match a SUBSET of keys — extra keys are fine, which is
# exactly right for JSON from an API you do not control (Day 66).
# Class patterns — case Point(x=0, y=0) — arrive with Day 41.


# ---------------------------------------------------------------------------
# 6. When NOT to use match
# ---------------------------------------------------------------------------

print()

# For a plain value-to-value mapping, a DICT is better. Shorter, data-driven,
# and extensible without touching any code:
MOVES = {"n": "north", "s": "south", "e": "east", "w": "west"}
for word in ("n", "w", "x"):
    print(f"  {word} -> {MOVES.get(word, 'nowhere')}")

# That is Day 24's material, and it beats both match and if/elif for lookups.
#
# match earns its place when you are DESTRUCTURING — when the SHAPE of the
# data decides what to do and you want the pieces out of it. Parsing
# commands, walking a syntax tree, handling variably-shaped JSON.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete the `case _` from section 1 and feed it something unmatched.
#   * Reproduce the section 4 trap yourself, then fix it two different ways.
#   * Write `case ["go", direction] if direction in ("north", "south")` and
#     see what an unguarded "go sideways" does afterwards.
#   * Match {"type": "move"} against `case {"type": "move", "dir": d}`. It
#     does not match — a mapping pattern needs all the keys it names.
