# Day 061 — Dates and times

**Phase 7 · The outside world** · ~80 minutes

> **Today's build:** an age and countdown calculator that gets leap years and time zones right.

**Concepts:** `datetime` & `date` · `timedelta` · `strftime` & `strptime` · `zoneinfo` · UTC discipline

---

## The article

### Why this day exists

Time is the first thing in this course that is genuinely, irreducibly complicated — not because the
API is hard, but because the *world* is. Governments move clocks with a few weeks' notice, one hour a
year does not exist, another happens twice, and "one month later" has no agreed meaning.

Python's answer is a small, correct library that refuses to guess. Most bugs come from making it
guess anyway.

### 1. Four types, and `date` is the one you want

| | |
|---|---|
| `date` | a day. No time, no zone. |
| `time` | a time of day, with no day. Almost never what you want. |
| `datetime` | a moment… maybe. |
| `timedelta` | a **duration**, not a point. |

A birthday, an invoice date and a public holiday are all *days*. A `date` has no timezone, so three
of today's four hazards do not exist for it.

### 2. Naive and aware — the distinction everything depends on

```
naive   2026-03-18 14:30:00        tzinfo=None
aware   2026-03-18 14:30:00+00:00  tzinfo=UTC
```

**A naive datetime is not a moment in time.** It is a number on a clock face, and without knowing
whose clock it cannot be compared, converted or subtracted. Python refuses:

```
naive - aware   ->  TypeError: can't subtract offset-naive and offset-aware datetimes
naive < aware   ->  TypeError: can't compare offset-naive and offset-aware datetimes
```

That `TypeError` is the *good* outcome. The bad one is a program where everything is naive, in local
time, and the answers are quietly wrong for anybody in another country.

| | |
|---|---|
| `datetime.now()` | naive local time. **Almost always wrong.** |
| `datetime.now(UTC)` | aware, in UTC. Almost always right. |
| `datetime.now(tz)` | aware, local. For **display**. |
| `datetime.utcnow()` | a trap, deprecated from 3.12 — UTC time with **no** tzinfo |

### 3. Store UTC. Convert at the edges.

One moment — `2026-03-18 22:30 UTC` — from five places:

```
ZONE                LOCAL TIME                      OFFSET
UTC                 2026-03-18 22:30 UTC             +0000
Europe/London       2026-03-18 22:30 GMT             +0000
America/New_York    2026-03-18 18:30 EDT             -0400
Asia/Tokyo          2026-03-19 07:30 JST             +0900
Asia/Kolkata        2026-03-19 04:00 IST             +0530
```

Same instant, five clock readings, **three different dates**. And Kolkata is +05:30 — code that
assumes whole-hour offsets is wrong for about 1.4 billion people.

1. Get the time as UTC — `datetime.now(UTC)`
2. Store and compute in UTC — every comparison is then valid
3. Convert on the way out — `.astimezone(user_zone)`

`zoneinfo.ZoneInfo` (3.9+) reads the system database — 498 zones on this machine — so `pytz` is no
longer needed and no longer recommended.

### 4. The two hours a year that break everything

**A time that never happened:**

```
datetime(2026, 3, 29, 1, 30, tzinfo=LONDON)
  Python accepts it:    2026-03-29 01:30:00+00:00
  round-tripped:        2026-03-29 02:30:00+01:00
```

The clock jumped from 01:00 to 02:00 that morning, so 01:30 BST does not exist — and nothing raised.

**A time that happened twice:**

```
fold=0 (the first 01:30)   2026-10-25 01:30:00+01:00  ->  00:30 UTC
fold=1 (the second)        2026-10-25 01:30:00+00:00  ->  01:30 UTC
are they equal?            True
how far apart, really?     1:00:00
```

Read those together: Python says the two datetimes are **equal** and their UTC forms are an hour
apart. `fold` exists to disambiguate, defaults to 0, and almost nothing consults it — which is why a
job scheduled for 01:30 local runs twice or not at all, once a year, in a way nobody can reproduce in
March.

**You avoid all of it by working in UTC**, which has no DST.

### 5. `timedelta` has no months, and that is correct

```
31 January + 1 month = ?     28 February? 3 March?
29 February + 1 year = ?     28 February? 1 March?
```

Nobody agrees, so the standard library declines to guess. Clamping to the end of the month is *one*
right answer — and it is **not reversible**: 31 Jan + 1 month is 28 Feb, and 28 Feb − 1 month is
28 Jan.

And a day is not always 24 hours:

```
2026-03-28 12:00 GMT + timedelta(days=1) = 2026-03-29 12:00 BST
elapsed in UTC: 23:00:00
```

`timedelta(days=1)` on an aware datetime means *the same clock time tomorrow*. If you meant twenty-four
hours, say `timedelta(hours=24)` — or do the arithmetic in UTC, where they are the same thing.

### 6. ISO for machines, `strftime` for humans

```python
.isoformat()                    '2026-03-18T14:30:15+00:00'
datetime.fromisoformat(...)     parses it back, exactly
```

`01/02/2026` is two different days depending on who typed it, and nothing in the string says which.
`strptime` **raises** on a mismatch, which is what you want: a date parser that guesses is wrong
twelve times a year.

### 7. Leap years, and the rule people half-know

