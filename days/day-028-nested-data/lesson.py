"""Day 028 — Nested data.

    python3 lesson.py
"""

import copy
import json

CONFIG = {
    "app": {"name": "shopmind", "version": "2.1"},
    "regions": {
        "north": {
            "manager": "Ada",
            "stores": [
                {"name": "Leeds", "staff": ["kim", "raj"], "hours": "9-6"},
                {"name": "York", "staff": []},                # no hours key
            ],
        },
        "south": {
            "manager": "Alan",
            "stores": [],                                     # no stores at all
        },
    },
}

# ---------------------------------------------------------------------------
# 1. SHAPE FIRST. Before writing any traversal, be able to SAY the shape.
# ---------------------------------------------------------------------------

print(f"top level:  {type(CONFIG).__name__} with keys {list(CONFIG)}")
print(f"regions:    {type(CONFIG['regions']).__name__} with keys "
      f"{list(CONFIG['regions'])}")
print(f"one region: {list(CONFIG['regions']['north'])}")
print(f"one store:  {list(CONFIG['regions']['north']['stores'][0])}")

# Said out loud:
#   "A dict with app and regions. regions maps a name to a dict with a
#    manager string and a stores LIST, each store having name, staff (a
#    list) and an OPTIONAL hours."
#
# If you cannot say that sentence, you cannot traverse it, and you will find
# out one TypeError at a time.

# The fastest way to make any nested structure legible:
print("\n" + json.dumps(CONFIG, indent=2)[:260] + " ...")


# ---------------------------------------------------------------------------
# 2. THE ACCESS LADDER
# ---------------------------------------------------------------------------

# LEVEL 1 — direct. Raises on anything missing. Correct when a missing key
# IS a bug and you want to hear about it immediately.
print(f"\ndirect:   {CONFIG['regions']['north']['manager']}")
try:
    CONFIG["regions"]["east"]["manager"]
except KeyError as e:
    print(f"          missing region -> KeyError: {e}")

# LEVEL 2 — chained .get(). The trick is that THE DEFAULT IS THE SAME TYPE
# as the thing you would have got, so the next .get() still works.
print(f"chained:  {CONFIG.get('regions', {}).get('east', {}).get('manager')}")
print(f"+default: "
      f"{CONFIG.get('regions', {}).get('east', {}).get('manager', 'unassigned')}")

# ITS TWO LIMITS:

# (a) lists have no .get()
try:
    CONFIG["regions"]["north"]["stores"].get(0)
except AttributeError as e:
    print(f"list .get() -> AttributeError: {e}")

# (b) a WRONG TYPE raises AttributeError, not KeyError. .get() chains do not
#     protect you from a string where you expected a dict:
odd = {"regions": "not a dict at all"}
try:
    odd.get("regions", {}).get("north", {})
except AttributeError as e:
    print(f"wrong type  -> AttributeError: {e}")


# ---------------------------------------------------------------------------
# 3. LEVEL 4 — a dig() helper. Write it once, use it everywhere.
# ---------------------------------------------------------------------------


def dig(data, *keys, default=None):
    """Walk a nested structure by keys and indices. Never raises.

    Handles dicts, lists, missing keys, out-of-range indices AND values
    that turn out to be the wrong type entirely.
    """
    for key in keys:
        if isinstance(data, dict):
            if key not in data:
                return default
            data = data[key]
        elif isinstance(data, (list, tuple)):
            if not isinstance(key, int) or not -len(data) <= key < len(data):
                return default
            data = data[key]
        else:
            return default                 # a str/int/None — cannot go deeper
    return data


print(f"\ndig deep:      {dig(CONFIG, 'regions', 'north', 'stores', 0, 'name')}")
print(f"dig missing:   {dig(CONFIG, 'regions', 'east', 'manager', default='-')}")
print(f"dig past end:  {dig(CONFIG, 'regions', 'south', 'stores', 5, default='-')}")
print(f"dig wrong type:{dig(odd, 'regions', 'north', default='-')}")
print(f"dig optional:  {dig(CONFIG, 'regions', 'north', 'stores', 1, 'hours', default='n/a')}")

