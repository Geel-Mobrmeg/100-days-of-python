"""Day 052 build — a validation layer with error types of its own.

    python3 build.py

Day 50's inventory system raised ValueError, KeyError and TypeError. Those
are honest but useless to a caller: you cannot tell "the supplier sent a
price of -3" from "there is a bug in my code", and you cannot put either
into a form next to the field it belongs to.

Today the same failures get NAMES, DATA and MESSAGES:

    InventoryError                     one clause catches all of mine
      ValidationError                  a field of an incoming record
        MissingField / BadType / OutOfRange / UnknownReference
      StockError
        InsufficientStock              carries sku, wanted, available
      DuplicateSku

Every one carries the field, the value it saw and the value it wanted, so
the message, the log line and the API response are all built from the same
object instead of being re-typed three times.
"""

import json
import sys
import traceback
from decimal import Decimal, InvalidOperation
from pathlib import Path

WIDTH = 78


# ###########################################################################
# THE ERROR TYPES
# ###########################################################################

class InventoryError(Exception):
    """Base for everything this module raises deliberately.

    Its entire job is this line, in the caller:

        except InventoryError:      -> my failures
        except Exception:           -> my failures AND every bug I have

    One base per package. Not one per function.
    """


class ValidationError(InventoryError, ValueError):
    """An incoming field is unusable.

    ALSO A ValueError, on purpose. Code written before these types existed
    says `except ValueError` and keeps working; new code can be precise.
    That is how you add exception types to a library people already use.
    """

    expected = "a valid value"

    def __init__(self, field, value, expected=None, source=None):
        self.field = field
        self.value = value
        self.expected = expected or type(self).expected
        self.source = source
        super().__init__(str(self))

    def __str__(self):
        where = f" (from {self.source})" if self.source else ""
        return f"{self.field} must be {self.expected}, got {self.value!r}{where}"

    def as_dict(self):
        """The same failure, shaped for an API response or a form.

        Built from the ATTRIBUTES. Nobody has to parse the message —
        which is the practical reason to carry data on an exception.
        """
        return {
            "field": self.field,
            "problem": type(self).__name__,
            "expected": self.expected,
            "got": self.value,
        }


class MissingField(ValidationError):
    expected = "present"

    def __init__(self, field, source=None):
        super().__init__(field, None, source=source)

    def __str__(self):
        where = f" (from {self.source})" if self.source else ""
        return f"{self.field} is required and was not supplied{where}"


class BadType(ValidationError):
    """Present, but not convertible to what the field needs."""


class OutOfRange(ValidationError):
    """The right type, outside the permitted values."""


class UnknownReference(ValidationError):
    """Well-formed, and points at something that does not exist."""

    def __str__(self):
        near = f"; did you mean {self.suggestion}?" if self.suggestion else ""
        return (f"{self.field} {self.value!r} is not in the {self.expected}"
                f"{near}")

    def __init__(self, field, value, expected, suggestion=None, source=None):
        self.suggestion = suggestion
        super().__init__(field, value, expected, source)


class StockError(InventoryError):
    """Nothing wrong with the request. The warehouse cannot satisfy it."""


class InsufficientStock(StockError):
    def __init__(self, sku, wanted, available):
        self.sku = sku
        self.wanted = wanted
        self.available = available
        self.shortfall = wanted - available
        super().__init__(
            f"{sku}: wanted {wanted}, only {available} available "
            f"(short by {self.shortfall})"
        )


class DuplicateSku(InventoryError):
    def __init__(self, sku):
        self.sku = sku
        super().__init__(f"{sku} is already in the catalogue")


# ###########################################################################
# THE VALIDATORS — each raises the most specific type it can
# ###########################################################################

CATEGORIES = ("hardware", "consumable", "premium", "general")


def required(record, field, source):
    if field not in record or record[field] in (None, ""):
        raise MissingField(field, source=source)
    return record[field]


