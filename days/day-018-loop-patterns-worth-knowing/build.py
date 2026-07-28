"""Day 018 build — mean, median, mode, min and max, from scratch.

No imports. Not even `sorted`, for the median — the sort is written by hand,
because "compute the median" turns out to be mostly "get the data in order",
and that is worth feeling once.

In real code use `statistics.median()`. Writing it yourself once is how you
learn what it costs and where it breaks.

    python3 build.py
    python3 build.py 3 1 4 1 5 9 2 6 5 3 5
    python3 build.py 1 2 3 4          # even length — median is between values
    python3 build.py 7                # one value
"""

import sys

WIDTH = 62

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

if len(sys.argv) > 1:
    data = []
    for arg in sys.argv[1:]:
        clean = arg.replace("-", "", 1).replace(".", "", 1)
        if clean.isdigit():
            data.append(float(arg) if "." in arg else int(arg))

print("=" * WIDTH)
print(f"{'STATISTICS FROM SCRATCH':^{WIDTH}}")
print("=" * WIDTH)
print(f"data: {data}")
print(f"n:    {len(data)}")

# ---------------------------------------------------------------------------
# THE EMPTY CASE, decided in writing before any code runs.
#
#   count    0        — the only statistic that is defined
#   sum      0        — the identity for addition
#   mean     undefined, division by zero. Report "-", do not invent 0.
#   min/max  undefined. There is no smallest element of nothing.
#   median   undefined.
#   mode     undefined.
#
# Inventing 0 for the mean of no data is the kind of quiet lie that ends up
# in a report. Say "no data" instead.
# ---------------------------------------------------------------------------

if not data:
    print("\nNo data. count = 0, sum = 0, everything else is undefined.")
    sys.exit(0)

# ===========================================================================
# 1. SINGLE PASS — count, sum, min, max, mean, and the positions of extrema
# ===========================================================================
#
# Everything in this block is computable while the data goes past ONCE, which
# means it would still work on a 500 MB file or a live sensor feed.

count = 0
total = 0
lowest = data[0]          # start with a REAL value, not 0
highest = data[0]
lowest_at = 0
highest_at = 0

for i, n in enumerate(data):
    count += 1
    total += n
    if n < lowest:        # `<` keeps the FIRST minimum on a tie
        lowest = n
        lowest_at = i
    if n > highest:       # `>` keeps the FIRST maximum on a tie
        highest = n
        highest_at = i

mean = total / count

print()
print("-" * WIDTH)
print("SINGLE PASS  (works on data too big to hold in memory)")
print("-" * WIDTH)
print(f"{'count':<26}{count:>34}")
print(f"{'sum':<26}{total:>34}")
print(f"{'min':<26}{lowest:>34}")
print(f"{'  first found at index':<26}{lowest_at:>34}")
print(f"{'max':<26}{highest:>34}")
print(f"{'  first found at index':<26}{highest_at:>34}")
print(f"{'range (max - min)':<26}{highest - lowest:>34}")
print(f"{'mean':<26}{mean:>34.4f}")

# ===========================================================================
# 2. SORTING — needed for the median, and impossible in a single pass
# ===========================================================================
#
# Insertion sort: take each item and slide it left until it is in place.
# O(n^2), which is fine here and disastrous at scale — Day 27 hands you
# Timsort, which is O(n log n) and written by people who did this properly.

ordered = data[:]          # a COPY. Never reorder the caller's data.
comparisons = 0

for i in range(1, len(ordered)):
    current = ordered[i]
    j = i - 1
    while j >= 0 and ordered[j] > current:
        comparisons += 1
        ordered[j + 1] = ordered[j]
        j -= 1
    if j >= 0:
        comparisons += 1
    ordered[j + 1] = current

print()
print("-" * WIDTH)
print("SORTED  (needs every value before it can answer anything)")
print("-" * WIDTH)
print(f"sorted: {ordered}")
print(f"{'comparisons made':<26}{comparisons:>34}")
print(f"{'matches sorted()?':<26}{str(ordered == sorted(data)):>34}")

