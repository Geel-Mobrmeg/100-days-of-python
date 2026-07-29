"""Day 036 — Recursion.

    python3 lesson.py
"""

import sys
import time
from functools import cache

WIDTH = 72

# ---------------------------------------------------------------------------
# 1. The two parts. Write the BASE CASE first, always.
# ---------------------------------------------------------------------------


def countdown(n, depth=0):
    """Count down to liftoff, showing the stack as it grows."""
    print(f"  {'| ' * depth}countdown({n})")
    if n <= 0:                       # BASE CASE — stop, do not recurse
        print(f"  {'| ' * depth}liftoff")
        return
    countdown(n - 1, depth + 1)      # RECURSIVE CASE — SMALLER problem
    print(f"  {'| ' * depth}...returning from countdown({n})")


countdown(3)

print("""
Each call gets its own frame with its own locals. They stack up on the way
down and unwind in reverse — which is why Day 9's traceback said "most
recent call last".

THE THREE QUESTIONS to ask of any recursive function:

  1. What is the SMALLEST input, and what do I return for it?
  2. Does every recursive call get STRICTLY closer to that?
  3. If I ASSUME the recursive call is correct, is my answer correct?

Question 3 is the leap. TRUST THE RECURSION. Do not trace three levels down
in your head — assume the inner call works and check that you combine its
result correctly. People who find recursion hard are almost always trying
to simulate the stack mentally.""")


# ---------------------------------------------------------------------------
# 2. What happens without a base case
# ---------------------------------------------------------------------------


def no_base_case(n):
    return no_base_case(n - 1)       # never stops


try:
    no_base_case(10)
except RecursionError as e:
    print(f"\nno base case: RecursionError: {e}")

print(f"the limit is {sys.getrecursionlimit()} frames")

# sys.setrecursionlimit(3000) is possible and is USUALLY THE WRONG FIX. A
# depth over 1000 means either a missing base case or a problem that wants
# iteration. And Python has NO tail-call optimisation, deliberately — so a
# depth of 100,000 will not work however you write it.

# A base case that exists but is never REACHED fails the same way:


def never_reaches(n):
    if n == 0:
        return 0
    return never_reaches(n - 2)      # from an odd n, skips straight past 0


try:
    never_reaches(5)
except RecursionError:
    print("a base case that is never REACHED fails identically — and is")
    print("much harder to see. never_reaches(5) steps 5,3,1,-1,-3...")


# ---------------------------------------------------------------------------
# 3. Where recursion GENUINELY wins: the data is a tree
# ---------------------------------------------------------------------------

NESTED = [1, [2, [3, [4, [5]]], 6], [7, 8]]


def total(items):
    """Sum a list nested to any depth. Try writing this with a loop."""
    result = 0
    for item in items:
        if isinstance(item, list):
            result += total(item)     # trust it
        else:
            result += item
    return result


print(f"\nsum of {NESTED} = {total(NESTED)}")

CONFIG = {"a": 1, "b": {"c": 2, "d": {"e": 3, "f": [4, {"g": 5}]}}}


def find_all(data, key):
    """Every value for `key`, at ANY depth. Day 28's natural next step."""
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                found.append(v)
            found.extend(find_all(v, key))
    elif isinstance(data, list):
        for item in data:
            found.extend(find_all(item, key))
    return found


print(f"every 'g' anywhere in the config: {find_all(CONFIG, 'g')}")
print(f"every 'c' anywhere in the config: {find_all(CONFIG, 'c')}")

# THE COMMON SHAPE: the data is a TREE and the number of levels is not
# known in advance. Directory trees, JSON, comment threads, expressions,
# divide-and-conquer, flood fill.


# ---------------------------------------------------------------------------
# 4. Where recursion LOSES: flat sequences
# ---------------------------------------------------------------------------


def factorial_recursive(n):
    return 1 if n <= 1 else n * factorial_recursive(n - 1)


