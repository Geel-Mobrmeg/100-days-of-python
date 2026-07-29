"""decorators — the four worth writing yourself.

Part of the toolkit that started on Day 31. Nothing in here knows anything
about the functions it decorates: they all forward with *args/**kwargs and
close over their configuration.

    Day 31  toolkit.py written
    Day 37  this file — @timer, @retry, @cache, @validated     <- here
    Day 39  both become one package
    Day 40  documented and importable
"""

import functools
import time

__all__ = ["timer", "retry", "cache", "validated", "TIMINGS", "RetryError"]

# Every @timer'd call appends here, so the report at the end of build.py can
# be computed from data rather than from whatever scrolled past.
TIMINGS = []


class RetryError(RuntimeError):
    """Raised when every attempt failed. Day 52 covers custom exceptions."""


# ---------------------------------------------------------------------------
# @timer
# ---------------------------------------------------------------------------

def timer(func=None, *, quiet=False):
    """Measure how long each call takes and record it in TIMINGS.

    Works as @timer and as @timer(quiet=True) — the `func is None` check
    from lesson.py section 5.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return f(*args, **kwargs)          # RETURN IT
            finally:
                # `finally` so a raising call is still timed and recorded.
                elapsed = time.perf_counter() - start
                TIMINGS.append((f.__name__, elapsed))
                if not quiet:
                    print(f"    [timer] {f.__name__} took {elapsed * 1000:.3f} ms")
        return wrapper

    return decorator if func is None else decorator(func)


# ---------------------------------------------------------------------------
# @retry
# ---------------------------------------------------------------------------

def retry(times=3, delay=0.05, backoff=2.0, catching=Exception, quiet=False):
    """Retry a failing call, waiting longer between each attempt.

    `catching` defaults to Exception for teaching, and in real code you
    should NARROW IT — retrying a TypeError just runs the same bug three
    times. Day 66 uses this against a real API with catching=HTTPError.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            last = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except catching as exc:
                    last = exc
                    if not quiet:
                        print(f"    [retry] attempt {attempt}/{times} failed: "
                              f"{type(exc).__name__}: {exc}")
                    if attempt < times:
                        time.sleep(wait)
                        wait *= backoff          # exponential backoff
            raise RetryError(
                f"{func.__name__} failed after {times} attempts"
            ) from last
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# @cache
# ---------------------------------------------------------------------------

def cache(func=None, *, max_size=128):
    """Memoise on the arguments. Day 34's closure, as a decorator.

    Requires HASHABLE arguments, exactly like functools.lru_cache and for
    the same reason: the key is a tuple of the arguments (Day 23).
    """
    def decorator(f):
        store = {}
        hits = misses = 0

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            key = (args, tuple(sorted(kwargs.items())))
            try:
                if key in store:
                    hits += 1
                    # Move to the end so eviction is genuinely LRU, not FIFO
                    # — the bug Day 34's build exposed.
                    store[key] = store.pop(key)
                    return store[key]
            except TypeError:
                # An unhashable argument. Do not pretend to cache it.
                misses += 1
                return f(*args, **kwargs)

            misses += 1
            result = f(*args, **kwargs)
            store[key] = result
            if len(store) > max_size:
                store.pop(next(iter(store)))     # evict least recently used
            return result

        def cache_info():
            total = hits + misses
            return {
                "hits": hits, "misses": misses, "size": len(store),
                "hit_rate": hits / total if total else 0.0,
                "max_size": max_size,
            }

        def cache_clear():
            nonlocal hits, misses
            store.clear()
            hits = misses = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator if func is None else decorator(func)


# ---------------------------------------------------------------------------
# @validated
# ---------------------------------------------------------------------------

def validated(**rules):
    """Check named arguments against predicates before the call.

    @validated(n=lambda v: v >= 0)
    def sqrt(n): ...

    Uses inspect to bind positional arguments to their names, so the rule
    fires whether the caller wrote sqrt(-1) or sqrt(n=-1) — which a naive
    kwargs-only check would miss.
    """
    import inspect

    def decorator(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, check in rules.items():
                if name in bound.arguments and not check(bound.arguments[name]):
                    raise ValueError(
                        f"{func.__name__}: {name}={bound.arguments[name]!r} "
                        f"failed validation"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator
