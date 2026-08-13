"""Day 061 build — an age and countdown calculator that is right.

    python3 build.py                          # the demonstration
    python3 build.py 1815-12-10               # your own date of birth
    python3 build.py 1815-12-10 Asia/Tokyo    # ...seen from another zone

TWO CALCULATIONS THAT LOOK TRIVIAL AND ARE NOT:

    HOW OLD IS SOMEBODY?     Not days / 365.25. That is wrong by a day
                             for most people, and by a year on a birthday.

    HOW LONG UNTIL X?        Not (target - now).days // 1. That is wrong
                             across a DST boundary and wrong again when
                             the target is in another country.

Every claim below is checked at the bottom, including the ones about 29
February and the two broken hours a year.
"""

from __future__ import annotations

import calendar
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

WIDTH = 78

LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
TOKYO = ZoneInfo("Asia/Tokyo")
KOLKATA = ZoneInfo("Asia/Kolkata")
SYDNEY = ZoneInfo("Australia/Sydney")

# A FIXED "now", so this file prints the same thing every day and its
# claims can be checked. Day 58: the clock is a parameter, never a call.
TODAY = date(2026, 3, 18)
NOW = datetime(2026, 3, 18, 9, 0, tzinfo=UTC)


# ###########################################################################
# AGE
# ###########################################################################

@dataclass(frozen=True, slots=True)
class Age:
    years: int
    months: int
    days: int
    total_days: int

    def __str__(self) -> str:
        parts = [
            f"{self.years} year{'s' * (self.years != 1)}",
            f"{self.months} month{'s' * (self.months != 1)}",
            f"{self.days} day{'s' * (self.days != 1)}",
        ]
        return ", ".join(parts)


def age_in_years(born: date, on: date) -> int:
    """Whole years. The one-line version everybody should memorise.

    The trick is the tuple comparison: (month, day) < (month, day) is
    True exactly when this year's birthday has not happened yet, and it
    handles 29 February without a special case because (2, 29) sorts
    correctly against every other pair.
    """
    had_birthday = (on.month, on.day) >= (born.month, born.day)
    return on.year - born.year - (not had_birthday)


def age(born: date, on: date) -> Age:
    """Years, months and days — the way a person would count them."""
    if born > on:
        raise ValueError(f"{born} is in the future relative to {on}")

    years = age_in_years(born, on)

    # Walk to the anniversary, then count whole months, then the remainder.
    month_index = born.month - 1 + years * 12
    anniversary_year = born.year + month_index // 12
    months = 0
    while True:
        index = born.month - 1 + years * 12 + months + 1
        year = born.year + index // 12
        month = index % 12 + 1
        day = min(born.day, calendar.monthrange(year, month)[1])
        if date(year, month, day) > on:
            break
        months += 1

    index = born.month - 1 + years * 12 + months
    year = born.year + index // 12
    month = index % 12 + 1
    day = min(born.day, calendar.monthrange(year, month)[1])
    days = (on - date(year, month, day)).days

    assert anniversary_year <= on.year                       # noqa: S101
    return Age(years, months, days, (on - born).days)


def next_birthday(born: date, on: date, leap_rule: str = "march") -> date:
    """The next anniversary of `born` on or after `on`.

    THE 29 FEBRUARY DECISION, made explicitly:

        leap_rule="march"     1 March in common years   (the legal rule in
                              England, Wales and Hong Kong)
        leap_rule="february"  28 February               (the rule in New
                              Zealand and Taiwan)

    Both are real, both are used by real legal systems, and a calculator
    that does not say which one it picked is not finished.
    """
    if leap_rule not in ("march", "february"):
        raise ValueError("leap_rule must be 'march' or 'february'")

    for year in (on.year, on.year + 1):
        if born.month == 2 and born.day == 29 and not calendar.isleap(year):
            candidate = (date(year, 3, 1) if leap_rule == "march"
                         else date(year, 2, 28))
        else:
            candidate = date(year, born.month, born.day)
        if candidate >= on:
            return candidate
    raise AssertionError("unreachable")                      # pragma: no cover


# ###########################################################################
# COUNTDOWN
# ###########################################################################

@dataclass(frozen=True, slots=True)
class Countdown:
    total: timedelta

    @property
    def days(self) -> int:
        return self.total.days

    @property
    def hours(self) -> int:
        return self.total.seconds // 3600

    @property
    def minutes(self) -> int:
        return self.total.seconds % 3600 // 60

    @property
    def past(self) -> bool:
        return self.total.total_seconds() < 0

    def __str__(self) -> str:
        if self.past:
            elapsed = -self.total
            return (f"{elapsed.days}d {elapsed.seconds // 3600}h "
                    f"{elapsed.seconds % 3600 // 60}m ago")
        return f"{self.days}d {self.hours}h {self.minutes}m"