# ===========================================================================
# 3. MEDIAN — the middle value, with the even case decided explicitly
# ===========================================================================
#
# Odd length:  one middle element.
# Even length: conventionally the MEAN OF THE TWO middle elements — which
#              means the median of a list of integers can be a non-integer,
#              and can be a value that does not appear in the data at all.
#              That surprises people. It is still the convention.

middle = count // 2
if count % 2 == 1:
    median = ordered[middle]
    median_note = f"the single middle value, at index {middle}"
else:
    low_mid = ordered[middle - 1]
    high_mid = ordered[middle]
    median = (low_mid + high_mid) / 2
    median_note = f"mean of {low_mid} and {high_mid} (indices {middle - 1}, {middle})"

print()
print("-" * WIDTH)
print("MEDIAN")
print("-" * WIDTH)
print(f"{'median':<26}{median:>34}")
print(f"{'why':<26}{median_note:>34}")
print(f"{'in the data?':<26}{str(median in data):>34}")

# ===========================================================================
# 4. MODE — the most common value, and what to do about ties
# ===========================================================================
#
# Counting without a dict (Day 25 does this in two lines with Counter).
# The sorted list makes it a single pass: equal values are adjacent.

best_count = 0
modes = []
run_value = ordered[0]
run_length = 0

for n in ordered + [None]:          # a sentinel to flush the final run
    if n == run_value:
        run_length += 1
        continue
    if run_length > best_count:
        best_count = run_length
        modes = [run_value]
    elif run_length == best_count:
        modes.append(run_value)
    run_value = n
    run_length = 1

print()
print("-" * WIDTH)
print("MODE")
print("-" * WIDTH)
print(f"{'most common value(s)':<26}{str(modes):>34}")
print(f"{'occurring':<26}{f'{best_count} time(s)':>34}")
print(f"{'unique mode?':<26}{str(len(modes) == 1):>34}")

if len(modes) > 1:
    print()
    print("A tie has no single right answer. This build returns ALL of them,")
    print("like statistics.multimode(). statistics.mode() returns the first.")
    print("Either is defensible. Not deciding is not.")

# ===========================================================================
# 5. WHY THERE ARE THREE AVERAGES
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'THE THREE AVERAGES':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'mean':<12}{mean:>16.4f}   shared out equally")
print(f"{'median':<12}{median:>16}   the middle one")
print(f"{'mode':<12}{str(modes):>16}   the most common")
print()

# The demonstration that matters: add one outlier and watch what moves.
outlier = highest * 1000
with_outlier = data + [outlier]
mean_after = sum(with_outlier) / len(with_outlier)

ordered_after = sorted(with_outlier)
m = len(ordered_after) // 2
if len(ordered_after) % 2:
    median_after = ordered_after[m]
else:
    median_after = (ordered_after[m - 1] + ordered_after[m]) / 2

print(f"Now add a single outlier of {outlier}:")
print("-" * WIDTH)
print(f"{'':<12}{'before':>16}{'after':>16}{'moved by':>16}")
print(f"{'mean':<12}{mean:>16.2f}{mean_after:>16.2f}"
      f"{mean_after - mean:>16.2f}")
print(f"{'median':<12}{median:>16.2f}{median_after:>16.2f}"
      f"{median_after - median:>16.2f}")
print("-" * WIDTH)
print("One value dragged the mean across the room and barely touched the")
print("median. That is why incomes and house prices are reported as medians,")
print("and why a mean with no median beside it is often a rhetorical choice.")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run with no arguments that parse, e.g. `python3 build.py x y`. The
#     empty-data path should trigger. Check it says "undefined" rather than
#     printing a confident 0.
#
#   * Run `python3 build.py 1 2 3 4`. The median is 2.5 — a value that does
#     not appear in the data. Confirm the "in the data?" line says False.
#
#   * Run `python3 build.py 1 1 2 2`. Two modes. Confirm both are reported.
#
#   * The insertion sort is O(n^2). Feed it 2,000 numbers and time it, then
#     compare with sorted(). Day 27 explains the difference; today just see
#     it.
#
#   * Add the standard deviation. It needs the mean first, so it is a SECOND
#     pass — unless you accumulate the sum of squares as you go. Look up
#     Welford's algorithm and note that it exists precisely because of the
#     single-pass constraint from this lesson.
