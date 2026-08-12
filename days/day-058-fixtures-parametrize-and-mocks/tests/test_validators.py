"""Table-driven tests for the booking validator.

THE TABLE IS THE TEST. Everything below is one of two shapes:

    a list of (input, expected) rows fed to @parametrize
    a property asserted over many generated inputs

No test constructs a Booking by hand — `make_booking` (in conftest.py)
does, so adding a field to Booking changes one function instead of thirty.
"""

from datetime import timedelta

import pytest
from bookings import MAX_PARTY, Booking, hold_expired, next_free_slot, validate


def fields(problems):
    """The set of fields that were complained about."""
    return {problem.field for problem in problems}


# ---------------------------------------------------------------------------
# The happy path, once
# ---------------------------------------------------------------------------

def test_a_valid_booking_has_no_problems(valid, now):
    assert validate(valid, now=now) == []


# ---------------------------------------------------------------------------
# THE TABLE: one row per way a booking can be wrong
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("overrides, expected_field", [
    # reference
    ({"reference": ""}, "reference"),
    ({"reference": "   "}, "reference"),
    ({"reference": "ab-1234"}, "reference"),          # lower case
    ({"reference": "AB1234"}, "reference"),           # no dash
    ({"reference": "ABC-1234"}, "reference"),         # three letters
    ({"reference": "AB-12345"}, "reference"),         # five digits
    # email
    ({"email": ""}, "email"),
    ({"email": "ada"}, "email"),
    ({"email": "ada@"}, "email"),
    ({"email": "ada@example"}, "email"),              # no TLD
    ({"email": "ada @example.com"}, "email"),         # a space
    ({"email": "ada@@example.com"}, "email"),
    # party size
    ({"party_size": 0}, "party_size"),
    ({"party_size": -1}, "party_size"),
    ({"party_size": MAX_PARTY + 1}, "party_size"),
    ({"party_size": 4.5}, "party_size"),
    ({"party_size": True}, "party_size"),             # bool is not an int
])
def test_one_bad_field_is_reported(make_booking, now, overrides,
                                   expected_field):
    """SEVENTEEN CASES, seventeen independently named tests.

    Each row breaks exactly ONE field of an otherwise valid booking, so a
    failure names the rule that stopped working.
    """
    problems = validate(make_booking(**overrides), now=now)
    assert expected_field in fields(problems)


@pytest.mark.parametrize("overrides", [
    {"reference": "AB-1234"},
    {"email": "ada@example.com"},
    {"party_size": 1},
    {"party_size": MAX_PARTY},
])
def test_the_boundaries_that_should_be_ACCEPTED(make_booking, now, overrides):
    """The other half of every table: what must NOT be rejected.

    A validator that rejects everything passes every test above.
    """
    assert validate(make_booking(**overrides), now=now) == []


# ---------------------------------------------------------------------------
# Time — and not one mock in sight
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hours, expect_problem", [
    (-24, True),      # yesterday
    (-1, True),
    (0, True),        # exactly now: not the future
    (4, False),       # the default
    (24 * 30, False),
])
def test_a_booking_must_start_in_the_future(make_booking, now, hours,
                                            expect_problem):
    booking = make_booking(starts_at=now + timedelta(hours=hours),
                           ends_at=now + timedelta(hours=hours + 2))
    problems = [p for p in validate(booking, now=now)
                if p.message == "must be in the future"]
    assert bool(problems) is expect_problem


@pytest.mark.parametrize("minutes, expected", [
    (0, "ends_at"),          # zero length
    (-30, "ends_at"),        # ends before it starts
    (14, "ends_at"),         # under the minimum
    (15, None),              # exactly the minimum
    (60, None),
    (8 * 60, None),          # exactly the maximum
    (8 * 60 + 1, "ends_at"),  # over it
])
def test_duration_limits(make_booking, now, minutes, expected):
    """THE BOUNDARIES, from both sides. 15 passes, 14 fails, 480 passes,
    481 fails — which is where an off-by-one lives."""
    start = now + timedelta(hours=4)
    booking = make_booking(starts_at=start,
                           ends_at=start + timedelta(minutes=minutes))
    problems = [p for p in validate(booking, now=now) if p.field == "ends_at"]
    assert (problems[0].field if problems else None) == expected


