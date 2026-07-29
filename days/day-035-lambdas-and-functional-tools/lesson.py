"""Day 035 — Lambdas and functional tools.

    python3 lesson.py
"""

import math
from functools import partial, reduce
from operator import itemgetter

WORDS = ["  Ada ", "CHARLES", "alan", "", "Grace  ", "42", "bjarne"]
NUMBERS = [3, -1, 4, -1, 5, 9, -2, 6]
PEOPLE = [
    {"name": "Ada", "age": 36},
    {"name": "Alan", "age": 41},
    {"name": "Grace", "age": 85},
]

# ---------------------------------------------------------------------------
# 1. lambda — an expression that makes a function
# ---------------------------------------------------------------------------

# DO NOT do this. It is a worse `def` that loses its name in tracebacks:
#     double = lambda n: n * 2          # ruff E731


def double(n):
    return n * 2


# lambda EARNS ITS PLACE as an argument to something else, when the function
# is too small to deserve a name:
print(sorted(PEOPLE, key=lambda p: p["age"])[0])
print(max(PEOPLE, key=lambda p: p["age"])["name"])
print(sorted({"a": 3, "b": 1}.items(), key=lambda kv: kv[1]))

# The restrictions ARE the design: one expression, no statements, no
# assignment, no return, no type hints. Want any of those? Use def.

anonymous = lambda n: n * 2         # noqa: E731 - to show the name
print(f"\na lambda's __name__ is {anonymous.__name__!r}, "
      f"a def's is {double.__name__!r}")
print("  ^ which is what you see in a traceback")


# ---------------------------------------------------------------------------
# 2. map and filter are LAZY
# ---------------------------------------------------------------------------

upper = map(str.upper, ["a", "b"])
print(f"\nmap object:   {upper}")
print(f"consumed:     {list(upper)}")
print(f"again:        {list(upper)}   <- empty. It is used up.")

print(f"\nfilter: {list(filter(str.isalpha, ['abc', '42', 'de']))}")

# filter(None, ...) drops every FALSY value — a genuinely useful idiom:
mixed = ["a", "", None, "b", 0, [], "c"]
print(f"filter(None, ...): {list(filter(None, mixed))}")
print(f"comprehension:     {[x for x in mixed if x]}")


# ---------------------------------------------------------------------------
# 3. map + lambda vs a comprehension
# ---------------------------------------------------------------------------

print(f"\nmap + lambda:  {list(map(lambda n: n * 2, NUMBERS))}")
print(f"comprehension: {[n * 2 for n in NUMBERS]}")
#      ^ same answer. The comprehension does not need the word `lambda`,
#        and puts the expression where you read it first.

# WHEN YOU ALREADY HAVE A NAMED FUNCTION, map is fine and arguably neater:
print(f"\nmap + named:   {list(map(str.strip, WORDS))}")
print(f"comprehension: {[w.strip() for w in WORDS]}")

# THE RULE: when the transform needs a lambda, use a comprehension. When it
# is an existing named function, either is good.

# And the reason it matters, at three clauses:
functional = list(map(str.upper, filter(str.isalpha, map(str.strip, WORDS))))
comprehension = [w.strip().upper() for w in WORDS if w.strip().isalpha()]
print(f"\nnested functional: {functional}")
print(f"comprehension:     {comprehension}")
print(f"identical: {functional == comprehension}")
print("""  The functional version reads INSIDE OUT and right to left: strip,
  then filter, then upper. The comprehension reads in the order the data
  flows. That is the whole readability argument.""")


# ---------------------------------------------------------------------------
# 4. reduce — recognise it, rarely write it
# ---------------------------------------------------------------------------

print(f"\nreduce(add):   {reduce(lambda a, b: a + b, [1, 2, 3, 4])}")
print(f"sum():         {sum([1, 2, 3, 4])}          <- use this")

print(f"reduce(max):   {reduce(lambda a, b: a if a > b else b, NUMBERS)}")
print(f"max():         {max(NUMBERS)}          <- use this")

print(f"reduce(mul):   {reduce(lambda a, b: a * b, [1, 2, 3, 4])}")
print(f"math.prod():   {math.prod([1, 2, 3, 4])}         <- use this")

# BEFORE REACHING FOR reduce, CHECK WHETHER A BUILTIN EXISTS:
#
#     a + b            -> sum()
#     a if a > b       -> max()
#     a * b            -> math.prod()
#     string concat    -> "".join()
#     a and b          -> all()
#
# reduce was a BUILTIN in Python 2. Guido moved it to functools on purpose,
# arguing almost every real use is clearer as a loop or an existing builtin.
# He was right.

# ALWAYS PASS THE INITIAL VALUE. Without it, an empty sequence raises:
try:
    reduce(lambda a, b: a + b, [])
except TypeError as e:
    print(f"\nreduce on empty: TypeError: {e}")
print(f"with an initial value: {reduce(lambda a, b: a + b, [], 0)}")

# A legitimate use: a custom accumulation with no builtin equivalent —
# merging a list of dicts, right-most winning.
configs = [{"a": 1}, {"b": 2}, {"a": 9}]
print(f"\nmerged: {reduce(lambda acc, d: {**acc, **d}, configs, {})}")

merged = {}
for config in configs:
    merged.update(config)
print(f"loop:   {merged}   <- and honestly this is clearer")


# ---------------------------------------------------------------------------
# 5. partial and operator
# ---------------------------------------------------------------------------

int_from_binary = partial(int, base=2)
int_from_hex = partial(int, base=16)

print(f"\npartial: {int_from_binary('1010')} and {int_from_hex('ff')}")

# partial fixes some arguments and returns a new function. It is a closure
# (Day 34) with a standard name, and it is genuinely useful for callbacks.


def make_int_parser(base):
    """The same thing, as a closure."""
    def parse(text):
        return int(text, base=base)
    return parse


print(f"closure: {make_int_parser(2)('1010')}")

# `operator` replaces the most common trivial lambdas, and is faster:
print(f"\nlambda:     {[p['name'] for p in sorted(PEOPLE, key=lambda p: p['age'])]}")
print(f"itemgetter: {[p['name'] for p in sorted(PEOPLE, key=itemgetter('age'))]}")


# ---------------------------------------------------------------------------
# 6. The ranking, and the three ideas actually worth keeping
# ---------------------------------------------------------------------------

print("""
PREFERENCE ORDER FOR PYTHON

  1. a comprehension                for map/filter work — the default
  2. a generator expression         when the data is large or one-pass
  3. a for loop                     side effects, early exit, >1 output
  4. map/filter + a NAMED function  neat, reads well
  5. map/filter + a lambda          almost always worse than (1)
  6. reduce                         only when no builtin fits

WHAT IS GENUINELY WORTH TAKING FROM FUNCTIONAL PROGRAMMING

  * PURE FUNCTIONS — same input, same output, no side effects. Trivial to
    test (Day 57) and to reason about.
  * IMMUTABILITY — return new values rather than mutating (Day 21).
  * FUNCTIONS AS VALUES — passing behaviour as an argument: key=,
    decorators, callbacks.

Those three improve code in ANY style. reduce does not.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Print a map object, then list() it twice.
#   * Write `f = lambda x: x` and run ruff with --select E731.
#   * Replace three reduce calls with builtins.
#   * Write the nastiest nested map/filter you can, then rewrite it as a
#     comprehension and show both to someone who has not seen either.