# Twelve lines, written once, and every traversal in the program becomes
# readable AND unable to crash. Worth keeping for your Day 40 toolkit.


# ---------------------------------------------------------------------------
# 4. try/except — the other answer (Day 51 covers it properly)
# ---------------------------------------------------------------------------

try:
    name = CONFIG["regions"]["east"]["stores"][0]["name"]
except (KeyError, IndexError, TypeError):
    name = "-"
print(f"\ntry/except:    {name}")

# THE TRADE:
#   .get() chains   say what happens INLINE, at each step
#   try/except      keeps the happy path clean and catches EVERY failure
#                   mode, including the type errors .get() cannot
#
# For one deep access, try/except is often clearer. For a dozen, dig() wins.


# ---------------------------------------------------------------------------
# 5. GUARDED ITERATION — the habit that matters most
# ---------------------------------------------------------------------------

print("\nevery store, guarded at each level:")
for region, info in CONFIG.get("regions", {}).items():
    for store in info.get("stores", []):
        staff = store.get("staff", [])
        hours = store.get("hours", "not set")
        print(f"  {region:<8}{store.get('name', '?'):<10}"
              f"{len(staff):>3} staff   {hours}")

# EVERY DEFAULT IS THE EMPTY VERSION OF WHAT SHOULD BE THERE:
#   a missing dict  -> {}     -> .items() yields nothing
#   a missing list  -> []     -> the for loop runs zero times
#
# So a missing key means ZERO ITERATIONS rather than an exception. `south`
# has an empty store list and simply contributes nothing, with no `if`.
#
# The dangerous default is None: .get("stores") returns None, and iterating
# None is a TypeError.


# ---------------------------------------------------------------------------
# 6. FLATTENING — usually the right move before analysis
# ---------------------------------------------------------------------------

rows = [
    {
        "region": region,
        "manager": info.get("manager", "-"),
        "store": store.get("name", "?"),
        "staff": len(store.get("staff", [])),
    }
    for region, info in CONFIG.get("regions", {}).items()
    for store in info.get("stores", [])
]

print("\nflattened to rows:")
for row in rows:
    print(f"  {row}")

# Flat rows are what sorting (Day 27), counting (Day 25) and pandas
# (Day 73) all want. A tree is good for storage; a table is good for
# analysis. Converting between them is most of data work.
print(f"\nnow sortable: {sorted(rows, key=lambda r: -r['staff'])[0]['store']} has the most staff")


# ---------------------------------------------------------------------------
# 7. Copying — Day 21's warning, with real consequences
# ---------------------------------------------------------------------------

shallow = CONFIG.copy()
shallow["regions"]["north"]["manager"] = "CHANGED"
print(f"\nafter mutating a SHALLOW copy: "
      f"{CONFIG['regions']['north']['manager']}")

CONFIG["regions"]["north"]["manager"] = "Ada"          # put it back

deep = copy.deepcopy(CONFIG)
deep["regions"]["north"]["manager"] = "CHANGED"
print(f"after mutating a DEEP copy:    "
      f"{CONFIG['regions']['north']['manager']}")


# ---------------------------------------------------------------------------
# 8. Depth is a smell
# ---------------------------------------------------------------------------
#
#   2 levels   comfortable
#   3 levels   tolerable
#   4 levels   you are modelling something that wants to be a CLASS (Day 41),
#              a flat list of records, or a DATABASE (Day 78)
#
# The signal is code full of ["a"]["b"]["c"]["d"]: at that point the
# STRUCTURE is the problem, not the data.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete "stores" from north and re-run section 5. Nothing should break.
#   * Change "stores" to the string "none" and re-run. Something WILL break —
#     find out what, and which of the four access levels survives it.
#   * Use dig() to reach a value five levels down in a structure you invent.
#   * Write a recursive find_all(data, key) that returns every value for a
#     key at any depth. That is Day 36, and it is the natural next step.
