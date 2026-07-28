"""Day 016 build — a dice simulator with text histograms.

    python3 build.py                # 10,000 rolls, unseeded
    python3 build.py 1000000        # a million rolls
    python3 build.py 10000 42       # seeded — byte-identical every run

The interesting result is not that a d6 is flat. It is that 2d6 is a
TRIANGLE, and that the triangle appears out of nothing but counting. Nobody
programmed the peak at 7 — it is a consequence of there being six ways to
make 7 and one way to make 2.
"""

import random
import sys

WIDTH = 74
BAR = 40

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

trials = 10_000
seed = None

if len(sys.argv) >= 2 and sys.argv[1].isdigit():
    trials = max(1, min(int(sys.argv[1]), 5_000_000))
if len(sys.argv) >= 3 and sys.argv[2].isdigit():
    seed = int(sys.argv[2])

# A PRIVATE generator, so nothing else in the process can disturb it and so
# that seeding here cannot leak into other code.
rng = random.Random(seed)

print("=" * WIDTH)
print(f"{'DICE SIMULATOR':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'rolls per experiment':<40}{trials:>34,}")
print(f"{'seed':<40}{str(seed) if seed is not None else 'none (varies)':>34}")
print("=" * WIDTH)


def histogram(counts, low, title, expected=None):
    """Print a labelled bar chart from a list of counts starting at `low`."""
    total = sum(counts)
    peak = max(counts) or 1

    print()
    print(title)
    print("-" * WIDTH)
    print(f"{'face':>5}{'count':>10}{'share':>9}{'expect':>9}  {'':<{BAR}}")

    for offset, count in enumerate(counts):
        value = low + offset
        share = count / total
        bar = "#" * int(count / peak * BAR)
        want = f"{expected[offset]:>8.2%}" if expected else " " * 8
        print(f"{value:>5}{count:>10,}{share:>9.2%}{want}  {bar:<{BAR}}")

    print("-" * WIDTH)
    print(f"{'total':>5}{total:>10,}")


# ===========================================================================
# 1. One die — flat, and a useful lesson in what "flat" looks like
# ===========================================================================

counts_1d6 = [0] * 6
for _ in range(trials):
    counts_1d6[rng.randint(1, 6) - 1] += 1

histogram(counts_1d6, 1, "ONE d6 — every face equally likely", [1 / 6] * 6)

spread = max(counts_1d6) - min(counts_1d6)
print(f"{'gap between most and least common':<52}{spread:>22,}")
print(f"{'as a share of all rolls':<52}{spread / trials:>22.2%}")
print()
print("The bars are NOT identical, and they never will be. That wobble is")
print("what fair randomness looks like; it shrinks as sqrt(n), so raise the")
print("roll count tenfold and the gap only falls by about three.")

# ===========================================================================
# 2. Two dice — where the shape comes from nowhere
# ===========================================================================

# There are 36 equally likely ordered outcomes. The number of ways to make
# each total is 1,2,3,4,5,6,5,4,3,2,1 — which is the triangle.
WAYS = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
expected_2d6 = [w / 36 for w in WAYS]

counts_2d6 = [0] * 11
for _ in range(trials):
    total = rng.randint(1, 6) + rng.randint(1, 6)
    counts_2d6[total - 2] += 1

histogram(counts_2d6, 2, "TWO d6, SUMMED — the triangle", expected_2d6)

print()
print("Nobody programmed that peak. There are six ways to roll a 7 and one")
print("way to roll a 2, so 7 turns up six times as often. This is why board")
print("games use 2d6: it gives a most-likely outcome and rare extremes.")

# ===========================================================================
# 3. Three dice — the triangle becomes a bell
# ===========================================================================

counts_3d6 = [0] * 16
for _ in range(trials):
    total = rng.randint(1, 6) + rng.randint(1, 6) + rng.randint(1, 6)
    counts_3d6[total - 3] += 1

histogram(counts_3d6, 3, "THREE d6, SUMMED — the bell appears")

print()
print("Add more dice and the shape converges on the normal distribution.")
print("That is the Central Limit Theorem, arriving unannounced in a dice")
print("program, which is the most persuasive way to meet it.")

# ===========================================================================
# 4. A fairness check on the d6
# ===========================================================================
#
# Chi-squared: sum over faces of (observed - expected)^2 / expected. For a
# fair d6 (5 degrees of freedom) a value above 11.07 would happen by chance
# less than 5% of the time — so a big number is evidence of a loaded die.

expected_each = trials / 6
chi_squared = sum((c - expected_each) ** 2 / expected_each for c in counts_1d6)

print()
print("=" * WIDTH)
print(f"{'IS THE DIE FAIR?':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'chi-squared statistic':<52}{chi_squared:>22.3f}")
print(f"{'5% critical value (5 d.o.f.)':<52}{11.07:>22.3f}")
print(f"{'looks fair?':<52}{str(chi_squared < 11.07):>22}")
print()
print("A fair die exceeds 11.07 about one run in twenty, so a single high")
print("value proves nothing. Run it again — that is the whole discipline.")

# ===========================================================================
# 5. A loaded die, for contrast
# ===========================================================================

loaded_counts = [0] * 6
loaded_rolls = rng.choices(
    [1, 2, 3, 4, 5, 6], weights=[1, 1, 1, 1, 1, 2], k=trials
)
for roll in loaded_rolls:
    loaded_counts[roll - 1] += 1

histogram(loaded_counts, 1, "A LOADED d6 — six is twice as likely")

loaded_chi = sum((c - expected_each) ** 2 / expected_each for c in loaded_counts)
print(f"{'chi-squared':<52}{loaded_chi:>22.3f}")
print(f"{'looks fair?':<52}{str(loaded_chi < 11.07):>22}")
print()
print("The test catches it easily at 10,000 rolls. Try 100 rolls and it may")
print("not — which is the practical meaning of 'small samples lie'.")

# ===========================================================================
# 6. Reproducibility
# ===========================================================================

print("=" * WIDTH)
if seed is None:
    print("This run was UNSEEDED, so it will differ next time.")
    print(f"Run `python3 build.py {trials} 42` twice and diff the output:")
    print("it will be byte-identical, on any machine, forever.")
else:
    a = random.Random(seed)
    b = random.Random(seed)
    same = [a.randint(1, 6) for _ in range(10)] == [
        b.randint(1, 6) for _ in range(10)
    ]
    print(f"Seeded with {seed}. Two fresh generators agree: {same}")
    print("Every number above is reproducible. That is what makes a")
    print("simulation a result rather than an anecdote.")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 build.py 10000 42 > a.txt` twice and diff. Empty diff.
#     Then run it unseeded twice and diff. That difference is the whole point
#     of seeding.
#
#   * Run with 100 rolls, then 1,000,000. Watch the d6 bars flatten and the
#     chi-squared value stay in the same range — it does not grow with n,
#     which is what makes it a fair test at any sample size.
#
#   * Add "advantage": roll two d6 and keep the higher. Predict the shape
#     before you plot it. (It is not symmetric.)
#
#   * Simulate the Monty Hall problem here: 100,000 games each way. Switching
#     wins 2/3 of the time. Nobody believes it until they run it, including
#     several very famous mathematicians who wrote in to say so.
