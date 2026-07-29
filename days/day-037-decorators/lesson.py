"""Day 037 — Decorators.

    python3 lesson.py
"""

import functools
import time

WIDTH = 72

# ---------------------------------------------------------------------------
# 1. @ IS NOTATION. Nothing else.
# ---------------------------------------------------------------------------


def logged(func):
    """A decorator: takes a function, returns a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  calling {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"  got {result!r}")
        return result                  # RETURN IT. See section 3.
    return wrapper


@logged
def add(a, b):
    """Return a + b."""
    return a + b


print(add(2, 3))


# The @ line means EXACTLY this and nothing more:
def multiply(a, b):
    """Return a * b."""
    return a * b


multiply = logged(multiply)            # <- what @logged does
print(multiply(2, 3))

print("""
A decorator is A FUNCTION THAT TAKES A FUNCTION AND RETURNS A FUNCTION.
`@d` is sugar for `f = d(f)`. That is the whole feature.

Three things you already know are doing the work:
  * *args, **kwargs (Day 33) — accept and forward any signature
  * the closure over `func` (Day 34) — the wrapper remembers what it wraps
  * functools.wraps — section 2""")


# ---------------------------------------------------------------------------
# 2. functools.wraps — not optional
# ---------------------------------------------------------------------------


def undecorated(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper                     # no @wraps


@undecorated
def slugify_a(text):
    """Return a URL-safe slug."""
    return text.lower()


@logged
def slugify_b(text):
    """Return a URL-safe slug."""
    return text.lower()


print(f"\n{'':<14}{'__name__':<16}{'__doc__'}")
print(f"{'without wraps':<14}{slugify_a.__name__:<16}{slugify_a.__doc__}")
print(f"{'with wraps':<14}{slugify_b.__name__:<16}{slugify_b.__doc__}")

# wraps copies __name__, __doc__, __module__, __qualname__ and __wrapped__.
# Debuggers, help(), pytest and inspect.signature all rely on those.

print(f"\n__wrapped__ gets you back to the original: "
      f"{slugify_b.__wrapped__.__name__}")


# ---------------------------------------------------------------------------
# 3. THE SILENT BUG: forgetting to return
# ---------------------------------------------------------------------------


def broken(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)          # computed, and thrown away
    return wrapper


@broken
def double(n):
    return n * 2


print(f"\n@broken double(5) = {double(5)}   <- None. Day 31's bug, in a hat.")


# ---------------------------------------------------------------------------
# 4. Decorators WITH ARGUMENTS — three nested functions
# ---------------------------------------------------------------------------


def repeat(times=2):                   # 1. takes the ARGUMENTS
    def decorator(func):               # 2. takes the FUNCTION
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # 3. takes the CALL
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(times=3)
def greet(name):
    print(f"  hello {name}")
    return name


print()
greet("Ada")

# @repeat(times=3) is CALLED FIRST, and its RESULT is used as the decorator:
#
#     greet = repeat(times=3)(greet)
#            ^^^^^^^^^^^^^^^^         returns `decorator`
#                            ^^^^^^^  which is then applied
#
# Note the TWO sets of parentheses. Read the definition outside-in:
# arguments, function, call. Every decorator-with-arguments has this shape.


# ---------------------------------------------------------------------------
# 5. Supporting BOTH @d and @d(arg)
# ---------------------------------------------------------------------------


def flexible(func=None, *, prefix=">>"):
    """Works as @flexible AND as @flexible(prefix='##')."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print(f"  {prefix} {f.__name__}")
            return f(*args, **kwargs)
        return wrapper

    if func is None:                   # called as @flexible(...)
        return decorator
    return decorator(func)             # called as bare @flexible


@flexible
def bare():
    return "bare"


@flexible(prefix="##")
def configured():
    return "configured"


print()
bare()
configured()
print("  ^ the `if func is None` check is why some library decorators")
print("    work with and without parentheses. No magic.")


# ---------------------------------------------------------------------------
# 6. STACKING applies BOTTOM-UP, and the order changes the meaning
# ---------------------------------------------------------------------------


def announce(label):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"  {label} enter")
            result = func(*args, **kwargs)
            print(f"  {label} exit")
            return result
        return wrapper
    return decorator


@announce("OUTER")
@announce("inner")
def work():
    print("    working")


print()
work()
print("""
  work = announce("OUTER")(announce("inner")(work))

  Bottom-up: `inner` is applied first, so it is CLOSEST to the function and
  OUTER wraps it. That is why OUTER's messages bracket inner's.

  It matters. @timer on top of @retry times ALL the retries together;
  swapped, it times each attempt. Write a comment saying which you meant.""")


# ---------------------------------------------------------------------------
# 7. A class can be a decorator too
# ---------------------------------------------------------------------------


class CountCalls:
    """Anything CALLABLE can decorate. A class with __call__ qualifies."""

    def __init__(self, func):
        functools.update_wrapper(self, func)     # the wraps equivalent
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)


@CountCalls
def ping():
    return "pong"


for _ in range(3):
    ping()
print(f"\nping was called {ping.count} times")
print("  ^ the count is REACHABLE, which a closure's would not be (Day 34).")
print("    That is the trade: inspectable state versus real privacy.")


# ---------------------------------------------------------------------------
# 8. The cost
# ---------------------------------------------------------------------------


def plain(n):
    return n * 2


@logged
def decorated_once(n):
    return n * 2


print(f"""
WHEN TO USE ONE — is this concern ORTHOGONAL to what the function does?

  YES   timing, retrying, caching, logging, access control, rate limiting,
        validation, registration. None of those are part of "compute a
        slug", and all of them apply identically to fifty functions.

  NO    anything that changes the function's LOGIC; anything that makes the
        signature unclear; a one-off. A decorator used once is a function
        call wearing a hat.

THE REAL COST IS DEBUGGABILITY. A traceback through three decorators has
three extra frames, and inspect.signature can lie. Use them for genuinely
cross-cutting concerns, not for cleverness.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Remove the `return` from a wrapper and watch every decorated function
#     start returning None.
#   * Remove @functools.wraps and check __name__ and help().
#   * Write @repeat without the middle layer and read the TypeError.
#   * Swap the two @announce lines and predict the output before running.
#   * Decorate a function twice with the same decorator. What happens?
