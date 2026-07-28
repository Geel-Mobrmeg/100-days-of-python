"""Day 030 MILESTONE — an expense tracker with monthly reports.

    python3 build.py                 # report on the bundled data
    python3 build.py --interactive   # add your own, then report
    printf 'add 2024-03-14 food 12.50 lunch\\nreport\\nquit\\n' | python3 build.py --interactive

Everything from the phase: dicts for the model, defaultdict for grouping,
Counter for frequency, sets for distinct values, sorted() with multi-key
tie-breaks, comprehensions for the aggregations, Decimal for the money.

The design rule, stated once and followed everywhere below:

    THERE IS ONE LIST OF RECORDS. EVERY REPORT IS DERIVED FROM IT.

Nothing is stored twice. No running totals are kept. If a total and the
records disagree there is nowhere for the disagreement to hide, because
there is only one source of truth — Day 19's principle, applied to money.
"""

import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

WIDTH = 78
PENNY = Decimal("0.01")
CURRENCY = "GBP"

CATEGORIES = ("food", "transport", "housing", "utilities", "fun", "health")

# ===========================================================================
# THE MODEL: a flat list of dicts. One record, one dict, every field named.
#
# Compare with Day 20's five parallel lists. Adding a field here is one key
# on one record; there is no second list to keep in step, and no index that
# can drift.
# ===========================================================================

expenses = [
    {"date": "2024-01-04", "category": "food", "amount": Decimal("42.10"), "note": "weekly shop"},
    {"date": "2024-01-04", "category": "transport", "amount": Decimal("2.80"), "note": "bus"},
    {"date": "2024-01-11", "category": "food", "amount": Decimal("38.55"), "note": "weekly shop"},
    {"date": "2024-01-15", "category": "housing", "amount": Decimal("875.00"), "note": "rent"},
    {"date": "2024-01-18", "category": "utilities", "amount": Decimal("64.20"), "note": "energy"},
    {"date": "2024-01-22", "category": "fun", "amount": Decimal("31.00"), "note": "cinema"},
    {"date": "2024-01-28", "category": "food", "amount": Decimal("45.90"), "note": "weekly shop"},
    {"date": "2024-02-02", "category": "food", "amount": Decimal("41.35"), "note": "weekly shop"},
    {"date": "2024-02-05", "category": "health", "amount": Decimal("18.00"), "note": "prescription"},
    {"date": "2024-02-14", "category": "fun", "amount": Decimal("96.40"), "note": "dinner out"},
    {"date": "2024-02-15", "category": "housing", "amount": Decimal("875.00"), "note": "rent"},
    {"date": "2024-02-17", "category": "transport", "amount": Decimal("112.00"), "note": "rail card"},
    {"date": "2024-02-19", "category": "utilities", "amount": Decimal("71.85"), "note": "energy"},
    {"date": "2024-02-24", "category": "food", "amount": Decimal("52.20"), "note": "weekly shop"},
    {"date": "2024-03-01", "category": "fun", "amount": Decimal("14.99"), "note": "streaming"},
    {"date": "2024-03-03", "category": "food", "amount": Decimal("39.80"), "note": "weekly shop"},
    {"date": "2024-03-15", "category": "housing", "amount": Decimal("875.00"), "note": "rent"},
    {"date": "2024-03-16", "category": "transport", "amount": Decimal("8.60"), "note": "taxi"},
    {"date": "2024-03-21", "category": "utilities", "amount": Decimal("58.40"), "note": "energy"},
    {"date": "2024-03-22", "category": "health", "amount": Decimal("240.00"), "note": "dentist"},
    {"date": "2024-03-29", "category": "food", "amount": Decimal("47.05"), "note": "weekly shop"},
]


# ===========================================================================
# VALIDATION — one place, returning (record, error). Nothing else parses.
# ===========================================================================

def parse_expense(date, category, amount, note):
    """Turn four strings into a record, or return the reason it is not one."""
    date = date.strip()
    parts = date.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None, f"date {date!r} is not YYYY-MM-DD"
    year, month, day = (int(p) for p in parts)
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 < year < 2100):
        return None, f"date {date!r} is not a plausible date"

    category = category.strip().lower()
    if category not in CATEGORIES:
        return None, f"category {category!r} is not one of {', '.join(CATEGORIES)}"

    try:
        value = Decimal(amount.strip())
    except (InvalidOperation, AttributeError):
        return None, f"amount {amount!r} is not a number"
    if value <= 0:
        return None, f"amount {value} is not positive"

    return {
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "category": category,
        "amount": value.quantize(PENNY, rounding=ROUND_HALF_UP),
        "note": note.strip() or "-",
    }, None


# ===========================================================================
# AGGREGATION — every function takes the records and returns a fresh answer.
# No caching, no running totals, nothing to fall out of step.
# ===========================================================================

