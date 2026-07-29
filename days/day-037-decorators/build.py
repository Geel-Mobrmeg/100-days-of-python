"""Day 037 build — @timer, @retry and @cache applied to the Day 31 toolkit.

    python3 build.py

The point of the exercise: NOT ONE LINE OF toolkit.py CHANGES. Timing,
caching, retrying and validation are bolted on from outside, because none of
them is part of what those functions do.

`decorators.py` in this folder holds the four decorators. This file applies
them and measures what they bought.
"""

import random
import time

import toolkit
from decorators import RetryError, TIMINGS, cache, retry, timer, validated

WIDTH = 78
random.seed(42)

print("=" * WIDTH)
print(f"{'DECORATING THE TOOLKIT':^{WIDTH}}")
print("=" * WIDTH)

# ===========================================================================
# 1. @timer — applied WITHOUT touching toolkit.py
# ===========================================================================
#
# The toolkit was written on Day 31 with no idea this would happen. Because
# `@d` is just `f = d(f)`, decorating an imported function is one line.

print("\n1. @timer, applied to functions that know nothing about it")
print("-" * WIDTH)

timed_slugify = timer(toolkit.slugify)
timed_chunked = timer(toolkit.chunked)

timed_slugify("Day 37: Decorators and Other Things")
timed_chunked(list(range(10_000)), 250)

print(f"\n    toolkit.slugify is unchanged: "
      f"{toolkit.slugify('Still Plain') == 'still-plain'}")
print(f"    and keeps its identity:       {timed_slugify.__name__}, "
      f"{timed_slugify.__doc__.splitlines()[0][:34]}...")

# ===========================================================================
# 2. @cache — where it wins, and where it must not be used
# ===========================================================================

print("\n\n2. @cache")
print("-" * WIDTH)


@cache
def slow_slug(text):
    """A deliberately expensive slugify, to make caching visible."""
    time.sleep(0.01)
    return toolkit.slugify(text)


TITLES = ["Day 37: Decorators", "Day 31: Functions", "Day 37: Decorators",
          "Day 37: Decorators", "Day 34: Closures", "Day 31: Functions"]

start = time.perf_counter()
for title in TITLES:
    slow_slug(title)
cached_time = time.perf_counter() - start

info = slow_slug.cache_info()
print(f"    {len(TITLES)} calls, {info['misses']} distinct")
print(f"    hits {info['hits']}, misses {info['misses']}, "
      f"hit rate {info['hit_rate']:.0%}")
print(f"    took {cached_time * 1000:.0f} ms")
print(f"    would have taken ~{len(TITLES) * 10} ms uncached")

# THE LIMITS, both real:
print()
try:
    slow_slug(["not", "hashable"])
    print("    unhashable argument: handled (not cached, still computed)")
except TypeError as e:
    print(f"    unhashable argument: TypeError: {e}")


@cache
def read_counter():
    """Returns a DIFFERENT value each call — so caching it is a bug."""
    return random.randint(1, 1_000_000)


first, second = read_counter(), read_counter()
print(f"    caching a changing value: {first} then {second} — "
      f"{'STALE FOREVER' if first == second else 'fine'}")
print("""
    @cache on anything reading a file, a clock, a database or a random
    source returns the first answer for the life of the process. That is
    not a caching subtlety, it is a wrong program.""")

# ===========================================================================
# 3. @retry — with backoff, and against a specific exception
# ===========================================================================

print("\n3. @retry")
print("-" * WIDTH)

attempts = {"count": 0}


@retry(times=4, delay=0.02, backoff=2.0, catching=ConnectionError)
def flaky_fetch(url):
    """Fails twice, then succeeds. Stands in for Day 65's real HTTP."""
    attempts["count"] += 1
    if attempts["count"] < 3:
        raise ConnectionError(f"timed out reaching {url}")
    return f"200 OK from {url}"


print(f"    {flaky_fetch('https://example.test/api')}")
print(f"    succeeded on attempt {attempts['count']}")


@retry(times=3, delay=0.01, catching=ConnectionError)
def always_fails():
    raise ConnectionError("host unreachable")


print()
try:
    always_fails()
except RetryError as e:
    print(f"    after every attempt: RetryError: {e}")
    print(f"    original cause preserved: {type(e.__cause__).__name__}: "
          f"{e.__cause__}")

print("""
    `raise ... from last` keeps the ORIGINAL exception as __cause__, so the
    traceback shows both what the caller saw and what actually went wrong.
    Day 52 covers that properly.

    Note `catching=ConnectionError`, not a bare `except`. Retrying a
    TypeError just runs the same bug three times, more slowly.""")

# ===========================================================================
# 4. @validated — arguments checked before the call
# ===========================================================================

