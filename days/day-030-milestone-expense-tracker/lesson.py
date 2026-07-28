"""Day 030 — Milestone techniques: modelling, aggregation, and one source of truth.

No new syntax. This is about the three decisions that determine whether a
program that holds data stays correct as it grows.

    python3 lesson.py
"""

from collections import defaultdict
from decimal import Decimal

WIDTH = 72

RECORDS = [
    {"date": "2024-01-15", "category": "housing", "amount": Decimal("875.00")},
    {"date": "2024-01-22", "category": "fun", "amount": Decimal("31.00")},
    {"date": "2024-02-15", "category": "housing", "amount": Decimal("875.00")},
    {"date": "2024-02-14", "category": "fun", "amount": Decimal("96.40")},
]

# ---------------------------------------------------------------------------
# 1. THE SHAPE OF THE MODEL — three options, and why one wins
# ---------------------------------------------------------------------------

# OPTION A — parallel lists. Day 20's world, and the reason that build hurt.
dates = ["2024-01-15", "2024-01-22"]
categories = ["housing", "fun"]
amounts = [Decimal("875.00"), Decimal("31.00")]
# Three lists that must stay the same length and order forever, with nothing
# enforcing it. Adding a field means a fourth list and touching every loop.

# OPTION B — a dict keyed by something. Looks tidy, and quietly loses data:
by_date = {
    "2024-01-15": {"category": "housing", "amount": Decimal("875.00")},
    "2024-01-22": {"category": "fun", "amount": Decimal("31.00")},
}
by_date["2024-01-15"] = {"category": "food", "amount": Decimal("12.00")}
print(f"after a second expense on the same date: {len(by_date)} records")
print("  ^ the rent is GONE. Keys are unique; expenses are not.")

# OPTION C — A FLAT LIST OF DICTS. One record, one dict, every field named.
print(f"\nflat list of records: {len(RECORDS)} records, none lost")

# THE RULE: key by something only when it is genuinely UNIQUE AND STABLE.
# Dates are neither. A list of records is the default shape for anything
# that can happen more than once, and it is also exactly what a database
# table, a CSV file and a pandas DataFrame all are.


# ---------------------------------------------------------------------------
# 2. ONE SOURCE OF TRUTH — Day 19's principle, applied to money
# ---------------------------------------------------------------------------

# THE TEMPTING VERSION: keep a running total alongside the records.
records = list(RECORDS)
running_total = sum(r["amount"] for r in records)
print(f"\nrunning total: {running_total}")

records.append({"date": "2024-03-01", "category": "fun",
                "amount": Decimal("14.99")})
# ...and someone forgot to update running_total. Nothing raised.
print(f"after appending: total says {running_total}, "
      f"records say {sum(r['amount'] for r in records)}")
print("  ^ two numbers that should be equal, and are not. There is no error")
print("    to catch, because nothing went wrong — something did not happen.")

# THE FIX: DERIVE, DO NOT STORE. Compute totals when they are needed.
print(f"derived on demand: {sum(r['amount'] for r in records)}   (always right)")

# "But it will be slow." Summing a hundred thousand records takes
# milliseconds. Cache only after MEASURING (Day 29), and only behind a
# single function so there is still one place that knows.


# ---------------------------------------------------------------------------
# 3. AGGREGATION IS ALWAYS THE SAME THREE LINES
# ---------------------------------------------------------------------------

def totals_by(rows, key_func):
    """Sum amounts grouped by whatever key_func returns."""
    out = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        out[key_func(row)] += row["amount"]
    return dict(out)


print(f"\nby category: {totals_by(RECORDS, lambda r: r['category'])}")
print(f"by month:    {totals_by(RECORDS, lambda r: r['date'][:7])}")
print(f"by day:      {totals_by(RECORDS, lambda r: r['date'][-2:])}")

# ONE function, three reports, because the GROUPING KEY is a parameter
# rather than something baked into the loop. Write the aggregation once and
# pass in what makes the groups.
#
# This is the same shape at three scales:
#   Day 25  defaultdict           in memory
#   Day 75  pandas .groupby()     over a table
#   Day 78  SQL GROUP BY          in a database


# ---------------------------------------------------------------------------
# 4. '2024-03' — why dates are stored as strings here
# ---------------------------------------------------------------------------

print(f"\nsorted months: {sorted({r['date'][:7] for r in RECORDS})}")

# ISO 8601 (YYYY-MM-DD) sorts correctly AS TEXT, because the components run
# from most significant to least. That is not a coincidence; it is why the
# standard is that way round.
#
# "15/01/2024" does not sort. Neither does "Jan 15, 2024".
#
# Real date objects (Day 61) are still better — they can do arithmetic, know
# about leap years and time zones, and reject 2024-13-01. Until then, ISO
# strings get you sorting and grouping for free.


# ---------------------------------------------------------------------------
# 5. VALIDATE IN ONE PLACE, AND RETURN THE REASON
# ---------------------------------------------------------------------------

def parse_amount(text):
    """Return (value, error). Exactly one of the two is None."""
    try:
        value = Decimal(text.strip())
    except Exception:
        return None, f"{text!r} is not a number"
    if value <= 0:
        return None, f"{value} is not positive"
    return value, None


for candidate in ("12.50", "-3", "ten", "0"):
    value, error = parse_amount(candidate)
    print(f"  {candidate!r:<10}{'-> ' + error if error else '-> ok: ' + str(value)}")

# RETURNING THE REASON is what separates a validator from a filter. A
# function that returns True/False makes the caller invent the error
# message, and the message is the part the user actually reads.
#
# One function, so the rules cannot drift. Everything else in the program
# receives records that are already known to be good.


# ---------------------------------------------------------------------------
# 6. A REPORT IS A VIEW, NOT A CALCULATION
# ---------------------------------------------------------------------------
#
#     COMPUTE   produces numbers from the records. No printing.
#     REPORT    prints. No arithmetic beyond formatting.
#
# Day 10 introduced this and it now earns its keep: every figure in the
# build's report comes from a function that could be tested (Day 57)
# without capturing output. A total computed inside an f-string cannot be.
#
# The practical test: could you swap the terminal output for a CSV, a web
# page (Day 82) or a chart (Day 77) without touching any arithmetic? If
# not, the two halves are tangled.


# ---------------------------------------------------------------------------
# 7. CHECK THE MARGINS
# ---------------------------------------------------------------------------

by_month = totals_by(RECORDS, lambda r: r["date"][:7])
by_category = totals_by(RECORDS, lambda r: r["category"])
grand = sum(r["amount"] for r in RECORDS)

print(f"\n{'rows sum to the total':<34}{str(sum(by_month.values()) == grand):>10}")
print(f"{'columns sum to the total':<34}{str(sum(by_category.values()) == grand):>10}")

# A cross-tab whose margins do not agree with its grand total is wrong, and
# the check costs two lines. Any report with two independent routes to the
# same number should compare them — that is a test (Day 57) living inside
# the program, and it catches the errors that look plausible.


print("\n" + "=" * WIDTH)
print("""FIVE RULES FROM THIS PHASE

  1. A flat list of dicts is the default model for repeatable events.
  2. Key by something only when it is unique AND stable.
  3. Derive every total; store none of them.
  4. Make the grouping key a parameter, not part of the loop.
  5. Validate in one place and return the reason, not a bool.""")
print("=" * WIDTH)
