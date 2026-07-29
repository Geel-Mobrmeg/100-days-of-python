"""Text helpers."""

__all__ = ["truncate", "slugify", "initials"]


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
    """
    kept = [ch.lower() if ch.isalnum() else " " for ch in text]
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
