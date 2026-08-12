"""Day 054 build — cleaning a CSV nobody was careful with.

    python3 build.py                 # generate a messy file and clean it
    python3 build.py messy.csv out   # clean a file of your own

INPUT: a supplier export with everything real exports have — a BOM,
headers with spaces and capitals, padded values, three spellings of the
same category, prices as '£4.50' and '4,50' and '', a name with a comma,
a note with a newline inside it, two ragged rows, a duplicate SKU, and a
part code that must not become a number.

OUTPUT: two files.
    products-clean.csv        one row per product, normalised
    summary-by-category.csv   the report somebody actually asked for

...and a rejection report with LINE NUMBERS, because a cleaner that turns
23 rows into 17 and says nothing has hidden six problems.

Everything is written to a temporary directory that is removed at the end.
"""

import csv
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

WIDTH = 78

NULLS = {"", "-", "n/a", "na", "none", "null", "tbc", "?"}
CATEGORIES = {"hardware", "consumable", "premium", "general"}


# ###########################################################################
# THE MESSY INPUT
# ###########################################################################

MESSY = (
    # Headers as exported: capitals, spaces, a trailing space.
    "SKU , Product Name,Category ,Unit Price,Units In Stock,Part Code,Notes\r\n"
    'WID-001,Widget,hardware,4.50,150,0117,"fine"\r\n'
    'wid-002 , Bracket ,HARDWARE,£12.00, 40 ,0118,\r\n'
    'GZM-003,"Gizmo, large",Hardware,"1,299.00",12,0119,"quoted, with comma"\r\n'
    'DHK-004,Doohickey, consumable ,2.25,80,0120,"a note\r\nspanning two lines"\r\n'
    'THG-005,Thingummy,premium,,3,0121,no price\r\n'
    'SPR-006,Sprocket,Premium,48.00,,0122,no units\r\n'
    'CMP-007,Component,widgets,7.25,25,0123,unknown category\r\n'
    'FLG-008,Flange,general,-5.00,10,0124,negative price\r\n'
    'BSH-009,Bushing,general,3.50,-2,0125,negative units\r\n'
    'GRM-010,Grommet,general,0.75\r\n'                       # too few fields
    'CLP-011,Clip,general,1.20,500,0127,note,surplus,fields\r\n'   # too many
    'WID-001,Widget (updated),hardware,4.75,160,0117,duplicate sku\r\n'
    '\r\n'                                                    # a blank line
    'SKW-013,Skew,general,"4,50",7,0129,European decimal comma\r\n'
    'AMB-014,Ambiguous,general,"1,299",5,0130,is that 1299 or 1.299?\r\n'
    'BLT-015,Bolt,GENERAL,  2.00  ,  60  ,0131,padded everywhere\r\n'
    'NUT-016,Nut,general,0.10,1200,0132,fine\r\n'
    'ZZZ-017,,general,1.00,5,0133,no name\r\n'
)


def write_messy(path):
    """Write it with a BOM, exactly as a spreadsheet would."""
    path.write_bytes(b"\xef\xbb\xbf" + MESSY.encode("utf-8"))
    return path


# ###########################################################################
# THE FIELD CLEANERS — each returns (value, problem)
# ###########################################################################

def normalise_header(name):
    """'  Product Name ' -> 'product_name'. Do this once, at the top."""
    return name.strip().lower().replace(" ", "_")


def clean_text(value):
    return (value or "").strip()


def clean_code(value):
    """A part code is TEXT. int('0117') is 117 and the zero is gone."""
    text = clean_text(value)
    return text, None if text else "part code is empty"


def clean_category(value):
    text = clean_text(value).lower()
    if text in NULLS:
        return None, "category is missing"
    if text not in CATEGORIES:
        return None, f"category {text!r} is not one of {sorted(CATEGORIES)}"
    return text, None