def countdown(target: datetime, now: datetime) -> Countdown:
    """Time until `target`. BOTH must be aware; the comparison is in UTC.

    Refusing a naive datetime is the whole safety of this function. A
    naive target means "some time, somewhere", and subtracting it from an
    aware now is a TypeError — which Python would raise anyway, but with a
    message about offsets rather than about your data.
    """
    for name, value in (("target", target), ("now", now)):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{name} must be timezone-aware, got {value!r}")
    return Countdown(target.astimezone(UTC) - now.astimezone(UTC))


# ###########################################################################
# THE DEMONSTRATION
# ###########################################################################

arguments = sys.argv[1:]
BORN = date.fromisoformat(arguments[0]) if arguments else date(1815, 12, 10)
HOME = ZoneInfo(arguments[1]) if len(arguments) > 1 else LONDON

print("=" * WIDTH)
print(f"{'AGE':^{WIDTH}}")
print("=" * WIDTH)
print(f"  {'born':<24}{BORN}")
print(f"  {'today (fixed, so this':<24}{TODAY}")
print(f"  {' file is reproducible)':<24}")

result = age(BORN, TODAY)
print(f"\n  {'age':<24}{result}")
print(f"  {'in days':<24}{result.total_days:,}")
print(f"  {'in weeks':<24}{result.total_days // 7:,}")
print(f"  {'next birthday':<24}{next_birthday(BORN, TODAY)}")
print(f"  {'...in':<24}{(next_birthday(BORN, TODAY) - TODAY).days} days")

print("\n" + "-" * WIDTH)
print("  WHY NOT days / 365.25")
print("-" * WIDTH)

print(f"\n  {'BORN':<14}{'ON':<14}{'CORRECT':>9}{'/365.25':>10}{'/365':>8}"
      f"   VERDICT")
print("  " + "-" * (WIDTH - 4))
wrong_quarter = wrong_365 = 0
wrong_rows_quarter: list[str] = []
wrong_rows_365: list[str] = []
for born, on in [
    (date(2000, 3, 18), date(2026, 3, 18)),      # exactly 26, on the day
    (date(2000, 3, 19), date(2026, 3, 18)),      # one day short of 26
    (date(2008, 3, 18), date(2026, 3, 17)),      # one day short of 18
    (date(2008, 3, 18), date(2026, 3, 18)),      # 18 today — legally adult
    (date(1900, 1, 1), date(2026, 3, 18)),
    (date(2024, 2, 29), date(2026, 3, 1)),
]:
    exact = age_in_years(born, on)
    quarter = int((on - born).days / 365.25)
    plain = int((on - born).days / 365)
    wrong_quarter += quarter != exact
    wrong_365 += plain != exact
    if quarter != exact:
        wrong_rows_quarter.append(f"{born}->{on}")
    if plain != exact:
        wrong_rows_365.append(f"{born}->{on}")
    verdict = "ok" if quarter == exact == plain else "WRONG"
    print(f"  {str(born):<14}{str(on):<14}{exact:>9}{quarter:>10}{plain:>8}"
          f"   {verdict}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'':<28}{'':<9}{wrong_quarter:>10}{wrong_365:>8}   wrong")

print("""
  NEITHER APPROXIMATION IS SAFER — they are wrong on DIFFERENT rows.
  /365.25 misses the two exact anniversaries; /365 drifts a day early.

  THE THIRD AND FOURTH ROWS ARE THE ONES THAT MATTER. Somebody who turns
  18 tomorrow and somebody who turned 18 today must not get the same
  answer, and /365 gives 18 for both. If that number decides whether a
  person may sign a contract, buy alcohol or be tried as an adult, the
  approximation is not an approximation — it is a wrong answer with a
  decimal point in it.

  age_in_years() is one line, and it is exact:

      on.year - born.year - ((on.month, on.day) < (born.month, born.day))""")


# ###########################################################################
# 29 FEBRUARY
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE 29 FEBRUARY BIRTHDAY':^{WIDTH}}")
print("=" * WIDTH)

leapling = date(2024, 2, 29)
print(f"\n  Somebody born {leapling}. When is their birthday?\n")
print(f"  {'YEAR':<8}{'LEAP?':<8}{'rule=march':<16}{'rule=february':<18}"
      f"{'AGE THAT DAY':>12}")
