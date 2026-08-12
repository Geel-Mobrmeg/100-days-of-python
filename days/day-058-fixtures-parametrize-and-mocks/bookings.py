"""A booking validator — the thing under test today.

TWO DESIGN DECISIONS MAKE THIS TESTABLE, and both are decisions rather
than techniques:

    1. NOTHING HERE CALLS datetime.now(). Every function that needs the
       current time takes it as an argument. A function that asks the
       world what time it is can only be tested at that time.

    2. NOTHING HERE READS A DATABASE. `existing` is a plain sequence the
       caller supplies. Tests pass a list; production passes a query
       result; neither one knows about the other.

Those two turn "we need a mocking framework" into "we need an argument".
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

MINIMUM = timedelta(minutes=15)
MAXIMUM = timedelta(hours=8)
HOLD = timedelta(minutes=15)
OPENING, CLOSING = 8, 22                  # the venue's hours, 24-hour clock
MAX_PARTY = 12

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Problem:
    """One thing wrong with one field. Day 52's shape, without the raising."""

    field: str
    message: str

    def __str__(self):
        return f"{self.field}: {self.message}"


@dataclass(frozen=True, slots=True)
class Booking:
    reference: str
    email: str
    starts_at: datetime
    ends_at: datetime
    party_size: int
    created_at: datetime = field(default=datetime.min)

    @property
    def duration(self):
        return self.ends_at - self.starts_at

    def overlaps(self, other):
        return (self.starts_at < other.ends_at
                and other.starts_at < self.ends_at)


def validate(booking, *, now, existing=()):
    """Return every problem with `booking`. Never raises, never guesses.

    `now` is a PARAMETER. That one word is why the tests for this file
    need no mocking library at all.
    """
    problems = []

    if not booking.reference.strip():
        problems.append(Problem("reference", "is required"))
    elif not re.fullmatch(r"[A-Z]{2}-\d{4}", booking.reference):
        problems.append(Problem(
            "reference", f"must look like AB-1234, got {booking.reference!r}"))

    if not EMAIL.match(booking.email or ""):
        problems.append(Problem("email", f"{booking.email!r} is not an email"))

    if booking.starts_at <= now:
        problems.append(Problem("starts_at", "must be in the future"))

    if booking.ends_at <= booking.starts_at:
        problems.append(Problem("ends_at", "must be after starts_at"))
    elif booking.duration < MINIMUM:
        problems.append(Problem(
            "ends_at", f"a booking must last at least {MINIMUM}"))
    elif booking.duration > MAXIMUM:
        problems.append(Problem(
            "ends_at", f"a booking must last at most {MAXIMUM}"))

    if not OPENING <= booking.starts_at.hour < CLOSING:
        problems.append(Problem(
            "starts_at", f"the venue opens at {OPENING}:00 and closes at "
                         f"{CLOSING}:00"))

    if not isinstance(booking.party_size, int) or isinstance(
            booking.party_size, bool):
        problems.append(Problem("party_size", "must be a whole number"))
    elif not 1 <= booking.party_size <= MAX_PARTY:
        problems.append(Problem(
            "party_size", f"must be between 1 and {MAX_PARTY}, "
                          f"got {booking.party_size}"))

    for other in existing:
        if other.reference == booking.reference:
            problems.append(Problem("reference", "is already taken"))
        elif booking.overlaps(other):
            problems.append(Problem(
                "starts_at", f"overlaps {other.reference}"))

    return problems


def hold_expired(booking, *, now, hold=HOLD):
    """Has an unconfirmed booking's hold run out? Again: `now` is given."""
    return now - booking.created_at >= hold


def next_free_slot(existing, *, now, length=timedelta(hours=1)):
    """The earliest slot of `length` that clashes with nothing."""
    start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    for _ in range(24 * 7):
        candidate = Booking("XX-0000", "x@example.com", start,
                            start + length, 1)
        if (OPENING <= start.hour < CLOSING
                and not any(candidate.overlaps(o) for o in existing)):
            return start
        start += timedelta(hours=1)
    return None
