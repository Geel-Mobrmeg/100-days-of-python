"""A first test suite. Day 57 does this properly; this is the seed of it.

    pytest
    python3 -m pytest tests/ -q
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from mytoolkit import (
    RetryError, cache, chunked, clamp, dig, duration, human_bytes,
    initials, percent, retry, slugify, truncate, unique,
)


class TestNumbers:
    def test_clamp_inside_range_is_unchanged(self):
        assert clamp(5, 0, 10) == 5

    @pytest.mark.parametrize("value,expected", [(15, 10), (-3, 0), (0, 0), (10, 10)])
    def test_clamp_boundaries(self, value, expected):
        assert clamp(value, 0, 10) == expected

    def test_clamp_rejects_inverted_range(self):
        with pytest.raises(ValueError):
            clamp(5, 10, 0)

    def test_percent_handles_zero_denominator(self):
        assert percent(5, 0) == "n/a"

    @pytest.mark.parametrize("count,expected", [
        (0, "0 B"), (512, "512 B"), (1024, "1.0 KB"), (1_500_000_000, "1.4 GB"),
    ])
    def test_human_bytes(self, count, expected):
        assert human_bytes(count) == expected

    @pytest.mark.parametrize("seconds,expected", [
        (0, "0:00"), (75, "1:15"), (3725, "1:02:05"), (86399, "23:59:59"),
    ])
    def test_duration(self, seconds, expected):
        assert duration(seconds) == expected


class TestText:
    def test_truncate_respects_the_limit_including_suffix(self):
        assert len(truncate("abcdefghij", 5)) == 5

    def test_truncate_leaves_short_text_alone(self):
        assert truncate("Hi", 8) == "Hi"

    def test_slugify_strips_punctuation_and_case(self):
        assert slugify("  Day 40: Ship It!  ") == "day-40-ship-it"

    def test_slugify_of_only_punctuation_is_empty(self):
        assert slugify("!!!") == ""

    def test_initials_handles_one_word_names(self):
        assert initials("prince") == "P"

    def test_initials_of_blank_is_empty(self):
        assert initials("   ") == ""


class TestContainers:
    def test_chunked_last_batch_may_be_short(self):
        assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_chunked_accepts_any_iterable(self):
        assert chunked(range(4), 2) == [[0, 1], [2, 3]]

    def test_chunked_rejects_zero_size(self):
        with pytest.raises(ValueError):
            chunked([1], 0)

    def test_chunked_does_not_mutate_its_argument(self):
        original = [1, 2, 3]
        chunked(original, 2)
        assert original == [1, 2, 3]

    def test_unique_keeps_first_seen_order(self):
        assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]

    def test_dig_reaches_through_lists_and_dicts(self):
        assert dig({"a": {"b": [10, 20]}}, "a", "b", 1) == 20

    def test_dig_never_raises(self):
        assert dig(None, "a", "b", default="-") == "-"
        assert dig({"a": 1}, "a", "b", default="-") == "-"
        assert dig([1, 2], 99, default="-") == "-"


class TestDecorators:
    def test_cache_returns_the_same_answer(self):
        @cache
        def square(n):
            return n * n

        assert square(4) == 16
        assert square(4) == 16
        assert square.cache_info()["hits"] == 1

    def test_cache_evicts_least_recently_used(self):
        @cache(max_size=2)
        def square(n):
            return n * n

        square(1); square(2); square(1)   # 1 is now most recently used
        square(3)                          # evicts 2, not 1
        before = square.cache_info()["hits"]
        square(1)
        assert square.cache_info()["hits"] == before + 1

    def test_retry_eventually_succeeds(self):
        state = {"n": 0}

        @retry(times=3, delay=0, catching=ValueError)
        def flaky():
            state["n"] += 1
            if state["n"] < 3:
                raise ValueError("not yet")
            return "ok"

        assert flaky() == "ok"
        assert state["n"] == 3

    def test_retry_gives_up_and_keeps_the_cause(self):
        @retry(times=2, delay=0, catching=ValueError)
        def always_fails():
            raise ValueError("nope")

        with pytest.raises(RetryError) as info:
            always_fails()
        assert isinstance(info.value.__cause__, ValueError)
