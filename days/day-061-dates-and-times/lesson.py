"""Day 061 — Dates and times, and the four ways they go wrong.

    python3 lesson.py

Every number below is computed. Where this file makes a claim about a
timezone or a leap year, it works it out rather than quoting it.
"""

from __future__ import annotations

import calendar
import time
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo, available_timezones

WIDTH = 76

LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
TOKYO = ZoneInfo("Asia/Tokyo")
KOLKATA = ZoneInfo("Asia/Kolkata")

# ---------------------------------------------------------------------------
# 1. The four types
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. FOUR TYPES, AND WHICH ONE YOU ACTUALLY WANT':^{WIDTH}}")
print("=" * WIDTH)

when = datetime(2026, 3, 18, 14, 30, 15, tzinfo=UTC)

print(f"""
  date          {when.date()}                    a day. No time, no zone.
  time          {when.time()}                     a time of day, with no day.
  datetime      {when.replace(tzinfo=None)}          a moment... maybe.
  timedelta     {timedelta(days=1, hours=6)}            a DURATION, not a point.

  USE `date` WHENEVER YOU CAN. A birthday, an invoice date and a public
  holiday are all days, not moments — and a date has no timezone, so
  three of today's four hazards do not exist for it.

  `time` on its own is almost never what you want: 09:00 in what zone, on
  which day? Store the datetime.""")


# ---------------------------------------------------------------------------
# 2. Naive and aware
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. THE DISTINCTION EVERYTHING ELSE DEPENDS ON':^{WIDTH}}")
print("=" * WIDTH)

naive = datetime(2026, 3, 18, 14, 30)
aware = datetime(2026, 3, 18, 14, 30, tzinfo=UTC)

print(f"""
  naive   {naive}        tzinfo={naive.tzinfo}
  aware   {aware}  tzinfo={aware.tzinfo}

  A NAIVE DATETIME IS NOT A MOMENT IN TIME. It is a number on a clock
  face, and without knowing whose clock, it cannot be compared with
  anything, converted to anything, or subtracted from anything.

  Python knows this, and refuses:""")

try:
    naive - aware
except TypeError as exc:
    print(f"\n  naive - aware   ->  TypeError: {exc}")
try:
    print(naive < aware)
except TypeError as exc:
    print(f"  naive < aware   ->  TypeError: {exc}")

print("""
  ...and that TypeError is the good outcome. The bad one is a program
  where everything happens to be naive, in local time, and the answers
  are quietly wrong for anybody in another country.

  THE THREE WAYS TO GET `NOW`:

      datetime.now()          NAIVE local time.  Almost always wrong.
      datetime.now(UTC)       aware, in UTC.     Almost always right.
      datetime.now(LONDON)    aware, local.      For DISPLAY.

  datetime.utcnow() is a trap and is deprecated from 3.12: it returns
  the UTC time with NO tzinfo — a naive datetime that lies about being
  local. Never use it.""")


# ---------------------------------------------------------------------------
# 3. UTC discipline
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. STORE UTC. CONVERT AT THE EDGES.':^{WIDTH}}")
print("=" * WIDTH)

moment = datetime(2026, 3, 18, 22, 30, tzinfo=UTC)

print(f"""
  ONE MOMENT — {moment} — seen from five places:
""")
print(f"  {'ZONE':<20}{'LOCAL TIME':<28}{'OFFSET':>10}")
print("  " + "-" * (WIDTH - 4))
for name, zone in [("UTC", UTC), ("Europe/London", LONDON),
                   ("America/New_York", NEW_YORK), ("Asia/Tokyo", TOKYO),
                   ("Asia/Kolkata", KOLKATA)]:
    local = moment.astimezone(zone)
    print(f"  {name:<20}{local.strftime('%Y-%m-%d %H:%M %Z'):<28}"
          f"{local.strftime('%z'):>10}")

