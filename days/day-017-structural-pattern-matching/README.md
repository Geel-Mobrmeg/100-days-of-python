# Day 017 — Structural pattern matching

**Phase 2 · Control flow** · ~75 minutes

> **Today's build:** a command parser that turns typed instructions like 'go north' into actions.

**Concepts:** `match` / `case` · literal & sequence patterns · guards · the wildcard case

---

## The article

### Why this day exists

`match` arrived in Python 3.10 and is the newest thing in this course. It looks like a `switch`
statement from other languages and it is not one — it matches on **shape**, not just value, which
makes it a genuinely different tool.

It is also easy to misuse, and there is one trap in it severe enough that it deserves its own
section: a `case` that looks like it compares against a variable actually *overwrites* that
variable and always matches.

### 1. The basic form

```python
match command:
    case "north":
        print("You go north.")
    case "south":
        print("You go south.")
    case _:
        print("I don't understand.")
```

`case _` is the **wildcard** — it matches anything, and it plays the role of `else`. If no case
matches and there is no wildcard, the `match` does nothing at all, silently. Always have a
wildcard unless you genuinely want that.

There is no fall-through: the first matching case runs, and then the `match` is over. No `break`
needed.

Multiple literals in one case use `|`, which reads as "or":

```python
case "north" | "n" | "up":
    ...
```

### 2. Sequence patterns — the actual point

This is where `match` stops being a `switch`:

```python
match command.split():
    case [action]:                    # exactly one word
        ...
    case ["go", direction]:           # exactly two, first is "go"
        ...                           # `direction` is BOUND to the second
    case ["take", *items]:            # "take" then any number of words
        ...                           # `items` is a list of the rest
    case []:                          # empty
        ...
```

Two things are happening at once: **matching a shape** and **capturing parts of it into names**.
`["go", direction]` says "a two-element sequence whose first element is the string `go`", and if
that matches, `direction` now holds the second element. Doing this with `if` requires a length
check, an index check and an assignment, and gets messy fast.

`*rest` captures "everything else" and can appear once per pattern.

A sequence pattern matches lists and tuples, but **not strings** — which is deliberate, since
otherwise `case [a, b]` would match every two-character string.

### 3. Guards

Add `if` to a case to constrain it further:

```python
case ["take", item] if item in inventory:
    print("You already have it.")
case ["take", item]:
    print(f"You take the {item}.")
```

The guard runs *after* the pattern matches. Order matters as always: the more specific case goes
first.

### 4. The trap: capture patterns

This is the one that will bite you, and it is silent.

```python
NORTH = "north"

match command:
    case NORTH:              # DOES NOT compare with NORTH!
        ...
```

A bare name in a pattern position is a **capture pattern**. It matches *anything* and binds the
value to that name — so this case always matches, and it reassigns `NORTH` to whatever `command`
was. No error, no warning.

The fix is a **value pattern**: a dotted name is compared rather than captured.

```python
case Direction.NORTH:        # dotted — compared. Works.
case constants.NORTH:        # also fine.
```

So: use literals directly, or put your constants in a class or module and use the dotted form.
`case _` works because `_` is the one name specially defined never to bind.

### 5. Mapping and class patterns

Two more forms you will meet later, listed now so you recognise them:

```python
case {"type": "user", "name": name}:      # dict with AT LEAST these keys
    ...
case Point(x=0, y=0):                     # a class instance (Day 41)
    ...
```

Mapping patterns match on a **subset** of keys — extra keys are fine, which is exactly right for
JSON from an API (Day 66).

### 6. When to use it

Honestly: **less often than you would think.** For a plain value-to-value mapping, a dict is
better:

```python
MOVES = {"n": "north", "s": "south"}
direction = MOVES.get(word, "nowhere")
```

That is Day 24's material and it beats both `match` and `if/elif` for lookups — it is shorter,
data-driven, and extensible without touching code.

`match` earns its place when you are **destructuring** — when the shape of the data decides what
to do and you want the pieces. Parsing commands, walking a syntax tree, handling variably-shaped
JSON. That is exactly today's build.

Also note: `match` needs Python 3.10+. If you must support 3.9, you cannot use it at all.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every pattern form, the capture-pattern trap demonstrated live, and dict-versus-match. |
| `build.py`  | The command parser: a small adventure that understands multi-word commands. |

```bash
python3 lesson.py
python3 build.py
printf 'look\ngo north\ntake lamp\ninventory\nquit\n' | python3 build.py
```

---

## Common mistakes

**`case SOME_CONSTANT:`** — captures instead of comparing, always matches, silently overwrites
the constant. Use a dotted name or a literal.

**No wildcard case.** Unmatched input does nothing at all, with no error.

**Expecting `case [a, b]` to match a string.** It does not, on purpose.

**Guard order.** The specific case must come before the general one.

**Using `match` for a lookup.** A dict is better.

**Using `match` on Python 3.9.** `SyntaxError`.

---

## Exercises

1. Write a `match` for a traffic light: `"red"`, `"amber"`, `"green"`, anything else.
2. Parse these with sequence patterns: `"quit"`, `"go north"`, `"take brass lamp"`,
   `"put lamp in bag"`, and an empty line.
3. Reproduce the capture trap: define `EXIT = "quit"`, use `case EXIT:`, and print `EXIT`
   afterwards. Watch it change.
4. Add a guard so `"take"` only succeeds when the item is actually in the room.
5. Rewrite one of your `match` blocks as a dict lookup, and say which is better and why.
6. Match a JSON-shaped dict: `{"type": "move", "dir": "north"}` versus
   `{"type": "say", "text": "hello"}`.

---

## Checklist

- [ ] I know `case NAME:` captures rather than compares
- [ ] I always include a wildcard case
- [ ] I can destructure a list with a sequence pattern and `*rest`
- [ ] I can add a guard to a case
- [ ] I use a dict for lookups and `match` for destructuring
- [ ] My parser handles one, two and many word commands, and an empty line
