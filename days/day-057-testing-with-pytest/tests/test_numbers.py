"""Tests for mytoolkit.numbers.

NAMING: the file starts with test_, the functions start with test_, and
that is the whole of pytest's discovery rule. No registration, no suite
object, no base class to inherit.

Each name says WHAT IS BEING CLAIMED, so a failure report reads as a
sentence:

    FAILED test_numbers.py::test_human_bytes_promotes_at_the_rounding_boundary
"""

import pytest
from mytoolkit import clamp, duration, human_bytes, percent


# ---------------------------------------------------------------------------
# clamp
# ---------------------------------------------------------------------------

def test_clamp_returns_the_value_when_it_is_inside_the_range():
    # ARRANGE — the inputs
    value, low, high = 5, 0, 10
    # ACT — the one call under test
    result = clamp(value, low, high)
    # ASSERT — one claim
    assert result == 5


def test_clamp_pulls_a_value_above_the_range_down_to_the_top():
    assert clamp(15, 0, 10) == 10


def test_clamp_pushes_a_value_below_the_range_up_to_the_bottom():
    assert clamp(-3, 0, 10) == 0


@pytest.mark.parametrize("value, expected", [
    (0, 0),         # the boundary itself
    (10, 10),       # the other boundary
    (0.0001, 0.0001),
    (9.9999, 9.9999),
    (-1e9, 0),
    (1e9, 10),
])
def test_clamp_at_and_around_the_boundaries(value, expected):
    """One test, six cases, six lines in the report if one fails."""
    assert clamp(value, 0, 10) == expected


def test_clamp_rejects_an_impossible_range():
    """An inverted range is a BUG in the caller, so it must raise."""
    with pytest.raises(ValueError) as caught:
        clamp(5, 10, 0)
    # The message is part of the contract: it must name both numbers.
    assert "10" in str(caught.value)
    assert "0" in str(caught.value)


# ---------------------------------------------------------------------------
# percent
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("part, whole, places, expected", [
    (1, 4, 1, "25.0%"),
    (1, 3, 2, "33.33%"),
    (1, 3, 0, "33%"),
    (0, 5, 1, "0.0%"),
    (5, 5, 1, "100.0%"),
    (-1, 4, 1, "-25.0%"),
    (3, 2, 1, "150.0%"),
])
def test_percent_formats(part, whole, places, expected):
    assert percent(part, whole, places=places) == expected


@pytest.mark.parametrize("whole", [0, 0.0, -0.0])
def test_percent_returns_a_sentinel_rather_than_dividing_by_zero(whole):
    """An empty dataset is a normal state, not an error. Day 40 decided
    this deliberately, so the test records the decision."""
    assert percent(5, whole) == "n/a"


# ---------------------------------------------------------------------------
# human_bytes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("count, expected", [
    (0, "0 B"),
    (1, "1 B"),
    (512, "512 B"),
    (1023, "1023 B"),
    (1024, "1.0 KB"),
    (1536, "1.5 KB"),
    (1_500_000_000, "1.4 GB"),
])
def test_human_bytes_formats(count, expected):
    assert human_bytes(count) == expected


@pytest.mark.parametrize("count, expected", [
    (1024 * 1024 - 1, "1.0 MB"),          # 1023.999 KB
    (1024 ** 3 - 1, "1.0 GB"),            # 1023.999 MB
    (1024 ** 4 - 1, "1.0 TB"),
])
def test_human_bytes_promotes_at_the_rounding_boundary(count, expected):
    """BUG 1, found by this test.

    A value that rounds UP to 1024.0 in its unit must be shown in the next
    unit. The Day 40 version compared before rounding and printed
    '1024.0 KB', which is a quantity that does not exist.
    """
    assert human_bytes(count) == expected


def test_human_bytes_never_prints_a_value_of_1024_or_more():
    """The property behind bug 1, checked over four decades of input.

    A test that states the RULE rather than three examples of it. This one
    would have caught the bug without anybody thinking of 1048575.
    """
    for exponent in range(0, 40):
        for offset in (-1, 0, 1):
            shown = human_bytes(2 ** exponent + offset)
            number = float(shown.split()[0])
            assert abs(number) < 1024, f"human_bytes said {shown!r}"


# ---------------------------------------------------------------------------
# duration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seconds, expected", [
    (0, "0:00"),
    (5, "0:05"),
    (59, "0:59"),
    (60, "1:00"),
    (75, "1:15"),
    (599, "9:59"),
    (3599, "59:59"),
    (3600, "1:00:00"),
    (3725, "1:02:05"),
    (86_400, "24:00:00"),
])
def test_duration_formats(seconds, expected):
    assert duration(seconds) == expected


@pytest.mark.parametrize("seconds, expected", [
    (-5, "-0:05"),
    (-75, "-1:15"),
    (-3725, "-1:02:05"),
])
def test_duration_handles_negative_values(seconds, expected):
    """BUG 2, found by this test.

    divmod floors on negatives — divmod(-5, 3600) is (-1, 3595) — so the
    Day 40 version rendered minus five seconds as '-1:59:55'.
    """
    assert duration(seconds) == expected


def test_duration_of_a_negative_is_the_negative_of_the_duration():
    """The property, rather than three examples."""
    for seconds in (1, 59, 60, 61, 3599, 3600, 7325):
        assert duration(-seconds) == "-" + duration(seconds)


def test_duration_truncates_rather_than_rounding():
    """A decision worth pinning down: 75.9 seconds is 1:15, not 1:16."""
    assert duration(75.9) == "1:15"
