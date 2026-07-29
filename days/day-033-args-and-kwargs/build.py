"""Day 033 build — a call logger that wraps any function.

    python3 build.py

`logged(func)` returns a new function with the same behaviour that records
every call: the arguments as typed, the result, how long it took, and any
exception on the way out.

It knows NOTHING about the functions it wraps. Positional, keyword, default,
variadic, failing, recursive — all handled by the same two lines:

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

On Day 37 this becomes `@logged` and the mechanism does not change at all.
"""

import functools
import inspect
import time

WIDTH = 78

CALLS = []          # the log: one record per call


def format_call(func, args, kwargs, *, use_names=True):
    """Return the call as a reader would type it.

    With use_names, positional arguments are matched to their PARAMETER
    NAMES via inspect, so clamp(15, 0, 10) is logged as
    clamp(value=15, low=0, high=10) — much easier to read in a log, and
    impossible to get from args alone.
    """
    if use_names:
        try:
            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()
            inner = ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items())
            return f"{func.__name__}({inner})"
        except (TypeError, ValueError):
            # The call does not match the signature — which is itself worth
            # logging, so fall through to the raw form rather than raising.
            pass
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func.__name__}({', '.join(parts)})"


def logged(func):
    """Return a version of func that records every call to CALLS."""

    @functools.wraps(func)          # keeps __name__, __doc__ and the rest
    def wrapper(*args, **kwargs):
        depth = sum(1 for c in CALLS if c["open"])
        record = {
            "call": format_call(func, args, kwargs),
            "depth": depth,
            "open": True,
            "result": None,
            "error": None,
            "seconds": 0.0,
        }
        CALLS.append(record)

        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            record["seconds"] = time.perf_counter() - start
            record["open"] = False
            raise                    # log it, then let it through unchanged
        record["seconds"] = time.perf_counter() - start
        record["result"] = result
        record["open"] = False
        return result

    return wrapper


# ===========================================================================
# Functions with deliberately different shapes. The logger has seen none of
# them and needs no changes for any of them.
# ===========================================================================


@logged
def clamp(value, low, high):
    """Return value limited to low..high."""
    return max(low, min(value, high))


@logged
def greet(name, greeting="Hello", *, punctuation="!"):
    """Positional, default, and keyword-only, all at once."""
    return f"{greeting}, {name}{punctuation}"


@logged
def total(*numbers, scale=1):
    """Genuinely variadic."""
    return sum(numbers) * scale


@logged
def divide(a, b):
    """Raises when b is zero — the logger must record that and re-raise."""
    return a / b


@logged
def fib(n):
    """Recursive, so the log shows nesting."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


@logged
def slow(seconds):
    """Does nothing, slowly, so the timing column has something in it."""
    time.sleep(seconds)
    return "done"


# ===========================================================================
# Exercise every shape
# ===========================================================================

print("=" * WIDTH)
print(f"{'CALL LOGGER':^{WIDTH}}")
print("=" * WIDTH)

clamp(15, 0, 10)                       # all positional
clamp(15, low=0, high=10)              # mixed
clamp(value=-3, low=0, high=10)        # all keyword

greet("Ada")                           # defaults
greet("Ada", "Hi")                     # override one positionally
greet("Ada", punctuation="?")          # keyword-only

total(1, 2, 3)                         # variadic
total()                                # variadic, empty
total(1, 2, 3, scale=10)               # variadic plus a keyword-only

slow(0.05)                             # measurable
fib(5)                                 # recursive: 15 calls

try:
    divide(1, 0)                       # raises
except ZeroDivisionError:
    pass                               # caught here; the logger recorded it

try:
    clamp(15)                          # does not match the signature at all
except TypeError:
    pass

# ===========================================================================
# The log
# ===========================================================================

print(f"{'CALL':<52}{'RESULT':>12}{'ms':>8}")
print("-" * WIDTH)
for record in CALLS:
    indent = "  " * record["depth"]
    call = f"{indent}{record['call']}"
    if record["error"]:
        shown = "RAISED"
    else:
        shown = repr(record["result"])
    print(f"{call[:50]:<52}{shown[:12]:>12}{record['seconds'] * 1000:>8.2f}")

# ===========================================================================
# What the log can now tell you
# ===========================================================================

errors = [c for c in CALLS if c["error"]]
slowest = max(CALLS, key=lambda c: c["seconds"])
by_name = {}
for record in CALLS:
    name = record["call"].split("(")[0]
    by_name[name] = by_name.get(name, 0) + 1

total_ms = sum(c["seconds"] for c in CALLS) * 1000

print()
print("=" * WIDTH)
print(f"{'calls recorded':<40}{len(CALLS):>{WIDTH - 40}}")
print(f"{'distinct functions':<40}{len(by_name):>{WIDTH - 40}}")
print(f"{'calls that raised':<40}{len(errors):>{WIDTH - 40}}")
print(f"{'total time':<40}{f'{total_ms:.1f} ms':>{WIDTH - 40}}")
print(f"{'slowest call':<40}{slowest['call'][:36]:>{WIDTH - 40}}")
print("-" * WIDTH)
for name, count in sorted(by_name.items(), key=lambda kv: -kv[1]):
    print(f"  {name:<30}{count:>4}  {'#' * count}")

print()
print("ERRORS")
print("-" * WIDTH)
for record in errors:
    print(f"  {record['call'][:48]:<50}{record['error']}")

# ===========================================================================
# The three things that make this work
# ===========================================================================

print()
print("=" * WIDTH)
print(f"""1. *args, **kwargs FORWARD ANYTHING

   `clamp` takes three positional parameters, `greet` has a default and a
   keyword-only, `total` is variadic, `fib` recurses. The wrapper handles
   all of them with the same two lines and no special cases, because it
   never looks at what it received — it packs and re-spreads.

2. functools.wraps KEEPS THE IDENTITY

   Without it, every wrapped function would report itself as "wrapper":

      clamp.__name__  = {clamp.__name__!r}
      clamp.__doc__   = {clamp.__doc__!r}

   Those came through @functools.wraps. Remove it and the log above says
   "wrapper(...)" fifteen times over, and help(clamp) shows nothing.

3. THE EXCEPTION IS LOGGED AND RE-RAISED

   `divide(1, 0)` appears in the log AND still raised ZeroDivisionError for
   the caller to handle. A wrapper that swallows exceptions changes the
   behaviour of everything it touches — which is the fastest way to make a
   debugging tool into a bug.""")
print("=" * WIDTH)

print(f"""
The @ lines above are DECORATOR syntax, and `@logged` is exactly
`clamp = logged(clamp)`. That is all a decorator is, and it is Day 37 —
which is now mostly syntax, because the mechanism is this file.""")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Delete @functools.wraps and re-run. Every line of the log becomes
#     "wrapper(...)". That is why it exists.
#
#   * fib(5) makes 15 calls, and fib(30) makes over 2.7 million. Run fib(20)
#     and look at how many entries appear for the SAME arguments. That
#     observation is the entire argument for @cache on Day 37.
#
#   * format_call falls back to the raw form when .bind() fails — which is
#     what happens for clamp(15). Find that line in the log and confirm it
#     recorded the bad call rather than hiding it.
#
#   * Add a `max_depth` option so recursive calls beyond a certain depth are
#     summarised rather than logged. You will need it before fib(25).
#
#   * On Day 64 replace the CALLS list with the `logging` module, and get
#     levels, timestamps and file output for free.
