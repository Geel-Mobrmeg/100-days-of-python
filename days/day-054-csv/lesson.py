"""Day 054 — CSV: the format everyone thinks is simple.

    python3 lesson.py

Everything runs in a scratch directory that is deleted at the end.
"""

import csv
import io
import os
import shutil
import sys
import tempfile

WIDTH = 76

WORK = tempfile.mkdtemp(prefix="day054-")
os.chdir(WORK)

# ---------------------------------------------------------------------------
# 1. Why not line.split(",")
# ---------------------------------------------------------------------------

print("=" * WIDTH)
TITLE_1 = "1. WHY NOT line.split(',')"
print(f"{TITLE_1:^{WIDTH}}")
print("=" * WIDTH)

ROW = [
    "Lovelace, Ada",           # a comma INSIDE a field
    'she said "hello"',        # quotes inside a field
    "line one\nline two",      # a NEWLINE inside a field
    "",                        # an empty field
    "  padded  ",              # significant whitespace
    "0117",                    # a leading zero that is not a number
]

buffer = io.StringIO()
csv.writer(buffer).writerow(ROW)
encoded = buffer.getvalue()

print("\n  six fields, written properly by csv.writer:\n")
print(f"    {encoded.rstrip()!r}")

NAIVE_LABEL = "line.split(',')"
naive = encoded.rstrip("\r\n").split(",")
proper = next(csv.reader(io.StringIO(encoded)))

print(f"\n  {'':<22}{'FIELDS':>8}   FIRST FIELD")
print(f"  {NAIVE_LABEL:<22}{len(naive):>8}   {naive[0]!r}")
print(f"  {'csv.reader':<22}{len(proper):>8}   {proper[0]!r}")
print(f"  {'expected':<22}{len(ROW):>8}   {ROW[0]!r}")

print(f"""
  THE SPLIT VERSION GOT {len(naive)} FIELDS INSTEAD OF {len(ROW)}, and its first field is
  half a name. Every one of those six values is legal CSV and every one
  breaks a hand-rolled parser:

    a comma in a field      ->  quoted, and split() cuts it in half
    a quote in a field      ->  doubled ("" ), and split() keeps both
    a NEWLINE in a field    ->  one record spans two lines, so even
                                `for line in f` is wrong
    an empty field          ->  ,, — is that empty or missing?
    leading whitespace      ->  preserved, and usually not wanted
    '0117'                  ->  a string. int() would eat the zero.

  THE RULE: never parse CSV by hand. Not "usually", not "unless the data
  is simple" — the data becomes complicated the week after you ship.""")


# ---------------------------------------------------------------------------
# 2. newline="" — the argument that looks like noise
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
TITLE_2 = '2. newline="" IS NOT OPTIONAL'
print(f"{TITLE_2:^{WIDTH}}")
print("=" * WIDTH)

# A file with CRLF line endings and a CRLF *inside* a quoted field, which
# is what a Windows-produced export actually looks like.
with open("crlf.csv", "wb") as f:
    f.write(b'name,note\r\n"Ada","line1\r\nline2"\r\n"Alan","fine"\r\n')

print()
for label, kwargs in [("open(...)", {}), ("open(..., newline='')", {"newline": ""})]:
    with open("crlf.csv", encoding="utf-8", **kwargs) as f:
        rows = list(csv.reader(f))
    print(f"  {label:<26}note field = {rows[1][1]!r}")

print("""
  Without newline='', Python's universal-newline translation rewrites the
  \\r\\n INSIDE the quoted field before csv ever sees it. The row count is
  right and the DATA IS SILENTLY CHANGED — which is the worst kind of bug,
  because every test that counts rows still passes.

  ON WRITING, on Windows, the same omission is more visible: the csv writer
  emits \\r\\n, text mode turns the \\n into \\r\\n, and you get \\r\\r\\n — a
  blank row between every record. Everybody has seen that file.

      open(path, newline="")      always, for read AND write
      encoding="utf-8"            always, as ever""")


# ---------------------------------------------------------------------------
# 3. reader/writer and DictReader/DictWriter
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. FOUR OBJECTS':^{WIDTH}}")
print("=" * WIDTH)

