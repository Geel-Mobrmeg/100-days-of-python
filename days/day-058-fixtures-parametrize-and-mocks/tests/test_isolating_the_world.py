"""monkeypatch, mock, and the argument for needing neither.

Four things a test must take away from the code it is testing:

    the clock          or the test passes only in the afternoon
    the environment    or it passes only on your machine
    the filesystem     or it leaves rubbish and fails the second time
    the network        or it is not a test, it is a monitoring check

pytest gives you a tool for each, and the last section of this file argues
that the best tool is usually a parameter.
"""

import datetime as datetime_module
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, call

import bookings
import legacy
import pytest
from mytoolkit import RetryError, retry


# ---------------------------------------------------------------------------
# 1. monkeypatch: the clock, taken away
# ---------------------------------------------------------------------------

class FrozenDatetime(datetime):
    """A datetime whose now() is a constant. Set FrozenDatetime.frozen."""

    frozen = datetime(2026, 3, 18, 10, 0)

    @classmethod
    def now(cls, tz=None):
        return cls.frozen


@pytest.fixture
def frozen_clock(monkeypatch, now):
    """Replace the `datetime` name INSIDE legacy.py for one test.

    PATCH WHERE IT IS USED, NOT WHERE IT IS DEFINED. legacy.py says
    `from datetime import datetime`, which binds its OWN name at import
    time. Patching datetime.datetime rebinds the attribute on the
    datetime module and legacy.datetime carries on pointing at the
    original — see the test below, which measures exactly that.

    monkeypatch undoes every change when the test ends, even if the test
    failed or raised. That is the reason to use it rather than assigning
    to the module yourself: an un-undone patch leaks into every test that
    runs afterwards, and the failure then appears somewhere else entirely.
    """
    FrozenDatetime.frozen = now
    monkeypatch.setattr(legacy, "datetime", FrozenDatetime)

    def move_to(moment):
        FrozenDatetime.frozen = moment
    return move_to


def test_patching_the_wrong_module_does_nothing(monkeypatch, now):
    """The single commonest mocking mistake, demonstrated rather than
    described.

    Patching the datetime MODULE'S attribute is correct, targeted, undone
    properly — and has no effect at all on a module that imported the name
    directly.
    """
    FrozenDatetime.frozen = now.replace(hour=3)      # the middle of the night
    monkeypatch.setattr(datetime_module, "datetime", FrozenDatetime)

    assert legacy.datetime is not FrozenDatetime     # legacy kept its own
    assert legacy.datetime.now().year >= 2024        # ...and the real clock


@pytest.mark.parametrize("minutes, expired", [
    (0, False), (14, False), (15, True), (60, True),
])
def test_legacy_hold_expired_needs_the_clock_patched(frozen_clock, valid, now,
                                                     minutes, expired):
    frozen_clock(now + timedelta(minutes=minutes))
    assert legacy.hold_expired(valid) is expired


@pytest.mark.parametrize("hour, open_now", [
    (7, False), (8, True), (21, True), (22, False),
])
def test_legacy_is_open_needs_the_clock_patched(frozen_clock, now, hour,
                                                open_now):
    frozen_clock(now.replace(hour=hour))
    assert legacy.is_open() is open_now


def test_the_patch_is_undone_afterwards():
    """Proof, in a test that deliberately runs after the ones above.

    If monkeypatch had leaked, legacy.datetime would still be frozen at
    10:00 on 18 March 2026 — and every test below would inherit it.
    """
    assert legacy.datetime is datetime
    assert datetime_module.datetime is datetime
    assert legacy.datetime.now().year >= 2024


# ---------------------------------------------------------------------------
# 2. monkeypatch: the environment
# ---------------------------------------------------------------------------

def test_venue_name_falls_back_when_unset(monkeypatch):
    monkeypatch.delenv("VENUE_NAME", raising=False)
    assert legacy.venue_name() == "unnamed venue"


def test_venue_name_reads_the_environment(monkeypatch):
    monkeypatch.setenv("VENUE_NAME", "The Analytical Engine")
    assert legacy.venue_name() == "The Analytical Engine"


# ---------------------------------------------------------------------------
# 3. monkeypatch: time.sleep, which is what makes retry testable
# ---------------------------------------------------------------------------

@pytest.fixture
def no_waiting(monkeypatch):
    """Make every time.sleep() instant, and record what was asked for.

    @retry(times=4, delay=0.5, backoff=2) really waits 0.5 + 1 + 2 = 3.5
    seconds. Three such tests is eleven seconds of a suite that should
    take milliseconds — and a suite people stop running is a suite that
    does not protect anything.
    """
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)
    return slept


def test_retry_gives_up_after_the_right_number_of_attempts(no_waiting):
    attempts = []

    @retry(times=4, delay=0.5, backoff=2.0, quiet=True)
    def always_fails():
        attempts.append(1)
        raise ConnectionError("no route to host")

    with pytest.raises(RetryError):
        always_fails()

    assert len(attempts) == 4


