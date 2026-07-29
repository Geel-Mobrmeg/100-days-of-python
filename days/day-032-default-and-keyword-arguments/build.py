"""Day 032 build — a report generator whose common call is one argument long.

    python3 build.py

The whole exercise is the signature:

    def report(rows, *, title=..., columns=None, sort_by=None, ...)

ONE required positional argument — the data. Everything else is a
keyword-only option with a default chosen so the common case needs nothing.

Judge it by the calls, not by the definition. They are at the bottom.
"""

from decimal import Decimal

WIDTH = 78

ROWS = [
    {"name": "Leeds", "region": "north", "sales": Decimal("41000"), "staff": 12},
    {"name": "York", "region": "north", "sales": Decimal("18200"), "staff": 5},
    {"name": "Bristol", "region": "west", "sales": Decimal("30500"), "staff": 9},
    {"name": "Bath", "region": "west", "sales": Decimal("22750"), "staff": 6},
    {"name": "Truro", "region": "west", "sales": Decimal("9400"), "staff": 3},
]


def report(
    rows,
    *,
    title="REPORT",
    columns=None,
    sort_by=None,
    descending=True,
    top=None,
    layout="table",
    totals=True,
    bar_column=None,
    width=WIDTH,
):
    """Return a formatted report of `rows` as a string.

    Every option is keyword-only, so a call can never become
    report(rows, "x", None, True, 5, "csv") — a line nobody can read and
    which breaks silently the day the parameters are reordered.

    `columns=None` means "all of them, in the order of the first row".
    None is used rather than a mutable default: a list default here would
    be the B006 bug, and it would let one call's column choice leak into
    the next.
    """
    if not rows:
        return f"{title}\n(no data)"

    columns = list(columns) if columns else list(rows[0])

    ordered = list(rows)                       # never sort the caller's list
    if sort_by:
        ordered.sort(key=lambda r: r.get(sort_by), reverse=descending)
    if top:
        ordered = ordered[:top]

    numeric = {
        c for c in columns
        if all(isinstance(r.get(c), (int, float, Decimal)) for r in ordered)
    }

    if layout == "csv":
        lines = [",".join(columns)]
        lines += [",".join(str(r.get(c, "")) for c in columns) for r in ordered]
        if totals:
            lines.append(",".join(
                str(sum(r.get(c, 0) for r in ordered)) if c in numeric else ""
                for c in columns
            ))
        return "\n".join(lines)

    if layout == "list":
        lines = [title, "-" * len(title)]
        for row in ordered:
            lines.append(f"{row.get(columns[0])}")
            for c in columns[1:]:
                lines.append(f"    {c:<12}{row.get(c, '-')}")
        return "\n".join(lines)

    # --- the default: a table -------------------------------------------
    label_w = max(len(str(c)) for c in columns)
    label_w = max(label_w, max(len(str(r.get(columns[0], ""))) for r in ordered))
    label_w = min(label_w + 2, 24)
    cell_w = 12
    bar_w = 0
    if bar_column and bar_column in numeric:
        bar_w = max(10, width - label_w - cell_w * (len(columns) - 1) - 4)

    lines = ["=" * width, f"{title:^{width}}", "=" * width]
    header = f"{str(columns[0]):<{label_w}}"
    header += "".join(f"{str(c):>{cell_w}}" for c in columns[1:])
    if bar_w:
        header += f"  {'':<{bar_w - 2}}"
    lines.append(header)
    lines.append("-" * width)

    peak = max((r.get(bar_column, 0) for r in ordered), default=0) if bar_w else 0

    for row in ordered:
        line = f"{str(row.get(columns[0], '')):<{label_w}}"
        for c in columns[1:]:
            value = row.get(c, "-")
            if isinstance(value, Decimal):
                line += f"{value:>{cell_w},}"
            elif isinstance(value, (int, float)):
                line += f"{value:>{cell_w},}"
            else:
                line += f"{str(value):>{cell_w}}"
        if bar_w and peak:
            filled = int(row.get(bar_column, 0) / peak * (bar_w - 3))
            line += "  " + "#" * filled
        lines.append(line)

    if totals:
        lines.append("-" * width)
        line = f"{'TOTAL':<{label_w}}"
        for c in columns[1:]:
            if c in numeric:
                line += f"{sum(r.get(c, 0) for r in ordered):>{cell_w},}"
            else:
                line += f"{'':>{cell_w}}"
        lines.append(line)

    lines.append("=" * width)
    return "\n".join(lines)


