"""Day 014 build — a prime finder that stops the moment it knows.

Four versions of the same test, each one line different from the last, each
one counting the divisions it performs. The counts are the point: this build
is an argument, and the numbers are the evidence.

    python3 build.py
    python3 build.py 999983
    python3 build.py 1000000
"""

import sys

WIDTH = 68

number = 999983                   # a prime, chosen so the naive version hurts
if len(sys.argv) >= 2 and sys.argv[1].isdigit():
    number = int(sys.argv[1])


# ===========================================================================
# The four versions. Each returns (is_prime, divisions_performed).
# ===========================================================================

def v1_naive(n):
    """Check every divisor from 2 to n-1, and never stop early."""
    if n < 2:
        return False, 0
    divisions = 0
    prime = True
    for d in range(2, n):
        divisions += 1
        if n % d == 0:
            prime = False          # found a factor, but keeps going anyway
    return prime, divisions


def v2_break(n):
    """Same, but stop at the first factor found."""
    if n < 2:
        return False, 0
    divisions = 0
    for d in range(2, n):
        divisions += 1
        if n % d == 0:
            return False, divisions
    return True, divisions


def v3_sqrt(n):
    """Stop at the square root — a factor above it implies one below."""
    if n < 2:
        return False, 0
    divisions = 0
    # int(n ** 0.5) + 1 as the range stop means the last divisor TESTED is
    # int(sqrt(n)). Drop the +1 and perfect squares are misclassified: 25
    # would never test 5 and would be called prime.
    for d in range(2, int(n**0.5) + 1):
        divisions += 1
        if n % d == 0:
            return False, divisions
    return True, divisions


def v4_odds(n):
    """Handle 2 once, then test only odd divisors. Halves the remaining work."""
    if n < 2:
        return False, 0
    if n == 2:
        return True, 0
    if n % 2 == 0:
        return False, 1
    divisions = 1                  # the n % 2 test above counts
    for d in range(3, int(n**0.5) + 1, 2):
        divisions += 1
        if n % d == 0:
            return False, divisions
    return True, divisions


# ===========================================================================
# 1. Correctness first. A fast wrong answer is worth nothing.
# ===========================================================================

print("=" * WIDTH)
print(f"{'CORRECTNESS — the cases that break naive versions':^{WIDTH}}")
print("=" * WIDTH)

# Known answers, including every edge case that catches people:
#   0, 1     not prime (1 is the classic mistake — it has no factor in
#            range(2, 1), so a loop-else version calls it prime)
#   2        prime, and the only even prime
#   25, 49   perfect squares, where an off-by-one in the sqrt bound shows
CASES = (
    (0, False), (1, False), (2, True), (3, True), (4, False),
    (9, False), (17, True), (25, False), (49, False), (97, True),
    (100, False), (7919, True),
)

print(f"{'n':>8}{'expect':>9}{'v1':>7}{'v2':>7}{'v3':>7}{'v4':>7}{'all agree':>12}")
print("-" * WIDTH)

all_ok = True
for n, expected in CASES:
    r1 = v1_naive(n)[0]
    r2 = v2_break(n)[0]
    r3 = v3_sqrt(n)[0]
    r4 = v4_odds(n)[0]
    agree = r1 == r2 == r3 == r4 == expected
    all_ok = all_ok and agree
    print(
        f"{n:>8}{str(expected):>9}{str(r1):>7}{str(r2):>7}"
        f"{str(r3):>7}{str(r4):>7}{str(agree):>12}"
    )

print("-" * WIDTH)
print(f"{'every version correct on every case':<52}{str(all_ok):>16}")
print()

# ===========================================================================
# 2. Now the cost. Same answer, four very different amounts of work.
# ===========================================================================

print("=" * WIDTH)
print(f"{f'COST — testing {number}':^{WIDTH}}")
print("=" * WIDTH)

prime_1, cost_1 = v1_naive(number)
prime_2, cost_2 = v2_break(number)
prime_3, cost_3 = v3_sqrt(number)
prime_4, cost_4 = v4_odds(number)

print(f"{'version':<34}{'prime?':>9}{'divisions':>12}{'vs v1':>12}")
print("-" * WIDTH)
print(f"{'v1  every divisor, no break':<34}{str(prime_1):>9}{cost_1:>12,}{'1x':>12}")
print(
    f"{'v2  stop at first factor':<34}{str(prime_2):>9}{cost_2:>12,}"
    f"{f'{cost_1 / (cost_2 or 1):.0f}x':>12}"
)
print(
    f"{'v3  stop at sqrt(n)':<34}{str(prime_3):>9}{cost_3:>12,}"
    f"{f'{cost_1 / (cost_3 or 1):.0f}x':>12}"
)
print(
    f"{'v4  sqrt, odd divisors only':<34}{str(prime_4):>9}{cost_4:>12,}"
    f"{f'{cost_1 / (cost_4 or 1):.0f}x':>12}"
)
print("-" * WIDTH)
print(f"{'work avoided by v4':<46}{cost_1 - cost_4:>22,}")
print()

# Notice what did NOT change: the answer. Every version above agrees on
# every case in the table. That is what makes this an optimisation rather
# than a rewrite — and why the correctness table comes first.

# ===========================================================================
# 3. break vs no break on a COMPOSITE — where v2 alone wins big
# ===========================================================================

composite = number + 1
print("=" * WIDTH)
print(f"{f'THE SAME TEST ON {composite} (composite)':^{WIDTH}}")
print("=" * WIDTH)
_, c1 = v1_naive(composite)
_, c2 = v2_break(composite)
_, c4 = v4_odds(composite)
print(f"{'v1  no break':<40}{c1:>28,}")
print(f"{'v2  break at first factor':<40}{c2:>28,}")
print(f"{'v4  break + sqrt + odds':<40}{c4:>28,}")
print()
print("An even composite falls out after ONE division. Most composites die")
print("almost immediately; it is the PRIMES that are expensive, because they")
print("are the only numbers that make the loop run to the end.")
print()

# ===========================================================================
# 4. The first primes, using for...else as the search
# ===========================================================================

print("=" * WIDTH)
print(f"{'THE FIRST 20 PRIMES (for...else)':^{WIDTH}}")
print("=" * WIDTH)

primes = []
candidate = 2
while len(primes) < 20:
    for d in range(2, int(candidate**0.5) + 1):
        if candidate % d == 0:
            break
    else:
        # "no break" — nothing divided it, so it is prime.
        primes.append(candidate)
    candidate += 1

for i, p in enumerate(primes, start=1):
    print(f"{p:>6}", end="\n" * (i % 10 == 0))
print()
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 build.py 1000003` (prime) and then 1000004 (even). Compare
#     the division counts. The difference between "expensive" and "free" is
#     entirely about whether the loop gets to finish.
#
#   * Delete the `+ 1` from `int(n**0.5) + 1` in v3 and re-run. The
#     correctness table should immediately flag 25 and 49. That table is
#     doing the job a test suite will do properly on Day 57.
#
#   * v4 tests 3, 5, 7, 9, 11 ... but 9 is not prime, so testing it is
#     wasted. Testing only PRIME divisors would be better still — but it
#     needs a list of primes you have not computed yet. Think about why that
#     is a chicken-and-egg problem, then look up the Sieve of Eratosthenes,
#     which solves it by turning the question inside out.
#
#   * Time the four versions with time.perf_counter() (Day 19) instead of
#     counting divisions. The ratios should match. If they do not, you have
#     learned something about what actually costs time.