def test_retry_backs_off_exponentially(no_waiting):
    """The WAITS are asserted without any waiting happening.

    This is the payoff: the delays are data now, so the schedule can be
    checked exactly instead of being taken on trust.
    """
    @retry(times=4, delay=0.5, backoff=2.0, quiet=True)
    def always_fails():
        raise ConnectionError("no route to host")

    with pytest.raises(RetryError):
        always_fails()

    assert no_waiting == [0.5, 1.0, 2.0]        # three waits for four tries
    assert sum(no_waiting) == 3.5               # ...which never happened


def test_retry_stops_as_soon_as_a_call_succeeds(no_waiting):
    calls = []

    @retry(times=5, delay=1.0, quiet=True)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("temporary")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3
    assert len(no_waiting) == 2                 # two waits, not five


def test_the_suite_did_not_actually_sleep(no_waiting):
    """A test about the tests: 3.5 seconds of configured delay, and this
    file runs in milliseconds."""
    started = time.perf_counter()

    @retry(times=4, delay=1.0, backoff=3.0, quiet=True)
    def always_fails():
        raise ValueError("nope")

    with pytest.raises(RetryError):
        always_fails()

    assert sum(no_waiting) == 13.0              # 1 + 3 + 9
    assert time.perf_counter() - started < 0.5


# ---------------------------------------------------------------------------
# 4. tmp_path and capsys — the two built-ins you will use most
# ---------------------------------------------------------------------------

def test_tmp_path_is_a_fresh_directory_every_time(tmp_path):
    """pytest creates it, hands it over, and cleans it up. No fixture of
    your own, no leftover files, no test that only passes the first time.
    """
    assert tmp_path.is_dir()
    assert not list(tmp_path.iterdir())

    (tmp_path / "diary.txt").write_text("AB-1234\n", encoding="utf-8")
    assert (tmp_path / "diary.txt").read_text(encoding="utf-8") == "AB-1234\n"


def test_tmp_path_is_not_shared_with_the_previous_test(tmp_path):
    assert not (tmp_path / "diary.txt").exists()


def test_capsys_captures_what_was_printed(capsys):
    @retry(times=2, delay=0)
    def always_fails():
        raise ValueError("boom")

    with pytest.raises(RetryError):
        always_fails()

    printed = capsys.readouterr().out
    assert "attempt 1/2" in printed
    assert "ValueError: boom" in printed


# ---------------------------------------------------------------------------
# 5. Mock — for a collaborator you must not really call
# ---------------------------------------------------------------------------

def test_confirm_sends_exactly_one_message(valid):
    notifier = Mock()

    assert legacy.confirm(valid, notifier) == "confirmed"

    notifier.send.assert_called_once()
    address, subject, body = notifier.send.call_args.args
    assert address == "ada@example.com"
    assert "AB-1234" in subject


def test_confirm_passes_the_time_through_to_the_message(valid, now):
    notifier = Mock()
    legacy.confirm(valid, notifier)
    _, _, body = notifier.send.call_args.args
    assert f"{valid.starts_at:%H:%M}" in body


def test_a_mock_can_be_made_to_fail(valid):
    """side_effect is how you test the unhappy path of a collaborator."""
    notifier = Mock()
    notifier.send.side_effect = ConnectionError("SMTP is down")

    with pytest.raises(ConnectionError):
        legacy.confirm(valid, notifier)


def test_a_mock_records_every_call_in_order(valid, make_booking):
    notifier = Mock()
    for reference in ("AB-1234", "CD-5678"):
        legacy.confirm(make_booking(reference=reference), notifier)

    assert notifier.send.call_count == 2
    assert notifier.send.call_args_list[0] != notifier.send.call_args_list[1]
    assert notifier.send.mock_calls[0] == call(
        "ada@example.com", "Booking AB-1234 confirmed",
        notifier.send.call_args_list[0].args[2])


def test_a_mock_agrees_to_anything_which_is_the_danger(valid):
    """THE COST OF MOCKING, in four lines.

    A Mock has every attribute and accepts every call. Rename send() to
    deliver() in Notifier and this test still passes, because the mock
    grows a deliver() too — so the test now proves nothing about a class
    it no longer matches.
    """
    notifier = MagicMock()
    notifier.send_the_thing_that_does_not_exist("anything", 1, 2, 3)
    notifier.nonsense.deeply.nested.attribute()
    assert notifier.whatever() is not None


# ---------------------------------------------------------------------------
# 6. ...and the version that needed none of this
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("minutes, expired", [
    (0, False), (14, False), (15, True), (60, True),
])
def test_the_same_rule_with_the_clock_as_a_parameter(valid, later, minutes,
                                                     expired):
    """Compare with test_legacy_hold_expired_needs_the_clock_patched.

    Same four cases, same assertions. This one needs no fixture that
    subclasses datetime, no monkeypatch, and nothing to undo — because
    bookings.hold_expired() takes `now` instead of asking for it.

    MOCKING IS A TOOL FOR CODE YOU CANNOT CHANGE. When you can change it,
    a parameter is cheaper, faster and cannot leak into another test.
    """
    assert bookings.hold_expired(valid, now=later(minutes=minutes)) is expired
