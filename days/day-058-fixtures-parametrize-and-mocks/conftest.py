"""Fixtures shared by every test file in this directory and below.

conftest.py is not imported by anything — pytest finds it, imports it, and
makes every fixture in it available by NAME to every test underneath. That
is the whole mechanism, and it is why fixtures never need importing.

It also puts this directory on sys.path, which is how tests/ imports
bookings.py without an installed package.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "day-040-milestone-your-own-toolkit"))

from bookings import Booking  # noqa: E402


# ---------------------------------------------------------------------------
# The clock
# ---------------------------------------------------------------------------

@pytest.fixture
def now():
    """A FIXED moment. Every time-dependent test starts from here.

    Wednesday 18 March 2026, 10:00. Chosen and written down, so a test
    that behaves differently on a Sunday fails on purpose rather than at
    the weekend.
    """
    return datetime(2026, 3, 18, 10, 0)


@pytest.fixture
def later(now):
    """A fixture that USES another fixture. Ask for it by name; that is all.

    pytest resolves the graph: a test asking for `later` gets `now` built
    first, and both see the SAME object.
    """
    def at(**offset):
        return now + timedelta(**offset)
    return at


# ---------------------------------------------------------------------------
# The thing under test
# ---------------------------------------------------------------------------

@pytest.fixture
def make_booking(now):
    """A FACTORY fixture — the pattern worth stealing.

    A plain fixture gives every test the same object. A factory gives each
    test the object IT needs, while keeping the twelve boring defaults in
    one place. When a field is added, this function changes and no test
    does.
    """
    def build(**overrides):
        defaults = {
            "reference": "AB-1234",
            "email": "ada@example.com",
            "starts_at": now + timedelta(hours=4),
            "ends_at": now + timedelta(hours=6),
            "party_size": 4,
            "created_at": now,
        }
        return Booking(**{**defaults, **overrides})
    return build


@pytest.fixture
def valid(make_booking):
    """One booking with nothing wrong with it, for the tests that need
    a baseline to break in exactly one way."""
    return make_booking()


@pytest.fixture
def diary(make_booking, now):
    """Three existing bookings, for the overlap rules."""
    return [
        make_booking(reference="ZZ-0001",
                     starts_at=now + timedelta(hours=12),
                     ends_at=now + timedelta(hours=13)),
        make_booking(reference="ZZ-0002",
                     starts_at=now + timedelta(hours=26),
                     ends_at=now + timedelta(hours=28)),
        make_booking(reference="ZZ-0003",
                     starts_at=now + timedelta(hours=30),
                     ends_at=now + timedelta(hours=31)),
    ]
