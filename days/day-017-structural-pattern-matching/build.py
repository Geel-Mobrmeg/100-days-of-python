"""Day 017 build — a command parser for a text adventure.

The parser is the interesting half of any adventure game, and it is exactly
what match/case is for: the SHAPE of what the player typed decides what
happens, and you want the pieces out of it.

This is a rehearsal for Day 20's milestone. Keep it — you will extend it.

    python3 build.py
    printf 'look\\ngo north\\ntake lamp\\ni\\nquit\\n' | python3 build.py
"""

import sys

if sys.version_info < (3, 10):
    sys.exit("match/case needs Python 3.10+.")

WIDTH = 62

# ---------------------------------------------------------------------------
# Constants in a class, so `case Verb.GO:` COMPARES rather than captures.
# A bare `case GO:` would match everything and overwrite GO — see lesson.py
# section 4. This class exists entirely to avoid that trap.
# ---------------------------------------------------------------------------


class Verb:
    GO = "go"
    TAKE = "take"
    DROP = "drop"
    LOOK = "look"
    QUIT = "quit"


# Synonyms live in a dict, because this is a LOOKUP and a dict beats match
# for lookups every time. Adding a synonym is a data change.
SYNONYMS = {
    "n": "go north", "s": "go south", "e": "go east", "w": "go west",
    "north": "go north", "south": "go south",
    "east": "go east", "west": "go west",
    "i": "inventory", "inv": "inventory",
    "l": "look", "x": "examine",
    "get": "take", "grab": "take",
    "q": "quit", "exit": "quit",
}

DIRECTIONS = ("north", "south", "east", "west", "up", "down")

# ---------------------------------------------------------------------------
# World state. Day 24's dicts will do this properly; two lists is enough now.
# ---------------------------------------------------------------------------

room_items = ["brass lamp", "rusty key"]
inventory = []
here = "the hall"

BANNER = """
+------------------------------------------------------------+
|  A COMMAND PARSER                                          |
|  try:  look / go north / take lamp / drop lamp / i / quit  |
|        n s e w / get lamp / put lamp in bag / help         |
+------------------------------------------------------------+"""

print(BANNER)
print(f"\nYou are in {here}. You can see: {', '.join(room_items)}.")

running = True
while running:
    try:
        raw = input("\n> ")
    except EOFError:
        break

    # -----------------------------------------------------------------
    # NORMALISE FIRST, MATCH SECOND. Every parser that skips this step
    # ends up with a case for "Go North" and another for "go  north".
    # -----------------------------------------------------------------
    cleaned = raw.strip().lower()
    cleaned = SYNONYMS.get(cleaned, cleaned)      # whole-line synonyms
    words = cleaned.split()

    # Word-level synonyms: "get lamp" -> "take lamp"
    if words:
        words[0] = SYNONYMS.get(words[0], words[0])

    # -----------------------------------------------------------------
    # THE PARSER. Cases run top to bottom; specific before general.
    # -----------------------------------------------------------------
    match words:
        case []:
            print("Say something.")

        case ["quit" | "bye"]:
            print("Goodbye.")
            running = False

        case ["help"]:
            print("Verbs: go, take, drop, look, examine, inventory, quit.")
            print("Directions: " + ", ".join(DIRECTIONS))

        case ["look"]:
            if room_items:
                print(f"You are in {here}. You can see: "
                      f"{', '.join(room_items)}.")
            else:
                print(f"You are in {here}. There is nothing here.")

        case ["inventory"]:
            if inventory:
                print("You are carrying: " + ", ".join(inventory))
            else:
                print("You are empty-handed.")

        # A GUARD constrains a pattern that already matched. Without it,
        # "go sideways" would be accepted as a movement.
        case [Verb.GO, direction] if direction in DIRECTIONS:
            here = f"the room to the {direction}"
            room_items = []
            print(f"You go {direction}. You are now in {here}.")

        case [Verb.GO, direction]:
            print(f"You cannot go {direction}. Try: "
                  f"{', '.join(DIRECTIONS)}.")

        case [Verb.GO]:
            print("Go where?")

        # *words captures "everything else", so multi-word item names work:
        # "take brass lamp" gives item_words = ["brass", "lamp"].
        case [Verb.TAKE, *item_words] if item_words:
            item = " ".join(item_words)
            if item in inventory:
                print(f"You already have the {item}.")
            elif item in room_items:
                room_items.remove(item)
                inventory.append(item)
                print(f"You take the {item}.")
            else:
                # A partial match, so "take lamp" finds "brass lamp".
                matches = [i for i in room_items if item in i]
                if len(matches) == 1:
                    room_items.remove(matches[0])
                    inventory.append(matches[0])
                    print(f"You take the {matches[0]}.")
                elif len(matches) > 1:
                    print(f"Which one? {', '.join(matches)}")
                else:
                    print(f"There is no {item} here.")

        case [Verb.TAKE]:
            print("Take what?")

        case [Verb.DROP, *item_words] if item_words:
            item = " ".join(item_words)
            matches = [i for i in inventory if item in i]
            if matches:
                inventory.remove(matches[0])
                room_items.append(matches[0])
                print(f"You drop the {matches[0]}.")
            else:
                print(f"You are not carrying a {item}.")

        case ["examine", *item_words] if item_words:
            item = " ".join(item_words)
            known = inventory + room_items
            matches = [i for i in known if item in i]
            if matches:
                print(f"The {matches[0]} looks ordinary but important.")
            else:
                print(f"You see no {item} here.")

        # A three-part pattern with a literal in the MIDDLE — the kind of
        # thing that is genuinely awkward with if/elif and trivial here.
        case ["put", item, "in", container]:
            print(f"You try to put the {item} in the {container}. "
                  f"It does not fit.")

        # Catch-all for a known verb used wrongly, before the true wildcard.
        case [verb, *rest] if verb in vars(Verb).values():
            print(f"I understand {verb!r} but not {' '.join(rest)!r}.")

        case [verb, *_]:
            print(f"I don't know how to {verb!r}. Try 'help'.")

print("\n" + "=" * WIDTH)
print(f"Final inventory: {', '.join(inventory) or '(empty)'}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Replace `case [Verb.GO, direction]` with `case [GO, direction]` using a
#     module-level GO = "go". Every command will now be treated as movement,
#     and GO will silently become whatever you typed. That is the trap, and
#     seeing it once is worth more than reading about it twice.
#
#   * Add "unlock DOOR with KEY" as a four-element pattern with a literal in
#     the middle. Then write the same thing with if/elif and compare.
#
#   * The room is currently two lists and a string. On Day 24 rebuild it as a
#     dict of rooms, each with exits and items — which is what Day 20 needs.
#
#   * The `SYNONYMS` dict and the `match` block do two different jobs here:
#     lookup and destructuring. Try moving the synonyms into `match` cases
#     and count how many lines it costs. That count is the argument for
#     using the right tool for each half.
