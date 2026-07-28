"""Day 028 build — five questions about a hostile config, without crashing.

The config below is deliberately awful, in exactly the ways real config
files are awful. Every defect is labelled. The program must answer all five
questions without a single traceback, and must be able to say WHICH data was
unusable rather than silently reporting a smaller number.

    python3 build.py
"""

import json

WIDTH = 74

# ===========================================================================
# THE CONFIG. Every defect here has been seen in production somewhere.
# ===========================================================================

CONFIG = {
    "app": {"name": "shopmind", "version": "3.0"},
    "defaults": {"currency": "GBP", "opening": "09:00", "closing": "18:00"},
    "regions": {
        "north": {
            "manager": "Ada Lovelace",
            "stores": [
                {
                    "name": "Leeds",
                    "staff": [
                        {"name": "Kim", "role": "manager", "hours": 37.5},
                        {"name": "Raj", "role": "sales", "hours": 20},
                    ],
                    "sales": {"2024": {"q1": 41000, "q2": 45500}},
                },
                {
                    "name": "York",
                    # DEFECT 1: no "staff" key at all
                    "sales": {"2024": {"q1": 18200}},        # and no q2
                },
            ],
        },
        "south": {
            "manager": "Alan Turing",
            "stores": [],                     # DEFECT 2: an empty list
        },
        "west": {
            # DEFECT 3: no "manager" key
            "stores": [
                {
                    "name": "Bristol",
                    "staff": [
                        {"name": "Sam", "role": "sales"},   # DEFECT 4: no hours
                        {"name": "Lee", "role": "sales", "hours": "part-time"},
                        # DEFECT 5: hours is a STRING, not a number
                    ],
                    "sales": {"2024": {"q1": 30500, "q2": 33000}},
                },
                {
                    "name": "Bath",
                    "staff": [{"name": "Jo", "role": "manager", "hours": 40}],
                    "sales": {},              # DEFECT 6: empty sales dict
                },
            ],
        },
        # DEFECT 7: a region whose value is not a dict at all
        "east": "closed pending review",
    },
}


def dig(data, *keys, default=None):
    """Walk a nested structure by keys and indices. Never raises."""
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
            return default
        if data is None:
            return default
    return data


# ===========================================================================
# STEP 1 — FLATTEN. Do this once, guard everything, and record what was
# unusable instead of quietly dropping it.
# ===========================================================================

rows = []
problems = []

regions = CONFIG.get("regions", {})
if not isinstance(regions, dict):
    problems.append("'regions' is not a mapping — nothing can be read")
    regions = {}

for region_name, region in regions.items():
    # DEFECT 7 lands here: a string where a dict belongs. .get() chains do
    # NOT protect against this; an explicit type check does.
    if not isinstance(region, dict):
        problems.append(
            f"region {region_name!r} is a {type(region).__name__}, not a "
            f"mapping — skipped ({region!r})"
        )
        continue

    manager = region.get("manager")
    if manager is None:
        problems.append(f"region {region_name!r} has no manager")
        manager = "(unassigned)"

    stores = region.get("stores", [])
    if not isinstance(stores, list):
        problems.append(f"region {region_name!r}: 'stores' is not a list")
        stores = []
    if not stores:
        problems.append(f"region {region_name!r} has no stores")

    for store in stores:
        if not isinstance(store, dict):
            problems.append(f"{region_name}: a store entry is not a mapping")
            continue

        store_name = store.get("name", "(unnamed)")
        staff = store.get("staff")
        if staff is None:
            problems.append(f"{region_name}/{store_name}: no staff list")
            staff = []

        # Hours: missing on one person, a STRING on another. Sum only what
        # is genuinely numeric, and count the rest rather than hiding it.
        hours_total = 0.0
        hours_unknown = 0
        for member in staff:
            value = member.get("hours") if isinstance(member, dict) else None
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                hours_total += value
            else:
                hours_unknown += 1
                who = dig(member, "name", default="?")
                problems.append(
                    f"{region_name}/{store_name}: {who} has unusable hours "
                    f"({value!r})"
                )

        sales_2024 = dig(store, "sales", "2024", default={})
        if not isinstance(sales_2024, dict):
            sales_2024 = {}
        quarters = {
            q: v for q, v in sales_2024.items()
            if isinstance(v, (int, float))
        }
        if not quarters:
            problems.append(f"{region_name}/{store_name}: no 2024 sales")

        rows.append({
            "region": region_name,
            "manager": manager,
            "store": store_name,
            "headcount": len(staff),
            "hours": hours_total,
            "hours_unknown": hours_unknown,
            "quarters": len(quarters),
            "sales": sum(quarters.values()),
        })