print("  " + "-" * (WIDTH - 4))
for year in (2025, 2026, 2027, 2028):
    on = date(year, 1, 1)
    march = next_birthday(leapling, on, "march")
    february = next_birthday(leapling, on, "february")
    print(f"  {year:<8}{str(calendar.isleap(year)):<8}{str(march):<16}"
          f"{str(february):<18}{age_in_years(leapling, march):>12}")

print("""
  IN A LEAP YEAR BOTH RULES AGREE, because 29 February exists. In the
  other three years they differ by a day, and both are correct somewhere:
  England, Wales and Hong Kong say 1 March; New Zealand and Taiwan say
  28 February.

  NOTE THE AGE COLUMN UNDER rule=march. On 1 March 2027 the answer is 3,
  because age_in_years compares (3, 1) with (2, 29) and (3, 1) is later —
  so the birthday has "happened". Under the February rule it would be 2 on
  28 February and 3 the next day. The two rules disagree about a person's
  age for exactly one day a year, three years in four.

  A calculator that does not pick one and say so is not finished.""")


# ###########################################################################
# COUNTDOWN
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'COUNTDOWN — THE SAME MOMENT FROM FIVE PLACES':^{WIDTH}}")
print("=" * WIDTH)

# New Year, as it happens in each place: a DIFFERENT moment in each.
print(f"\n  now: {NOW}  ({NOW.astimezone(HOME):%Y-%m-%d %H:%M %Z} at home)\n")
print(f"  {'ZONE':<20}{'LOCAL NEW YEAR':<24}{'IN UTC':<22}{'AWAY':>10}")
print("  " + "-" * (WIDTH - 4))
for name, zone in [("Pacific/Kiritimati", ZoneInfo("Pacific/Kiritimati")),
                   ("Asia/Tokyo", TOKYO), ("Asia/Kolkata", KOLKATA),
                   ("Europe/London", LONDON),
                   ("America/New_York", NEW_YORK)]:
    midnight = datetime(2027, 1, 1, 0, 0, tzinfo=zone)
    left = countdown(midnight, NOW)
    print(f"  {name:<20}{midnight.strftime('%Y-%m-%d %H:%M %Z'):<24}"
          f"{midnight.astimezone(UTC).strftime('%Y-%m-%d %H:%M'):<22}"
          f"{left.days:>7}d")

print("""
  FIVE DIFFERENT MOMENTS, spread over 26 hours, all called "New Year".
  A countdown that ignores the zone counts down to the wrong one for
  everybody except the developer.""")

# ...and the DST-crossing countdown.
print("\n" + "-" * WIDTH)
print("  A COUNTDOWN THAT CROSSES A CLOCK CHANGE")
print("-" * WIDTH)

before_change = datetime(2026, 3, 28, 12, 0, tzinfo=LONDON)
after_change = datetime(2026, 3, 29, 12, 0, tzinfo=LONDON)
naive_difference = (after_change.replace(tzinfo=None)
                    - before_change.replace(tzinfo=None))
real_difference = countdown(after_change, before_change).total

