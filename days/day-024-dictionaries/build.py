"""Day 024 build — a contact book that never raises on a missing name.

    python3 build.py
    python3 build.py --demo
    printf 'find ada\\nsearch tur\\nadd bob 555 work\\nlist\\nquit\\n' | python3 build.py

Commands: list | find NAME | search TEXT | tag TAG | add KEY PHONE TAGS...
          del KEY | stats | quit

The design point: every lookup path has a defined answer for "not there".
Nothing in this program can raise KeyError, and the reason is visible on
every line that touches the data.
"""

import sys

WIDTH = 70

# ---------------------------------------------------------------------------
# One dict per person, keyed by a short handle. Compare with Day 20's five
# parallel lists: adding a field here is one key, not a sixth list that has
# to be kept the same length as the other five.
# ---------------------------------------------------------------------------

contacts = {
    "ada": {
        "name": "Ada Lovelace",
        "phone": "020 7946 0011",
        "email": "ada@analytical.example",
        "tags": ["work", "maths"],
    },
    "alan": {
        "name": "Alan Turing",
        "phone": "020 7946 0022",
        "email": "alan@bletchley.example",
        "tags": ["work", "chess", "maths"],
    },
    "grace": {
        "name": "Grace Hopper",
        "phone": "020 7946 0033",
        "email": "grace@navy.example",
        "tags": ["work", "compilers"],
    },
    "katherine": {
        "name": "Katherine Johnson",
        "phone": "020 7946 0044",
        "tags": ["work", "orbits"],
        # NOTE: no "email" key at all. Everything below must cope, and the
        # way it copes is the lesson.
    },
}

DEMO = [
    "list", "find ada", "find bob", "search tur", "search o",
    "tag maths", "add bob 020 7946 0055 work chess",
    "find bob", "del alan", "stats", "quit",
]
script = DEMO[:] if "--demo" in sys.argv else None


def show(key, record):
    """Print one contact. Every field access has a defined missing answer."""
    print(f"  {key:<12}{record.get('name', '(no name)'):<24}"
          f"{record.get('phone', '-'):<18}")
    print(f"  {'':<12}{record.get('email', '(no email on file)'):<24}"
          f"{', '.join(record.get('tags', [])):<18}")


