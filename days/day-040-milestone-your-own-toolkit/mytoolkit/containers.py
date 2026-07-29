"""Collection helpers.

NOT named collections.py — that would shadow the standard library
module of the same name for every file in this package. See README
section 2.
"""

__all__ = ["chunked", "unique", "dig"]


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
    return default if data is None else data
