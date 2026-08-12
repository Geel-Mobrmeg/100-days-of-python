"""Day 034 build — a counter factory and a memo cache, both from closures.

    python3 build.py

Two things worth building this way, and then the honest comparison against
the class version of the same thing.

The cache is the interesting one: it is `functools.lru_cache` in fifteen
lines, and having written it makes Day 37's @cache a notation change rather
than a magic trick.
"""

import time

WIDTH = 74

# ===========================================================================
# 1. THE COUNTER FACTORY
# ===========================================================================


def make_counter(start=0, step=1):
    """Return a function that counts, and a function that reads the count.

    Two closures over ONE captured variable. Neither the caller nor anything
    else can reach `count` except through these two — which is stronger
    privacy than a class gives you, because there is no attribute to poke.
    """
    count = start

    def increment():
        nonlocal count            # without this: UnboundLocalError
        count += step
        return count

    def value():
        return count              # only READS, so no nonlocal needed

    return increment, value


print("=" * WIDTH)
print(f"{'COUNTER FACTORY':^{WIDTH}}")
print("=" * WIDTH)

tick, read = make_counter()
evens, read_evens = make_counter(start=0, step=2)
countdown, read_down = make_counter(start=10, step=-1)

print(f"{'default':<20}{[tick() for _ in range(5)]}")
print(f"{'step=2':<20}{[evens() for _ in range(5)]}")
print(f"{'step=-1':<20}{[countdown() for _ in range(5)]}")
print()
print(f"{'and they are independent:':<28}"
      f"tick={read()}  evens={read_evens()}  down={read_down()}")

# Prove the state is not reachable from outside:
reachable = [a for a in dir(tick) if not a.startswith("__")]
print(f"{'public attributes on tick:':<28}{reachable or '(none)'}")
print(f"{'but it IS in the closure:':<28}"
      f"{tick.__closure__[0].cell_contents}")

print("""
The count lives in a CELL that the two functions share. `increment` needs
`nonlocal` because it assigns; `value` does not, because it only reads.
That asymmetry is the whole of scope in one function.""")

# ===========================================================================
# 2. THE MEMO CACHE — functools.lru_cache, by hand
# ===========================================================================


def memoize(func, *, max_size=None):
    """Return a caching version of func, plus a stats reader.

    `cache`, `hits` and `misses` are captured. Nothing outside can reach
    them except through the two returned functions.
    """
    cache = {}
    hits = 0
    misses = 0

    def cached(*args):
        nonlocal hits, misses
        # A tuple of the arguments is the key — which is exactly why Day 23
        # mattered: a list argument would be unhashable and this would fail.
        if args in cache:
            hits += 1
            return cache[args]
        misses += 1
        result = func(*args)
        if max_size is not None and len(cache) >= max_size:
            # Evict the OLDEST entry. Dicts keep insertion order (Day 24),
            # so the first key is the oldest — that is FIFO, not true LRU.
            cache.pop(next(iter(cache)))
        cache[args] = result
        return result

    def stats():
        total = hits + misses
        return {
            "hits": hits,
            "misses": misses,
            "size": len(cache),
            "hit_rate": hits / total if total else 0.0,
        }

    return cached, stats


# ---------------------------------------------------------------------------
# The classic case: naive recursive Fibonacci
# ---------------------------------------------------------------------------

calls = 0


def fib(n):
    """Naive recursion: recomputes the same values exponentially often."""
    global calls                  # noqa: PLW0603 - counting calls, deliberately
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


cached_fib_inner, fib_stats = None, None


def cached_fib(n):
    """Memoised Fibonacci. Recursion goes through the CACHED version."""
    if n < 2:
        return n
    return cached_fib_inner(n - 1) + cached_fib_inner(n - 2)


cached_fib_inner, fib_stats = memoize(cached_fib)

print()
print("=" * WIDTH)
print(f"{'MEMOISATION':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'n':>4}{'fib(n)':>12}{'naive calls':>14}{'cached calls':>15}"
      f"{'saved':>14}")
print("-" * WIDTH)

for n in (10, 20, 25, 28):
    calls = 0
    start = time.perf_counter()
    naive_result = fib(n)
    naive_time = time.perf_counter() - start
    naive_calls = calls

    cached_result = cached_fib_inner(n)
    stats = fib_stats()
    total_cached = stats["hits"] + stats["misses"]

    assert naive_result == cached_result, "the cache changed the answer!"
    print(f"{n:>4}{naive_result:>12,}{naive_calls:>14,}{total_cached:>15,}"
          f"{naive_calls - total_cached:>14,}")

