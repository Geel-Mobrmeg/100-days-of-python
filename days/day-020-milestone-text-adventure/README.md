# Day 020 — Milestone: text adventure 🏁

**Phase 2 · Control flow** · ~180 minutes

> **Today's build:** a multi-room adventure with an inventory, locked doors and at least two endings.

**Concepts:** game loop · state · rooms & transitions · inventory · win conditions

---

## The article

### What you are actually building

A text adventure is the classic milestone for control flow because it needs every single thing
from the last ten days at once — and, more importantly, it is the first program you have written
that has **state**: facts that persist between commands and change what the next command does.

Everything before today was a pipeline. Input went in, output came out, and running it twice gave
the same answer. A game is different: the same command means different things depending on what
has already happened. `go up` is refused, then allowed. That is the shift.

### 1. The game loop

Every interactive program — every game, every shell, every web server — is these five steps,
forever:

```
while running:
    raw   = read input
    words = parse it              (Day 17)
    act   = change the state      (the rules)
    show  = report                (the view)
    check = has anything ended?
```

The discipline that matters is keeping **act** and **show** apart. A program that prints from
inside its rules cannot be tested, replayed, or given a different interface, because the only way
to find out what happened is to read the screen.

### 2. The world is data, not code

This is the structural idea of the day, and it is the one that transfers furthest.

**The version that rots:**

```python
if here == "hall":
    if direction == "north":
        here = "library"
    elif direction == "east":
        here = "garden"
elif here == "library":
    ...
```

Adding a room means editing logic, and the geography ends up scattered across a hundred lines of
branches.

**The version that works:** the geography is a *table*, and one small piece of code walks it.

```python
EXITS = [
    [1, -1, 2, -1],       # hall:    north -> library, east -> garden
    [-1, 0, -1, -1],      # library: south -> hall
]
target = EXITS[here][DIRECTIONS.index(direction)]
```

That is the entire movement system, for any number of rooms. Adding a room is a data change.
**A data table plus one interpreter** is the most reusable structural idea in this course — it
comes back as routes on Day 82, schemas on Day 85, and a database on Day 84.

### 3. Three kinds of state

Tell them apart before you write anything:

| Kind | Example | Rule |
|---|---|---|
| **World** | room names, descriptions, exits | fixed; never changes at runtime |
| **State** | where you are, what you carry, what is unlocked | changes; this is the game |
| **Derived** | "is it dark here?" | **compute it, never store it** |

Storing a derived value gives you two sources of truth, and the day somebody drops the candle
without updating `is_dark`, the cellar is lit forever. Compute it:

```python
dark = here == CELLAR and "candle" not in inventory
```

This is Day 19's drift problem in a different costume: *derive from a source of truth, do not
accumulate.*

### 4. Parallel lists, and why today's build is deliberately awkward

You do not have dicts until Day 24, so the build holds the world as five lists all indexed by
room number: `ROOM_NAMES`, `ROOM_TEXT`, `EXITS`, `room_items`, `visited`.

They must stay the same length and in the same order forever, and **nothing enforces that**.
Insert a room in the middle of one list and the game silently describes the wrong place, with no
error anywhere.

Notice the discomfort. On Day 24 one dict per room makes that impossible; on Day 41 a `Room`
class makes it impossible *and* checked. Feeling the problem is what makes the fix land.

### 5. Sentinels that are valid values — again

`EXITS` uses `-1` for "no exit". But **`-1` is a legal Python index**: `rooms[-1]` is the last
room, not an error. So a missing `if target == -1` check does not crash — it silently teleports
the player to the last room, forever.

This is exactly Day 12's warning, and this is what it looks like in real code. `None` would be
safer, because `rooms[None]` raises.

### 6. Make it replayable before you finish it

The build takes a `--walkthrough` flag that plays the winning path from a list of commands
instead of from `input()`. It costs about four lines and buys:

- proof the game is winnable, **every time you change it**
- a reproducible bug report ("run this list of commands")
- something you can hand to pytest on Day 57 with almost no rework

A game you cannot replay is a game you must test by hand after every edit — so a game you will
stop testing.

### 7. Endings

Two endings is the brief. The interesting one is the third possibility: **getting stuck**. Drop
the key somewhere unreachable and the game may become unwinnable. Decide whether that is a bug or
a feature — and either way, make sure the player can *tell*. Silently unwinnable is the worst
answer of the three.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The game loop, world-as-data, the three kinds of state, and the parallel-list failure demonstrated. |
| `build.py`  | The full adventure: 5 rooms, inventory, a locked tower, a dark cellar, 3 endings, and a walkthrough. |

```bash
python3 lesson.py
python3 build.py                    # play it
python3 build.py --walkthrough      # watch the winning path
printf 'take key\ngo east\nunlock door\ngo up\ntake box\nopen box\n' | python3 build.py
```

---

## The brief

Build your own before opening `build.py`. It must have:

- [ ] at least four rooms with real exits between them
- [ ] an inventory you can add to and drop from
- [ ] at least one item that changes what you can do (a key, a light)
- [ ] a locked door that refuses you, then does not
- [ ] at least two distinct endings
- [ ] a command parser that handles nonsense without crashing
- [ ] a `look` that works everywhere, and a `quit` that always works
- [ ] a way to replay a winning sequence without typing

---

## Common mistakes

**Geography in `if` statements.** Put it in a table.

**Storing derived state.** `is_dark` goes stale. Compute it.

**Printing from inside the rules.** Now nothing is testable.

**A parser that only handles perfect input.** Every command needs a fallback.

**No way to lose, or only one ending.** Then it is a corridor, not a game.

**Unreachable win state.** If the key can be dropped in the dark cellar, say what happens.

**`-1` as a sentinel index.** It is a valid index. Silent teleportation.

---

## Extend it

1. Add a sixth room. Count how many places you had to edit — that number is the argument for
   Day 24.
2. Add a lamp with a limited number of turns. That is the first thing in the game that is
   genuinely *game state* rather than geography.
3. Add a character who moves between rooms on their own each turn.
4. Save and load the game (Day 55's JSON). Notice that this is easy exactly to the extent that
   your state is data rather than scattered variables.
5. **On Day 24**, rebuild the world as a dict of rooms. **On Day 41**, as `Room` and `Item`
   classes. Keep all three versions and read them side by side — that progression is the clearest
   illustration of what data structures and objects are actually *for*.

---

## Phase 2 checklist

You are leaving Control flow. Before you do:

- [ ] I can write `if`/`elif` chains ordered correctly and test their boundaries
- [ ] I can name the setup, condition and progress of any `while` loop I write
- [ ] I reach for `for` by default and `while` only when the count is unknown
- [ ] I use `break`, `continue` and `for...else` deliberately
- [ ] I can reason about the cost of a nested loop
- [ ] I seed randomness when I need to reproduce a result
- [ ] I can parse a multi-word command into an action
- [ ] **My adventure is winnable, losable, and cannot be crashed by typing**

Tomorrow: lists. Every "five parallel lists" problem in today's build starts getting solved.
