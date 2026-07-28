"""Day 016 — Randomness and simulation.

    python3 lesson.py

Every section is seeded, so this file prints the SAME numbers every time you
run it. That is the point of section 3, and it also means you can compare
your output against a friend's.
"""

import random

# ---------------------------------------------------------------------------
# 1. The functions
# ---------------------------------------------------------------------------

random.seed(42)

print("randint(1, 6)     ", random.randint(1, 6))       # 1..6 INCLUSIVE
print("randrange(1, 7)   ", random.randrange(1, 7))     # 1..6, stop excluded
print("random()          ", round(random.random(), 4))  # 0.0 <= x < 1.0
print("uniform(1.5, 3.5) ", round(random.uniform(1.5, 3.5), 4))
print("choice(...)       ", random.choice(["rock", "paper", "scissors"]))

# randint INCLUDES BOTH ENDS. It is the only range-like thing in Python that
# does, and it is why this is a classic off-by-one:
items = ["a", "b", "c"]
# random.randint(0, len(items))     # can return 3 -> IndexError
print("safe index        ", random.randrange(len(items)))   # 0, 1 or 2
print("safer still       ", random.choice(items))           # no index at all


# ---------------------------------------------------------------------------
# 2. shuffle mutates and returns None
# ---------------------------------------------------------------------------

cards = ["A", "K", "Q", "J", "10"]

wrong = random.shuffle(cards)
print("\nreturn value of shuffle:", wrong)      # None!
print("but the list itself:    ", cards)        # shuffled in place

# `x = something.method()` giving None is a shape you will meet again on
# Day 21 with .sort() and .append(). Python's convention: METHODS THAT CHANGE
# A THING IN PLACE RETURN None, so you cannot believe you got a copy.

original = ["A", "K", "Q", "J", "10"]
copy = random.sample(original, len(original))    # a shuffled COPY
print("original untouched:     ", original)
print("shuffled copy:          ", copy)


# ---------------------------------------------------------------------------
# 3. Seeding — the half that matters
# ---------------------------------------------------------------------------

# Python's randomness is PSEUDO-random: a deterministic sequence computed
# from a starting number. Same seed, same sequence, every machine, forever.

random.seed(42)
first = [random.randint(1, 6) for _ in range(5)]
random.seed(42)
second = [random.randint(1, 6) for _ in range(5)]

print(f"\nseeded 42: {first}")
print(f"seeded 42: {second}")
print(f"identical: {first == second}")

# Seed WHEN YOU NEED TO REPRODUCE:
#   * debugging  — a bug that shows up 1 run in 50 becomes a bug that shows
#                  up every run
#   * tests      — a test that sometimes fails is worse than no test (Day 57)
#   * results    — anyone re-running your simulation gets your numbers
#
# Do NOT seed when you need unpredictability (a game, a shuffle for a user).

# THE CLASSIC SEEDING BUG: seeding inside the loop.
print("\nseeding inside the loop:", end=" ")
for _ in range(5):
    random.seed(1)
    print(random.randint(1, 100), end=" ")
print("  <- the same 'random' number five times")

# A PRIVATE generator is better than the module-level functions when it
# matters, because module level shares one global state that any library can
# reseed underneath you:
rng = random.Random(42)
print("\nprivate generator:", [rng.randint(1, 6) for _ in range(5)])

# NEVER use `random` for anything security-related — passwords, tokens,
# session ids, password resets. It is fast and predictable BY DESIGN, and a
# few outputs are enough to compute the rest. Use `secrets`:
#
#     import secrets
#     secrets.token_hex(16)
#     secrets.randbelow(100)
#     secrets.choice(items)


# ---------------------------------------------------------------------------
# 4. choices vs sample — with and without replacement
# ---------------------------------------------------------------------------

random.seed(7)
deck = ["A", "K", "Q", "J", "10", "9"]

print(f"\nchoices (can repeat):  {random.choices(deck, k=5)}")
print(f"sample  (cannot):      {random.sample(deck, k=5)}")

# choices = rolling a die five times. sample = dealing five cards.
# Picking the wrong one gives a subtle, plausible bug: duplicate cards in a
# hand look like bad data rather than bad code.

# choices also takes weights, which is how you make an unfair die:
random.seed(7)
loaded = random.choices([1, 2, 3, 4, 5, 6], weights=[1, 1, 1, 1, 1, 5], k=12)
print(f"loaded die (6 is 5x):  {loaded}")


# ---------------------------------------------------------------------------
# 5. Small samples lie — and the error shrinks with sqrt(n)
# ---------------------------------------------------------------------------

print(f"\n{'flips':>10}{'heads':>10}{'share':>10}{'error':>10}")
print("-" * 40)
for trials in (10, 100, 1_000, 10_000, 100_000, 1_000_000):
    rng = random.Random(42)
    heads = 0
    for _ in range(trials):
        heads += rng.random() < 0.5
    share = heads / trials
    print(f"{trials:>10,}{heads:>10,}{share:>10.4f}{abs(share - 0.5):>10.4f}")

print("-" * 40)
print("100x the trials for 10x the accuracy. That is the sqrt(n) rule, and")
print("it is why real simulations run millions of iterations, not thousands.")


# ---------------------------------------------------------------------------
# 6. Real randomness CLUMPS
# ---------------------------------------------------------------------------

random.seed(3)
flips = "".join(random.choice("HT") for _ in range(100))
print(f"\n{flips}")

longest = 0
current = 1
for i in range(1, len(flips)):
    if flips[i] == flips[i - 1]:
        current += 1
        longest = max(longest, current)
    else:
        current = 1
print(f"longest run in 100 flips: {longest}")

# A run of six in 100 flips is MORE LIKELY THAN NOT. Humans asked to fake a
# random sequence produce too few long runs, which is exactly how fabricated
# data gets caught.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write `cards = random.shuffle(cards)` and then try to use cards.
#   * Use randint(0, len(items)) to index a list until it raises IndexError.
#   * Simulate the birthday problem: how many people before two share a
#     birthday? Average over 10,000 runs. It is close to 23, and almost
#     nobody believes it before they run it.
#   * Estimate pi by throwing darts at a square and counting the ones inside
#     the inscribed circle. Then work out how many darts you need for 3.14
#     reliably, and be depressed by sqrt(n).
