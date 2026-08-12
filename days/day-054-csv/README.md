# Day 054 — CSV

**Phase 6 · Robust code** · ~85 minutes

> **Today's build:** clean a CSV with missing fields and inconsistent casing, then write a summary CSV back out.

**Concepts:** `csv.reader` · `DictReader` & `DictWriter` · headers · delimiters · messy real data

---

## The article

### Why this day exists

CSV looks like the one format you could parse yourself in an afternoon. It is not, and the reason it
is not is that the format is fine — the *data* is written by people, exported by spreadsheets, and
concatenated by scripts that were also written in an afternoon.

### 1. Why not `line.split(",")`

`lesson.py` writes six perfectly legal fields and parses them both ways:

```
'"Lovelace, Ada","she said ""hello""","line one\nline two",,  padded  ,0117'

                        FIELDS   FIRST FIELD
line.split(',')              7   '"Lovelace'
csv.reader                   6   'Lovelace, Ada'
```

Every one of those six values breaks a hand-rolled parser:

| the value | what it does |
|---|---|
| a comma inside a field | quoted, and `split()` cuts it in half |
| a quote inside a field | doubled (`""`), and `split()` keeps both |
| **a newline inside a field** | one record spans two lines, so even `for line in f` is wrong |
| an empty field | `,,` — is that empty or missing? |
| leading whitespace | preserved, and usually not wanted |
| `0117` | a string. `int()` would eat the zero. |

**Never parse CSV by hand.** Not "usually" — the data becomes complicated the week after you ship.

### 2. `newline=""` is not optional

```
open(...)                 note field = 'line1\nline2'
open(..., newline='')     note field = 'line1\r\nline2'
```

Without it, Python's universal-newline translation rewrites the `\r\n` **inside a quoted field**
before `csv` ever sees it. The row count is right and the data is silently changed — the worst kind
of bug, because every test that counts rows still passes.

On writing, on Windows, the same omission is more visible: the writer emits `\r\n`, text mode turns
the `\n` into `\r\n`, and you get a blank row between every record. Everybody has seen that file.

```python
open(path, newline="", encoding="utf-8")     # read AND write, always
```

### 3. Four objects

| | gives you | use when |
|---|---|---|
| `csv.reader` | a list per row | you are counting bytes |
| `csv.DictReader` | a dict per row, keyed by header | almost always |
| `csv.writer` | rows from lists | |
| `csv.DictWriter` | rows from dicts, `fieldnames` sets column order | almost always |

`row["price"]` still works when somebody inserts a column; `row[3]` does not.

`DictWriter` needs `fieldnames` — a dict is not a schema, so *you* decide the column order — and
`writeheader()` is a separate call that is easy to forget. `restval=` fills missing keys;
`extrasaction=` decides what happens to undeclared ones (the default, raising, is usually right).

### 4. Ragged rows are silent

```
{'sku': 'GZM-002', 'name': 'Gizmo', 'price': None}
{'sku': 'DHK-003', 'name': 'D', 'price': '1', None: ['extra']}
```

`DictReader` does not raise. Too few fields → the missing keys get `None`. Too many → the surplus
lands under the key `None`, **as a list**. Then `float(None)` is a `TypeError` three functions away
from the cause.

**Check the shape yourself**, and report the line number. Today's build does:

```
   12  GRM-010   has 4 fields, header has 7
   13  CLP-011   has 9 fields, header has 7
```

On a 40,000-row export, the line number is the difference between a fixable report and a shrug.

### 5. Every value is a string

CSV has no types. `'true'`, `''`, `'4.50'` and `'0117'` are all `str`.

- `bool('false')` is `True` — the classic way to turn a disabled account back on.
- `''` is a string too, so "empty" and "missing" look identical until you decide which you mean.
- `'0117'` is the one that costs money: `int()` makes it `117`, and it was a postcode, a phone
  number or a part code.

**Convert only what you will do arithmetic on.** Identifiers stay text.

### 6. Not all CSV is comma-separated

```
comma                       delimiter ','   -> ['WID-001', 'Widget', '4.50']
semicolon (European Excel)  delimiter ';'   -> ['WID-001', 'Widget', '4,50']
tab                         delimiter '\t'  -> ['WID-001', 'Widget', '4.50']
```

`csv.Sniffer().sniff(sample)` guesses the dialect — genuinely useful for a file a human just handed
you, and a *guess*. For a file you receive every night, state the dialect and let a wrong one fail
loudly.

Note the semicolon row: `'4,50'` is four-and-a-half euros. Half of Europe writes decimals with a
comma, which is exactly why those files are semicolon-separated.

### 7. The BOM