PRODUCTS = [
    ["sku", "name", "category", "price", "units"],
    ["WID-001", "Widget", "hardware", "4.50", "150"],
    ["GZM-002", "Gizmo, large", "hardware", "12.00", "40"],
    ["DHK-003", "Doohickey", "consumable", "2.25", "80"],
]

with open("products.csv", "w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(PRODUCTS)

with open("products.csv", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)                     # the header is just row 0
    first = next(reader)

print(f"\n  csv.reader     header {header}")
print(f"                 row    {first}")

with open("products.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

print(f"\n  csv.DictReader row    {rows[0]}")
print(f"                 access row['price'] -> {rows[0]['price']!r}")

print("""
  reader      a list per row. Positional. Fast, and breaks the day
              somebody inserts a column.
  DictReader  a dict per row, keyed by the header. Reads like the data.

  USE DictReader unless you are counting bytes. `row['price']` still works
  when a column moves; `row[3]` does not.""")

# ...writing

summary = [
    {"category": "hardware", "products": 2, "units": 190},
    {"category": "consumable", "products": 1, "units": 80},
]

with open("summary.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["category", "products", "units"])
    writer.writeheader()                      # ← easy to forget
    writer.writerows(summary)

with open("summary.csv", encoding="utf-8", newline="") as f:
    print("\n  DictWriter wrote:")
    for line in f:
        print(f"    {line.rstrip()}")

print("""
  DictWriter needs fieldnames, and they decide the COLUMN ORDER — a dict
  is not a schema. Two more arguments earn their place:

      restval='n/a'            what to write when a key is missing
      extrasaction='ignore'    what to do about keys you did not declare
                               (the default is to RAISE, which is usually
                               what you want)""")


# ---------------------------------------------------------------------------
# 4. Ragged rows
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. ROWS THAT DO NOT MATCH THE HEADER':^{WIDTH}}")
print("=" * WIDTH)

RAGGED = "sku,name,price\nWID-001,Widget,4.50\nGZM-002,Gizmo\nDHK-003,D,1,extra\n"

print()
for row in csv.DictReader(io.StringIO(RAGGED)):
    print(f"  {row}")

print("""
  DictReader does NOT raise on a ragged row.

    too few fields   the missing keys get None   (restval= changes this)
    too many         the surplus lands under the key None, as a LIST

  Both are silent. `row['price']` on the short row returns None, and
  float(None) is a TypeError three functions away from the cause.

  CHECK THE SHAPE YOURSELF. Today's build compares len(row) against the
  header and reports the line number, which is the only thing that makes a
  40,000-line file debuggable.""")


# ---------------------------------------------------------------------------
# 5. Everything is a string
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  EVERY VALUE IS A STRING. CSV HAS NO TYPES.")
print("-" * WIDTH)

TYPED = "id,price,active,note,code\n1,4.50,true,,0117\n"
row = next(csv.DictReader(io.StringIO(TYPED)))

print()
for key, value in row.items():
    print(f"  {key:<10}{value!r:<12}{type(value).__name__}")

print("""
  'true' is a string, and bool('false') is True — the classic way to turn
  a disabled account back on. '' is a string too, so "empty" and "missing"
  look identical unless you decide which one you mean.

  '0117' is the one that costs money: int() makes it 117, and it was a
  postcode, a phone number or a part code. CONVERT ONLY WHAT YOU WILL DO
  ARITHMETIC ON, and leave identifiers as text.""")


# ---------------------------------------------------------------------------
# 6. Dialects, delimiters, and the Sniffer
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. NOT ALL CSV IS COMMA-SEPARATED':^{WIDTH}}")
print("=" * WIDTH)

SAMPLES = {
    "comma": "sku,name,price\nWID-001,Widget,4.50\n",
    "semicolon (European Excel)": "sku;name;price\nWID-001;Widget;4,50\n",
    "tab": "sku\tname\tprice\nWID-001\tWidget\t4.50\n",
    "pipe": "sku|name|price\nWID-001|Widget|4.50\n",
}

print()
for label, text in SAMPLES.items():
    sniffed = csv.Sniffer().sniff(text)
    rows = list(csv.reader(io.StringIO(text), sniffed))
    print(f"  {label:<28}delimiter {sniffed.delimiter!r:<6}-> {rows[1]}")

print("""
  csv.Sniffer guesses the dialect from a sample. It is genuinely useful for
  a file a human just handed you, and it GUESSES — on a file you receive
  every night, state the dialect and let a wrong one fail loudly.

  NOTE THE SEMICOLON ROW: '4,50' is four-and-a-half euros. Half of Europe
  writes decimals with a comma, which is precisely why those files are
  semicolon-separated. float('4,50') raises, and that is the good case.

  QUOTING, when writing:
      csv.QUOTE_MINIMAL   (default) quote only when necessary
      csv.QUOTE_ALL       quote everything — safest for fussy consumers
      csv.QUOTE_NONNUMERIC  quotes text, and READS unquoted fields as
                            floats, which is occasionally exactly right""")


# ---------------------------------------------------------------------------
# 7. The BOM
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  THE BOM — WHY YOUR FIRST COLUMN NAME DOES NOT MATCH")
print("-" * WIDTH)

with open("excel.csv", "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerows([["sku", "name"], ["WID-001", "Widget"]])

print()
for encoding in ("utf-8", "utf-8-sig"):
    with open("excel.csv", encoding=encoding, newline="") as f:
        fields = next(csv.reader(f))
    print(f"  encoding={encoding:<12}header {fields}")
    print(f"  {'':<21}row['sku'] would "
          f"{'work' if fields[0] == 'sku' else 'KeyError'}")

with open("excel.csv", encoding="utf-8", newline="") as f:
    bommed = next(csv.reader(f))[0]

print(f"""
  Excel writes a byte-order mark at the start of a UTF-8 file. Read it as
  'utf-8' and your first column is named {bommed!r} — one invisible
  character in front — so row['sku'] raises KeyError while the header
  PRINTS as 'sku'. Hours have been lost to this.

      encoding='utf-8-sig'    reading anything a human exported
                              (it also reads files with no BOM, so it is a
                              safe default for other people's files)""")


# ---------------------------------------------------------------------------
# 8. Cleaning
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. WHAT CLEANING ACTUALLY MEANS':^{WIDTH}}")
print("=" * WIDTH)
print("""
  NORMALISE, in this order:

    1. HEADERS   strip, lower, replace spaces with underscores. Do it once
                 and every later line stops caring how the export was
                 configured.
    2. WHITESPACE  strip every value. ' hardware' and 'hardware' are the
                 same category and will not group together until you say so.
    3. CASE      pick one for anything you group or compare. 'Hardware',
                 'HARDWARE' and 'hardware' are three rows in a report.
    4. EMPTINESS decide what '' means, ONCE: missing, zero, or invalid.
                 They are three different answers.
    5. TYPES     convert only what you compute with. Identifiers stay text.
    6. DUPLICATES  decide the key, then decide whether to keep the first,
                 the last, or complain.

  AND THE PART PEOPLE SKIP: COUNT WHAT YOU DROPPED. A cleaner that turns
  10,000 rows into 9,300 and says nothing has hidden 700 problems. Today's
  build reports every rejection with its line number.""")

print()
print("=" * WIDTH)
print("""  1. Never split(','). Use the csv module.
  2. newline='' on read and write, always.
  3. encoding='utf-8-sig' for files humans exported.
  4. DictReader unless you are counting bytes.
  5. Ragged rows are silent. Check the shape yourself.
  6. Every value is a string. Convert only what you compute with.
  7. Normalise headers, whitespace and case before you group.
  8. Report what you dropped, with line numbers.""")
print("=" * WIDTH)

os.chdir("/")
shutil.rmtree(WORK, ignore_errors=True)
print(f"\n(scratch directory {WORK} removed)", file=sys.stderr)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write a field containing a comma, a quote and a newline, then parse
#     the file with split(','). Count how many ways it is wrong.
#
#   * Read a CRLF file without newline='' and diff the field against the
#     original bytes.
#
#   * Feed DictReader a row with one column too few, then call float() on
#     the missing value and read the traceback. Note how far it is from
#     the cause.
#
#   * Save a spreadsheet as CSV from Excel or Numbers and read it with
#     encoding='utf-8'. Print repr(fieldnames[0]).
#
#   * Sniff a file with only two rows. Then sniff one where a text field
#     happens to contain semicolons.
