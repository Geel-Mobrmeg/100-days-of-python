"""Day 020 — Milestone techniques: game state and the game loop.

No new syntax today. This file is about the three structural ideas that make
a program with STATE work, and about the one thing that makes such programs
rot: mixing the world up with the code that walks around it.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. THE GAME LOOP
# ---------------------------------------------------------------------------
#
# Every interactive program — every game, every shell, every server — is the
# same five steps, forever:
#
#       while running:
#           raw   = read input
#           words = parse it            (Day 17)
#           act   = change the state    (the rules)
#           show  = report              (the view)
#           check = has anything ended?
#
# Keeping those five apart is what stops a game becoming unmaintainable.
# The specific failure is mixing ACT and SHOW: a program that prints from
# inside the rules cannot be tested, replayed, or given a different front
# end, because the only way to find out what happened is to read the screen.
#
# In the build, `describe()` only shows and never changes anything except
# `visited`. That one exception is deliberate and marked.


# ---------------------------------------------------------------------------
# 2. THE WORLD IS DATA, NOT CODE
# ---------------------------------------------------------------------------

# THE BAD VERSION — a branch per room. Adding a room means editing logic,
# and the geography is scattered across a hundred lines of if:
#
#     if here == "hall":
#         if direction == "north":
#             here = "library"
#         elif direction == "east":
#             here = "garden"
#     elif here == "library":
#         ...
#
# THE GOOD VERSION — the geography is a table, and ONE piece of code walks
# it. Adding a room is a data change:

ROOM_NAMES = ["hall", "library", "garden"]
DIRECTIONS = ["north", "south", "east", "west"]
EXITS = [
    [1, -1, 2, -1],       # hall:    north -> library, east -> garden
    [-1, 0, -1, -1],      # library: south -> hall
    [-1, -1, -1, 0],      # garden:  west  -> hall
]

here = 0
for direction in ("north", "east", "west", "up"):
    if direction not in DIRECTIONS:
        print(f"  {direction:<6} is not a direction")
        continue
    target = EXITS[here][DIRECTIONS.index(direction)]
    if target == -1:
        print(f"  {direction:<6} no exit from {ROOM_NAMES[here]}")
    else:
        print(f"  {direction:<6} {ROOM_NAMES[here]} -> {ROOM_NAMES[target]}")
        here = target

# That loop is the ENTIRE movement system, for any number of rooms. This
# separation — a data table plus one interpreter — is the single most
# reusable structural idea in the whole course. It reappears as routes on
# Day 82, as schemas on Day 85, and as a database on Day 84.


# ---------------------------------------------------------------------------
# 3. PARALLEL LISTS, AND WHY THEY ARE A PLACEHOLDER
# ---------------------------------------------------------------------------

# Today's build stores the world as five lists, all indexed by room number:
#
#     ROOM_NAMES[i]   ROOM_TEXT[i]   EXITS[i]   room_items[i]   visited[i]
#
# They must stay the same length, in the same order, forever. NOTHING
# enforces that. Insert a room in the middle of one list and the game
# silently describes the wrong place.

names = ["hall", "library", "garden"]
items = ["key", "candle", ""]
names.insert(1, "cellar")          # forgot to update `items`

print()
for i, name in enumerate(names):
    floor = items[i] if i < len(items) else "*** OUT OF RANGE ***"
    print(f"  {name:<10} contains {floor!r}")

# The cellar now has the library's candle, the garden has nothing, and there
# is no error anywhere. On Day 24 one dict per room makes this impossible:
#
#     {"name": "hall", "items": ["key"], "exits": {"north": "library"}}
#
# and on Day 41 a Room class makes it impossible AND checked.


# ---------------------------------------------------------------------------
# 4. STATE THAT IS NOT GEOGRAPHY
# ---------------------------------------------------------------------------

# Three different kinds of thing live in a game, and it is worth telling
# them apart before you write one:
#
#   WORLD     fixed:   room names, descriptions, exits.  Never changes.
#   STATE     varies:  where you are, what you carry, what is unlocked.
#   DERIVED   computed: "is it dark here?" = in cellar AND no candle.
#
# DERIVED VALUES SHOULD NEVER BE STORED. If you keep an `is_dark` variable
# you now have two sources of truth, and the day someone drops the candle
# without updating it, the cellar is lit forever. Compute it:

inventory = ["rusty key"]
here = "cellar"
dark = here == "cellar" and "candle" not in inventory
print(f"\n  dark? {dark}   (computed, so it cannot fall out of date)")

inventory.append("candle")
dark = here == "cellar" and "candle" not in inventory
print(f"  dark? {dark}   (picked up the candle — nothing else to update)")

# Same principle as Day 19's clock: DERIVE FROM A SOURCE OF TRUTH, DO NOT
# ACCUMULATE. It is the same bug in a different costume.


# ---------------------------------------------------------------------------
# 5. SENTINELS, AGAIN
# ---------------------------------------------------------------------------

# EXITS uses -1 for "no exit". That is a sentinel (Day 12), and it is a
# slightly dangerous one, because -1 IS A VALID PYTHON INDEX:

rooms = ["hall", "library", "garden"]
print(f"\n  rooms[-1] is {rooms[-1]!r} — not an error, the LAST room")

# So a missing `if target == -1` check does not crash. It teleports the
# player to the last room in the list, silently, forever. A sentinel that
# is also a legal value is exactly the bug Day 12 warned about, and this is
# what it looks like in practice.
#
# `None` would be a safer sentinel here, because `rooms[None]` raises.


# ---------------------------------------------------------------------------
# 6. MAKE IT TESTABLE BEFORE IT IS FINISHED
# ---------------------------------------------------------------------------

# The build takes a --walkthrough flag that plays the winning path from a
# list of commands instead of from input(). It cost four lines:
#
#     script = WALKTHROUGH[:] if "--walkthrough" in sys.argv else None
#     ...
#     raw = script.pop(0) if script is not None else input("> ")
#
# and it buys:
#
#   * proof the game is winnable, every time you change it
#   * a bug report you can reproduce ("run this list of commands")
#   * something to hand to pytest on Day 57 with almost no rework
#
# A game you cannot replay is a game you must play by hand after every
# edit, and so a game you will stop testing.


# ---------------------------------------------------------------------------
# 7. THE ENDING CHECKLIST
# ---------------------------------------------------------------------------
#
# A finished game answers all of these. Most unfinished ones fail on 3 or 5:
#
#   1. Can the player win?                     (walkthrough proves it)
#   2. Can the player lose, distinctly?        (not just "you died")
#   3. Can the player get STUCK?               (drop the key somewhere
#                                               unreachable — is that a
#                                               dead end or a third ending?)
#   4. Does every command work in every room?
#   5. Does nonsense input crash it?           (it must not)
#   6. Is the goal discoverable without the source code?
#
# Number 3 is the one that separates a game from a demo. Decide whether an
# unwinnable state is a bug or a feature — and then make sure the player can
# TELL, because silently unwinnable is the worst answer.
