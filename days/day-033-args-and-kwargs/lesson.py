"""Day 033 — *args and **kwargs.

    python3 lesson.py
"""

import inspect

# ---------------------------------------------------------------------------
# 1. PACKING — * and ** in a DEFINITION collect many into one
# ---------------------------------------------------------------------------


def total(*numbers):
    """*numbers collects all positional arguments into a TUPLE."""
    print(f"  received {numbers!r} — a {type(numbers).__name__}")
    return sum(numbers)


print(f"total(1, 2, 3) = {total(1, 2, 3)}")
print(f"total()        = {total()}")


def tag(name, **attributes):
    """**attributes collects all keyword arguments into a DICT."""
    pairs = " ".join(f'{k}="{v}"' for k, v in attributes.items())
    return f"<{name} {pairs}>" if pairs else f"<{name}>"


print(f"\n{tag('a', href='/x', target='_blank')}")
print(f"{tag('br')}")

# `args` and `kwargs` are CONVENTIONS, not keywords. The * and ** do the
# work. Use better names when you have them: *numbers, **attributes.

# Order in a signature is fixed, and anything after *args is automatically
# KEYWORD-ONLY — which is exactly what Day 32's bare * was doing:


def show(a, b=1, *rest, c, **options):
    return f"a={a} b={b} rest={rest} c={c} options={options}"


print(f"\n{show(1, 2, 3, 4, c=5, x=6)}")
try:
    show(1, 2, 3)
except TypeError as e:
    print(f"omitting the keyword-only c: TypeError: {e}")


# ---------------------------------------------------------------------------
# 2. UNPACKING — the same symbols at a CALL spread one into many
# ---------------------------------------------------------------------------

values = [1, 2, 3]
print(f"\ntotal(*values) = {total(*values)}")     # calls total(1, 2, 3)
print("total(values)  = ", end="")
print(f"{total(values)}" if False else "TypeError — one tuple, not three ints")

options = {"sep": "-", "end": "!\n"}
print("a", "b", "c", **options)                   # sep="-", end="!\n"

#   IN A DEFINITION   collect many arguments into one name
#   AT A CALL         spread one collection into many arguments
#
# Same symbol, opposite direction. That is the whole confusion.

# Unpacking works outside calls too, and is often the neatest merge:
a, b = [1, 2], [3, 4]
print(f"\n[*a, *b]        = {[*a, *b]}")
defaults = {"colour": "black", "size": "M"}
chosen = {"size": "L"}
print(f"{{**d, **c}}      = {({**defaults, **chosen})}   <- right side wins")
first, *rest = [1, 2, 3, 4]
print(f"first, *rest    = {first}, {rest}   (Day 23)")


# ---------------------------------------------------------------------------
# 3. FORWARDING — the two lines everything else is built on
# ---------------------------------------------------------------------------


def clamp(value, low, high):
    """Return value limited to low..high."""
    return max(low, min(value, high))


def make_wrapper(func):
    def wrapper(*args, **kwargs):          # PACK whatever arrived
        print(f"  -> calling {func.__name__}")
        return func(*args, **kwargs)       # UNPACK it again, unchanged
    return wrapper


wrapped = make_wrapper(clamp)
print(f"\n{wrapped(15, 0, 10)}")
print(f"{wrapped(15, low=0, high=10)}")
print(f"{wrapped(value=15, low=0, high=10)}")

# THOSE TWO LINES ACCEPT ANY CALL AND PASS IT THROUGH UNCHANGED. Nothing is
# inspected, nothing assumed, and a function that gains a parameter next
# year still passes through. This is the foundation of:
#     * decorators (Day 37)
#     * functools.partial
#     * almost every library that wraps another library


# ---------------------------------------------------------------------------
# 4. Reading a function's metadata
# ---------------------------------------------------------------------------

print(f"\n{'__name__':<16}{clamp.__name__}")
print(f"{'__doc__':<16}{clamp.__doc__}")
print(f"{'__module__':<16}{clamp.__module__}")
print(f"{'signature':<16}{inspect.signature(clamp)}")

# .bind() matches the ACTUAL arguments to the PARAMETER NAMES, so you can
# report a call with names even when the caller passed positionally:
bound = inspect.signature(clamp).bind(15, 0, 10)
bound.apply_defaults()
print(f"{'bound':<16}{dict(bound.arguments)}")


# ---------------------------------------------------------------------------
# 5. Logging a call: use repr, not str
# ---------------------------------------------------------------------------


def format_call(func, args, kwargs):
    """Return the call as you would have typed it."""
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func.__name__}({', '.join(parts)})"


print(f"\n{format_call(clamp, (15, 0, 10), {})}")
print(f"{format_call(clamp, (15,), {'low': 0, 'high': 10})}")

# WHY repr AND NOT str:
print(f"\nwith str():  {'clamp(' + str(1) + ')':<20} and "
      f"{'clamp(' + str('1') + ')'}")
print(f"with repr(): {'clamp(' + repr(1) + ')':<20} and "
      f"{'clamp(' + repr('1') + ')'}")
print("  ^ str() makes 1 and '1' identical. They are different calls.")


# ---------------------------------------------------------------------------
# 6. WHAT THEY COST — and when not to use them
# ---------------------------------------------------------------------------


def bad_connect(**kwargs):
    """Real parameters hidden in kwargs. Do not do this."""
    host = kwargs.get("host", "localhost")
    timeout = kwargs.get("timeout", 30)
    return f"{host}:{timeout}"


def good_connect(*, host="localhost", timeout=30):
    """The same options, written down."""
    return f"{host}:{timeout}"


print(f"\n{bad_connect(host='db', timout=5)}   <- 'timout' typo: SILENTLY ignored")
try:
    good_connect(host="db", timout=5)
except TypeError as e:
    print(f"good_connect: TypeError: {e}")

print(f"\nsignature of bad_connect:  {inspect.signature(bad_connect)}")
print(f"signature of good_connect: {inspect.signature(good_connect)}")

# *args/**kwargs COST YOU EVERYTHING A SIGNATURE GIVES:
#   * a reader cannot tell what the function accepts
#   * editors cannot autocomplete
#   * type checkers (Day 59) cannot help
#   * a misspelled keyword becomes a silent no-op instead of a TypeError
#
# USE THEM FOR:
#   * FORWARDING — you genuinely do not know the signature
#   * GENUINELY VARIADIC functions — sum, max, print
#
# DO NOT use them as a shortcut for "several options". That is Day 32's
# keyword-only parameters, and they catch the typo above.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Call total(values) instead of total(*values) and read the TypeError.
#   * Write a wrapper and check wrapper.__name__. It says "wrapper", not the
#     wrapped function's name — that is the problem functools.wraps solves
#     on Day 37.
#   * Merge two dicts with {**a, **b} and then {**b, **a}. Which wins?
#   * Rewrite bad_connect with explicit parameters and count the bugs that
#     become impossible.
