"""Day 031 — Writing functions.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. def defines; it does not run
# ---------------------------------------------------------------------------


def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"


print("nothing has been greeted yet — def only DEFINED it")
print(greet("Ada"))

# PARAMETERS are the names in the definition (name).
# ARGUMENTS are the values at the call ("Ada").
# Knowing which is which makes the error messages readable.

# The parentheses ARE the call:
print(f"\ngreet   -> {greet}")
print(f"greet() -> {greet('Ada')}")

# Passing a function WITHOUT parentheses is how you hand it to something
# else — and forgetting them produces no error until much later:
print(sorted(["ccc", "a", "bb"], key=len))       # key=len, not key=len()


# ---------------------------------------------------------------------------
# 2. return exits immediately — which is what makes guard clauses work
# ---------------------------------------------------------------------------


def classify(n):
    """Return 'negative', 'zero' or 'positive'."""
    if n < 0:
        return "negative"        # leaves here; nothing below runs
    if n == 0:
        return "zero"
    return "positive"


print(f"\n{[classify(n) for n in (-5, 0, 5)]}")

# Day 11 introduced guard clauses and had nothing to leave with. Now you do.
# Compare the nested version:


def classify_nested(n):
    if n < 0:
        result = "negative"
    else:
        if n == 0:
            result = "zero"
        else:
            result = "positive"
    return result


print("both agree:", [classify(n) for n in (-5, 0, 5)]
      == [classify_nested(n) for n in (-5, 0, 5)])


# ---------------------------------------------------------------------------
# 3. THE IMPLICIT None — the biggest beginner bug in this topic
# ---------------------------------------------------------------------------


def add_printing(a, b):
    print(a + b)                 # prints. Returns None.


def add_returning(a, b):
    return a + b                 # returns. Prints nothing.


print()
total = add_printing(2, 3)
print(f"add_printing returned: {total}")

try:
    add_printing(2, 3) + 1
except TypeError as e:
    print(f"and using it: TypeError: {e}")

print(f"add_returning(2, 3) + 1 = {add_returning(2, 3) + 1}")

# PRINT OR RETURN, AND KNOW WHICH YOU ARE DOING.
#
# A function that prints can be used exactly one way. A function that
# returns can be printed, stored, summed, tested (Day 57), or fed to
# another function. Return by default; print at the EDGES of the program.

# return with several values returns one tuple (Day 23):


def min_max(values):
    """Return the smallest and largest value."""
    return min(values), max(values)


low, high = min_max([3, 1, 4, 1, 5])
print(f"min_max -> {min_max([3, 1, 4, 1, 5])}, unpacked to {low}, {high}")


# ---------------------------------------------------------------------------
# 4. Local scope — the boundary doing its job
# ---------------------------------------------------------------------------


def make_local():
    x = 10                       # local to make_local
    return x


make_local()
try:
    print(x)
except NameError as e:
    print(f"\nafter the call: NameError: {e}")

# Two functions can both use `i` with no chance of collision. That is what
# makes them composable.

GREETING = "Hello"                # module level


def uses_a_global(name):
    return f"{GREETING}, {name}"   # READING from outside is fine


print(uses_a_global("Ada"))

# ASSIGNING to it is not, without `global` (Day 34):
#
#     def broken():
#         GREETING = GREETING + "!"     # UnboundLocalError
#
# THE RULE: PASS WHAT YOU NEED IN, RETURN WHAT YOU PRODUCE OUT. A function
# that reads globals cannot be moved, reused or tested without dragging its
# whole environment along.


# ---------------------------------------------------------------------------
# 5. Mutable arguments — rebinding vs mutating
# ---------------------------------------------------------------------------


def rebind(items):
    items = [1, 2, 3]            # rebinds the LOCAL name. Caller unaffected.
    return items


def mutate(items):
    items.append(4)              # mutates the SHARED object. Caller sees it.
    return items


original = [9]
rebind(original)
print(f"\nafter rebind:  {original}   <- unchanged")

original = [9]
mutate(original)
print(f"after mutate:  {original}   <- changed!")

# Both are legitimate. Doing the second BY ACCIDENT is not. If a function
# modifies its arguments, say so in the NAME and the DOCSTRING:


def sorted_copy(items):
    """Return a sorted copy, leaving the original alone."""
    items = list(items)          # now it is mine
    items.sort()
    return items


data = [3, 1, 2]
print(f"sorted_copy: {sorted_copy(data)}, original still {data}")


# ---------------------------------------------------------------------------
# 6. Docstrings and doctests
# ---------------------------------------------------------------------------


def clamp(value, low, high):
    """Return value limited to the range low..high.

    >>> clamp(15, 0, 10)
    10
    >>> clamp(-3, 0, 10)
    0
    """
    return max(low, min(value, high))


print(f"\nhelp text: {clamp.__doc__.splitlines()[0]}")
print(f"the name:  {clamp.__name__}")

# CONVENTION: one imperative line saying what it RETURNS, a blank line, then
# detail. If you cannot write that one line, the function does more than
# one thing.
#
# Examples that look like a REPL session are DOCTESTS and can be run:
#
#     python3 -m doctest -v toolkit.py
#
# toolkit.py in this folder has 28 of them, so the library tests itself
# before pytest arrives on Day 57.

import doctest                    # noqa: E402 - demonstrated in place

result = doctest.testmod(verbose=False)
print(f"doctests in THIS file: {result.attempted} run, {result.failed} failed")


# ---------------------------------------------------------------------------
# 7. What makes a good function
# ---------------------------------------------------------------------------
#
#   ONE JOB              if the docstring needs "and", split it
#   A NAME THAT SAYS     total_price, is_valid, parse_date. Verbs for
#   WHAT IT RETURNS      actions, is_/has_ for booleans
#   FEW PARAMETERS       more than about four means some belong together
#   NO SURPRISES         calculate_total() must not print or write files
#   SAME IN, SAME OUT    such functions are trivial to test and to reason
#                        about; ones that read the clock or a file are not
#   SHORT                not a rule — but a long function is usually
#                        several short ones not yet separated


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write a function that prints, then try to use its result in a sum.
#   * Put code after a return and watch ruff flag it as unreachable.
#   * Assign to a module-level name inside a function. Read the error.
#   * Write append_item(items) that mutates and with_item(items) that does
#     not, and prove the difference with `is`.