def clean_money(value):
    """Parse a price written by somebody who was not thinking about you.

    THE RULES, stated because they are decisions and not facts:

        strip currency symbols and spaces      '£4.50'    -> 4.50
        one comma, two digits after it         '4,50'     -> 4.50
        commas with three digits after each    '1,299.00' -> 1299.00
        anything still ambiguous               '1,299'    -> REFUSED

    '1,299' is 1299 in Britain and 1.299 in Germany. Guessing turns a
    thousandfold error into a silent one, so this refuses instead.
    """
    text = clean_text(value).replace("£", "").replace("$", "").replace("€", "")
    text = text.replace(" ", "")
    if text.lower() in NULLS:
        return None, "price is missing"

    if "," in text and "." in text:
        text = text.replace(",", "")                 # 1,299.00 -> 1299.00
    elif text.count(",") == 1:
        whole, _, fraction = text.partition(",")
        if len(fraction) == 2:
            text = f"{whole}.{fraction}"             # 4,50 -> 4.50
        else:
            return None, f"price {value.strip()!r} is ambiguous (1,299 or 1.299?)"

    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None, f"price {value.strip()!r} is not a number"
    if amount <= 0:
        return None, f"price {amount} is not greater than zero"
    return amount.quantize(Decimal("0.01")), None


def clean_units(value):
    text = clean_text(value)
    if text.lower() in NULLS:
        return None, "units is missing"
    try:
        units = int(text.replace(",", ""))
    except ValueError:
        return None, f"units {text!r} is not a whole number"
    if units < 0:
        return None, f"units {units} is negative"
    return units, None


# ###########################################################################
# THE CLEANER
# ###########################################################################

FIELDS = ["sku", "product_name", "category", "unit_price",
          "units_in_stock", "part_code", "notes"]


def clean(source):
    """Read a messy CSV. Return (rows, rejections, tally).

    Every rejection carries the FILE LINE NUMBER. On a 40,000-row export
    that is the difference between a fixable report and a shrug.
    """
    rows, rejections = [], []
    tally = Counter()
    seen = {}

    #  utf-8-sig   strips the BOM if there is one, and is harmless if not
    #  newline=""  so a newline inside a quoted field survives intact
    with open(source, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        raw_header = next(reader)
        header = [normalise_header(name) for name in raw_header]
        tally["columns"] = len(header)

        for raw in reader:
            line = reader.line_num          # the FILE line, not the row index
            tally["rows read"] += 1

            if not any(field.strip() for field in raw):
                tally["blank rows"] += 1
                continue

            # THE SHAPE CHECK. DictReader would have done this silently.
            if len(raw) != len(header):
                rejections.append((line, raw[0] if raw else "?",
                                   f"has {len(raw)} fields, header has "
                                   f"{len(header)}"))
                tally["wrong shape"] += 1
                continue

            record = dict(zip(header, raw))
            problems = []

            sku = clean_text(record["sku"]).upper()
            if not sku:
                problems.append("sku is empty")
            name = clean_text(record["product_name"])
            if not name:
                problems.append("product name is empty")

            category, problem = clean_category(record["category"])
            problems += [problem] if problem else []
            price, problem = clean_money(record["unit_price"])
            problems += [problem] if problem else []
            units, problem = clean_units(record["units_in_stock"])
            problems += [problem] if problem else []
            code, problem = clean_code(record["part_code"])
            problems += [problem] if problem else []

            if problems:
                rejections.append((line, sku or "?", "; ".join(problems)))
                tally["rejected"] += 1
                continue

            cleaned = {
                "sku": sku,
                "product_name": name,
                "category": category,
                "unit_price": f"{price:.2f}",
                "units_in_stock": units,
                "part_code": code,
                "notes": clean_text(record["notes"]).replace("\r\n", " ")
                                                    .replace("\n", " "),
            }

            if sku in seen:
                # DECIDED, not defaulted: the later row wins, and the
                # replacement is REPORTED rather than done quietly.
                tally["duplicates replaced"] += 1
                rejections.append((seen[sku]["line"], sku,
                                   f"superseded by the row at line {line}"))
                rows[seen[sku]["index"]] = cleaned
            else:
                seen[sku] = {"line": line, "index": len(rows)}
                rows.append(cleaned)
            tally["accepted"] += 1

    return rows, rejections, tally


def write_clean(rows, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_summary(rows, path):
    """The report: one line per category, sorted by value."""
    groups = defaultdict(lambda: {"products": 0, "units": 0,
                                  "value": Decimal("0")})
    for row in rows:
        group = groups[row["category"]]
        group["products"] += 1
        group["units"] += row["units_in_stock"]
        group["value"] += Decimal(row["unit_price"]) * row["units_in_stock"]

    lines = [
        {"category": category,
         "products": g["products"],
         "units": g["units"],
         "stock_value": f"{g['value']:.2f}",
         "average_price": f"{g['value'] / g['units']:.2f}" if g["units"] else ""}
        for category, g in groups.items()
    ]
    lines.sort(key=lambda r: Decimal(r["stock_value"]), reverse=True)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "products", "units",
                                               "stock_value", "average_price"])
        writer.writeheader()
        writer.writerows(lines)
    return lines


