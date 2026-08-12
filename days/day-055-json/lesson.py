"""Day 055 — JSON: four functions, and a dozen things that surprise people.

    python3 lesson.py
"""

import json
import math
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

WIDTH = 76

# ---------------------------------------------------------------------------
# 1. The four functions
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. FOUR FUNCTIONS, AND THE LETTER THAT DISTINGUISHES THEM':^{WIDTH}}")
print("=" * WIDTH)
print("""
      json.dumps(obj)      -> a STRING            "s" for string
      json.loads(text)     -> a Python object
      json.dump(obj, f)    -> writes to a FILE
      json.load(f)         -> reads from a file

  The pair without the "s" take a file object, not a path — so they work
  on anything file-like, which is Day 53's point arriving again.""")

settings = {"host": "localhost", "port": 8080, "debug": False,
            "tags": ["api", "eu"], "limits": {"rate": 100, "burst": 20}}

text = json.dumps(settings)
print(f"\n  dumps  {text}")
print(f"  loads  {json.loads(text) == settings}   <- round-trips exactly")


# ---------------------------------------------------------------------------
# 2. The type mapping, and where it loses
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. WHAT SURVIVES THE ROUND TRIP':^{WIDTH}}")
print("=" * WIDTH)

cases = [
    ("dict", {"a": 1}),
    ("list", [1, 2, 3]),
    ("str", "text"),
    ("int", 42),
    ("float", 4.5),
    ("bool", True),
    ("None", None),
    ("tuple", (1, 2, 3)),
    ("set", None),                       # handled below
    ("int keys", {1: "one", 2: "two"}),
    ("float precision", 0.1 + 0.2),
]

print(f"\n  {'PYTHON':<18}{'JSON':<20}{'BACK AS':<14}SAME?")
print("  " + "-" * (WIDTH - 4))
for label, value in cases:
    if label == "set":
        print(f"  {'set':<18}{'TypeError':<20}{'-':<14}no")
        continue
    encoded = json.dumps(value)
    decoded = json.loads(encoded)
    same = "yes" if decoded == value and type(decoded) is type(value) else "NO"
    print(f"  {label:<18}{encoded[:19]:<20}"
          f"{type(decoded).__name__:<14}{same}")

print("""
  THREE OF THOSE ARE LOSSY AND NONE OF THEM RAISES:

    tuple      -> list. JSON has one sequence type. If a caller did
                  `x, y = data['point']` it still works; if it did
                  `isinstance(..., tuple)` it does not.
    int keys   -> STRING keys. JSON object keys are strings, full stop.
    a set      -> TypeError, which is the honest one of the three.

  So `json.loads(json.dumps(x)) == x` is FALSE for a great many x, and
  that is the assumption most JSON bugs are made of.""")

SOURCE = "{1: 'one', True: 'TRUE', None: 'nothing'}"
collision = {1: "one", True: "TRUE", None: "nothing"}  # noqa: F601
print(f"\n  {'you wrote':<16}{SOURCE:<44}3 entries")
print(f"  {'the dict is':<16}{str(collision):<44}"
      f"{len(collision)} keys")
print(f"  {'the JSON is':<16}{json.dumps(collision):<44}"
      f"{len(json.loads(json.dumps(collision)))} keys")
print("""
  TWO SEPARATE COLLAPSES, neither of which raised. Python merged 1 and
  True before json was involved at all, because 1 == True and they hash
  the same — so 'one' was gone already. Then json turned the remaining
  int key and the None key into the STRINGS "1" and "null".

  (A linter DOES catch the first one — ruff calls it F601, and this file
  needs a `# noqa` on that line to keep it. Nothing catches the second.)

  KEEP JSON KEYS AS STRINGS IN PYTHON TOO. Then what you send is what you
  meant.""")


# ---------------------------------------------------------------------------
# 3. NaN, Infinity, and non-standard JSON
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  PYTHON WRITES JSON THAT IS NOT JSON, BY DEFAULT")
print("-" * WIDTH)

broken = {"rate": float("inf"), "ratio": float("nan")}
print(f"\n  json.dumps({broken})")
print(f"    -> {json.dumps(broken)}")
print("""
  `NaN` and `Infinity` are NOT in the JSON specification. Python emits them
  happily and reads them back happily, and every other parser in the world
  rejects the file — so this is a bug you find in a different language, in
  production, at the boundary.

      json.dumps(data, allow_nan=False)     -> ValueError, at your desk""")