def month_of(record):
    """'2024-03-14' -> '2024-03'. Sortable as a string, which is the point."""
    return record["date"][:7]


def totals_by(records, key_func):
    """Sum amounts grouped by whatever key_func returns."""
    out = defaultdict(lambda: Decimal("0.00"))
    for record in records:
        out[key_func(record)] += record["amount"]
    return dict(out)


def cross_tab(records):
    """month -> category -> total. A dict of dicts (Day 24)."""
    table = defaultdict(lambda: defaultdict(lambda: Decimal("0.00")))
    for record in records:
        table[month_of(record)][record["category"]] += record["amount"]
    return {m: dict(c) for m, c in table.items()}


def bar(value, peak, width=26):
    if peak <= 0:
        return ""
    return "#" * int(value / peak * width)


# ===========================================================================
# REPORT
# ===========================================================================

def report(records):
    if not records:
        print("No expenses recorded.")
        return

    total = sum(r["amount"] for r in records)
    months = sorted({month_of(r) for r in records})       # a SET, then sorted
    used = sorted({r["category"] for r in records})
    by_month = totals_by(records, month_of)
    by_category = totals_by(records, lambda r: r["category"])
    table = cross_tab(records)

    print()
    print("=" * WIDTH)
    print(f"{'EXPENSE REPORT':^{WIDTH}}")
    print("=" * WIDTH)
    print(f"{'entries':<34}{len(records):>{WIDTH - 34},}")
    print(f"{'months covered':<34}{f'{months[0]} to {months[-1]}':>{WIDTH - 34}}")
    print(f"{'categories used':<34}{f'{len(used)} of {len(CATEGORIES)}':>{WIDTH - 34}}")
    print(f"{'total spent':<34}{f'{CURRENCY} {total:,}':>{WIDTH - 34}}")
    print(f"{'mean per month':<34}"
          f"{f'{CURRENCY} {(total / len(months)).quantize(PENNY)}':>{WIDTH - 34}}")
    print(f"{'mean per entry':<34}"
          f"{f'{CURRENCY} {(total / len(records)).quantize(PENNY)}':>{WIDTH - 34}}")

    # ---- by month -------------------------------------------------------
    print()
    print("-" * WIDTH)
    print("BY MONTH")
    print("-" * WIDTH)
    peak = max(by_month.values())
    previous = None
    for month in months:
        value = by_month[month]
        change = ""
        if previous is not None and previous > 0:
            delta = (value - previous) / previous
            change = f"{delta:+7.1%}"
        print(f"  {month}{value:>12,}  {change:>8}  {bar(value, peak):<26}")
        previous = value

    # ---- by category ----------------------------------------------------
    print()
    print("-" * WIDTH)
    print("BY CATEGORY")
    print("-" * WIDTH)
    peak = max(by_category.values())
    # sorted() with a two-key tuple: total DESC (negated), then name ASC.
    ordered = sorted(by_category.items(), key=lambda kv: (-kv[1], kv[0]))
    for category, value in ordered:
        share = value / total
        print(f"  {category:<12}{value:>12,}{share:>8.1%}  "
              f"{bar(value, peak):<26}")

    unused = sorted(set(CATEGORIES) - set(used))          # set difference
    if unused:
        print(f"\n  never used: {', '.join(unused)}")

    # ---- the cross-tab --------------------------------------------------
    print()
    print("-" * WIDTH)
    print("MONTH x CATEGORY")
    print("-" * WIDTH)
    col = 11
    print(f"  {'':<10}" + "".join(f"{c[:9]:>{col}}" for c in used)
          + f"{'TOTAL':>{col}}")
    for month in months:
        row = table.get(month, {})
        cells = "".join(
            f"{row.get(c, Decimal('0')):>{col},}" for c in used
        )
        print(f"  {month:<10}{cells}{by_month[month]:>{col},}")
    footer = "".join(f"{by_category.get(c, Decimal('0')):>{col},}" for c in used)
    print(f"  {'TOTAL':<10}{footer}{total:>{col},}")

    # The check that makes the cross-tab trustworthy: both margins and the
    # grand total are computed independently, and they must agree.
    row_sum = sum(by_month.values())
    col_sum = sum(by_category.values())
    print(f"\n  {'rows sum to the total':<40}{str(row_sum == total):>{WIDTH - 44}}")
    print(f"  {'columns sum to the total':<40}{str(col_sum == total):>{WIDTH - 44}}")

    # ---- the biggest spends ---------------------------------------------
    print()
    print("-" * WIDTH)
    print("BIGGEST SINGLE SPENDS")
    print("-" * WIDTH)
    biggest = sorted(records, key=lambda r: (-r["amount"], r["date"]))[:5]
    for rank, record in enumerate(biggest, start=1):
        print(f"  {rank}. {record['date']}  {record['category']:<11}"
              f"{record['amount']:>10,}   {record['note']}")

    top_month = max(by_month.items(), key=lambda kv: kv[1])
    top_category = max(by_category.items(), key=lambda kv: kv[1])
    print(f"\n  {'most expensive month':<30}"
          f"{f'{top_month[0]}  ({CURRENCY} {top_month[1]:,})':>{WIDTH - 34}}")
    print(f"  {'largest category':<30}"
          f"{f'{top_category[0]}  ({top_category[1] / total:.0%} of spend)':>{WIDTH - 34}}")

    # ---- habits ---------------------------------------------------------
    print()
    print("-" * WIDTH)
    print("HABITS")
    print("-" * WIDTH)
    notes = Counter(r["note"] for r in records)
    for note, n in notes.most_common(4):
        spent = sum(r["amount"] for r in records if r["note"] == note)
        print(f"  {note:<22}{n:>3} times{spent:>12,}"
              f"{f'(avg {(spent / n).quantize(PENNY)})':>18}")

    recurring = {
        note for note, n in notes.items() if n >= len(months)
    }
    print(f"\n  looks recurring (once a month or more): "
          f"{', '.join(sorted(recurring)) or 'none'}")
    print("=" * WIDTH)