# ###########################################################################
# RUN IT
# ###########################################################################

if len(sys.argv) >= 2:
    SOURCE = Path(sys.argv[1])
    WORK = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    WORK.mkdir(parents=True, exist_ok=True)
    TEMPORARY = False
else:
    WORK = Path(tempfile.mkdtemp(prefix="day054-"))
    SOURCE = write_messy(WORK / "suppliers-messy.csv")
    TEMPORARY = True

rows, rejections, tally = clean(SOURCE)
clean_path = write_clean(rows, WORK / "products-clean.csv")
summary = write_summary(rows, WORK / "summary-by-category.csv")

print("=" * WIDTH)
print(f"{'CLEANING A SUPPLIER EXPORT':^{WIDTH}}")
print("=" * WIDTH)
print(f"  {'source':<24}{SOURCE.name}  ({SOURCE.stat().st_size:,} bytes)")
BOM = b"\xef\xbb\xbf"
has_bom = SOURCE.read_bytes()[:3] == BOM
print(f"  {'starts with a BOM':<24}{has_bom}")
print()
print(f"  {'rows read':<34}{tally['rows read']:>6}")
for label, count in [("blank rows skipped", tally["blank rows"]),
                     ("wrong shape", tally["wrong shape"]),
                     ("rejected on content", tally["rejected"]),
                     ("accepted", tally["accepted"])]:
    print(f"    {label:<32}{count:>6}")
print(f"    {'...of those, superseded by a later':<32}"
      f"{tally['duplicates replaced']:>6}")
print(f"    {'   row with the same sku':<32}{'':>6}")
print(f"  {'ROWS WRITTEN OUT':<34}{len(rows):>6}")


# ###########################################################################
# THE REJECTIONS, WITH LINE NUMBERS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT WAS DROPPED, AND WHY':^{WIDTH}}")
print("=" * WIDTH)
print(f"\n  {'LINE':>5}  {'SKU':<10}REASON")
print("  " + "-" * (WIDTH - 4))
for line, sku, reason in rejections:
    print(f"  {line:>5}  {sku:<10}{reason[:WIDTH - 22]}")

print("""
  Every one names the line you would open in a text editor. Note the two
  that are NOT data errors:

    * the ragged rows are a FILE problem — a stray comma inside an
      unquoted field, almost always
    * the superseded duplicate is a DECISION (last row wins) that has been
      written down instead of happening quietly""")


# ###########################################################################
# THE BEFORE AND AFTER
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'BEFORE AND AFTER':^{WIDTH}}")
print("=" * WIDTH)

with open(SOURCE, encoding="utf-8-sig", newline="") as f:
    raw_rows = [r for r in csv.reader(f)][1:]

interesting = ["WID-002", "GZM-003", "SKW-013", "BLT-015"]
print()
for row in rows:
    if row["sku"] not in interesting:
        continue
    before = next((r for r in raw_rows if r and r[0].strip().upper()
                   == row["sku"]), None)
    if not before:
        continue
    print(f"  {row['sku']}")
    print(f"    before   {before[:5]}")
    print(f"    after    {[row[f] for f in FIELDS[:5]]}")

print("""
  ' Bracket ' -> 'Bracket', 'HARDWARE' -> 'hardware', '£12.00' -> '12.00',
  ' 40 ' -> 40, and '4,50' -> '4.50'. None of those is clever. All of them
  are the difference between a report with one 'hardware' row and a report
  with three.""")


# ###########################################################################
# THE OUTPUT FILES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE TWO FILES THIS PRODUCES':^{WIDTH}}")
print("=" * WIDTH)

for path in (clean_path, WORK / "summary-by-category.csv"):
    print(f"\n  {path.name}  ({path.stat().st_size:,} bytes)")
    with open(path, encoding="utf-8", newline="") as f:
        for index, line in enumerate(f):
            if index > 5:
                print("    ...")
                break
            print(f"    {line.rstrip()[:WIDTH - 6]}")


# ###########################################################################
# THE CHECKS — including a full round trip
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