@pytest.mark.parametrize("hour, ok", [
    (7, False), (8, True), (12, True), (21, True), (22, False), (23, False),
])
def test_opening_hours(make_booking, now, hour, ok):
    start = (now + timedelta(days=1)).replace(hour=hour)
    booking = make_booking(starts_at=start, ends_at=start + timedelta(hours=1))
    problems = [p for p in validate(booking, now=now)
                if "opens at" in p.message]
    assert (not problems) is ok


# ---------------------------------------------------------------------------
# The diary
# ---------------------------------------------------------------------------

def test_a_booking_that_clashes_is_rejected(make_booking, now, diary):
    clash = make_booking(reference="CD-5678",
                         starts_at=now + timedelta(hours=12, minutes=30),
                         ends_at=now + timedelta(hours=14))
    problems = validate(clash, now=now, existing=diary)
    assert any("overlaps ZZ-0001" in p.message for p in problems)


def test_a_booking_that_ends_exactly_when_another_starts_is_fine(
        make_booking, now, diary):
    """THE BOUNDARY THAT MATTERS: touching is not overlapping."""
    adjacent = make_booking(reference="CD-5678",
                            starts_at=now + timedelta(hours=11),
                            ends_at=now + timedelta(hours=12))
    assert validate(adjacent, now=now, existing=diary) == []


def test_a_duplicate_reference_is_rejected(make_booking, now, diary):
    duplicate = make_booking(reference="ZZ-0001",
                             starts_at=now + timedelta(hours=2),
                             ends_at=now + timedelta(hours=3))
    problems = validate(duplicate, now=now, existing=diary)
    assert any(p.message == "is already taken" for p in problems)


def test_the_diary_is_not_modified_by_validation(now, diary, make_booking):
    before = list(diary)
    validate(make_booking(reference="CD-5678"), now=now, existing=diary)
    assert diary == before


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def test_every_problem_names_a_real_field(make_booking, now):
    """Whatever is wrong, the field must exist on the object — otherwise a
    form cannot show the message next to the input that caused it."""
    disaster = make_booking(reference="", email="no", party_size=99,
                            starts_at=now - timedelta(days=1),
                            ends_at=now - timedelta(days=2))
    problems = validate(disaster, now=now)
    assert problems
    for problem in problems:
        assert problem.field in Booking.__dataclass_fields__


def test_validation_is_deterministic(valid, now, diary):
    """Two runs, same answer. A validator that consults the clock, a set's
    ordering or a dict's hash would fail this intermittently."""
    first = validate(valid, now=now, existing=diary)
    second = validate(valid, now=now, existing=diary)
    assert [str(p) for p in first] == [str(p) for p in second]


# ---------------------------------------------------------------------------
# hold_expired and next_free_slot — pure functions of `now`
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("minutes, expired", [
    (0, False), (14, False), (15, True), (60, True),
])
def test_hold_expires_after_fifteen_minutes(valid, now, later, minutes,
                                            expired):
    assert hold_expired(valid, now=later(minutes=minutes)) is expired


def test_next_free_slot_skips_a_busy_hour(now, diary):
    """now is 10:00; the diary is busy 22:00-23:00 tomorrow, so the first
    free slot is simply the next hour."""
    assert next_free_slot(diary, now=now).hour == 11


def test_next_free_slot_never_returns_a_closed_hour(now, diary):
    for hours in range(0, 24):
        moment = now + timedelta(hours=hours)
        slot = next_free_slot(diary, now=moment)
        assert slot is None or 8 <= slot.hour < 22
