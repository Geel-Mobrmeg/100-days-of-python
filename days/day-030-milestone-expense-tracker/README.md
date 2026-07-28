# Day 030 — Milestone: expense tracker 🏁

**Phase 3 · Data structures** · ~165 minutes

> **Today's build:** track expenses by category and month, then print a report with totals and the biggest spend.

**Concepts:** modelling with nested dicts · aggregation · reporting · input validation

---

## The article

### What this milestone is really testing

Not whether you can use a dict. Whether you can **choose a shape for data and live with the
consequences** — because every report you are asked for afterwards is easy or impossible
depending on that one decision, made before you wrote any of them.

### 1. Choosing the model

Three candidates for "a list of expenses":

**A. Parallel lists.** `dates`, `categories`, `amounts`. This is Day 20's world, and it is why
that build hurt: three lists that must stay the same length and order forever, with nothing
enforcing it, and a fourth list needed the moment you add a field.

**B. A dict keyed by date.** Looks tidy. Silently loses data — two expenses on the same day and
one overwrites the other, with no error.

**C. A flat list of dicts.** One record, one dict, every field named.

```python
{"date": "2024-01-15", "category": "housing", "amount": Decimal("875.00"), "note": "rent"}
```

C wins, and the rule behind it is worth stating: **key by something only when it is genuinely
unique and stable.** Dates are neither.

A flat list of records is also exactly what a CSV file (Day 54), a database table (Day 78) and a
pandas DataFrame (Day 73) are. Choosing it now means those three days are format changes rather
than rewrites.

### 2. One source of truth

The tempting mistake is a running total kept alongside the records. It is faster and it *will*
disagree, because someone will append a record and not update it. Nothing raises — the failure is
something that did not happen.

**Derive every total. Store none of them.** Summing 100,000 records takes milliseconds. Cache only
after measuring (Day 29), and only behind a single function.

This is Day 19's clock problem again: derive from a source of truth, do not accumulate.

### 3. Aggregation is always the same three lines

```python
def totals_by(rows, key_func):
    out = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        out[key_func(row)] += row["amount"]
    return dict(out)
```

By month, by category, by day of week, by note — one function, because the **grouping key is a
parameter** rather than baked into the loop.

You have now seen this shape three times and will see it twice more: `defaultdict` here, pandas
`.groupby()` on Day 75, SQL `GROUP BY` on Day 78. Same idea, three sizes.

For month-by-category you want a **cross-tab**: a dict of dicts, `{month: {category: total}}`.
Then check the margins — rows and columns must both sum to the grand total. Two lines, and it
catches the errors that look plausible.

### 4. Dates as ISO strings

`"2024-03-14"` sorts correctly *as text*, because the components run most-significant first. That
is why the standard is that way round, and it means `sorted()` and `date[:7]` for the month both
work with no imports.

`"15/03/2024"` does not sort. Neither does `"Mar 15, 2024"`.

Real `date` objects (Day 61) are better still — arithmetic, leap years, and rejecting
`2024-13-01`. Until then ISO strings get you sorting and grouping for free.

### 5. Money is `Decimal`

Day 5 established this and today is where it pays: a report whose category totals do not add up to
the grand total is worthless, and with floats they eventually will not. `Decimal("875.00")` from
a **string**, and `.quantize()` at the point of display.

### 6. Validation returns the reason

```python
def parse_expense(...):
    return None, "category 'snacks' is not one of food, transport, ..."
```

A validator that returns `True`/`False` makes every caller invent the error message — and the
message is the part the user actually reads. Return `(value, error)` with exactly one of them
`None`.

One function, so the rules cannot drift, and everything downstream receives records already known
to be good.

**Be strict about meaning, generous about format.** `"2024-3-4"` with category `"FOOD"` and amount
`"10.5"` is sloppy but unambiguous: normalise it. `"snacks"` is not a category: refuse it.

### 7. Compute and report are different jobs

```
COMPUTE   produces numbers from records. No printing.
REPORT    prints. No arithmetic beyond formatting.
```

The test: could you swap the terminal output for a CSV, a web page (Day 82) or a chart (Day 77)
without touching any arithmetic? If not, they are tangled — and nothing is testable on Day 57,
because a total computed inside an f-string cannot be checked.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The three model options and why C wins, running-total drift shown live, parameterised aggregation, margin checks. |
| `build.py`  | The tracker: validation with reasons, by-month, by-category, a month×category cross-tab with margin checks, biggest spends, recurring costs. |

```bash
python3 lesson.py
python3 build.py
python3 build.py --interactive
printf 'add 2024-03-14 food 12.50 lunch\nreport\nquit\n' | python3 build.py --interactive
```

---

## The brief

Build yours before opening `build.py`. It must:

- [ ] store expenses as a flat list of records with named fields
- [ ] use `Decimal` for money, built from strings
- [ ] validate date, category and amount in one place, returning *why* on rejection
- [ ] total by month and by category
- [ ] produce a month × category cross-tab whose margins agree with the grand total
- [ ] report the biggest single spends and the largest category
- [ ] derive every figure from the records — no stored totals
- [ ] cope with an empty list without crashing

---

## Common mistakes

**A dict keyed by date.** Two expenses on one day; one disappears.

**A running total.** It will drift, silently.

**Floats for money.** Category totals stop summing to the grand total.

**Validation scattered across the program.** The rules drift apart.

**Returning `False` from a validator.** Every caller reinvents the message.

**Arithmetic inside `print()`.** Nothing is testable or reusable.

**Non-ISO date strings.** Sorting and grouping both break.

**Assuming every category appears every month.** `.get(category, 0)` in the cross-tab.

---

## Extend it

1. Add budgets: a `{category: monthly_limit}` dict and an over/under column.
2. Corrupt one amount after aggregation and confirm the margin check catches it. That check is a
   test (Day 57) living inside the program.
3. **Day 54** — load from CSV. **Day 55** — save to JSON. Both should be a format change only.
4. **Day 61** — real `date` objects, so "the last 30 days" becomes expressible.
5. **Day 77** — plot the monthly bars with matplotlib. If `compute` and `report` are properly
   separated this costs almost nothing.

---

## Phase 3 checklist

You are leaving Data structures. Before you do:

- [ ] I know when to reach for a list, tuple, dict or set, and can justify each
- [ ] I understand aliasing, and shallow vs deep copying
- [ ] I write comprehensions for one-in-one-out work and loops for everything else
- [ ] I use `Counter` and `defaultdict` rather than hand-rolling them
- [ ] I can do a mixed-direction multi-key sort
- [ ] I can traverse nested data without crashing on missing or wrong-typed fields
- [ ] I can state what O(n²) means and recognise it in a timing table
- [ ] **My tracker's totals agree, in every direction, on every dataset I try**

Tomorrow: functions. Every build so far has been one long script — that stops now.
