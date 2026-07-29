"""Day 035 build — one pipeline, four implementations, judged.

    python3 build.py

THE TASK, in English:

    From a list of raw sales lines, keep the completed orders over £100,
    apply each customer's discount, and report the total revenue and the
    three largest orders.

Four implementations. All four must produce IDENTICAL results — the build
checks that — so the only thing left to compare is how they READ.

This is a judgement exercise, not a technique one. The point is to be able
to say WHY, not to know which one this file prefers.
"""

import time
from functools import reduce
from operator import itemgetter

WIDTH = 76

RAW = """1001,ada,COMPLETED,240.00
1002,alan,cancelled,180.00
1003,grace,completed, 95.50
1004,ada,COMPLETED,1200.00
1005,katherine,completed,340.25
1006,alan,PENDING,500.00
1007,grace,completed,150.75
1008,ada,completed,99.99
1009,katherine,COMPLETED,875.00
1010,bjarne,completed,410.40
1011,bjarne,refunded,220.00
1012,grace,COMPLETED,610.00"""

DISCOUNTS = {"ada": 0.10, "grace": 0.05, "katherine": 0.15}
MINIMUM = 100.00


# ===========================================================================
# 1. THE EXPLICIT LOOP
# ===========================================================================

def pipeline_loop(raw):
    """Every step named, in the order it happens."""
    results = []
    for line in raw.splitlines():
        reference, customer, status, amount = line.split(",")
        if status.strip().lower() != "completed":
            continue
        value = float(amount.strip())
        if value <= MINIMUM:
            continue
        discount = DISCOUNTS.get(customer.strip().lower(), 0.0)
        results.append({
            "ref": reference.strip(),
            "customer": customer.strip().lower(),
            "gross": value,
            "net": round(value * (1 - discount), 2),
        })
    return results


# ===========================================================================
# 2. THE COMPREHENSION
# ===========================================================================

def pipeline_comprehension(raw):
    """One expression. Note the intermediate step to avoid splitting twice."""
    rows = [line.split(",") for line in raw.splitlines()]
    completed = [
        r for r in rows
        if r[2].strip().lower() == "completed" and float(r[3]) > MINIMUM
    ]
    return [
        {
            "ref": r[0].strip(),
            "customer": r[1].strip().lower(),
            "gross": float(r[3]),
            "net": round(
                float(r[3]) * (1 - DISCOUNTS.get(r[1].strip().lower(), 0.0)), 2
            ),
        }
        for r in completed
    ]


# ===========================================================================
# 3. THE FUNCTIONAL VERSION — map, filter, reduce
# ===========================================================================

def parse(line):
    ref, customer, status, amount = line.split(",")
    return {
        "ref": ref.strip(),
        "customer": customer.strip().lower(),
        "status": status.strip().lower(),
        "gross": float(amount.strip()),
    }


def is_wanted(row):
    return row["status"] == "completed" and row["gross"] > MINIMUM


def apply_discount(row):
    discount = DISCOUNTS.get(row["customer"], 0.0)
    return {
        "ref": row["ref"],
        "customer": row["customer"],
        "gross": row["gross"],
        "net": round(row["gross"] * (1 - discount), 2),
    }


def pipeline_functional(raw):
    """map/filter/map over NAMED functions. This is the readable version."""
    return list(
        map(apply_discount, filter(is_wanted, map(parse, raw.splitlines())))
    )


# ===========================================================================
# 4. THE SAME THING, WRITTEN BADLY — one expression, all lambdas
# ===========================================================================

def pipeline_lambdas(raw):
    """Deliberately unreadable. It works. Do not write this."""
    return list(map(lambda r: {"ref": r[0].strip(), "customer": r[1].strip().lower(), "gross": float(r[3]), "net": round(float(r[3]) * (1 - DISCOUNTS.get(r[1].strip().lower(), 0.0)), 2)}, filter(lambda r: r[2].strip().lower() == "completed" and float(r[3]) > MINIMUM, map(lambda line: line.split(","), raw.splitlines()))))  # noqa: E501


# ===========================================================================
# VERIFY THEY AGREE — otherwise there is nothing to compare
# ===========================================================================

VERSIONS = [
    ("explicit loop", pipeline_loop),
    ("comprehension", pipeline_comprehension),
    ("functional (named)", pipeline_functional),
    ("functional (lambdas)", pipeline_lambdas),
]

results = {name: func(RAW) for name, func in VERSIONS}
reference = results["explicit loop"]
all_agree = all(rows == reference for rows in results.values())

print("=" * WIDTH)
print(f"{'ONE PIPELINE, FOUR IMPLEMENTATIONS':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'input lines':<40}{len(RAW.splitlines()):>{WIDTH - 40}}")
print(f"{'rows surviving the filter':<40}{len(reference):>{WIDTH - 40}}")
print(f"{'all four produce identical output':<40}"
      f"{str(all_agree):>{WIDTH - 40}}")

if not all_agree:
    raise SystemExit("The versions disagree — there is nothing to compare.")