```
encoding=utf-8       header ['﻿sku', 'name']     row['sku'] -> KeyError
encoding=utf-8-sig   header ['sku', 'name']           row['sku'] -> works
```

Excel writes a byte-order mark at the start of a UTF-8 file. Read it as `'utf-8'` and your first
column is named `'﻿sku'` — one invisible character in front — so `row['sku']` raises `KeyError`
while the header *prints* as `sku`. Hours have been lost to this.

Use `encoding="utf-8-sig"` for anything a human exported. It also reads files with no BOM, so it is
a safe default for other people's files.

### 8. What cleaning actually means

In this order, because each step depends on the one before:

1. **Headers** — strip, lower, underscore. Once, at the top, and every later line stops caring how
   the export was configured.
2. **Whitespace** — strip every value. `' hardware'` and `'hardware'` will not group together until
   you say so.
3. **Case** — pick one for anything you group or compare. `Hardware`, `HARDWARE` and `hardware` are
   three rows in a report.
4. **Emptiness** — decide what `''` means, once: missing, zero, or invalid. Three different answers.
5. **Types** — convert only what you compute with.
6. **Duplicates** — decide the key, then decide whether to keep the first, the last, or complain.

And the step people skip: **count what you dropped.** A cleaner that turns 18 rows into 7 and says
nothing has hidden eleven problems.

### 9. The decision worth copying: refuse to guess

The build's price parser handles `'£4.50'`, `'4,50'` and `'1,299.00'`. It refuses `'1,299'`:

```
   17  AMB-014   price '1,299' is ambiguous (1,299 or 1.299?)
```

That value is 1299 in Britain and 1.299 in Germany, and nothing in the file says which. A cleaner
that guesses is a cleaner that is wrong by a factor of a thousand — silently, on somebody else's
data. Refusing costs one line in a report; guessing costs an invoice.

The rules it *does* apply are written in the docstring, because they are decisions, not facts.

### 10. What the build checks

Fourteen checks, and three of them are the interesting ones:

- **The output round-trips.** Read the written file back with `DictReader` and compare every field
  to what was meant. That catches quoting bugs, encoding bugs and column-order bugs at once.
- **Nothing was silently dropped.** `rows read == blank + wrong shape + rejected + accepted`.
- **The embedded newline did not create an extra row.** The file has 20 lines and 18 rows, because
  one note contains a real newline. `for line in f` would have produced two broken records there and
  nothing would have complained.

A naive `split(",")` gets **6 of the rows wrong** in the same file.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `split(",")` failing on six legal fields, `newline=""` changing data, ragged rows, dialects, the BOM, and the cleaning order. |
| `build.py`  | The cleaner: a BOM'd 18-row export with two ragged rows, a duplicate, an embedded newline and three price formats → a clean file, a summary file, a rejection report with line numbers, and 14 checks. |

```bash
python3 lesson.py
python3 build.py                    # generates a messy file and cleans it
python3 build.py messy.csv output   # your own file
```

---

## Common mistakes

**`line.split(",")`.** Wrong on quoted commas, quoted quotes and embedded newlines.

**Forgetting `newline=""`.** Silently changed data on read, blank rows on write.

**Reading an Excel export as `utf-8`.** `KeyError` on a header that prints correctly.

**Trusting `DictReader` on ragged rows.** `None` where a value should be.

**`int()` on an identifier.** Leading zeros gone.

**Grouping before normalising case and whitespace.** Three rows where there should be one.

**Guessing at ambiguous numbers.** `1,299`.

**Dropping rows without counting them.** Nobody finds out until the totals are wrong.

**Writing a summary without checking it against the detail.** They drift.

---

## Exercises

1. Write a field containing a comma, a quote and a newline; parse the file with `split(",")` and
   count the ways it is wrong.
2. Read a CRLF file with and without `newline=""` and diff one field.
3. Feed `DictReader` a short row, then call `float()` on the missing value. Note how far the
   traceback is from the cause.
4. Export a spreadsheet as CSV and print `repr(fieldnames[0])`.
5. Take a messy CSV of your own and write the cleaner: normalise, validate, reject with line
   numbers.
6. Write the summary, then check its totals against the detail rows in code.
7. Change the duplicate rule from "last wins" to "first wins" and to "raise". All three are
   defensible; the point is that you chose.

---

## Checklist

- [ ] I never split on commas
- [ ] I pass `newline=""` on read and write
- [ ] I use `utf-8-sig` for files humans exported
- [ ] I check row shape myself and report line numbers
- [ ] I know every value is a string
- [ ] I normalise headers, whitespace and case before grouping
- [ ] I convert only what I compute with
- [ ] I refuse ambiguous values instead of guessing
- [ ] I count and report what I dropped