# Round trip: read back what was written and compare it to what was meant.
with open(clean_path, encoding="utf-8", newline="") as f:
    read_back = list(csv.DictReader(f))

round_tripped = all(
    all(str(written[field]) == read[field] for field in FIELDS)
    for written, read in zip(rows, read_back)
)

# The naive parser, on the same file, for comparison.
naive_wrong = 0
for line in SOURCE.read_text(encoding="utf-8-sig").splitlines()[1:]:
    if line.strip() and len(line.split(",")) != 7:
        naive_wrong += 1

summary_units = sum(int(r["units"]) for r in summary)
summary_value = sum(Decimal(r["stock_value"]) for r in summary)
cleaned_units = sum(r["units_in_stock"] for r in rows)
cleaned_value = sum(Decimal(r["unit_price"]) * r["units_in_stock"] for r in rows)

claims = [
    ("the BOM was stripped, so the first column is usable",
     read_back[0].get("sku") is not None),
    ("nothing was silently dropped",
     tally["rows read"] == tally["blank rows"] + tally["wrong shape"]
     + tally["rejected"] + tally["accepted"]),
    ("every rejection has a line number",
     all(isinstance(line, int) and line > 0 for line, _, _ in rejections)),
    ("the output round-trips exactly", round_tripped),
    ("...and reads back with plain utf-8 (no BOM written)",
     clean_path.read_bytes()[:3] != BOM),
    ("the summary totals match the cleaned rows",
     summary_units == cleaned_units and summary_value == cleaned_value),
    ("skus are unique after cleaning",
     len({r["sku"] for r in rows}) == len(rows)),
    ("the duplicate kept the LATER row",
     next(r for r in rows if r["sku"] == "WID-001")["unit_price"] == "4.75"),
    ("part codes kept their leading zero",
     all(r["part_code"].startswith("0") for r in rows)),
    ("the embedded newline did not create an extra row",
     tally["rows read"] == 18),
    ("categories are one spelling each",
     {r["category"] for r in rows} <= CATEGORIES),
    ("the ambiguous '1,299' was refused, not guessed",
     any("ambiguous" in reason for _, _, reason in rejections)),
    ("...while the unambiguous '1,299.00' was accepted",
     any(r["unit_price"] == "1299.00" for r in rows)),
    ("a naive split(',') would have mis-parsed rows",
     naive_wrong > 0),
]

print()
for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(p for _, p in claims)} of {len(claims)} checks pass")

print(f"""
  THE TENTH CHECK IS THE ONE THAT PROVES THE PARSER. DHK-004's note
  contains a real newline, so the file has more LINES than it has ROWS —
  {len(MESSY.splitlines())} against {tally['rows read']}. `for line in f` would have produced two
  broken records there and nothing would have complained.

  THE TWELFTH AND THIRTEENTH ARE A PAIR. '1,299.00' is unambiguous and
  becomes 1299.00; '1,299' is 1299 in Britain and 1.299 in Germany, so it
  is REFUSED with its line number. A cleaner that guesses is a cleaner
  that is wrong by a factor of a thousand, silently, on somebody else's
  data.

  A NAIVE split(',') GETS {naive_wrong} ROWS WRONG in this file — the quoted commas,
  the embedded newline and the surplus fields.""")
print("=" * WIDTH)

if TEMPORARY:
    shutil.rmtree(WORK, ignore_errors=True)
    print(f"\n(temporary directory {WORK} removed)", file=sys.stderr)
else:
    print(f"\nwrote {clean_path} and summary-by-category.csv", file=sys.stderr)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Swap the shape check for DictReader and watch the ragged rows go
#     through silently, with None where a price should be. Find where the
#     TypeError finally surfaces.
#
#   * Change the duplicate rule to "first wins" and to "raise". All three
#     are defensible; only one is right for your data, and the point is
#     that you chose.
#
#   * Add a --dry-run that reports without writing (Day 56 does this
#     properly), and a --strict that exits non-zero if anything was
#     rejected. The second one is what you want in a nightly job.
#
#   * Write the rejections to a rejects.csv with the original row intact,
#     so a human can fix and re-submit exactly the rows that failed.
#
#   * Read the cleaned file with encoding='utf-8-sig' and confirm it still
#     works. That is why it is a safe default.
#
#   * On Day 74, do the same job with pandas in about fifteen lines — and
#     then find out what it did with '1,299' without asking you.