try:
    json.dumps(broken, allow_nan=False)
except ValueError as exc:
    print(f"\n  with allow_nan=False:  ValueError: {exc}")

DUPLICATE = '{"a": 1, "a": 2}'
print(f"\n  duplicate keys:  json.loads({DUPLICATE!r})")
print(f"                   -> {json.loads(DUPLICATE)}")
print("  ...last one wins, silently. Valid JSON, and almost never intended.")


# ---------------------------------------------------------------------------
# 4. Formatting
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. HOW IT IS WRITTEN':^{WIDTH}}")
print("=" * WIDTH)

data = {"name": "café", "port": 8080, "tags": ["b", "a"], "on": True}

variants = [
    ("default", {}),
    ("indent=2", {"indent": 2}),
    ("sort_keys=True", {"indent": 2, "sort_keys": True}),
    ("compact", {"separators": (",", ":")}),
    ("ensure_ascii=False", {"ensure_ascii": False}),
]

print(f"\n  {'OPTIONS':<22}{'BYTES':>7}   OUTPUT")
for label, options in variants:
    encoded = json.dumps(data, **options)
    shown = encoded.replace("\n", "⏎")[:44]
    print(f"  {label:<22}{len(encoded):>7}   {shown}")

print("""
  indent=2        for anything a human will open or a git diff will show
  separators      for anything on a network — the saving is real at scale
  sort_keys=True  makes the output STABLE, so a config file re-saved with
                  no changes produces an empty diff. Do this.
  ensure_ascii    the default escapes every non-ASCII character to \\uXXXX,
                  which is safe everywhere and unreadable. False writes
                  real UTF-8, which is right for files you own.""")


# ---------------------------------------------------------------------------
# 5. Things JSON cannot hold
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. TYPES OF YOUR OWN':^{WIDTH}}")
print("=" * WIDTH)

record = {
    "id": 7,
    "created": datetime(2026, 3, 14, 9, 30),
    "due": date(2026, 4, 1),
    "price": Decimal("19.99"),
    "path": Path("/etc/app.conf"),
    "tags": {"eu", "beta"},
}

print()
try:
    json.dumps(record)
except TypeError as exc:
    print(f"  json.dumps(record) -> TypeError: {exc}")


def encode_extra(value):
    """Called ONLY for values json cannot handle. Raise for the rest."""
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": str(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"cannot serialise {type(value).__name__}")


encoded = json.dumps(record, default=encode_extra, indent=None)
print("\n  with default=encode_extra:")
print(f"    {encoded[:WIDTH - 6]}")


def decode_extra(obj):
    """object_hook runs on every decoded object. Reverse the tagging."""
    kind = obj.get("__type__")
    if kind == "datetime":
        return datetime.fromisoformat(obj["value"])
    if kind == "date":
        return date.fromisoformat(obj["value"])
    if kind == "decimal":
        return Decimal(obj["value"])
    return obj


restored = json.loads(encoded, object_hook=decode_extra)
print(f"\n  {'FIELD':<12}{'BACK AS':<14}{'EQUAL?':<9}VALUE")
for key in ("created", "due", "price", "path", "tags"):
    same = restored[key] == record[key]
    print(f"  {key:<12}{type(restored[key]).__name__:<14}"
          f"{str(same):<9}{str(restored[key])[:28]}")

print("""
  THE TAGGED-OBJECT TRICK — {"__type__": ..., "value": ...} — is how you
  round-trip a type JSON does not have. Note which two did NOT come back:

    path   was written as a plain string, so it returns as a string
    tags   was written as a list, so it returns as a list

  That was a CHOICE: those two are consumed by other systems that want a
  string and an array, and tagging them would have made the file harder to
  read for no benefit. `created`, `due` and `price` are consumed by this
  program, so they are tagged and restored exactly.

  DECIDE PER FIELD, and know that a Decimal written as a float is a
  rounding bug you cannot see: json has no decimal type.""")

print(f"\n  Decimal('19.99') as a float would be "
      f"{float(Decimal('19.99')) * 3:.17g} when tripled")