print(f"""
  Same instant, five clock readings, three different DATES. Kolkata is
  +05:30 — not every offset is a whole number of hours, and code that
  assumes one is wrong for about 1.4 billion people.

  THE DISCIPLINE, and it is only three lines:

      1. Get the time as UTC.        datetime.now(UTC)
      2. Store and compute in UTC.   every comparison is then valid
      3. Convert on the way out.     .astimezone(user_zone)

  There are {len(available_timezones())} zones in the database on this machine, and the
  rules change — governments move DST dates with a few weeks' notice.
  That is why the offset is looked up rather than stored.""")


# ---------------------------------------------------------------------------
# 4. DST: the two broken hours
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. THE TWO HOURS A YEAR THAT BREAK EVERYTHING':^{WIDTH}}")
print("=" * WIDTH)


def find_transitions(zone: ZoneInfo, year: int) -> list[datetime]:
    """Find DST changes by walking the year in UTC and watching the offset."""
    found = []
    moment = datetime(year, 1, 1, tzinfo=UTC)
    previous = moment.astimezone(zone).utcoffset()
    while moment.year == year:
        moment += timedelta(hours=1)
        current = moment.astimezone(zone).utcoffset()
        if current != previous:
            found.append(moment)
            previous = current
    return found


spring, autumn = find_transitions(LONDON, 2026)

print(f"""
  Europe/London in 2026, found by walking the year rather than remembering:

    clocks go forward   {spring.astimezone(LONDON)}
    clocks go back      {autumn.astimezone(LONDON)}
""")

# The hour that does not exist.
missing = datetime(2026, 3, 29, 1, 30, tzinfo=LONDON)
print("  A TIME THAT NEVER HAPPENED:  datetime(2026, 3, 29, 1, 30)")
print(f"    Python accepts it:         {missing}")
print(f"    ...and in UTC it is:       {missing.astimezone(UTC)}")
print(f"    round-tripped back:        {missing.astimezone(UTC).astimezone(LONDON)}")
print("""    01:30 became 02:30. The clock jumped from 01:00 to 02:00 that
    morning, so 01:30 BST does not exist — and nothing raised.""")

# The hour that happens twice.
first = datetime(2026, 10, 25, 1, 30, tzinfo=LONDON, fold=0)
second = datetime(2026, 10, 25, 1, 30, tzinfo=LONDON, fold=1)
print("\n  A TIME THAT HAPPENED TWICE:  datetime(2026, 10, 25, 1, 30)")
print(f"    fold=0 (the first 01:30)   {first}  ->  {first.astimezone(UTC)}")
print(f"    fold=1 (the second)        {second}  ->  {second.astimezone(UTC)}")
print(f"    are they equal?            {first == second}")
print(f"    how far apart, really?     {second.astimezone(UTC) - first.astimezone(UTC)}")

print("""
  READ THOSE TWO LINES TOGETHER. Python says the two datetimes are EQUAL
  and their UTC forms are an hour apart. `fold` exists to disambiguate,
  it defaults to 0, and almost nothing consults it — which is why a job
  scheduled for 01:30 local either runs twice or not at all, once a year,
  in a way nobody can reproduce in March.

  YOU AVOID ALL OF THIS BY WORKING IN UTC. There is no ambiguous hour in
  UTC, because UTC has no DST.""")


# ---------------------------------------------------------------------------
# 5. Arithmetic
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. timedelta HAS NO MONTHS, AND THAT IS CORRECT':^{WIDTH}}")
print("=" * WIDTH)

gap = date(2026, 12, 25) - date(2026, 3, 18)
print(f"""
  date - date        {gap}       a timedelta
  .days              {gap.days}
  in weeks           {gap.days / 7:.1f}

  A timedelta holds DAYS, SECONDS and MICROSECONDS. There is no months=
  and no years=, and that is a deliberate refusal rather than an omission:

      31 January + 1 month = ?      28 February? 3 March? 2 March?
      29 February + 1 year  = ?      28 February? 1 March?

  Nobody agrees, so the standard library declines to guess. Adding a month
  means deciding what you mean:""")