print("-" * WIDTH)
final = fib_stats()
print(f"{'cache entries':<30}{final['size']:>{WIDTH - 30}}")
print(f"{'hits':<30}{final['hits']:>{WIDTH - 30},}")
print(f"{'misses':<30}{final['misses']:>{WIDTH - 30},}")
print(f"{'hit rate':<30}{final['hit_rate']:>{WIDTH - 30}.1%}")
print(f"{'naive time for fib(28)':<30}{f'{naive_time * 1000:.1f} ms':>{WIDTH - 30}}")

print("""
The naive version makes over 600,000 calls for fib(28) because it
recomputes fib(10) thousands of times. The cache turns an exponential
algorithm into a linear one — WITHOUT CHANGING THE ALGORITHM. The assert
above checks that: same answers, different amount of work.

`args in cache` is why Day 23's tuples mattered. Pass a LIST argument to a
memoised function and it raises TypeError: unhashable type — which is a
real limitation of functools.lru_cache too, not a shortcut taken here.""")

# ===========================================================================
# 3. max_size — and why FIFO is not LRU
# ===========================================================================

square, square_stats = memoize(lambda n: n * n, max_size=3)

print()
print("-" * WIDTH)
print("A BOUNDED CACHE (max_size=3)")
print("-" * WIDTH)

for n in [1, 2, 3, 1, 4, 1]:
    square(n)
    s = square_stats()
    print(f"  square({n})   size={s['size']}  hits={s['hits']}  "
          f"misses={s['misses']}")

print("""
  Look at the last line. square(1) was called at step 4 and HIT, then
  square(4) evicted the oldest entry — which was 1, because eviction here
  is FIFO (first inserted, first out). So square(1) at step 6 MISSED, even
  though it was the most recently used key.

  A true LRU would have kept it. Fixing that means moving a key to the end
  on every hit — `cache[args] = cache.pop(args)` — which is what
  collections.OrderedDict.move_to_end and functools.lru_cache do.

  This is the difference between a cache that works and a cache that works
  WELL, and you only find it by watching one evict.""")

# ===========================================================================
# 4. THE SAME CACHE AS A CLASS
# ===========================================================================


class MemoCache:
    """The closure version, as an object. Same behaviour."""

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def __call__(self, *args):
        if args in self.cache:
            self.hits += 1
            return self.cache[args]
        self.misses += 1
        self.cache[args] = self.func(*args)
        return self.cache[args]


class_cache = MemoCache(lambda n: n * n)
for n in [2, 3, 2, 2]:
    class_cache(n)

closure_cache, closure_stats = memoize(lambda n: n * n)
for n in [2, 3, 2, 2]:
    closure_cache(n)

print()
print("=" * WIDTH)
print(f"{'CLOSURE vs CLASS — same behaviour':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'':<20}{'closure':>16}{'class':>16}")
print(f"{'hits':<20}{closure_stats()['hits']:>16}{class_cache.hits:>16}")
print(f"{'misses':<20}{closure_stats()['misses']:>16}{class_cache.misses:>16}")
print(f"{'agree':<20}"
      f"{str(closure_stats()['hits'] == class_cache.hits):>32}")
print()
print(f"  the class exposes its cache:   {class_cache.cache}")
print("  and you can corrupt it:        ", end="")
class_cache.cache[(2,)] = "nonsense"
print(f"class_cache(2) now returns {class_cache(2)!r}")
print("""
  The closure cannot be corrupted that way — there is no attribute to
  assign to. That is real encapsulation, and it is the closure's genuine
  advantage.

  The class's advantages are equally real: you can inspect the cache while
  debugging, subclass it to change the eviction policy, pickle it, and add
  a fifth method without changing any signature.

  RULE OF THUMB
    one behaviour + a little state  ->  closure
    several operations on one state ->  class  (Day 41)

  This build returns TWO functions from memoize(). A third would be the
  point at which it should have been a class.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Make the eviction true LRU: on a hit, move the key to the end with
#     `cache[args] = cache.pop(args)`. Re-run section 3 and confirm
#     square(1) at step 6 now HITS.
#
#   * Add **kwargs support. The key becomes (args, frozenset(kwargs.items()))
#     — and now you know why frozenset exists (Day 26).
#
#   * Call cached_fib_inner with a list argument and read the TypeError.
#     Then work out what functools.lru_cache does about it. (Nothing. It has
#     the same limitation, for the same reason.)
#
#   * On Day 37 this becomes @cache, applied with one line. Nothing about
#     the mechanism changes — you have already written it.
#
#   * Compare against functools.lru_cache(maxsize=None) on fib(30). Yours
#     will be slower, because theirs is written in C. Measure it rather
#     than assuming, and note that "slower" here still means microseconds.