# ===========================================================================
# INTERACTIVE
# ===========================================================================

if "--interactive" in sys.argv:
    print("=" * WIDTH)
    print(f"{'EXPENSE TRACKER':^{WIDTH}}")
    print("=" * WIDTH)
    print("add YYYY-MM-DD CATEGORY AMOUNT NOTE... | list | report | quit")
    print(f"categories: {', '.join(CATEGORIES)}")

    while True:
        try:
            raw = input("\n> ").strip()
        except EOFError:
            break
        if not raw:
            continue
        words = raw.split()
        verb = words[0].lower()

        if verb in ("quit", "q"):
            break
        elif verb == "report":
            report(expenses)
        elif verb == "list":
            for r in sorted(expenses, key=lambda r: r["date"])[-10:]:
                print(f"  {r['date']}  {r['category']:<11}"
                      f"{r['amount']:>10,}  {r['note']}")
        elif verb == "add":
            if len(words) < 4:
                print("  add YYYY-MM-DD CATEGORY AMOUNT [NOTE...]")
                continue
            record, error = parse_expense(
                words[1], words[2], words[3], " ".join(words[4:])
            )
            if error:
                print(f"  rejected: {error}")
            else:
                expenses.append(record)
                print(f"  added {record['category']} {record['amount']} "
                      f"on {record['date']}")
        else:
            print(f"  unknown command {verb!r}")

# ===========================================================================
# VALIDATION DEMO — the rejections matter as much as the report
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'WHAT THE VALIDATOR REJECTS':^{WIDTH}}")
print("=" * WIDTH)

BAD = [
    ("2024-13-01", "food", "10.00", "impossible month"),
    ("14/03/2024", "food", "10.00", "wrong date format"),
    ("2024-03-14", "snacks", "10.00", "category not on the list"),
    ("2024-03-14", "food", "ten pounds", "amount is not a number"),
    ("2024-03-14", "food", "-5.00", "negative amount"),
    ("2024-03-14", "food", "0", "zero amount"),
    ("2024-3-4", "FOOD", "10.5", "loose but valid — should be ACCEPTED"),
]

for date, category, amount, why in BAD:
    record, error = parse_expense(date, category, amount, why)
    verdict = f"rejected: {error}" if error else f"accepted as {record['date']} {record['amount']}"
    print(f"  {str((date, category, amount)):<44}{verdict}")

print("""
  The last row is the interesting one. '2024-3-4' with category 'FOOD' and
  amount '10.5' is sloppy but unambiguous, so it is normalised rather than
  refused. Being strict about MEANING and generous about FORMAT is what
  makes a tool usable — and doing it in ONE function is what stops the two
  rules drifting apart.""")

report(expenses)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Every figure in the report is DERIVED from `expenses`. Add a record
#     interactively and re-run `report` — every total, share, ranking and
#     margin updates, because none of them was stored. Try instead keeping a
#     `running_total` variable and see how quickly it can disagree.
#
#   * Add budgets: a dict of category -> monthly limit, and a column showing
#     over/under. That is one dict and one comprehension.
#
#   * The cross-tab sums both margins and checks them against the grand
#     total. Deliberately corrupt one amount after aggregation and confirm
#     the check catches it. That check is a test (Day 57) in disguise.
#
#   * On Day 54 load the expenses from a CSV; on Day 55 save them to JSON;
#     on Day 61 use real `date` objects so "last 30 days" becomes possible;
#     on Day 77 plot the monthly bars with matplotlib.