```
YEAR      div by 4    div by 100    div by 400    LEAP?
1900      True        True          False         False
2000      True        True          True          True
2100      True        True          False         False
```

**1900 was not a leap year and 2000 was.** Do not write the rule — `calendar.isleap(year)` is right,
and `calendar.monthrange(year, month)[1]` gives the length of any month.

### 8. The wall clock is not a stopwatch

| | |
|---|---|
| `time.time()` | the wall clock. Can jump **backwards** when NTP corrects it |
| `time.monotonic()` | never goes backwards. For timeouts and elapsed time |
| `time.perf_counter()` | highest resolution. For benchmarks |

Measuring a duration with `datetime.now()` is a bug that appears twice a year.

### 9. The build: age, without the approximation

```
BORN          ON              CORRECT   /365.25    /365   VERDICT
2000-03-18    2026-03-18           26        25      26   WRONG
2000-03-19    2026-03-18           25        25      26   WRONG
2008-03-18    2026-03-17           17        17      18   WRONG
2008-03-18    2026-03-18           18        17      18   WRONG
```

Neither approximation is safer — they are wrong on **different** rows. Rows three and four are the
ones that matter: somebody who turns 18 tomorrow and somebody who turned 18 today must not get the
same answer, and `/365` gives 18 for both. If that number decides whether a person may sign a
contract, the approximation is a wrong answer with a decimal point in it.

The exact version is one line:

```python
on.year - born.year - ((on.month, on.day) < (born.month, born.day))
```

The tuple comparison is the trick, and it handles 29 February with no special case.

### 10. The 29 February decision

```
YEAR    LEAP?   rule=march      rule=february     AGE THAT DAY
2025    False   2025-03-01      2025-02-28                   1
2026    False   2026-03-01      2026-02-28                   2
2028    True    2028-02-29      2028-02-29                   4
```

Both rules are real: England, Wales and Hong Kong say 1 March; New Zealand and Taiwan say
28 February. They disagree about a person's age for exactly one day a year, three years in four.

**A calculator that does not pick one and say so is not finished.**

### 11. Countdown, and why the zone is not decoration

```
ZONE                LOCAL NEW YEAR          IN UTC              AWAY
Pacific/Kiritimati  2027-01-01 00:00 +14    2026-12-31 10:00    288d
Asia/Tokyo          2027-01-01 00:00 JST    2026-12-31 15:00    288d
Europe/London       2027-01-01 00:00 GMT    2027-01-01 00:00    289d
America/New_York    2027-01-01 00:00 EST    2027-01-01 05:00    289d
```

Five different moments, spread over 26 hours, all called "New Year". A countdown that ignores the
zone counts down to the wrong one for everybody except the developer.

### 12. Checked, not asserted

The build's first check compares the one-line `age_in_years()` against a deliberately slow version
that counts anniversaries one at a time — on **every one of 4,384 days** between 2020 and 2032, for
five birthdays including 29 February. Zero disagreements.

That is Day 57's property test: not three examples, but the rule, over inputs nobody would list.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The four types, naive vs aware refusing to compare, DST transitions *found* by walking the year, `fold`, month arithmetic, ISO, leap years, and the wall clock vs the stopwatch. |
| `build.py` | Age and countdown, with 21 checks including an exhaustive comparison against a slow reference implementation. |

```bash
python3 lesson.py
python3 build.py                        # the demonstration
python3 build.py 1815-12-10             # your own date of birth
python3 build.py 1815-12-10 Asia/Tokyo
```

---

## Common mistakes

**`datetime.now()` for anything stored.** Naive local time.

**`datetime.utcnow()`.** A naive datetime that pretends to be local. Deprecated.

**Comparing naive with aware.** `TypeError` if you are lucky, wrong answers if everything is naive.

**Age as `days / 365.25`.** Wrong on birthdays, which is when it is asked.

**Writing the leap-year rule yourself.** 1900.

**`timedelta(days=1)` when you meant 24 hours.**

**Storing an offset instead of a zone.** `+01:00` is true for half the year.

**Scheduling anything at 01:30 local.**

**`%d/%m/%Y` between systems.** Two different days.

**Timing code with `datetime.now()`.** Use `perf_counter`.

---

## Exercises

1. Subtract a naive datetime from an aware one, then find which of yours are naive.
2. Construct 2026-03-29 01:30 in `Europe/London`, convert to UTC and back.
3. Add `timedelta(days=1)` to noon before a DST change and measure the gap in UTC.
4. Write `age_in_years` and check it against a counting version for a decade of days.
5. Decide your 29 February rule and write it in a docstring.
6. Parse `01/02/2026` with both `%d/%m/%Y` and `%m/%d/%Y`. Both succeed.
7. Build a countdown that takes the user's timezone as an argument.
8. Time a loop with `datetime.now()` and with `perf_counter()`.

---

## Checklist

- [ ] I use `date` when I mean a day
- [ ] I know a naive datetime is not a moment
- [ ] I use `datetime.now(UTC)` and never `utcnow()`
- [ ] I store UTC and convert with `.astimezone()` at the edges
- [ ] I know what happens to 01:30 twice a year
- [ ] I know `timedelta` has no months, and why
- [ ] I use ISO 8601 between machines
- [ ] I use `calendar.isleap` and `monthrange`
- [ ] I measure durations with `perf_counter`, not the clock