# ===========================================================================
# THE ANSWER
# ===========================================================================

total_gross = sum(r["gross"] for r in reference)
total_net = sum(r["net"] for r in reference)
top_three = sorted(reference, key=itemgetter("net"), reverse=True)[:3]

print()
print("-" * WIDTH)
print(f"{'REF':<8}{'CUSTOMER':<14}{'GROSS':>12}{'DISCOUNT':>11}{'NET':>12}")
print("-" * WIDTH)
for row in sorted(reference, key=itemgetter("net"), reverse=True):
    saved = row["gross"] - row["net"]
    print(f"{row['ref']:<8}{row['customer']:<14}{row['gross']:>12,.2f}"
          f"{saved:>11,.2f}{row['net']:>12,.2f}")
print("-" * WIDTH)
print(f"{'TOTAL':<22}{total_gross:>12,.2f}"
      f"{total_gross - total_net:>11,.2f}{total_net:>12,.2f}")
print()
print("TOP THREE BY NET")
for rank, row in enumerate(top_three, start=1):
    print(f"  {rank}. {row['ref']}  {row['customer']:<12}{row['net']:>10,.2f}")

# ===========================================================================
# THE JUDGEMENT
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE JUDGEMENT':^{WIDTH}}")
print("=" * WIDTH)

REPEATS = 2000
print(f"{'VERSION':<24}{'LINES':>7}{'CHARS':>8}{'ms/1k':>9}   {'VERDICT':<24}")
print("-" * WIDTH)

import inspect  # noqa: E402 - used only for the measurement below

VERDICTS = {
    "explicit loop": "clearest to modify",
    "comprehension": "clearest to read",
    "functional (named)": "fine; reads inside out",
    "functional (lambdas)": "never",
}

for name, func in VERSIONS:
    source = inspect.getsource(func)
    body = [ln for ln in source.splitlines() if ln.strip()
            and not ln.strip().startswith(("#", '"""'))]
    elapsed = 0.0
    start = time.perf_counter()
    for _ in range(REPEATS):
        func(RAW)
    elapsed = (time.perf_counter() - start) / REPEATS * 1000
    longest = max(len(ln) for ln in body)
    print(f"{name:<24}{len(body):>7}{longest:>8}{elapsed:>9.3f}   "
          f"{VERDICTS[name]:<24}")

print("-" * WIDTH)

helper_lines = sum(
    len([ln for ln in inspect.getsource(f).splitlines() if ln.strip()])
    for f in (parse, is_wanted, apply_discount)
)
print(f"""  NOTE: the LINES column measures each pipeline function only. The
  functional (named) row says 4, but it also needs parse, is_wanted and
  apply_discount — another {helper_lines} lines. Counting only the call site
  flatters it, which is exactly the trick a one-liner plays. Its real
  advantage is that those {helper_lines} lines are separately testable, not that
  there are fewer of them.""")
print("-" * WIDTH)
print("""
SPEED IS NOT THE ARGUMENT. All four are within noise of each other on this
data, and would stay that way at a hundred times the size. Choose on how it
READS, and take the speed as whatever it is.

  EXPLICIT LOOP        Every step is named and happens in order. The only
                       version where you can add logging, count what was
                       skipped, or stop early without restructuring. This
                       is what a beginner writes and what a maintainer
                       often wants.

  COMPREHENSION        Shortest honest version. Reads top to bottom in the
                       order the data flows. Note it needs an intermediate
                       `rows` variable, because otherwise it splits every
                       line twice — the cost the one-liner tries to hide.

  FUNCTIONAL (NAMED)   parse / is_wanted / apply_discount are individually
                       testable and reusable, which is a real advantage.
                       But the call reads INSIDE OUT: map(apply, filter(is,
                       map(parse, lines))) happens right to left.

  FUNCTIONAL (LAMBDAS) One statement, 336 characters, identical output. It
                       is not clever, it is a liability. Nobody — including
                       its author next week — can change it safely.

THE RANKING THIS FILE WOULD DEFEND

  1. comprehension        for a pipeline this size
  2. functional (named)   when the steps are reused elsewhere
  3. explicit loop        the moment anything needs logging or early exit
  4. never the lambdas

Notice that (3) becomes (1) as soon as the requirements grow — which is
exactly what happens to real code. Optimising for the shortest version
today buys a rewrite later.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a requirement: "log every line that was skipped, and why." Try it
#     in each of the four. The loop takes one line; the comprehension needs
#     a second pass; the lambda version needs rewriting from scratch. That
#     exercise settles the argument better than any style guide.
#
#   * Add a requirement: "stop after the first 5 qualifying orders." Same
#     experiment. Only the loop can `break`.
#
#   * pipeline_comprehension calls float(r[3]) three times. Fix it with the
#     `for parts in [expensive()]` trick and decide honestly whether the
#     result is still more readable than the loop.
#
#   * Replace the whole thing with pandas on Day 73. It becomes four lines
#     and reads better than all four of these — which is what a purpose-
#     built tool buys.