print("=" * WIDTH)
print(f"{'CONTACT BOOK':^{WIDTH}}")
print("=" * WIDTH)
print("list | find NAME | search TEXT | tag TAG | add KEY PHONE TAGS...")
print("del KEY | stats | quit")

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
    verb, rest = words[0].lower(), words[1:]

    # -------------------------------------------------------------------
    if verb in ("quit", "q", "exit"):
        running = False

    elif verb in ("list", "l"):
        print(f"\n  {len(contacts)} contact(s):")
        for key, record in contacts.items():
            show(key, record)

    elif verb == "find":
        wanted = " ".join(rest).lower()

        # .get() with a default is the whole point. A missing name is a
        # normal thing for a search to encounter, not a bug — so no
        # KeyError, and no `if key in contacts` two-step either.
        record = contacts.get(wanted)

        if record is None:
            print(f"  No contact called {wanted!r}.")
            # Be helpful about near misses rather than just failing.
            close = [k for k in contacts if wanted and wanted in k]
            if close:
                print(f"  Did you mean: {', '.join(close)}?")
        else:
            print()
            show(wanted, record)

    elif verb == "search":
        needle = " ".join(rest).lower()
        if not needle:
            print("  search for what?")
            continue

        # Partial match across every field. `.get(..., "")` means a record
        # missing a field simply does not match on it, rather than raising.
        hits = {}
        for key, record in contacts.items():
            haystack = " ".join([
                key,
                record.get("name", ""),
                record.get("phone", ""),
                record.get("email", ""),
                " ".join(record.get("tags", [])),
            ]).lower()
            if needle in haystack:
                hits[key] = record

        print(f"\n  {len(hits)} match(es) for {needle!r}:")
        for key, record in hits.items():
            show(key, record)

    elif verb == "tag":
        wanted = " ".join(rest).lower()
        hits = {
            k: r for k, r in contacts.items()
            if wanted in [t.lower() for t in r.get("tags", [])]
        }
        print(f"\n  {len(hits)} contact(s) tagged {wanted!r}:")
        for key, record in hits.items():
            show(key, record)

    elif verb == "add":
        if len(rest) < 1:
            print("  add KEY [PHONE...] [TAGS...]")
            continue
        key = rest[0].lower()
        if key in contacts:
            print(f"  {key!r} already exists. Delete it first.")
            continue
        contacts[key] = {
            "name": key.title(),
            "phone": " ".join(rest[1:4]) if len(rest) > 1 else "-",
            "tags": [t.lower() for t in rest[4:]],
        }
        print(f"  added {key!r}")

    elif verb in ("del", "delete", "rm"):
        key = " ".join(rest).lower()
        # .pop with a default: remove if present, say so if not, never raise.
        removed = contacts.pop(key, None)
        if removed is None:
            print(f"  There is no {key!r} to delete.")
        else:
            print(f"  deleted {removed.get('name', key)!r}")

    elif verb == "stats":
        # Counting tags with .get(t, 0) + 1 — tomorrow's Counter does this
        # in one line, and it is worth having written it the long way once.
        tag_counts = {}
        for record in contacts.values():
            for tag in record.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        missing_email = [
            k for k, r in contacts.items() if not r.get("email")
        ]

        print()
        print(f"  {'contacts':<28}{len(contacts):>{WIDTH - 30}}")
        print(f"  {'distinct tags':<28}{len(tag_counts):>{WIDTH - 30}}")
        print(f"  {'without an email':<28}"
              f"{', '.join(missing_email) or 'none':>{WIDTH - 30}}")
        print(f"  {'-' * (WIDTH - 4)}")
        for tag, n in sorted(tag_counts.items(), key=lambda kv: -kv[1]):
            bar = "#" * n
            print(f"  {tag:<20}{n:>4}  {bar}")

    else:
        print(f"  I don't know {verb!r}. Try: list, find, search, tag, add,"
              f" del, stats, quit.")

# ===========================================================================
# What this replaced
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'WHY THIS IS A DICT AND NOT FIVE LISTS':^{WIDTH}}")
print("=" * WIDTH)
print("""
Day 20's world was five lists indexed by room number, which had to stay the
same length and in the same order forever, with nothing enforcing it. The
equivalent here would be:

    keys = ["ada", "alan", ...]
    names = ["Ada Lovelace", ...]
    phones = [...]
    emails = [...]           <- and what goes here for someone with none?
    tags = [...]

Three problems that simply do not exist above:

  1. A record cannot lose a field, because the fields ARE the record.
  2. A missing value is an ABSENT KEY, not a placeholder you have to
     remember to check for. Katherine has no "email" key at all, and every
     lookup in this file handles that without a single `if`.
  3. Adding a field is one key on one record, not a sixth list plus every
     place that indexes the other five.

And lookup by key went from scanning the list to a single hash — which at
four contacts is irrelevant and at forty thousand is the whole program.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Katherine has no "email" key. Find every place in this file that would
#     have raised KeyError with `record["email"]`, and check each one is
#     using .get() with a default that makes sense in context — "-" for a
#     column, "" for a search haystack, [] for a list. The right default is
#     different in each case, which is why there is no global answer.
#
#   * `add` builds "phone" from rest[1:4] and tags from rest[4:], which is
#     fragile. Rewrite it to split on a delimiter instead.
#
#   * `stats` counts tags with .get(t, 0) + 1. Tomorrow replace it with
#     collections.Counter and delete the loop.
#
#   * `search` scans every contact and every field — O(n) per query. Build a
#     tag INDEX ({tag: [keys]}) so `tag` lookups become O(1), and notice you
#     have just invented what a database calls an index.
#
#   * On Day 55, save and load the whole book as JSON. It will be almost no
#     work, because a dict of dicts of strings and lists IS JSON.
