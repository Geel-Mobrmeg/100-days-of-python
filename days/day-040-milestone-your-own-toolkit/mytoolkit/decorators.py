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
import inspect
import time
from collections.abc import Callable
from typing import ParamSpec, Protocol, TypedDict, TypeVar, cast, overload

__all__ = ["timer", "retry", "cache", "validated", "TIMINGS", "RetryError"]

# Every @timer'd call appends here, so the report at the end of build.py can
# be computed from data rather than from whatever scrolled past.
TIMINGS: list[tuple[str, float]] = []

# P is the PARAMETER LIST of the decorated function and R is its return
# type. Together they are what makes @timer(f)(1, 2) type-check exactly as
# f(1, 2) does — the thing that was impossible before ParamSpec (3.10).
P = ParamSpec("P")
R = TypeVar("R")

# A Protocol that RETURNS R must declare it covariant: a Cached[P, int] is
# usable wherever a Cached[P, object] is wanted, because every int is an
# object. mypy names this exactly, which is how you learn it.
R_co = TypeVar("R_co", covariant=True)


class RetryError(RuntimeError):
    """Raised when every attempt failed. Day 52 covers custom exceptions."""


# ---------------------------------------------------------------------------
# @timer
# ---------------------------------------------------------------------------

@overload
def timer(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def timer(*, quiet: bool = ...) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def timer(
    func: Callable[P, R] | None = None, *, quiet: bool = False
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Measure how long each call takes and record it in TIMINGS.

    Works as @timer and as @timer(quiet=True) — the `func is None` check
    from lesson.py section 5.
    """
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
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

def retry(
    times: int = 3,
    delay: float = 0.05,
    backoff: float = 2.0,
    catching: type[Exception] | tuple[type[Exception], ...] = Exception,
    quiet: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a failing call, waiting longer between each attempt.

    `catching` defaults to Exception for teaching, and in real code you
    should NARROW IT — retrying a TypeError just runs the same bug three
    times. Day 66 uses this against a real API with catching=HTTPError.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            wait = delay
            last: Exception | None = None
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

class CacheInfo(TypedDict):
    """The shape cache_info() returns. A dict with a KNOWN set of keys.

    TypedDict is what makes info["hit_rate"] check and info["hitrate"]
    an error, without changing anything at runtime.
    """

    hits: int
    misses: int
    size: int
    hit_rate: float
    max_size: int


class Cached(Protocol[P, R_co]):
    """A callable that ALSO has cache_info() and cache_clear().

    THIS PROTOCOL IS THE INTERESTING PART OF THE DAY. The package README
    has documented `square.cache_info()` since Day 40, and until this
    class existed there was no type that said so — mypy reported
    `"function" has no attribute "cache_info"` at every call site, which
    is a real gap in the API rather than a complaint about syntax.
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def cache_info(self) -> CacheInfo: ...

    def cache_clear(self) -> None: ...


@overload
def cache(func: Callable[P, R]) -> Cached[P, R]: ...


@overload
def cache(*, max_size: int = ...) -> Callable[[Callable[P, R]], Cached[P, R]]:
    ...


def cache(
    func: Callable[P, R] | None = None, *, max_size: int = 128
) -> Cached[P, R] | Callable[[Callable[P, R]], Cached[P, R]]:
    """Memoise on the arguments. Day 34's closure, as a decorator.

    Requires HASHABLE arguments, exactly like functools.lru_cache and for
    the same reason: the key is a tuple of the arguments (Day 23).
    """
    def decorator(f: Callable[P, R]) -> Cached[P, R]:
        store: dict[object, R] = {}
        hits = misses = 0

        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
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

        def cache_info() -> CacheInfo:
            total = hits + misses
            return {
                "hits": hits, "misses": misses, "size": len(store),
                "hit_rate": hits / total if total else 0.0,
                "max_size": max_size,
            }

        def cache_clear() -> None:
            nonlocal hits, misses
            store.clear()
            hits = misses = 0

        # setattr, not `wrapper.cache_info = ...`: mypy knows a plain
        # function object has no such attribute, and this is the honest
        # way to say "I am adding one". The cast on the return is what
        # promises the caller it is there.
        setattr(wrapper, "cache_info", cache_info)      # noqa: B010
        setattr(wrapper, "cache_clear", cache_clear)    # noqa: B010
        return cast(Cached[P, R], wrapper)

    return decorator if func is None else decorator(func)


# ---------------------------------------------------------------------------
# @validated
# ---------------------------------------------------------------------------

def validated(
    **rules: Callable[[object], bool],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Check named arguments against predicates before the call.

    @validated(n=lambda v: v >= 0)
    def sqrt(n): ...

    Uses inspect to bind positional arguments to their names, so the rule
    fires whether the caller wrote sqrt(-1) or sqrt(n=-1) — which a naive
    kwargs-only check would miss.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
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