# ===========================================================================
# THE FIVE QUESTIONS
# ===========================================================================

print("=" * WIDTH)
print(f"{'CONFIG REPORT':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'app':<30}{dig(CONFIG, 'app', 'name', default='?'):>{WIDTH - 30}}")
print(f"{'version':<30}{dig(CONFIG, 'app', 'version', default='?'):>{WIDTH - 30}}")
print(f"{'regions declared':<30}{len(regions):>{WIDTH - 30}}")
print(f"{'stores readable':<30}{len(rows):>{WIDTH - 30}}")
print(f"{'problems found':<30}{len(problems):>{WIDTH - 30}}")

# ---- Q1 ------------------------------------------------------------------
print()
print("-" * WIDTH)
print("Q1. How many stores are there, and where?")
print("-" * WIDTH)
by_region = {}
for row in rows:
    by_region.setdefault(row["region"], []).append(row["store"])
for region in sorted(regions):
    names = by_region.get(region, [])
    print(f"  {region:<10}{len(names):>3}   {', '.join(names) or '(none readable)'}")

# ---- Q2 ------------------------------------------------------------------
print()
print("-" * WIDTH)
print("Q2. Who manages each region?")
print("-" * WIDTH)
seen = {}
for row in rows:
    seen.setdefault(row["region"], row["manager"])
for region in sorted(regions):
    print(f"  {region:<10}{seen.get(region, '(no readable stores)')}")

# ---- Q3 ------------------------------------------------------------------
print()
print("-" * WIDTH)
print("Q3. Total contracted hours — and how much is unaccounted for?")
print("-" * WIDTH)
print(f"  {'STORE':<16}{'HEADS':>7}{'HOURS':>9}{'UNKNOWN':>9}")
for row in sorted(rows, key=lambda r: -r["hours"]):
    print(f"  {row['store']:<16}{row['headcount']:>7}"
          f"{row['hours']:>9.1f}{row['hours_unknown'] or '':>9}")
total_hours = sum(r["hours"] for r in rows)
total_unknown = sum(r["hours_unknown"] for r in rows)
print(f"  {'-' * 40}")
print(f"  {'TOTAL':<16}{sum(r['headcount'] for r in rows):>7}"
      f"{total_hours:>9.1f}{total_unknown:>9}")
print(f"\n  {total_unknown} staff member(s) have no usable hours. The total")
print("  above is therefore a LOWER BOUND, and the report says so rather")
print("  than presenting an incomplete sum as if it were complete.")

# ---- Q4 ------------------------------------------------------------------
print()
print("-" * WIDTH)
print("Q4. 2024 sales by store, and which quarters are missing?")
print("-" * WIDTH)
best = max((r["sales"] for r in rows), default=0) or 1
for row in sorted(rows, key=lambda r: -r["sales"]):
    bar = "#" * int(row["sales"] / best * 24)
    flag = "" if row["quarters"] == 2 else f"  ({row['quarters']}/2 quarters)"
    print(f"  {row['store']:<12}{row['sales']:>9,}  {bar:<24}{flag}")
print(f"  {'-' * 56}")
print(f"  {'TOTAL':<12}{sum(r['sales'] for r in rows):>9,}")

# ---- Q5 ------------------------------------------------------------------
print()
print("-" * WIDTH)
print("Q5. What is wrong with this config?")
print("-" * WIDTH)
for problem in problems:
    print(f"  - {problem}")

print()
print("=" * WIDTH)
print(f"""Not one of those {len(problems)} defects raised an exception, and not one of
them was silently swallowed either. That is the whole target: a reader can
see both the numbers AND what the numbers are missing.

A traversal that crashes is annoying. A traversal that quietly reports
"total sales: 168,200" while skipping a store is dangerous.""")
print("=" * WIDTH)

print()
print("The flattened rows — a tree turned into a table, ready for Day 27's")
print("sorting, Day 25's counting, and Day 73's pandas:")
print(json.dumps(rows[:2], indent=2))


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add DEFECT 8: make "stores" a dict instead of a list in one region.
#     The isinstance check catches it; confirm the report still runs.
#
#   * The "east" region is a string. Try answering Q1 with a plain
#     .get() chain instead of the isinstance check and see which line
#     raises AttributeError. That is the failure mode .get() cannot cover.
#
#   * `defaults` holds opening and closing times that no store overrides.
#     Add a lookup that uses a store's own value if present and falls back
#     to defaults — the config pattern behind almost every real application.
#
#   * Write the whole flattening step as one comprehension. It is possible
#     and it is much worse. Doing it is the fastest way to be convinced.
#
#   * On Day 55 load this from a real JSON file, and on Day 59 add type
#     hints so mypy can tell you which fields are optional.