def add_months(start: date, months: int) -> date:
    """Clamp to the end of the target month. ONE of several right answers."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


print(f"\n  {'START':<14}{'+1 MONTH':<14}{'+2 MONTHS':<14}{'+12 MONTHS':<14}")
print("  " + "-" * (WIDTH - 4))
for start in (date(2026, 1, 31), date(2026, 3, 31), date(2024, 2, 29),
              date(2026, 8, 15)):
    print(f"  {str(start):<14}{str(add_months(start, 1)):<14}"
          f"{str(add_months(start, 2)):<14}{str(add_months(start, 12)):<14}")

print("""
  Clamping means the operation is NOT REVERSIBLE: 31 January + 1 month is
  28 February, and 28 February - 1 month is 28 January. If that matters to
  your problem, say so in the docstring; if it matters a great deal, use
  dateutil.relativedelta and read its rules.

  AND A DAY IS NOT ALWAYS 24 HOURS:""")

before = datetime(2026, 3, 28, 12, 0, tzinfo=LONDON)
after = before + timedelta(days=1)
print(f"\n  {before}  + timedelta(days=1)")
print(f"  = {after}")
print(f"  elapsed in UTC: {after.astimezone(UTC) - before.astimezone(UTC)}"
      f"   <- 23 hours, not 24")
print("""
  timedelta(days=1) means "the same clock time tomorrow" when added to an
  aware datetime, and that day was 23 hours long. If you meant twenty-four
  hours, say timedelta(hours=24) — or do the arithmetic in UTC, where the
  two are the same thing.""")


# ---------------------------------------------------------------------------
# 6. Parsing and formatting
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. TEXT IN, TEXT OUT':^{WIDTH}}")
print("=" * WIDTH)

sample = datetime(2026, 3, 18, 14, 30, 15, tzinfo=LONDON)
formats = [
    ("%Y-%m-%d", "ISO date"),
    ("%Y-%m-%dT%H:%M:%S%z", "ISO datetime with offset"),
    ("%d/%m/%Y", "British — AMBIGUOUS"),
    ("%m/%d/%Y", "American — AMBIGUOUS"),
    ("%A %-d %B %Y", "for a human"),
    ("%H:%M", "just the time"),
    ("%j", "day of the year"),
    ("%U / %W", "week number (two conventions)"),
]

print()
for code, meaning in formats:
    print(f"  {code:<24}{sample.strftime(code):<26}{meaning}")

print(f"""
  ISO 8601 IS THE ONLY UNAMBIGUOUS ONE, and it has its own methods:

      .isoformat()                 {sample.isoformat()}
      datetime.fromisoformat(...)  parses it back, exactly

  Use those for anything a machine reads. strftime is for humans, and
  strptime is for other people's badly-chosen formats.""")

for text, code in [("18/03/2026", "%d/%m/%Y"), ("03/18/2026", "%m/%d/%Y"),
                   ("2026-03-18", "%Y-%m-%d")]:
    parsed = datetime.strptime(text, code).date()
    print(f"  strptime({text!r:<14}, {code!r:<12}) -> {parsed}")

print("""
  01/02/2026 IS TWO DIFFERENT DAYS depending on who typed it, and nothing
  in the string says which. Day 60's tool refuses that input for exactly
  this reason. When you must accept it, ask; when you can choose, demand
  ISO.

  strptime RAISES on anything that does not match, which is what you want:
  a date parser that guesses is a date parser that is wrong twelve times a
  year.""")


# ---------------------------------------------------------------------------
# 7. Leap years
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. LEAP YEARS, AND THE RULE PEOPLE HALF-KNOW':^{WIDTH}}")
print("=" * WIDTH)

