"""toolkit — ten small utilities worth keeping.

This file is not an exercise. It is the start of a real library that grows
for the rest of the course:

    Day 31  written, with docstrings and doctests      <- you are here
    Day 33  a call logger wraps it
    Day 37  @timer, @retry and @cache decorate it
    Day 39  split into a package with submodules
    Day 40  documented, exampled, importable
    Day 57  a pytest suite finds a bug in it
    Day 59  fully type-annotated, mypy clean
    Day 97  published to TestPyPI

Every function here returns a value, mutates nothing it was given, and does
not print. That is what makes them reusable — and testable on Day 57.

Run the doctests:

    python3 -m doctest -v toolkit.py
"""

# The only import in the file. slugify() needs it to fold accents off
# Latin letters; everything else here is plain Python.
import unicodedata

# ---------------------------------------------------------------------------
# 1. Numbers
# ---------------------------------------------------------------------------


def clamp(value, low, high):
    """Return value limited to the range low..high.

    >>> clamp(15, 0, 10)
    10
    >>> clamp(-3, 0, 10)
    0
    >>> clamp(5, 0, 10)
    5
    """
    if low > high:
        raise ValueError(f"low ({low}) is above high ({high})")
    return max(low, min(value, high))


def percent(part, whole, places=1):
    """Return part of whole as a percentage string, safe when whole is 0.

    >>> percent(1, 4)
    '25.0%'
    >>> percent(1, 3, places=2)
    '33.33%'
    >>> percent(5, 0)
    'n/a'
    """
    if not whole:
        return "n/a"
    return f"{part / whole:.{places}%}"


def human_bytes(count):
    """Return a byte count as a human-readable string.

    >>> human_bytes(512)
    '512 B'
    >>> human_bytes(2048)
    '2.0 KB'
    >>> human_bytes(1_500_000_000)
    '1.4 GB'
    >>> human_bytes(1024 * 1024 - 1)
    '1.0 MB'
    """
    size = float(count)
    units = ("B", "KB", "MB", "GB", "TB")
    index = 0
    while index < len(units) - 1:
        # Compare the value AS IT WILL BE SHOWN. 1048575 bytes is
        # 1023.99902 KB, which formats as '1024.0 KB' — a quantity that
        # does not exist. Rounding before the comparison promotes it.
        shown = abs(size) if index == 0 else round(abs(size), 1)
        if shown < 1024:
            break
        size /= 1024
        index += 1
    if units[index] == "B":
        return f"{int(size)} {units[index]}"
    return f"{size:.1f} {units[index]}"


def duration(seconds):
    """Return a number of seconds as h:mm:ss or m:ss.

    >>> duration(75)
    '1:15'
    >>> duration(3725)
    '1:02:05'
    >>> duration(0)
    '0:00'
    >>> duration(-75)
    '-1:15'
    """
    seconds = int(seconds)
    # divmod on a negative number floors, so divmod(-5, 3600) is
    # (-1, 3595) and the naive version prints '-1:59:55'. Take the sign
    # off first and put it back on the front.
    sign = "-" if seconds < 0 else ""
    hours, rest = divmod(abs(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{sign}{hours}:{minutes:02d}:{secs:02d}"
    return f"{sign}{minutes}:{secs:02d}"


# ---------------------------------------------------------------------------
# 2. Text
# ---------------------------------------------------------------------------


def truncate(text, limit, suffix="..."):
    """Return text shortened to limit characters INCLUDING the suffix.

    >>> truncate("Hello, world", 8)
    'Hello...'
    >>> truncate("Hi", 8)
    'Hi'
    >>> len(truncate("abcdefghij", 5))
    5
    """
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    if limit <= len(suffix):
        return text[:limit]
    return text[: limit - len(suffix)] + suffix


def slugify(text):
    """Return text as a lowercase, hyphenated, URL-safe slug.

    >>> slugify("Hello, World!")
    'hello-world'
    >>> slugify("  Day 31: Writing Functions  ")
    'day-31-writing-functions'
    >>> slugify("!!!")
    ''
    >>> slugify("Café Münster")
    'cafe-munster'
    """
    # URL-safe means ASCII. Decompose first so 'é' becomes 'e' plus a
    # combining mark, keep the 'e', and drop the mark with everything
    # else non-ASCII. Scripts with no Latin decomposition (Greek, Cyrillic,
    # Japanese) reduce to '' — a documented limit, not an accident.
    kept = []
    for character in unicodedata.normalize("NFKD", text):
        if unicodedata.combining(character):
            continue          # an accent: drop it, do not separate words
        kept.append(character.lower()
                    if character.isascii() and character.isalnum() else " ")
    return "-".join("".join(kept).split())


def initials(name):
    """Return the initials of a full name.

    >>> initials("Ada Augusta Byron King")
    'AABK'
    >>> initials("prince")
    'P'
    >>> initials("   ")
    ''
    """
    return "".join(part[0].upper() for part in name.split())


# ---------------------------------------------------------------------------
# 3. Collections
# ---------------------------------------------------------------------------


def chunked(items, size):
    """Return items split into lists of at most `size`.

    >>> chunked([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    >>> chunked([], 3)
    []
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    items = list(items)
    return [items[i : i + size] for i in range(0, len(items), size)]


def unique(items):
    """Return items with duplicates removed, keeping first-seen order.

    >>> unique([3, 1, 3, 2, 1])
    [3, 1, 2]
    >>> unique("abracadabra")
    ['a', 'b', 'r', 'c', 'd']
    """
    return list(dict.fromkeys(items))


def dig(data, *keys, default=None):
    """Walk nested dicts and lists by key or index. Never raises.

    >>> dig({"a": {"b": [10, 20]}}, "a", "b", 1)
    20
    >>> dig({"a": 1}, "a", "b", default="-")
    '-'
    >>> dig(None, "a", default=0)
    0
    >>> dig({"a": None}, "a", default="missing") is None
    True
    """
    for key in keys:
        if isinstance(data, dict):
            if key not in data:
                return default
            data = data[key]
        elif isinstance(data, (list, tuple)):
            if not isinstance(key, int) or not -len(data) <= key < len(data):
                return default
            data = data[key]
        else:
            return default
    # Return what was stored, including a stored None. Folding None into
    # `default` made "the key holds null" indistinguishable from "the key
    # is absent", which is exactly the question a caller asks dig().
    return data


# ---------------------------------------------------------------------------
# Notes on the design
# ---------------------------------------------------------------------------
#
# * Every one of these RETURNS. None of them prints. That is what lets them
#   be composed, stored, tested and reused — a function that prints can only
#   ever be used one way.
#
# * None of them mutates what it was given. `chunked` calls list(items)
#   before slicing, so passing a generator works and passing a list leaves
#   it alone.
#
# * Two of them RAISE rather than guessing: clamp() with low > high and
#   chunked() with size < 1 are programmer errors, not user input, and
#   silently returning something plausible would hide a bug. Day 52 covers
#   this properly.
#
# * percent() does NOT raise on a zero denominator, because "no data yet" is
#   a normal state for a report, not a bug. The difference between those two
#   judgements is the interesting part of API design.
#
# * Every docstring says what the function RETURNS, in one line, and carries
#   examples that are also tests.