print(f"  ...against the exact {Decimal('19.99') * 3}")


# ---------------------------------------------------------------------------
# 6. Reading data you did not write
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
TITLE_5 = "5. READING SOMEBODY ELSE'S JSON"
print(f"{TITLE_5:^{WIDTH}}")
print("=" * WIDTH)

hostile = [
    ("not JSON at all", "{host: 'localhost'}"),
    ("trailing comma", '{"a": 1,}'),
    ("single quotes", "{'a': 1}"),
    ("empty file", ""),
    ("a bare number", "42"),
    ("a bare string", '"hello"'),
    ("null", "null"),
    ("nested 40 deep", "[" * 40 + "]" * 40),
    ("nested 1000 deep", "[" * 1000 + "]" * 1000),
]

print()
for label, raw in hostile:
    try:
        value = json.loads(raw)
        outcome = f"ok -> {type(value).__name__}"
    except json.JSONDecodeError as exc:
        outcome = f"JSONDecodeError: line {exc.lineno} col {exc.colno}"
    except RecursionError:
        outcome = "RecursionError"
    print(f"  {label:<20}{outcome}")

print("""
  JSON IS NOT PYTHON. Single quotes, trailing commas and unquoted keys are
  all invalid, and all of them are things a human writing a config by hand
  will do. json.JSONDecodeError carries .lineno, .colno and .pos — put
  them in your message (Day 52) and the person fixing the file knows where
  to look.

  A BARE NUMBER, STRING OR null IS VALID JSON. `json.load(f)` can return
  42, or None, and code that immediately does `data["key"]` gets a
  TypeError rather than the KeyError it was ready for. Check the type of
  what you loaded before you index it.

  json.loads IS SAFE on untrusted text — it builds data, never code. That
  is the one thing it has over pickle and eval, and it is not a small
  thing: NEVER unpickle or eval data from outside your program.

  SAFE IS NOT THE SAME AS UNLIMITED. Nesting 1000 deep is 24 bytes of
  input and a RecursionError; a 500 MB array is 500 MB of RAM. If the text
  came from a network, cap its SIZE before you parse it — the parser has
  no opinion about how much work you have asked it to do.""")


# ---------------------------------------------------------------------------
# 7. JSON, CSV, or something else
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. WHEN JSON IS THE WRONG ANSWER':^{WIDTH}}")
print("=" * WIDTH)
print("""
  JSON        nested structure, config, APIs, anything with a shape
  CSV         a flat table, and anything a spreadsheet must open
  JSON LINES  one JSON object per line — streamable, appendable, and the
              right answer for logs and exports. Plain JSON is neither:
              you cannot append to an array without rewriting the file,
              and you cannot read it without holding it all.
  TOML        human-EDITED config. Comments, and no ambiguity about
              numbers. Python reads it with tomllib (3.11+), and cannot
              write it.
  pickle      Python objects, trusted source only, same Python version.
              Never over a network. Never from a user.

  THE TEST FOR JSON: is anything nested? Yes -> JSON. No -> CSV, and your
  users can open it.""")

print()
print("=" * WIDTH)
print("""  1. dumps/loads for strings, dump/load for files.
  2. tuple -> list, int keys -> strings, set -> TypeError.
  3. Python writes NaN and Infinity, which no other parser accepts.
  4. sort_keys=True and indent=2 for files people read.
  5. default= to write your types, object_hook= to read them back.
  6. Decimal via a string, or accept a rounding bug.
  7. JSONDecodeError has line and column. Use them.
  8. json.loads is safe. pickle and eval are not.""")
print("=" * WIDTH)

assert math.isnan(json.loads('{"x": NaN}')["x"])       # noqa: S101 - a claim


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Round-trip a dict with tuple values and then check isinstance.
#   * Round-trip {1: 'a', '1': 'b'} and count the keys.
#   * dumps with allow_nan=True, then parse the file with `jq`.
#   * Write a Decimal as a float, multiply by 3, and compare with the exact
#     answer.
#   * Hand-write a config with a trailing comma, then print exc.lineno.
#   * Serialise a class of your own with default=, then restore it with
#     object_hook. Decide which fields deserve a __type__ tag.
