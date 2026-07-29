"""Day 032 — Default and keyword arguments.

    python3 lesson.py
"""

import time

# ---------------------------------------------------------------------------
# 1. Defaults
# ---------------------------------------------------------------------------


def greet(name, greeting="Hello", punctuation="!"):
    """Return a greeting."""
    return f"{greeting}, {name}{punctuation}"


print(greet("Ada"))                          # both defaults
print(greet("Ada", "Hi"))                    # positionally
print(greet("Ada", punctuation="?"))         # by keyword, skipping the middle
print(greet(name="Ada", greeting="Salut"))   # all by keyword

# Parameters WITH defaults must come AFTER those without:
#
#     def broken(a=1, b): ...      # SyntaxError
#
# ...because a single argument would be ambiguous.

# CHOOSE DEFAULTS SO THE COMMON CASE NEEDS NO ARGUMENTS. If every caller
# passes the same value, that value is the default.


# ---------------------------------------------------------------------------
# 2. Keywords make call sites readable
# ---------------------------------------------------------------------------


def make_report(rows, layout, totals, ascending, top):
    return f"{len(rows)} rows, {layout}, totals={totals}, top={top}"


data = [1, 2, 3]

positional_call = make_report(data, "wide", True, False, 20)
keyword_call = make_report(
    data, layout="wide", totals=True, ascending=False, top=20
)
print(f"\npositional: {positional_call}")
print(f"keyword:    {keyword_call}")

# The first line is unreadable and the second is obvious. THE RULE WORTH
# ADOPTING: ANY BOOLEAN ARGUMENT SHOULD BE PASSED BY KEYWORD. `send(msg,
# True)` tells a reader nothing; `send(msg, urgent=True)` tells them
# everything.
#
# All POSITIONAL arguments must come first; keywords can be in any order.


# ---------------------------------------------------------------------------
# 3. Keyword-only parameters: a bare *
# ---------------------------------------------------------------------------


def report(rows, *, layout="table", totals=True, width=80):
    """Everything after the * MUST be passed by name."""
    return f"{len(rows)} rows as {layout} (totals={totals}, width={width})"


print(f"\n{report(data)}")
print(f"{report(data, layout='csv')}")

try:
    report(data, "csv")
except TypeError as e:
    print(f"positionally: TypeError: {e}")

# This is the tool for OPTIONS. It stops callers writing
# report(data, "csv", False, 100) — a line nobody can read, and which
# breaks silently the day you reorder the parameters.

# The mirror image is / , marking parameters POSITIONAL-ONLY:


def clamp(value, low, high, /):
    """The names value/low/high are NOT part of the public API."""
    return max(low, min(value, high))


print(f"\nclamp(15, 0, 10) = {clamp(15, 0, 10)}")
try:
    clamp(value=15, low=0, high=10)
except TypeError as e:
    print(f"by keyword: TypeError: {e}")

# Rare, and its purpose is to keep parameter NAMES out of your public API
# so you can rename them later without breaking anyone.

# THE FULL GRAMMAR, in order:
#     def f(pos_only, /, standard, *args, kw_only, **kwargs):


# ---------------------------------------------------------------------------
# 4. THE MUTABLE DEFAULT TRAP
# ---------------------------------------------------------------------------


def add_item(item, basket=[]):        # LOOKS reasonable. Is a bug.
    basket.append(item)
    return basket


print(f"\nadd_item('apple') -> {add_item('apple')}")
print(f"add_item('pear')  -> {add_item('pear')}")
print(f"add_item('fig')   -> {add_item('fig')}")
print("  ^ where did the apple come from?")

# DEFAULT VALUES ARE EVALUATED ONCE, WHEN THE def STATEMENT RUNS — not on
# each call. Every call that omits `basket` shares THE SAME LIST OBJECT.

print(f"\nthe default lives on the function: {add_item.__defaults__}")
print(f"and it is one object: "
      f"{add_item.__defaults__[0] is add_item.__defaults__[0]}")


def add_item_fixed(item, basket=None):
    """Return basket with item appended. A new list if none was given."""
    if basket is None:
        basket = []                   # a NEW list, per call
    basket.append(item)
    return basket


a = add_item_fixed("apple")
b = add_item_fixed("pear")
print(f"\nfixed: {a} and {b}, different objects: {a is not b}")

# Applies to EVERY mutable default: [], {}, set(), and your own objects.
# Ruff flags it as B006, which alone justifies running a linter.


# ---------------------------------------------------------------------------
# 5. The same rule bites computed defaults
# ---------------------------------------------------------------------------


def log_frozen(message, when=time.time()):
    return f"[{when:.4f}] {message}"


first = log_frozen("one")
time.sleep(0.15)
second = log_frozen("two")
print(f"\n{first}\n{second}")
print("  ^ the same timestamp, 0.15s apart. It was frozen at IMPORT.")


def log_fixed(message, when=None):
    if when is None:
        when = time.time()
    return f"[{when:.4f}] {message}"


print(f"\n{log_fixed('one')}")
time.sleep(0.15)
print(f"{log_fixed('two')}")


# ---------------------------------------------------------------------------
# 6. There is one legitimate use of the shared default
# ---------------------------------------------------------------------------

# An IMMUTABLE default is completely safe, because there is nothing to
# mutate. Tuples, strings, numbers, None and frozensets are all fine:


def tag(text, classes=()):
    """A tuple default is safe — it cannot accumulate."""
    return f"<p class='{' '.join(classes)}'>{text}</p>"


print(f"\n{tag('hi')}")
print(f"{tag('hi', ('big', 'bold'))}")
print(f"{tag('hi')}   <- still empty, because tuples cannot be appended to")


# ---------------------------------------------------------------------------
# 7. Designing a signature: write the CALLS first
# ---------------------------------------------------------------------------
#
#     report(rows)                        the common case: ONE argument
#     report(rows, top=10)                one thing different
#     report(rows, layout="csv", top=10)  still readable at any length
#
# If the common call needs four arguments, the defaults are wrong.
#
#   RULES
#     * order parameters by how often they change
#     * required and positional: the thing being operated on, usually one
#     * keyword-only with defaults: everything else
#     * never a mutable default
#     * never a positional boolean
#     * never reorder parameters after release — which is why * exists


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Call add_item() ten times and watch the basket grow.
#   * Add `basket={}` and `basket=set()` versions. Same bug.
#   * Run: ruff check --isolated --select B lesson.py
#   * Write a function with a keyword-only argument and call it positionally.
#   * Take a four-positional-argument function of yours and redesign it so
#     the common call needs one.
