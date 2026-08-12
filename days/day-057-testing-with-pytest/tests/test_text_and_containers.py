"""Tests for mytoolkit.text and mytoolkit.containers."""

import pytest
from mytoolkit import chunked, dig, initials, slugify, truncate, unique


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text, limit, expected", [
    ("Hello, world", 8, "Hello..."),
    ("Hi", 8, "Hi"),
    ("exactly8", 8, "exactly8"),          # the boundary: no truncation
    ("exactly9!", 8, "exactly9!"[:5] + "..."),
    ("abc", 3, "abc"),
    ("abcd", 3, "abc"),                   # limit == len(suffix): no room
    ("abcd", 2, "ab"),
    ("abcd", 0, ""),
    ("abcd", -1, ""),
])
def test_truncate(text, limit, expected):
    assert truncate(text, limit) == expected


@pytest.mark.parametrize("limit", range(0, 15))
def test_truncate_never_exceeds_its_limit(limit):
    """THE PROPERTY, over every limit from 0 to 14.

    The docstring promises the limit INCLUDES the suffix. That is the kind
    of promise that is easy to break in a later edit and impossible to
    notice by reading.
    """
    assert len(truncate("abcdefghijklmnop", limit)) <= max(limit, 0)


def test_truncate_honours_a_custom_suffix():
    assert truncate("abcdefghij", 6, suffix="…") == "abcde…"
    assert len(truncate("abcdefghij", 6, suffix="…")) == 6


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("Hello, World!", "hello-world"),
    ("  Day 31: Writing Functions  ", "day-31-writing-functions"),
    ("!!!", ""),
    ("", ""),
    ("already-a-slug", "already-a-slug"),
    ("multiple   spaces", "multiple-spaces"),
    ("Trailing punctuation...", "trailing-punctuation"),
    ("MiXeD CaSe", "mixed-case"),
    ("2026 report", "2026-report"),
])
def test_slugify(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("Café", "cafe"),
    ("Café Münster", "cafe-munster"),
    ("naïve résumé", "naive-resume"),
    ("Ångström", "angstrom"),
])
def test_slugify_folds_accents_off_latin_letters(text, expected):
    """BUG 3, found by this test.

    The docstring says "URL-safe", and URL-safe means ASCII. The Day 40
    version kept every letter isalnum() accepted, so 'Café' came out as
    'café' — and the package README claimed it came out as 'caf', which
    it never did. Two wrong answers about one function.
    """
    assert slugify(text) == expected


def test_slugify_output_is_always_url_safe():
    """The property behind bug 3, over inputs nobody would think to list."""
    hostile = ["Ünïcode", "日本語のテキスト", "Ελληνικά", "Кириллица",
               "a/b?c=d&e", "100% done", "<script>", "tab\there",
               "new\nline", "emoji 🎉 party", "  ", "--__--"]
    for text in hostile:
        slug = slugify(text)
        assert slug == slug.lower()
        assert all(c.isascii() and (c.isalnum() or c == "-") for c in slug), \
            f"slugify({text!r}) produced {slug!r}"
        assert not slug.startswith("-") and not slug.endswith("-")
        assert "--" not in slug


def test_slugify_is_idempotent():
    """Slugifying a slug must change nothing, or URLs drift."""
    for text in ["Hello, World!", "Café", "  spaced  out  ", "123"]:
        once = slugify(text)
        assert slugify(once) == once


# ---------------------------------------------------------------------------
# initials
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name, expected", [
    ("Ada Augusta Byron King", "AABK"),
    ("prince", "P"),
    ("   ", ""),
    ("", ""),
    ("ada lovelace", "AL"),
    ("  extra   spaces  ", "ES"),
])
def test_initials(name, expected):
    assert initials(name) == expected


def test_initials_does_not_split_hyphenated_names():
    """NOT a bug — a documented decision, pinned so a later edit is a
    deliberate change rather than an accident."""
    assert initials("Jean-Luc Picard") == "JP"


# ---------------------------------------------------------------------------
# chunked
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("items, size, expected", [
    ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
    ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
    ([], 3, []),
    ([1], 5, [[1]]),
    ([1, 2, 3], 1, [[1], [2], [3]]),
])
def test_chunked(items, size, expected):
    assert chunked(items, size) == expected


def test_chunked_accepts_any_iterable_not_only_a_list():
    assert chunked((n for n in range(5)), 2) == [[0, 1], [2, 3], [4]]
    assert chunked("abcde", 2) == [["a", "b"], ["c", "d"], ["e"]]


@pytest.mark.parametrize("size", [0, -1, -100])
def test_chunked_rejects_a_size_below_one(size):
    with pytest.raises(ValueError):
        chunked([1, 2, 3], size)


def test_chunked_never_loses_or_duplicates_an_item():
    """The property: flattening the chunks must give the input back."""
    items = list(range(37))
    for size in range(1, 40):
        assert [n for chunk in chunked(items, size) for n in chunk] == items


def test_chunked_does_not_mutate_its_argument():
    original = [1, 2, 3, 4, 5]
    chunked(original, 2)
    assert original == [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# unique
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("items, expected", [
    ([3, 1, 3, 2, 1], [3, 1, 2]),
    ([], []),
    ([1, 1, 1], [1]),
    ("abracadabra", ["a", "b", "r", "c", "d"]),
])
def test_unique(items, expected):
    assert unique(items) == expected


def test_unique_keeps_first_seen_order():
    assert unique(["z", "a", "z", "m", "a"]) == ["z", "a", "m"]


# ---------------------------------------------------------------------------
# dig
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("keys, expected", [
    (("a", "b", 1), 20),
    (("a", "b", 0), 10),
    (("a", "b", -1), 20),
    (("a", "b", 5), None),        # index out of range
    (("a", "missing"), None),
    (("a",), {"b": [10, 20]}),
    ((), {"a": {"b": [10, 20]}}),
])
def test_dig_walks_nested_data(keys, expected):
    assert dig({"a": {"b": [10, 20]}}, *keys) == expected


@pytest.mark.parametrize("data", [None, 42, "text", [1, 2], {"a": 1}])
def test_dig_never_raises_whatever_it_is_given(data):
    """The whole promise of the function, in one test."""
    assert dig(data, "a", "b", 3, "c", default="-") is not Ellipsis


def test_dig_distinguishes_a_stored_none_from_a_missing_key():
    """BUG 4, found by this test.

    The Day 40 version ended `return default if data is None else data`,
    so a key holding null returned the default — making
    "the field is absent" and "the field is explicitly null" the same
    answer. That is precisely the question a caller uses dig() to ask,
    and it matters the moment the data came from JSON (Day 55).
    """
    data = {"user": {"email": None}}
    assert dig(data, "user", "email", default="MISSING") is None
    assert dig(data, "user", "phone", default="MISSING") == "MISSING"
