"""The same two rules, written the way that NEEDS a mock.

Nothing imports this except the tests. It exists so the two styles can be
compared on the same behaviour, in the same test file, and the comparison
can be about cost rather than taste.

Every function here reaches out and asks the world a question:

    datetime.now()      what time is it?
    os.environ          how is this deployed?
    requests-shaped     what does the server say?

...and every one of those is a thing a test has to take away from it.
"""

import os
from datetime import datetime, timedelta

HOLD = timedelta(minutes=15)


def hold_expired(booking):
    """No `now` parameter. The clock is fetched, not given."""
    return datetime.now() - booking.created_at >= HOLD


def is_open():
    """Depends on the hour it happens to be run at."""
    return 8 <= datetime.now().hour < 22


def venue_name():
    """Depends on how the machine is configured."""
    return os.environ.get("VENUE_NAME", "unnamed venue")


class Notifier:
    """A collaborator that talks to something outside the process."""

    def send(self, address, subject, body):
        raise RuntimeError(
            "this would open a network connection; a test must not")


def confirm(booking, notifier):
    """Business logic with one side effect, injected."""
    notifier.send(booking.email, f"Booking {booking.reference} confirmed",
                  f"See you at {booking.starts_at:%H:%M on %d %B}.")
    return "confirmed"