def as_sku(record, source):
    value = str(required(record, "sku", source)).strip().upper()
    if len(value) < 3:
        raise OutOfRange("sku", value, "at least 3 characters", source)
    if not value.replace("-", "").isalnum():
        raise BadType("sku", value, "letters, digits and dashes only", source)
    return value


def as_money(record, field, source):
    raw = required(record, field, source)
    try:
        amount = Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        # `from exc` — the caller sees BOTH "cost must be a decimal amount"
        # and the InvalidOperation that proves why. One word, and the
        # traceback stops looking like a bug in this file.
        raise BadType(field, raw, "a decimal amount", source) from exc
    if amount <= 0:
        raise OutOfRange(field, str(amount), "greater than 0", source)
    if amount > Decimal("1000000"):
        raise OutOfRange(field, str(amount), "at most 1000000", source)
    return amount


def as_units(record, field, source):
    raw = required(record, field, source)
    try:
        units = int(str(raw))
    except ValueError as exc:
        raise BadType(field, raw, "a whole number of units", source) from exc
    if units < 0:
        raise OutOfRange(field, units, "0 or more", source)
    return units


def as_category(record, source):
    value = str(required(record, "category", source)).strip().lower()
    if value not in CATEGORIES:
        near = next((c for c in CATEGORIES if c.startswith(value[:4])), None)
        raise UnknownReference("category", value, "category list", near, source)
    return value


def validate_product(record, source="feed"):
    """Collect EVERY problem, then raise them together.

    Stopping at the first one means a supplier with four bad fields needs
    four round trips. The failures here are independent — a bad price does
    not make the category unknowable — so they are reported together.
    """
    fields, problems = {}, []
    for name, get in [
        ("sku", lambda: as_sku(record, source)),
        ("name", lambda: str(required(record, "name", source)).strip()),
        ("cost", lambda: as_money(record, "cost", source)),
        ("category", lambda: as_category(record, source)),
        ("units", lambda: as_units(record, "units", source)),
    ]:
        try:
            fields[name] = get()
        except ValidationError as exc:
            problems.append(exc)

    if problems:
        raise ExceptionGroup(
            f"{len(problems)} problem(s) in record {record.get('sku', '?')!r}",
            problems,
        )
    return fields


# ###########################################################################
# A SUPPLIER FEED, AS SUPPLIERS ACTUALLY SEND IT
# ###########################################################################

FEED = [
    {"sku": "WID-001", "name": "Widget", "cost": "4.50",
     "category": "hardware", "units": "150"},
    {"sku": "gz", "name": "Gizmo", "cost": "12.00",
     "category": "hardware", "units": "40"},
    {"sku": "DHK-003", "name": "Doohickey", "cost": "free",
     "category": "consumable", "units": "80"},
    {"sku": "THG-004", "name": "Thingummy", "cost": "-48",
     "category": "premuim", "units": "3.5"},
    {"sku": "GAD-005", "cost": "9.99", "category": "hardware"},
    {"sku": "SPR*006", "name": "Sprocket", "cost": "2500000",
     "category": "hardware", "units": "-4"},
    {"sku": "CMP-007", "name": "Component", "cost": "7.25",
     "category": "general", "units": "0"},
]

print("=" * WIDTH)
print(f"{'VALIDATING A SUPPLIER FEED':^{WIDTH}}")
print("=" * WIDTH)

accepted, rejected = [], []

for position, record in enumerate(FEED, 1):
    source = f"feed line {position}"
    try:
        accepted.append(validate_product(record, source))
        print(f"\n  line {position}  ACCEPTED  {record['sku']}")
    except* ValidationError as group:
        rejected.append((position, group.exceptions))
        print(f"\n  line {position}  REJECTED  "
              f"{len(group.exceptions)} problem(s)")
        for exc in group.exceptions:
            print(f"      {type(exc).__name__:<18}{exc}")