print("\n4. @validated")
print("-" * WIDTH)


@validated(
    value=lambda v: isinstance(v, (int, float)),
    low=lambda v: isinstance(v, (int, float)),
)
def clamp(value, low, high):
    """Day 31's clamp, with its preconditions written down."""
    return toolkit.clamp(value, low, high)


print(f"    clamp(15, 0, 10)      -> {clamp(15, 0, 10)}")
try:
    clamp("fifteen", 0, 10)
except ValueError as e:
    print(f"    clamp('fifteen', ...) -> ValueError: {e}")
try:
    clamp(value="x", low=0, high=10)
except ValueError as e:
    print(f"    by keyword too        -> ValueError: {e}")

print("""
    The rule fires for BOTH calling styles because @validated binds
    positional arguments to their parameter names with inspect.signature
    (Day 33). A naive kwargs-only check would have missed the first one.""")

# ===========================================================================
# 5. STACKING — the order changes the meaning
# ===========================================================================

print("\n5. STACKING — @timer outside @retry vs inside")
print("-" * WIDTH)

TIMINGS.clear()
state = {"n": 0}


@timer(quiet=True)
@retry(times=3, delay=0.03, catching=ConnectionError, quiet=True)
def outer_timer():
    state["n"] += 1
    if state["n"] < 3:
        raise ConnectionError("nope")
    return "ok"


outer_timer()
whole = TIMINGS[-1][1]

TIMINGS.clear()
state["n"] = 0


@retry(times=3, delay=0.03, catching=ConnectionError, quiet=True)
@timer(quiet=True)
def inner_timer():
    state["n"] += 1
    if state["n"] < 3:
        raise ConnectionError("nope")
    return "ok"


inner_timer()
per_attempt = [t for _, t in TIMINGS]

print(f"    @timer OUTSIDE @retry: 1 measurement of {whole * 1000:.0f} ms")
print(f"                           (all attempts plus the backoff waits)")
print(f"    @timer INSIDE  @retry: {len(per_attempt)} measurements of "
      f"{', '.join(f'{t * 1000:.1f}' for t in per_attempt)} ms")
print(f"                           (each attempt alone, no waiting)")
print("""
    Both are correct; they answer different questions. "How long did the
    user wait?" is the outer one. "How slow is one attempt?" is the inner.
    Stacking applies BOTTOM-UP, and it is worth a comment saying which you
    meant — because the two look almost identical in the source.""")

# ===========================================================================
# 6. WHAT IT COST
# ===========================================================================

print("\n6. THE COST")
print("-" * WIDTH)

REPEATS = 200_000
plain = toolkit.clamp
wrapped = timer(quiet=True)(toolkit.clamp)

start = time.perf_counter()
for _ in range(REPEATS):
    plain(15, 0, 10)
plain_time = time.perf_counter() - start

TIMINGS.clear()
start = time.perf_counter()
for _ in range(REPEATS // 20):
    wrapped(15, 0, 10)
wrapped_time = (time.perf_counter() - start) * 20
TIMINGS.clear()

print(f"    {REPEATS:,} plain calls      {plain_time:>8.4f} s")
print(f"    the same, decorated     {wrapped_time:>8.4f} s (extrapolated)")
print(f"    overhead                {wrapped_time / plain_time:>8.1f}x")
print("""
    A wrapper is a function call, a tuple pack and a dict pack per call.
    That is microseconds — irrelevant for anything doing real work, and
    genuinely significant in a tight numeric loop. Measure before you
    decorate something called a million times.

    The bigger cost is DEBUGGABILITY: a traceback through three decorators
    has three extra frames, and inspect.signature can lie.""")

print()
print("=" * WIDTH)
print(f"""NOT ONE LINE OF toolkit.py CHANGED.

Timing, caching, retrying and validating are all ORTHOGONAL to computing a
slug or chunking a list. That is the test for whether something should be a
decorator, and it is why these four are worth writing while a decorator
used once is just a function call wearing a hat.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * decorators.py's @cache moves a key to the end on a hit, so eviction is
#     genuinely LRU — the bug Day 34's build exposed. Set max_size=2, call
#     three distinct arguments then re-call the first, and confirm it HITS.
#
#   * Compare @cache against functools.lru_cache on fib(30). Theirs is
#     faster because it is written in C. Measure rather than assume.
#
#   * Add @rate_limit(calls=5, per=1.0) that sleeps to stay under a limit.
#     You will need it on Day 66 against a real API.
#
#   * Write @deprecated(reason) that emits a warnings.warn on first use.
#     Note that it must NOT change behaviour — only warn.
#
#   * On Day 39 toolkit.py and decorators.py become one package, and this
#     file's imports become `from mytoolkit import clamp, timer`.
