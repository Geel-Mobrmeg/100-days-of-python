"""The four bugs, run against BOTH versions of each function.

This is the file that turns "I think there is a bug" into evidence. Every
assertion below runs twice — once against the code Day 40 shipped
(as_shipped.py) and once against the corrected package — using pytest's
`indirect`-free trick of parametrising over the two modules.

    as_shipped   expected to FAIL, and marked xfail(strict=True)
    mytoolkit    expected to pass

`strict=True` matters: if somebody fixes as_shipped.py, the xfail becomes
an XPASS and pytest reports it as a FAILURE, telling you to delete the
marker. A non-strict xfail would quietly stay green forever, which is how
a test file rots.
"""

import pytest

import as_shipped
import mytoolkit

BROKEN = pytest.param(as_shipped, marks=pytest.mark.xfail(
    strict=True, reason="the bug this day exists to find"))
FIXED = pytest.param(mytoolkit, id="mytoolkit-1.1.0")

MODULES = [BROKEN, FIXED]


@pytest.mark.parametrize("module", MODULES)
def test_bug_1_human_bytes_at_the_rounding_boundary(module):
    assert module.human_bytes(1024 * 1024 - 1) == "1.0 MB"


@pytest.mark.parametrize("module", MODULES)
def test_bug_2_duration_of_a_negative_number(module):
    assert module.duration(-5) == "-0:05"


@pytest.mark.parametrize("module", MODULES)
def test_bug_3_slugify_is_url_safe(module):
    assert module.slugify("Café") == "cafe"


@pytest.mark.parametrize("module", MODULES)
def test_bug_4_dig_reports_a_stored_none_as_none(module):
    assert module.dig({"a": None}, "a", default="MISSING") is None


# ---------------------------------------------------------------------------
# The tests that pass on BOTH — the regression guard
# ---------------------------------------------------------------------------
#
# A fix is only trustworthy if the behaviour that was already right is
# still right. These are the original doctest examples, run against both.

@pytest.mark.parametrize("module", [as_shipped, mytoolkit])
@pytest.mark.parametrize("count, expected", [
    (512, "512 B"), (2048, "2.0 KB"), (1_500_000_000, "1.4 GB"),
])
def test_the_fix_did_not_change_what_already_worked(module, count, expected):
    assert module.human_bytes(count) == expected


@pytest.mark.parametrize("module", [as_shipped, mytoolkit])
@pytest.mark.parametrize("seconds, expected", [
    (75, "1:15"), (3725, "1:02:05"), (0, "0:00"),
])
def test_duration_still_formats_positives_the_same_way(module, seconds,
                                                       expected):
    assert module.duration(seconds) == expected


@pytest.mark.parametrize("module", [as_shipped, mytoolkit])
@pytest.mark.parametrize("text, expected", [
    ("Hello, World!", "hello-world"),
    ("  Day 31: Writing Functions  ", "day-31-writing-functions"),
    ("!!!", ""),
])
def test_slugify_still_slugifies_ascii_identically(module, text, expected):
    assert module.slugify(text) == expected


@pytest.mark.parametrize("module", [as_shipped, mytoolkit])
def test_dig_still_returns_the_default_for_a_missing_key(module):
    assert module.dig({"a": 1}, "a", "b", default="-") == "-"
    assert module.dig(None, "a", default=0) == 0