print()
print("-" * WIDTH)
print(f"  {len(accepted)} accepted, {len(rejected)} rejected, "
      f"{sum(len(p) for _, p in rejected)} problems reported in ONE pass")


# ###########################################################################
# THE SAME FAILURES, AS DATA
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE SAME OBJECTS, THREE AUDIENCES':^{WIDTH}}")
print("=" * WIDTH)

position, problems = rejected[2]                 # the four-problem record

print(f"\n  1. FOR A PERSON (str(exc)) — feed line {position}")
for exc in problems:
    print(f"     {exc}")

print("\n  2. FOR A LOG (type and attributes)")
for exc in problems:
    print(f"     {type(exc).__name__:<18}field={exc.field:<10}"
          f"value={exc.value!r}")

print("\n  3. FOR AN API RESPONSE (as_dict)")
payload = {"errors": [exc.as_dict() for exc in problems]}
for line in json.dumps(payload, indent=2).splitlines()[:14]:
    print(f"     {line}")
print(f"     ... {len(json.dumps(payload, indent=2).splitlines()) - 14} more")

print("""
  All three were built from the SAME objects. Nobody re-typed the field
  name, and nobody parsed a message with a regular expression to get it
  back out. That is what "carry data on the exception" buys, and it is the
  difference between an exception and a printed complaint.""")


# ###########################################################################
# raise ... from, IN A REAL TRACEBACK
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT THE 3AM TRACEBACK SAYS':^{WIDTH}}")
print("=" * WIDTH)


def show(fn):
    try:
        fn()
    except BaseException:                                # noqa: BLE001
        text = "".join(traceback.format_exception(*sys.exc_info()))
        text = text.replace(str(Path(__file__).parent) + "/", "")
        return text.rstrip()
    return "(no exception)"


def with_from():
    as_money({"cost": "free"}, "cost", "feed line 3")


print()
for line in show(with_from).splitlines():
    print(f"  {line}")

print("""
  TWO exceptions, in the right order: the InvalidOperation that actually
  happened, then "The above exception was the DIRECT CAUSE" of a BadType
  that says which field and what was expected.

  Without `from exc` the same two appear under "During handling of the
  above exception, ANOTHER exception occurred" — which reads as though the
  validator itself is broken. One word, and the reader's first guess
  changes from "the library is buggy" to "line 3 of my feed is wrong".""")


# ###########################################################################
# CATCHING AT THE RIGHT LEVEL
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'ONE CLAUSE FOR MY FAILURES, AND BUGS STILL CRASH':^{WIDTH}}")
print("=" * WIDTH)


class Catalogue:
    """Just enough of Day 50 to make the stock errors real."""

    def __init__(self):
        self._stock = {}

    def add(self, sku, units):
        if sku in self._stock:
            raise DuplicateSku(sku)
        self._stock[sku] = units

    def issue(self, sku, units):
        if sku not in self._stock:
            raise UnknownReference("sku", sku, "catalogue",
                                   suggestion=next(iter(self._stock), None))
        if units > self._stock[sku]:
            raise InsufficientStock(sku, units, self._stock[sku])
        self._stock[sku] -= units
        return self._stock[sku]

    def broken_report(self):
        """Contains a genuine BUG, on purpose. It must NOT be caught."""
        return self._stock.tota1_units()          # typo -> AttributeError


catalogue = Catalogue()
catalogue.add("WID-001", 150)

operations = [
    ("issue 50 widgets", lambda: catalogue.issue("WID-001", 50)),
    ("issue 500 widgets", lambda: catalogue.issue("WID-001", 500)),
    ("issue an unknown sku", lambda: catalogue.issue("NOPE-9", 1)),
    ("add WID-001 again", lambda: catalogue.add("WID-001", 10)),
    ("a typo in MY code", catalogue.broken_report),
]