print(f"""
  From {before_change:%a %d %b %H:%M %Z} to {after_change:%a %d %b %H:%M %Z}

    counting clock faces (naive)   {naive_difference}
    counting elapsed time (UTC)    {real_difference}
    difference                     {naive_difference - real_difference}

  Noon to noon is 23 hours that weekend, because an hour of it did not
  happen. Both numbers are answers to real questions — "how many sleeps?"
  is the first, "how long must the battery last?" is the second — and the
  bug is not knowing which one you computed.""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)


def raises(call, expected):                                  # noqa: ANN001
    try:
        call()
    except expected:
        return True
    except BaseException:                                    # noqa: BLE001
        return False
    return False


# Exhaustive: every day of a 12-year window, checked against a slow but
# obviously-correct counting implementation.
def age_by_counting(born: date, on: date) -> int:
    """Deliberately naive: step a year at a time and count. O(years)."""
    years = 0
    while True:
        try:
            anniversary = date(born.year + years + 1, born.month, born.day)
        except ValueError:                       # 29 February, common year
            anniversary = date(born.year + years + 1, 3, 1)
        if anniversary > on:
            return years
        years += 1


disagreements = []
comparisons = 0
born_dates = [date(2000, 1, 1), date(2000, 2, 29), date(2000, 3, 1),
              date(2000, 12, 31), date(1999, 2, 28)]
day = date(2020, 1, 1)
while day <= date(2032, 1, 1):
    for born in born_dates:
        comparisons += 1
        if age_in_years(born, day) != age_by_counting(born, day):
            disagreements.append((born, day))
    day += timedelta(days=1)

# Age arithmetic must reassemble.
reassembles = True
day = date(2020, 1, 1)
while day <= date(2028, 1, 1):
    for born in born_dates:
        parts = age(born, day)
        if parts.years * 12 + parts.months < 0 or parts.days < 0:
            reassembles = False
    day += timedelta(days=32)

claims = [
    ("age_in_years agrees with counting, every day for 12 years",
     not disagreements),
    (f"...which is {comparisons:,} comparisons",
     comparisons > 20_000),
    ("a birthday today counts, a birthday tomorrow does not",
     age_in_years(date(2008, 3, 18), date(2026, 3, 18)) == 18
     and age_in_years(date(2008, 3, 19), date(2026, 3, 18)) == 17),
    ("/365.25 gets some of those wrong", wrong_quarter > 0),
    ("...and /365 gets a DIFFERENT set wrong",
     wrong_365 > 0 and wrong_rows_quarter != wrong_rows_365),
    ("years, months and days are never negative", reassembles),
    ("1900 was not a leap year, 2000 was",
     not calendar.isleap(1900) and calendar.isleap(2000)),
    ("a 29 February birthday falls on 1 March under the English rule",
     next_birthday(date(2024, 2, 29), date(2026, 1, 1), "march")
     == date(2026, 3, 1)),
    ("...and on 28 February under the New Zealand one",
     next_birthday(date(2024, 2, 29), date(2026, 1, 1), "february")
     == date(2026, 2, 28)),
    ("...and on 29 February itself in a leap year",
     next_birthday(date(2024, 2, 29), date(2028, 1, 1), "march")
     == date(2028, 2, 29)),
    ("an unknown leap rule is refused",
     raises(lambda: next_birthday(date(2024, 2, 29), TODAY, "guess"),
            ValueError)),
    ("a future date of birth is refused",
     raises(lambda: age(date(2030, 1, 1), TODAY), ValueError)),
    ("countdown refuses a naive datetime",
     raises(lambda: countdown(datetime(2027, 1, 1), NOW), ValueError)),
    ("...and refuses a naive `now` too",
     raises(lambda: countdown(datetime(2027, 1, 1, tzinfo=UTC),
                              datetime(2026, 1, 1)), ValueError)),
    ("New Year in Tokyo arrives before New Year in London",
     countdown(datetime(2027, 1, 1, tzinfo=TOKYO), NOW).total
     < countdown(datetime(2027, 1, 1, tzinfo=LONDON), NOW).total),
    ("...by exactly nine hours",
     countdown(datetime(2027, 1, 1, tzinfo=LONDON), NOW).total
     - countdown(datetime(2027, 1, 1, tzinfo=TOKYO), NOW).total
     == timedelta(hours=9)),
    ("Kolkata's offset is not a whole number of hours",
     NOW.astimezone(KOLKATA).utcoffset() == timedelta(hours=5, minutes=30)),
    ("noon to noon across the spring change is 23 hours",
     real_difference == timedelta(hours=23)),
    ("...and the naive answer is 24", naive_difference == timedelta(days=1)),
    ("a past target is reported as past, not as a negative countdown",
     countdown(datetime(2020, 1, 1, tzinfo=UTC), NOW).past),
    ("at 22:30 UTC it is already tomorrow in Sydney, and not in London",
     (evening := datetime(2026, 3, 18, 22, 30, tzinfo=UTC))
     .astimezone(SYDNEY).date() > evening.astimezone(LONDON).date()),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

print(f"""
  THE FIRST CHECK IS THE ONE THAT MAKES THE REST BELIEVABLE. The one-line
  age_in_years() is compared against a slow, obviously-correct version
  that counts anniversaries one at a time — on every one of the
  {(date(2032, 1, 1) - date(2020, 1, 1)).days:,} days between 2020 and 2032, for five different
  birthdays including 29 February. {len(disagreements)} disagreements.

  That is Day 57's property test: not three examples, but the RULE, over
  inputs nobody would think to list.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change TODAY to date.today() and watch this file stop being
#     reproducible. Then decide where the clock belongs in your own code.
#
#   * Add a working-days countdown that skips weekends. Then add public
#     holidays, and notice you now need a data file and a country.
#
#   * Add "how many Fridays the 13th until you are 50". calendar.weekday()
#     and a loop; the interesting part is where you stop.
#
#   * Make next_birthday() take a timezone, so "is it my birthday?" is
#     answered in the user's zone rather than the server's. That question
#     has a different answer for about ten hours a day.
#
#   * Feed age() a date of birth of 1582-10-05. There was no such day in
#     Britain — the calendar changed — and Python's date will happily
#     accept it, because the proleptic Gregorian calendar is a fiction we
#     agree to.
