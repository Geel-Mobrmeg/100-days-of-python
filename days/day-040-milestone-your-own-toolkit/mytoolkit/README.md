# mytoolkit

Small utilities worth keeping. Zero dependencies, Python 3.11+.

Seventeen functions that kept getting rewritten across a hundred days of
Python, collected into one importable place.

```python
from mytoolkit import slugify, human_bytes, chunked, cache

slugify("Day 40: Ship It!")        # 'day-40-ship-it'
human_bytes(1_500_000_000)         # '1.4 GB'
chunked(range(7), 3)               # [[0, 1, 2], [3, 4, 5], [6]]
```

---

## Install

```bash
pip install -e .            # editable, for development
pip install -e ".[dev]"     # with pytest, ruff and mypy
```

Then anywhere:

```bash
python3 -m mytoolkit        # list everything the package exports
mytoolkit                   # the same, via the console script
```

---

## What is in it

### Numbers

| Function | Returns |
|---|---|
| `clamp(value, low, high)` | `value` limited to the range. Raises if `low > high`. |
| `percent(part, whole, places=1)` | `'25.0%'`. Returns `'n/a'` when `whole` is 0 — no division error. |
| `human_bytes(count)` | `'1.4 GB'`. Exact for `B`, one decimal above that. |
| `duration(seconds)` | `'1:02:05'`, dropping the hours when they are zero. |

### Text

| Function | Returns |
|---|---|
| `truncate(text, limit, suffix='...')` | Shortened to `limit` characters **including** the suffix. |
| `slugify(text)` | Lowercase, hyphenated, URL-safe. |
| `initials(name)` | `'AABK'` from `'Ada Augusta Byron King'`. Handles one-word names. |

### Containers

| Function | Returns |
|---|---|
| `chunked(items, size)` | Lists of at most `size`. Accepts any iterable. |
| `unique(items)` | Duplicates removed, **first-seen order kept**. |
| `dig(data, *keys, default=None)` | Walks nested dicts/lists. Never raises. |

### Decorators

| Decorator | Does |
|---|---|
| `@timer` / `@timer(quiet=True)` | Records elapsed time in `TIMINGS`. Times failing calls too. |
| `@retry(times, delay, backoff, catching)` | Retries with exponential backoff. Raises `RetryError` at the end, preserving the cause. |
| `@cache` / `@cache(max_size=128)` | Memoises. True LRU eviction. Exposes `.cache_info()` and `.cache_clear()`. |
| `@validated(**rules)` | Checks named arguments before the call, whether passed positionally or by keyword. |

---

## Design rules

Every function in this package follows all five. They are why it is a
library rather than a folder of scripts.

1. **Return, never print.** A function that prints can be used exactly one
   way. A function that returns can be printed, stored, tested, summed or
   composed.
2. **Never mutate an argument.** `chunked` calls `list(items)` before
   slicing; `unique` builds a new list. Callers keep what they passed in.
3. **Raise on programmer error, return a sentinel on expected absence.**
   `clamp(5, 10, 0)` raises — an inside-out range is a bug. `percent(5, 0)`
   returns `'n/a'` — an empty dataset is a normal state for a report.
4. **One line of docstring saying what it returns**, plus doctests that are
   also the examples.
5. **No dependencies.** Nothing here needs anything outside the standard
   library, so installing it can never break another project.

---

## Known limits

Stated rather than discovered:

- `@cache` requires **hashable arguments** — no lists or dicts. Unhashable
  arguments are computed but not cached, silently. Same limitation as
  `functools.lru_cache`, for the same reason.
- `@cache` on anything reading a file, a clock, a database or a random
  source returns the first answer **for the life of the process**.
- `@retry` defaults to `catching=Exception`, which is too broad for real
  use. Narrow it: retrying a `TypeError` runs the same bug three times.
- `slugify` handles ASCII well and transliterates nothing — `"Café"`
  becomes `"caf"`. Use `python-slugify` if you need Unicode folding.
- `human_bytes` uses 1024-based units labelled `KB`/`MB`. Strictly those
  should be `KiB`/`MiB`; the common labels were chosen deliberately.

---

## Development

```bash
pytest                      # tests plus every doctest
ruff check .
mypy mytoolkit
```

## Versioning

Semantic versioning. Public surface is exactly `mytoolkit.__all__`;
anything not listed there may change without a major bump.

## Licence

MIT.
