"""Day 020 MILESTONE — a text adventure.

    python3 build.py
    python3 build.py --walkthrough      # play the winning path automatically
    printf 'look\\ntake key\\ngo north\\nquit\\n' | python3 build.py

Multiple rooms, an inventory, a locked door, and three endings.

Everything from days 1-19 and nothing later: no dicts (Day 24), no classes
(Day 41), no functions taking objects apart. The world is held in parallel
lists indexed by room number, which is exactly the sort of thing a dict will
delete on Day 24 — notice how much bookkeeping it costs.
"""

import sys
import time

WIDTH = 66

# ===========================================================================
# THE WORLD
#
# Parallel lists, all indexed by room number. Every list MUST stay the same
# length and in the same order, and nothing enforces that but care. That
# fragility is the honest cost of not having a dict yet.
# ===========================================================================

HALL, LIBRARY, CELLAR, GARDEN, TOWER = 0, 1, 2, 3, 4

ROOM_NAMES = [
    "the Great Hall",
    "the Library",
    "the Cellar",
    "the Walled Garden",
    "the Tower Room",
]

ROOM_TEXT = [
    "Dust hangs in the light from a high window. Doors lead north and east.",
    "Shelves of rotting books. A cold draught comes from a stairway down.",
    "Black as pitch, and something drips. The stair back up is behind you.",
    "Roses gone wild over a sundial. A narrow door leads up into the tower.",
    "Wind, and a view of everything. A small brass box sits on the sill.",
]

# Exits as "north,south,east,west,up,down" — -1 means no exit that way.
NORTH, SOUTH, EAST, WEST, UP, DOWN = 0, 1, 2, 3, 4, 5
DIRECTION_NAMES = ["north", "south", "east", "west", "up", "down"]

EXITS = [
    [LIBRARY, -1, GARDEN, -1, -1, -1],        # hall
    [-1, HALL, -1, -1, -1, CELLAR],           # library
    [-1, -1, -1, -1, LIBRARY, -1],            # cellar
    [-1, -1, -1, HALL, TOWER, -1],            # garden
    [-1, -1, -1, -1, -1, GARDEN],             # tower
]

# Items on the floor of each room, as comma-separated strings.
room_items = [
    "rusty key,note",
    "candle",
    "silver coin",
    "",
    "brass box",
]

# The tower door is locked and needs the rusty key.
LOCKED_FROM = GARDEN
LOCKED_DIR = UP
locked = True

DARK_ROOM = CELLAR          # unlit without the candle

inventory = []
here = HALL
moves = 0
running = True
ending = ""
visited = [False] * len(ROOM_NAMES)
started = time.perf_counter()

WALKTHROUGH = [
    "look", "take note", "read note", "take rusty key",
    "go north", "take candle", "go down", "take silver coin",
    "go up", "go south", "go east", "unlock door",
    "go up", "take brass box", "open box",
]

script = WALKTHROUGH[:] if "--walkthrough" in sys.argv else None


def say(text=""):
    """Print, and pause slightly when playing the scripted walkthrough."""
    print(text)
    if script is not None:
        time.sleep(0.12)


def items_in(room):
    """Return the list of items on the floor of `room`."""
    return [i for i in room_items[room].split(",") if i]


def describe(room, full=False):
    """Describe a room. Short after the first visit, unless `full`."""
    if room == DARK_ROOM and "candle" not in inventory:
        say("\nIt is pitch dark. You can see nothing at all.")
        say("Something drips. Going back UP seems wise.")
        return

    say(f"\n== {ROOM_NAMES[room].upper()} ==")
    if full or not visited[room]:
        say(ROOM_TEXT[room])

    floor = items_in(room)
    if floor:
        say("You can see: " + ", ".join(floor) + ".")

    ways = []
    for d, target in enumerate(EXITS[room]):
        if target == -1:
            continue
        if room == LOCKED_FROM and d == LOCKED_DIR and locked:
            ways.append(DIRECTION_NAMES[d] + " (locked)")
        else:
            ways.append(DIRECTION_NAMES[d])
    say("Exits: " + ", ".join(ways) + ".")
    visited[room] = True


# ===========================================================================
# OPENING
# ===========================================================================

print("=" * WIDTH)
print(f"{'THE TOWER ROOM':^{WIDTH}}")
print("=" * WIDTH)
print("""
You wake on the flagstones of a hall you do not remember entering.
Somewhere above you, something is ticking.

Commands:  look, go <direction>, take <item>, drop <item>, read <item>,
           unlock door, open box, inventory (i), help, quit
Shortcuts: n s e w, up, down
""".rstrip())

describe(here)

# ===========================================================================
# THE GAME LOOP
# ===========================================================================

