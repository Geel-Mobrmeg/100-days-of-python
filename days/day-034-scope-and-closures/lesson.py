"""Day 034 — Scope and closures.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. LEGB — Local, Enclosing, Global, Built-in. First hit wins.
# ---------------------------------------------------------------------------

x = "global"


def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(f"  all three defined:      {x}")

    inner()

    def inner_no_local():
        print(f"  no local:               {x}")

    inner_no_local()


outer()


def no_enclosing():
    print(f"  no local, no enclosing: {x}")


no_enclosing()
print(f"  built-in:               {len('found len via B')}")

# This is also why shadowing a builtin is dangerous (Day 8): a name at
# module level sits in G, which is searched BEFORE B.
list_backup = list
list = [1, 2]                       # noqa: A001 - the exhibit
try:
    list("abc")
except TypeError as e:
    print(f"\nafter `list = [1, 2]`: TypeError: {e}")
list = list_backup                  # noqa: A001 - put it back


# ---------------------------------------------------------------------------
# 2. Reading is free. ASSIGNING makes the name local FOR THE WHOLE FUNCTION.
# ---------------------------------------------------------------------------

count = 0


def broken():
    print(count)                    # noqa: F823 - UnboundLocalError, not 0
    count = count + 1               # noqa: F841


try:
    broken()
except UnboundLocalError as e:
    print(f"\nbroken(): UnboundLocalError: {e}")

# Python decides scope at COMPILE time by scanning for assignments, not at
# run time. Because `count = ...` appears SOMEWHERE in the body, `count` is
# local THROUGHOUT — so the print reads a local that does not exist yet.
#
# `+=` counts as an assignment, which is why counters break exactly here.

print(f"the compiler already knew: locals of broken() = {broken.__code__.co_varnames}")


# ---------------------------------------------------------------------------
# 3. global and nonlocal
# ---------------------------------------------------------------------------


def with_global():
    global count
    count += 1
    return count


print(f"\nwith_global(): {with_global()}, {with_global()}  (module `count` moved)")

# AVOID global. A function that mutates module state cannot be tested in
# isolation, cannot be reasoned about locally, and cannot be run twice
# safely. Pass values in, return values out:


def without_global(current):
    return current + 1


print(f"without_global: {without_global(without_global(0))}")


def outer_counter():
    total = 0

    def bump():
        nonlocal total              # the NEAREST ENCLOSING FUNCTION scope
        total += 1

    bump()
    bump()
    return total


print(f"nonlocal: {outer_counter()}")

# global   reaches the MODULE level
# nonlocal reaches the nearest ENCLOSING FUNCTION — never the global one.
# `nonlocal` at module level is a SyntaxError: there is nothing to enclose.


# ---------------------------------------------------------------------------
# 4. Closures — a function that remembers where it was defined
# ---------------------------------------------------------------------------


def make_multiplier(factor):
    def multiply(value):
        return value * factor       # `factor` comes from the enclosing scope
    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)

print(f"\ndouble(5) = {double(5)}, triple(5) = {triple(5)}")

# make_multiplier(2) has RETURNED. Its frame is gone. And yet `double` still
# knows factor is 2, because Python kept the variable alive when the inner
# function referred to it. You can see the evidence:

print(f"double.__closure__[0].cell_contents = {double.__closure__[0].cell_contents}")
print(f"triple.__closure__[0].cell_contents = {triple.__closure__[0].cell_contents}")
print(f"separate objects: {double is not triple}")


# ---------------------------------------------------------------------------
# 5. THE LOOP TRAP — closures capture the VARIABLE, not the VALUE
# ---------------------------------------------------------------------------

functions = []
for i in range(3):
    functions.append(lambda: i)

print(f"\nlate binding:  {[f() for f in functions]}   <- not [0, 1, 2]")

# All three lambdas share the same `i`. By the time they run, the loop has
# finished and `i` is 2.

# FIX 1 — a default argument, which Day 32 taught is evaluated ONCE AT
# DEFINITION. Here that is exactly what you want:
functions = []
for i in range(3):
    functions.append(lambda i=i: i)
print(f"default arg:   {[f() for f in functions]}")

# FIX 2 — a factory, which is clearer about what is being captured:
functions = [make_multiplier(i) for i in range(3)]
print(f"factory:       {[f(1) for f in functions]}")


# ---------------------------------------------------------------------------
# 6. A CLOSURE IS AN OBJECT WITH ONE METHOD
# ---------------------------------------------------------------------------


def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count


closure_counter = make_counter()
class_counter = Counter()

print(f"\nclosure: {[closure_counter() for _ in range(3)]}")
print(f"class:   {[class_counter.increment() for _ in range(3)]}")

# Same behaviour, same encapsulation, same private state. The differences:
#
#              CLOSURE                       CLASS
#   scope      one behaviour                 many methods
#   state      genuinely PRIVATE — there     obj.count is reachable, and
#              is no way to reach `count`    that is sometimes what you want
#   weight     lighter, faster               introspectable, subclassable
#
# USE A CLOSURE for one behaviour with a little state.
# USE A CLASS when there are several operations on the same state.
#
# A closure with three inner functions returned in a tuple is a class that
# has not admitted it yet — which is Day 41.

print(f"\nthe class exposes its state:  {class_counter.count}")
print(f"the closure does not: {[a for a in dir(closure_counter) if 'count' in a] or 'nothing named count'}")


# ---------------------------------------------------------------------------
# 7. Why this matters: it is how decorators work
# ---------------------------------------------------------------------------


def announce(func):
    def wrapper(*args, **kwargs):
        print(f"  calling {func.__name__}")     # `func` is CAPTURED
        return func(*args, **kwargs)
    return wrapper


@announce
def add(a, b):
    return a + b


print(f"\n{add(2, 3)}")

# `wrapper` remembers `func` through a closure, which is the entire
# mechanism of Day 37. The @ is only notation.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Reproduce the UnboundLocalError, then fix it three ways: global,
#     passing the value in, and returning the new value.
#   * Make two counters and prove they are independent.
#   * Reproduce the loop trap with a list of lambdas, then fix it twice.
#   * Try `nonlocal x` at module level and read the SyntaxError.
#   * Write a closure that keeps a running average WITHOUT storing the
#     values — just a count and a total.
