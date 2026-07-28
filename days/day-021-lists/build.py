"""Day 021 build — a to-do list, in memory.

    python3 build.py
    printf 'add buy milk\\nadd write day 21\\ndone 1\\nlist\\nquit\\n' | python3 build.py
    python3 build.py --demo

Commands: add TEXT | done N | undone N | del N | up N | down N | top N
          list | clear | undo | quit

The interesting part is `undo`, which is where aliasing stops being trivia
and becomes the difference between a working feature and a baffling bug.
"""

import sys

WIDTH = 62

# Two parallel lists again — Day 24's dicts fix this properly. For now,
# tasks[i] and done[i] describe the same item, and every operation MUST
# touch both or they drift apart. There is a check at the bottom for that.
tasks = []
done = []

# Undo history: a list of (tasks, done) SNAPSHOTS.
history = []

DEMO = [
    "add buy milk",
    "add write day 21",
    "add call the bank",
    "add water the plants",
    "done 2",
    "list",
    "top 4",
    "list",
    "del 1",
    "undo",
    "list",
    "quit",
]
script = DEMO[:] if "--demo" in sys.argv else None


def snapshot():
    """Save the current state so `undo` can come back to it.

    THE WHOLE POINT OF TODAY: these MUST be copies. Appending `tasks`
    itself would store a reference to the live list, so every later edit
    would silently rewrite the history too, and undo would restore the
    present. See the demonstration at the bottom of this file.
    """
    history.append((tasks.copy(), done.copy()))
    if len(history) > 20:
        history.pop(0)


def show():
    """Print the list."""
    print()
    if not tasks:
        print("  (nothing to do)")
        return
    for i, (text, is_done) in enumerate(zip(tasks, done), start=1):
        mark = "x" if is_done else " "
        strike = " (done)" if is_done else ""
        print(f"  {i:>2}. [{mark}] {text}{strike}")
    outstanding = len(tasks) - sum(done)
    print(f"  {'-' * 40}")
    print(f"  {len(tasks)} item(s), {outstanding} outstanding")


def valid(n_text):
    """Return a 0-based index from user text, or None if it is not usable."""
    if not n_text.isdigit():
        return None
    n = int(n_text) - 1                  # humans count from 1
    if n < 0 or n >= len(tasks):
        return None
    return n


print("=" * WIDTH)
print(f"{'TO-DO':^{WIDTH}}")
print("=" * WIDTH)
print("add TEXT | done N | undone N | del N | up N | down N | top N")
print("list | clear | undo | quit")

running = True
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

    words = raw.strip().split()
    if not words:
        continue

    verb = words[0].lower()
    rest = " ".join(words[1:])

    if verb in ("quit", "q", "exit"):
        running = False

    elif verb in ("list", "l"):
        show()

    elif verb == "add":
        if not rest:
            print("  add what?")
        else:
            snapshot()
            tasks.append(rest)
            done.append(False)           # BOTH lists, always
            print(f"  added {len(tasks)}. {rest}")

    elif verb in ("done", "undone"):
        i = valid(rest)
        if i is None:
            print(f"  {rest!r} is not an item number (1-{len(tasks)}).")
        else:
            snapshot()
            done[i] = verb == "done"
            print(f"  {tasks[i]!r} marked {verb}")

    elif verb in ("del", "delete", "rm"):
        i = valid(rest)
        if i is None:
            print(f"  {rest!r} is not an item number (1-{len(tasks)}).")
        else:
            snapshot()
            # pop RETURNS the item, which is exactly what we want to report.
            removed = tasks.pop(i)
            done.pop(i)                  # keep the lists in step
            print(f"  deleted {removed!r}")

    elif verb in ("up", "down"):
        i = valid(rest)
        if i is None:
            print(f"  {rest!r} is not an item number (1-{len(tasks)}).")
        else:
            j = i - 1 if verb == "up" else i + 1
            if j < 0 or j >= len(tasks):
                print("  already at the end.")
            else:
                snapshot()
                # Swap, in both lists. Tuple assignment does it in one line
                # without a temporary — Day 23 explains why this works.
                tasks[i], tasks[j] = tasks[j], tasks[i]
                done[i], done[j] = done[j], done[i]
                print(f"  moved {tasks[j]!r} {verb}")

    elif verb == "top":
        i = valid(rest)
        if i is None:
            print(f"  {rest!r} is not an item number (1-{len(tasks)}).")
        else:
            snapshot()
            tasks.insert(0, tasks.pop(i))
            done.insert(0, done.pop(i))
            print(f"  {tasks[0]!r} moved to the top")

    elif verb == "clear":
        snapshot()
        tasks.clear()
        done.clear()
        print("  cleared. 'undo' brings it back.")

    elif verb == "undo":
        if not history:
            print("  nothing to undo.")
        else:
            previous_tasks, previous_done = history.pop()
            # Assign the CONTENTS back, not the names, so any other
            # reference to `tasks` still sees the restored list.
            tasks[:] = previous_tasks
            done[:] = previous_done
            print(f"  undone. {len(history)} step(s) of history left.")

    else:
        print(f"  I don't know {verb!r}. Try: add, done, del, up, top, undo.")

# ---------------------------------------------------------------------------
# Integrity check — the price of parallel lists
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'final state':<40}{f'{len(tasks)} item(s)':>{WIDTH - 40}}")
print(f"{'completed':<40}{sum(done):>{WIDTH - 40}}")
print(f"{'lists still the same length?':<40}"
      f"{str(len(tasks) == len(done)):>{WIDTH - 40}}")
print("=" * WIDTH)

# ===========================================================================
# WHY snapshot() USES .copy() — the bug this build exists to teach
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE ALIASING BUG, DEMONSTRATED':^{WIDTH}}")
print("=" * WIDTH)

# THE BROKEN VERSION: store the live list instead of a copy.
live = ["milk", "bread"]
broken_history = []
broken_history.append(live)          # <- no .copy()
live.append("cheese")

print(f"  saved:   {broken_history[0]}")
print(f"  current: {live}")
print(f"  same object? {broken_history[0] is live}")
print("  The 'saved' snapshot changed when the list did, because it WAS")
print("  the list. Undo would restore the present.")

# THE FIXED VERSION.
live = ["milk", "bread"]
good_history = []
good_history.append(live.copy())     # <- the whole fix
live.append("cheese")

print()
print(f"  saved:   {good_history[0]}")
print(f"  current: {live}")
print(f"  same object? {good_history[0] is live}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Delete `.copy()` from snapshot() and run `--demo`. Undo will appear to
#     do nothing at all — the most confusing possible symptom, from the
#     smallest possible change.
#
#   * `undo` uses `tasks[:] = previous` rather than `tasks = previous`. Try
#     the second one and work out why nothing breaks HERE but would break
#     the moment another part of the program held a reference to `tasks`.
#
#   * Add `redo`. You will need a second stack, and you will have to decide
#     what happens to it when a new edit arrives after an undo.
#
#   * Two parallel lists again. On Day 24 make each task a dict:
#     {"text": ..., "done": False}, and delete the integrity check at the
#     bottom, because the problem it checks for stops being possible.
#
#   * On Day 55 save the list to JSON so it survives closing the program.