escaped = []
print()
for label, operation in operations:
    try:
        outcome = f"ok -> {operation()}"
    except InventoryError as exc:
        outcome = f"{type(exc).__name__}: {exc}"
    except Exception as exc:                             # noqa: BLE001
        # This clause is the MEASUREMENT. In real code it would not exist,
        # and the AttributeError would end the program — correctly.
        escaped.append(type(exc).__name__)
        outcome = f"ESCAPED THE DOMAIN HANDLER -> {type(exc).__name__}"
    print(f"  {label:<24}{outcome[:52]}")

print(f"""
  The first four are handled by ONE clause, `except InventoryError`, and
  each still knows exactly what it was. The fifth is a typo in my own code
  and it went straight past — which is what should happen, because no
  amount of retrying fixes {escaped[0] if escaped else 'a bug'}.

  A domain base class is what makes that separation possible. `except
  Exception` would have swallowed the typo and reported it to the user as
  an inventory problem.""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)


def raises(fn, expected):
    try:
        fn()
    except expected:
        return True
    except BaseException:                                # noqa: BLE001
        return False
    return False


bad = OutOfRange("cost", "-48", "greater than 0", "feed line 4")
short = InsufficientStock("WID-001", 500, 100)

claims = [
    ("every rejection names its field",
     all(exc.field for _, problems in rejected for exc in problems)),
    ("one pass reports every problem in a record",
     len(rejected[2][1]) == 3 and sum(len(p) for _, p in rejected) == 10),
    ("old `except ValueError` code still catches validation errors",
     raises(lambda: as_units({"units": "x"}, "units", "t"), ValueError)),
    ("...and `except InventoryError` catches them too",
     raises(lambda: as_units({"units": "x"}, "units", "t"), InventoryError)),
    ("...while a stock error is NOT a ValueError",
     not isinstance(short, ValueError)),
    ("the cause is preserved by `from exc`",
     type(next(e for _, p in rejected for e in p
               if e.__cause__ is not None).__cause__).__name__
     in ("InvalidOperation", "ValueError")),
    ("the message says field, expectation and value",
     all(part in str(bad) for part in ("cost", "greater than 0", "-48"))),
    ("...and where it came from",
     "feed line 4" in str(bad)),
    ("an error can be serialised without parsing its message",
     bad.as_dict()["field"] == "cost" and bad.as_dict()["got"] == "-48"),
    ("InsufficientStock computes the shortfall",
     short.shortfall == 400),
    ("a typo suggests the nearest category",
     "premium" in str(next(e for _, p in rejected for e in p
                           if isinstance(e, UnknownReference)))),
    ("a bug in my own code is not caught by the domain handler",
     escaped == ["AttributeError"]),
]

print()
for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(p for _, p in claims)} of {len(claims)} checks pass")
print("""
  THE ONE WORTH RE-READING is the eleventh. `category: 'premuim'` produces
  "category 'premuim' is not in the category list; did you mean premium?"
  — because UnknownReference was given somewhere to PUT a suggestion.

  An exception class is a place to keep everything you knew at the moment
  it went wrong. Most of that knowledge is unrecoverable one frame later,
  which is why it has to be captured where it is raised.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Delete `from exc` in as_money() and re-read the traceback. The words
#     change from "direct cause" to "another exception occurred", and so
#     does the reader's first guess about who is at fault.
#
#   * Make validate_product() raise on the FIRST problem instead of
#     grouping. Then fix feed line 4 by running it repeatedly, and count
#     the runs.
#
#   * Add a Severity to ValidationError — a bad category might be a
#     warning with a default, while a negative price is fatal. Notice that
#     this belongs on the exception, not at the call site.
#
#   * Add `__notes__` (3.11): `exc.add_note(f"raw record: {record}")`. It
#     shows up in the traceback without changing the message.
#
#   * Feed a record that is not a dict at all. You get an AttributeError
#     from inside a validator — a BUG, correctly not converted. Decide
#     whether validate_product() should check its own argument first.
#
#   * On Day 57, write pytest for this file. `pytest.raises(OutOfRange)`
#     reads like a sentence, which is the last argument for named types.