print("""
  A year is a leap year if it is divisible by 4 — EXCEPT centuries, which
  must be divisible by 400. So:
""")
print(f"  {'YEAR':<10}{'div by 4':<12}{'div by 100':<14}{'div by 400':<14}LEAP?")
print("  " + "-" * (WIDTH - 4))
for year in (2024, 2025, 2026, 1900, 2000, 2100):
    print(f"  {year:<10}{str(year % 4 == 0):<12}{str(year % 100 == 0):<14}"
          f"{str(year % 400 == 0):<14}{calendar.isleap(year)}")

print(f"""
  1900 WAS NOT A LEAP YEAR and 2000 was. A great deal of software still
  believes otherwise, because a spreadsheet from 1985 got it wrong and
  everything since has had to bug-for-bug match it.

  DO NOT WRITE THE RULE. calendar.isleap(year) is right, and
  calendar.monthrange(year, month)[1] gives the length of any month:

      February 2024   {calendar.monthrange(2024, 2)[1]} days
      February 2026   {calendar.monthrange(2026, 2)[1]} days

  AND THE 29 FEBRUARY BIRTHDAY IS A REAL DECISION, not an edge case to
  ignore: does somebody born on 2024-02-29 have a birthday in 2026, and if
  so, when? Today's build picks 1 March, says so, and shows the other
  answer.""")

leaplings = sum(1 for year in range(1900, 2027) if calendar.isleap(year))
print(f"  ({leaplings} leap years between 1900 and 2026 inclusive.)")


# ---------------------------------------------------------------------------
# 8. Measuring vs telling the time
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'8. THE WALL CLOCK IS NOT A STOPWATCH':^{WIDTH}}")
print("=" * WIDTH)

start_wall = time.time()
start_monotonic = time.monotonic()
start_perf = time.perf_counter()
total = sum(range(2_000_000))
print(f"""
  time.time()          {time.time() - start_wall:.4f}s   the WALL CLOCK. Can jump
                                 backwards when NTP corrects it, or when
                                 somebody changes the system time.
  time.monotonic()     {time.monotonic() - start_monotonic:.4f}s   never goes backwards. For
                                 timeouts and elapsed time.
  time.perf_counter()  {time.perf_counter() - start_perf:.4f}s   the highest resolution
                                 available. For benchmarks.

  MEASURING A DURATION WITH datetime.now() IS A BUG that appears twice a
  year and on any machine whose clock is corrected mid-measurement. Day 19
  used perf_counter for exactly this reason.

  (The sum was {total:,}, so the compiler could not skip the work.)""")

print()
print("=" * WIDTH)
print("""  1. Use `date` when you mean a day.
  2. Naive datetimes are not moments. Attach a timezone or use UTC.
  3. datetime.now(UTC) — never .utcnow(), never bare .now() for storage.
  4. Store UTC, compute in UTC, convert with .astimezone() at the edges.
  5. Two hours a year are broken in every DST zone. UTC has neither.
  6. timedelta has no months. Adding one is a decision you must make.
  7. ISO 8601 for machines, strftime for humans, and never guess a format.
  8. calendar.isleap and calendar.monthrange. Do not write the rule.
  9. monotonic/perf_counter for durations, not the wall clock.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Subtract a naive datetime from an aware one and read the TypeError.
#     Then work out which of yours are naive.
#
#   * Construct 2026-03-29 01:30 in Europe/London, convert to UTC and back,
#     and watch it move.
#
#   * Add timedelta(days=1) to 12:00 on the day before a DST change, then
#     measure the gap in UTC.
#
#   * Ask add_months(date(2026, 1, 31), 1) and then subtract a month from
#     the answer. You will not get back where you started.
#
#   * Parse "01/02/2026" with both %d/%m/%Y and %m/%d/%Y. Both succeed.
#
#   * Time a loop with datetime.now() and again with perf_counter(), then
#     read about what NTP does to a laptop that has been asleep.