# ===========================================================================
# JUDGE THE SIGNATURE BY THE CALLS
# ===========================================================================

print(report(ROWS))

print("\n\n>>> report(ROWS)")
print("    The common case. ONE argument. Sensible title, all columns,")
print("    input order, totals on, table layout. Nothing to remember.")

# ---------------------------------------------------------------------------

print("\n" + report(
    ROWS,
    title="SALES BY STORE",
    sort_by="sales",
    bar_column="sales",
))
print("\n>>> report(ROWS, title=..., sort_by='sales', bar_column='sales')")
print("    Three options, each one obvious at the call site. Reordering")
print("    them would change nothing, because they are named.")

# ---------------------------------------------------------------------------

print("\n" + report(
    ROWS,
    title="TOP 3 BY STAFF",
    columns=["name", "staff"],
    sort_by="staff",
    top=3,
    bar_column="staff",
    width=52,
))

# ---------------------------------------------------------------------------

print("\n\n>>> report(ROWS, layout='csv', columns=['name', 'sales'])")
print("-" * WIDTH)
print(report(ROWS, layout="csv", columns=["name", "sales"], sort_by="sales"))

print("\n\n>>> report(ROWS[:2], layout='list', totals=False)")
print("-" * WIDTH)
print(report(ROWS[:2], layout="list", totals=False))

print("\n\n>>> report([])")
print("-" * WIDTH)
print(report([]))

# ===========================================================================
# WHAT THE SIGNATURE PREVENTS
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'WHAT THE KEYWORD-ONLY * PREVENTS':^{WIDTH}}")
print("=" * WIDTH)

try:
    report(ROWS, "SALES", None, "sales")
except TypeError as e:
    print(f"  report(ROWS, 'SALES', None, 'sales')")
    print(f"    -> TypeError: {e}")

print("""
  Without the *, that call would have worked, and it would have been:
  unreadable at the call site, silently broken the day someone inserts a
  parameter, and impossible to search for. The single character `*` in the
  signature buys all of that.

  Note also the two `None` defaults — `columns=None` and `sort_by=None`.
  `columns=[]` would be the B006 mutable-default bug, and it would let one
  call's column list leak into the next. Confirm with:

      ruff check --isolated --select B build.py""")

# ===========================================================================
# THE MUTABLE DEFAULT, ONE MORE TIME, WHERE IT WOULD HAVE LANDED
# ===========================================================================

print()
print("-" * WIDTH)
print("IF columns HAD DEFAULTED TO A LIST")
print("-" * WIDTH)


def broken_report(rows, columns=[]):        # noqa: B006 - the exhibit
    """Deliberately wrong, to show what would have happened."""
    if not columns:
        columns.extend(rows[0])             # mutates THE DEFAULT
    return columns


first = broken_report([{"name": 1, "sales": 2}])
second = broken_report([{"region": 3, "staff": 4}])
print(f"  first call:  {first}")
print(f"  second call: {second}")
print(f"  same object: {first is second}")
print("""
  The second report asked for different data and got the first report's
  columns — because the default list was created ONCE, when `def` ran, and
  the first call filled it in permanently.

  This is why every optional collection in this file defaults to None.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a `group_by=` option that prints subtotals per group. It should
#     default to None and require no change to any existing call — which is
#     the real payoff of keyword-only options.
#
#   * Add `layout="markdown"`. Note that `layout` is a string rather than
#     three boolean flags; three booleans would allow nonsense states like
#     csv=True, table=True.
#
#   * Try to write the same generator with all ten parameters positional.
#     Then write the call for "top 3 by staff, no totals, width 52" and
#     count how long you have to stare at it.
#
#   * On Day 37 add an @cache decorator to report() and discover why a
#     function taking a list argument cannot be cached without more work.
