"""Day 038 — Generators and yield.

    python3 lesson.py
"""

import sys
from itertools import count, cycle, islice, takewhile

WIDTH = 72

# ---------------------------------------------------------------------------
# 1. yield SUSPENDS. return DESTROYS.
# ---------------------------------------------------------------------------


def count_to(n):
    print("    (function body starts)")
    for i in range(n):
        print(f"    (about to yield {i})")
        yield i
    print("    (function body ends)")


print("calling count_to(3):")
gen = count_to(3)
print(f"  got {gen}")
print("  ^ NO CODE HAS RUN. Calling a generator function returns a")
print("    generator object and nothing else.\n")

print(f"  next() -> {next(gen)}")
print(f"  next() -> {next(gen)}")
print(f"  next() -> {next(gen)}")
try:
    next(gen)
except StopIteration:
    print("  next() -> StopIteration")

print("""
Between the two `next()` calls the function was FROZEN — its locals, its
position in the loop, everything. `return` throws that away; `yield` keeps
it and resumes on the next request.

`for x in gen:` calls next() for you and stops at StopIteration.""")


# ---------------------------------------------------------------------------
# 2. One-shot, no length, no indexing
# ---------------------------------------------------------------------------

gen = count_to(3)
print(f"\nfirst pass:  {[x for x in gen if True]}")
print(f"second pass: {list(gen)}   <- empty. It is used up.")

gen = count_to(3)
for attr, call in (("len()", lambda: len(gen)), ("gen[0]", lambda: gen[0])):
    try:
        call()
    except TypeError as e:
        print(f"{attr:<10} TypeError: {e}")

print("""
You cannot know how many items there are without consuming them, which is
the price of not having computed them. Need the data twice? list() it (and
pay the memory) or call the generator function again (and pay the work).""")


# ---------------------------------------------------------------------------
# 3. THE MEMORY DIFFERENCE — one word
# ---------------------------------------------------------------------------

N = 2_000_000

eager = [n * n for n in range(N)]
lazy = (n * n for n in range(N))

print(f"\n{'list comprehension':<26}{sys.getsizeof(eager):>14,} bytes")
print(f"{'generator expression':<26}{sys.getsizeof(lazy):>14,} bytes")
print(f"{'same total':<26}{str(sum(eager) == sum(n * n for n in range(N))):>14}")
del eager

# Round brackets instead of square (Day 22). Inside a function call the
# extra brackets can be dropped:
print(f"\nsum(n * n for n in range(10)) = {sum(n * n for n in range(10))}")

# any() and all() over a generator SHORT-CIRCUIT — they stop reading at the
# first decisive value:
checked = 0


def watched(limit):
    global checked                    # noqa: PLW0603 - counting, deliberately
    for n in range(limit):
        checked += 1
        yield n


checked = 0
print(f"any(n > 2 ...) over 1,000,000 = "
      f"{any(n > 2 for n in watched(1_000_000))}, after {checked} items read")


# ---------------------------------------------------------------------------
# 4. Infinite sequences
# ---------------------------------------------------------------------------


def naturals():
    n = 0
    while True:                       # never ends, and that is fine
        yield n
        n += 1


print(f"\nfirst 8 naturals:  {list(islice(naturals(), 8))}")
print(f"itertools.count:   {list(islice(count(10, 5), 5))}")
print(f"itertools.cycle:   {list(islice(cycle('abc'), 7))}")
print(f"takewhile:         {list(takewhile(lambda n: n < 5, naturals()))}")

# islice is the LAZY [:n]. `list(naturals())[:8]` would never finish.


# ---------------------------------------------------------------------------
# 5. PIPELINES — the reason generators are a design tool
# ---------------------------------------------------------------------------

LOG = """2024-03-01 INFO  request ok
2024-03-01 ERROR database timeout

2024-03-02 WARN  slow query 812ms
2024-03-02 ERROR database timeout
2024-03-02 INFO  request ok
# a comment line
2024-03-03 ERROR disk full"""


def source(text):
    for line in text.splitlines():
        yield line


lines = source(LOG)
stripped = (line.strip() for line in lines)
real = (line for line in stripped if line and not line.startswith("#"))
errors = (line for line in real if " ERROR " in line)
messages = (line.split(" ERROR ")[1] for line in errors)

print("\nnothing has been read yet. Now the for loop pulls:")
for message in messages:
    print(f"  {message}")

print("""
Each stage holds ONE item. The for loop at the bottom pulls a line all the
way through the chain, then the next one. This is the Unix pipe model, and
it composes the same way: each stage does one thing, stages can be
reordered or reused, and adding one costs a line and no memory.""")


# ---------------------------------------------------------------------------
# 6. yield from — delegation, and lazy recursion
# ---------------------------------------------------------------------------

NESTED = [1, [2, [3, [4, [5]]], 6], [7, 8]]


def flatten(items):
    """Day 36's recursion, lazily. Note `yield from` for the recursive call."""
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)      # delegate to the inner generator
        else:
            yield item


print(f"\nflatten({NESTED})")
print(f"  -> {list(flatten(NESTED))}")
print(f"  first two only: {list(islice(flatten(NESTED), 2))}  "
      f"<- the rest was never visited")

# Without `yield from` you would write:
#     for value in flatten(item):
#         yield value
# which is the same thing, three characters longer, and misses some
# generator plumbing (send/throw) that matters for coroutines.


# ---------------------------------------------------------------------------
# 7. Cleanup: the `with` goes INSIDE the generator
# ---------------------------------------------------------------------------
#
#     def read_lines(path):
#         with open(path) as f:          # opened on FIRST next()
#             for line in f:
#                 yield line.rstrip("\n")
#                                        # closed when exhausted or GC'd
#
# Put the `with` outside and the file closes before anything is consumed.
# Open without `with` and it may never close. Day 53 covers this properly.


# ---------------------------------------------------------------------------
# 8. When NOT to use one
# ---------------------------------------------------------------------------

print("""
USE A GENERATOR WHEN
  * the data is large, streamed, or infinite
  * you only need one pass
  * results should start arriving before the work is finished
  * you are building a pipeline

USE A LIST WHEN
  * you need len(), indexing, or slicing
  * you need more than one pass
  * you need to sort or reverse it (both need everything anyway)
  * it is small and clarity wins

The honest default: comprehension for small collections, generator the
moment the size is unbounded or unknown.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Consume a generator twice.
#   * Call len() and [0] on one.
#   * Turn one pipeline stage's () into [] and watch the memory jump.
#   * list(naturals()) — then Ctrl-C, and think about what islice avoided.
#   * Write flatten() without `yield from` and confirm it still works.