def factorial_loop(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(f"\nfactorial(20) both ways agree: "
      f"{factorial_recursive(20) == factorial_loop(20)}")

try:
    factorial_recursive(2000)
except RecursionError:
    print(f"factorial_recursive(2000): RecursionError")
print(f"factorial_loop(2000): {len(str(factorial_loop(2000)))} digits, no problem")

# Factorial is the example everyone is taught and it is a BAD one: it is a
# flat sequence, the loop is clearer, and only the loop scales.


# ---------------------------------------------------------------------------
# 5. Memoisation — one line, exponential to linear
# ---------------------------------------------------------------------------

calls = 0


def fib_naive(n):
    global calls                     # noqa: PLW0603 - counting, deliberately
    calls += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@cache
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


print(f"\n{'n':>4}{'fib(n)':>14}{'naive calls':>14}{'naive ms':>12}")
print("-" * 46)
for n in (20, 25, 30):
    calls = 0
    start = time.perf_counter()
    value = fib_naive(n)
    elapsed = (time.perf_counter() - start) * 1000
    assert value == fib_cached(n)
    print(f"{n:>4}{value:>14,}{calls:>14,}{elapsed:>12.1f}")

start = time.perf_counter()
big = fib_cached(300)
cached_ms = (time.perf_counter() - start) * 1000
print(f"\n@cache fib(300) = {str(big)[:20]}... in {cached_ms:.3f} ms")
print(f"cache stats: {fib_cached.cache_info()}")
print("""
  The naive version would not finish fib(300) before the sun goes out.
  ONE DECORATOR turned an exponential algorithm into a linear one without
  changing the algorithm — which is Day 34's build, now as a builtin.

  @cache is @lru_cache(maxsize=None). Both need HASHABLE arguments: no
  lists, no dicts (Day 23).""")


# ---------------------------------------------------------------------------
# 6. Converting recursion to iteration
# ---------------------------------------------------------------------------

TREE = {
    "root": ["a", "b"],
    "a": ["a1", "a2"],
    "b": ["b1"],
    "a1": [], "a2": [], "b1": [],
}


def walk_recursive(node, depth=0, out=None):
    if out is None:                  # NOT out=[] — Day 32's B006
        out = []
    out.append(f"{'  ' * depth}{node}")
    for child in TREE.get(node, []):
        walk_recursive(child, depth + 1, out)
    return out


def walk_iterative(root):
    """The same traversal with an EXPLICIT stack — no depth limit."""
    out = []
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        out.append(f"{'  ' * depth}{node}")
        # reversed() so children come off the stack in their original order
        for child in reversed(TREE.get(node, [])):
            stack.append((child, depth + 1))
    return out


def walk_breadth_first(root):
    """ONE LINE different: pop(0) instead of pop()."""
    out = []
    queue = [(root, 0)]
    while queue:
        node, depth = queue.pop(0)
        out.append(f"{'  ' * depth}{node}")
        for child in TREE.get(node, []):
            queue.append((child, depth + 1))
    return out


print("\nrecursive (depth-first):", walk_recursive("root"))
print("iterative (depth-first):", walk_iterative("root"))
print("identical:", walk_recursive("root") == walk_iterative("root"))
print("iterative (breadth-first):", walk_breadth_first("root"))

print("""
  The explicit stack does BY HAND exactly what the call stack was doing for
  you. The gain is no depth limit; the cost is more code and having to
  think about order — pop() is depth-first, pop(0) is breadth-first.

  Note walk_recursive uses out=None, not out=[]. A mutable default here
  would accumulate across every separate call to the function (Day 32).""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete the base case from countdown and read the RecursionError.
#   * Write never_reaches(4) — it works. Then never_reaches(5). Why?
#   * Remove @cache from fib_cached and try fib(50). Then put it back.
#   * Change walk_iterative's pop() to pop(0) and see the order change.
#   * Sum [1, [2, [3, ...]]] nested 2000 deep. It will fail — and the fix is
#     the explicit stack, not a bigger recursion limit.