while running:
    if script is not None:
        if not script:
            break
        raw = script.pop(0)
        print(f"\n> {raw}")
    else:
        try:
            raw = input("\n> ")
        except EOFError:
            break

    cleaned = raw.strip().lower()

    # Whole-line shortcuts, expanded before parsing.
    SHORTCUTS = "n:go north,s:go south,e:go east,w:go west," \
                "up:go up,down:go down,u:go up,d:go down," \
                "i:inventory,inv:inventory,l:look,q:quit,exit:quit"
    for pair in SHORTCUTS.split(","):
        short, long = pair.split(":")
        if cleaned == short:
            cleaned = long
            break

    words = cleaned.split()
    if not words:
        say("Say something.")
        continue

    verb = words[0]
    rest = " ".join(words[1:])
    dark = here == DARK_ROOM and "candle" not in inventory

    # -----------------------------------------------------------------
    match [verb, *words[1:]]:

        case ["quit"] | ["bye"]:
            ending = "You walk out of the hall and never speak of it."
            running = False

        case ["help"]:
            say("look, go <dir>, take, drop, read, unlock door, open box,")
            say("inventory, quit.  Directions: " + ", ".join(DIRECTION_NAMES))

        case ["look"]:
            describe(here, full=True)

        case ["inventory"]:
            if inventory:
                say("You are carrying: " + ", ".join(inventory) + ".")
            else:
                say("You are empty-handed.")

        case ["go"]:
            say("Go where?")

        case ["go", direction] if direction in DIRECTION_NAMES:
            d = DIRECTION_NAMES.index(direction)
            target = EXITS[here][d]

            if target == -1:
                say(f"You cannot go {direction} from here.")
            elif here == LOCKED_FROM and d == LOCKED_DIR and locked:
                say("The tower door is locked. There is a keyhole.")
            else:
                here = target
                moves += 1
                describe(here)

        case ["go", direction]:
            say(f"{direction!r} is not a direction. Try: "
                f"{', '.join(DIRECTION_NAMES)}.")

        case ["take", *what] if what:
            if dark:
                say("You grope about in the dark and find nothing.")
                continue
            wanted = " ".join(what)
            floor = items_in(here)
            matches = [i for i in floor if wanted in i]
            if not matches:
                say(f"There is no {wanted} here.")
            else:
                item = matches[0]
                floor.remove(item)
                room_items[here] = ",".join(floor)
                inventory.append(item)
                say(f"You take the {item}.")

        case ["drop", *what] if what:
            wanted = " ".join(what)
            matches = [i for i in inventory if wanted in i]
            if not matches:
                say(f"You are not carrying a {wanted}.")
            else:
                item = matches[0]
                inventory.remove(item)
                floor = items_in(here)
                floor.append(item)
                room_items[here] = ",".join(floor)
                say(f"You drop the {item}.")

        case ["read", *what] if what:
            wanted = " ".join(what)
            if not any(wanted in i for i in inventory):
                say(f"You are not carrying a {wanted}.")
            elif "note" in wanted:
                say('The note reads: "The tower is locked. The key is')
                say('where you woke. The cellar is dark — bring a light."')
            else:
                say("There is nothing written on it.")

        case ["unlock", *_] | ["open", "door"]:
            if here != LOCKED_FROM:
                say("There is nothing locked here.")
            elif not locked:
                say("It is already unlocked.")
            elif "rusty key" not in inventory:
                say("You have nothing to unlock it with.")
            else:
                locked = False
                say("The rusty key turns, grinding. The tower door swings open.")

        case ["open", *what] if what and "box" in " ".join(what):
            if "brass box" not in inventory:
                say("You are not carrying the box.")
            elif "silver coin" in inventory:
                ending = (
                    "Inside the box is a slot the exact size of a silver coin.\n"
                    "You drop it in. The ticking stops. The door below you\n"
                    "opens onto a morning you recognise.\n\n"
                    "                      *** YOU ESCAPE ***"
                )
                running = False
            else:
                ending = (
                    "Inside the box is a slot, the exact size of a coin you\n"
                    "do not have. Behind you, the tower door clicks shut.\n\n"
                    "                *** YOU ARE STILL HERE ***"
                )
                running = False

        case [verb_, *_]:
            say(f"You cannot {verb_!r} anything here. Try 'help'.")

# ===========================================================================
# ENDING
# ===========================================================================

print()
print("=" * WIDTH)
print(ending or "You stop playing.")
print("=" * WIDTH)
print(f"{'rooms visited':<34}{f'{sum(visited)} / {len(ROOM_NAMES)}':>{WIDTH - 34}}")
print(f"{'moves between rooms':<34}{moves:>{WIDTH - 34}}")
print(f"{'items carried':<34}{len(inventory):>{WIDTH - 34}}")
print(f"{'tower unlocked':<34}{str(not locked):>{WIDTH - 34}}")
print(f"{'time played':<34}"
      f"{f'{time.perf_counter() - started:.1f}s':>{WIDTH - 34}}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Count the parallel lists: ROOM_NAMES, ROOM_TEXT, EXITS, room_items,
#     visited — five lists that must stay the same length and order, with
#     nothing enforcing it. Add a sixth room and see how many places you
#     have to edit. THAT is what Day 24's dict fixes, and Day 41's classes
#     fix properly.
#
#   * EXITS uses -1 for "no exit". What happens if a room index is ever -1
#     by accident? (Python indexes from the end. It would silently teleport
#     you to the tower.) Sentinels that are valid values, again — Day 12.
#
#   * Add a third ending: something that happens if you drop the key in the
#     cellar and cannot get back.
#
#   * Add a lamp with a limited number of turns before it burns out. You
#     will need a counter that ticks on every command, which is the first
#     thing in this file that is genuinely GAME STATE rather than geography.
