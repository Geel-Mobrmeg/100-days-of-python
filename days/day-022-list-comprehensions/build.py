"""Day 022 build — ten loops rewritten as comprehensions, and two rewritten back.

Every pair below is checked: the loop version and the comprehension version
must produce identical results, or the build says so. A "refactor" that
changes behaviour is not a refactor (Day 8).

The last two are the point of the day. They are the ones where the
comprehension is WORSE, and being able to say why is the skill.

    python3 build.py
"""

WIDTH = 74

PEOPLE = [
    "  Ada Lovelace , 36 , engineer  ",
    "Charles Babbage,79,mathematician",
    "  Alan Turing ,41,  logician",
    "Grace Hopper, 85 ,rear admiral",
    "Katherine Johnson,101,physicist",
]
NUMBERS = [3, -1, 4, -1, 5, 9, -2, 6, 5, 3, -5]
GRID = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
WORDS = "the quick brown fox jumps over the lazy dog the end".split()

results = []


def check(n, name, loop_result, comp_result, note=""):
    """Record and print a before/after pair."""
    same = loop_result == comp_result
    results.append(same)
    print(f"\n{n:>2}. {name}")
    print(f"    {str(comp_result)[:66]}")
    print(f"    identical to the loop version: {same}{note}")


print("=" * WIDTH)
print(f"{'TEN LOOPS, REWRITTEN':^{WIDTH}}")
print("=" * WIDTH)

# ---------------------------------------------------------------------- 1
loop = []
for n in NUMBERS:
    loop.append(n * n)

comp = [n * n for n in NUMBERS]
check(1, "MAP: square everything", loop, comp)

# ---------------------------------------------------------------------- 2
loop = []
for n in NUMBERS:
    if n > 0:
        loop.append(n)

comp = [n for n in NUMBERS if n > 0]
check(2, "FILTER: keep positives  (`if` at the END)", loop, comp)

# ---------------------------------------------------------------------- 3
loop = []
for n in NUMBERS:
    if n > 0:
        loop.append(n)
    else:
        loop.append(0)

comp = [n if n > 0 else 0 for n in NUMBERS]
check(3, "TRANSFORM: clamp negatives  (`if/else` at the FRONT)", loop, comp,
      "  <- note: 11 items, not 7")

# ---------------------------------------------------------------------- 4
loop = []
for row in GRID:
    for cell in row:
        loop.append(cell)

comp = [cell for row in GRID for cell in row]
check(4, "NESTED: flatten a grid  (outer clause first)", loop, comp)

# ---------------------------------------------------------------------- 5
loop = []
for row in GRID:
    doubled = []
    for cell in row:
        doubled.append(cell * 2)
    loop.append(doubled)

comp = [[cell * 2 for cell in row] for row in GRID]
check(5, "NESTED OUTPUT: double every cell, keep the shape", loop, comp)

# ---------------------------------------------------------------------- 6
loop = []
for record in PEOPLE:
    loop.append(record.split(",")[0].strip())

comp = [r.split(",")[0].strip() for r in PEOPLE]
check(6, "PARSE: pull the name out of each record", loop, comp)

# ---------------------------------------------------------------------- 7
loop = []
for record in PEOPLE:
    parts = record.split(",")
    age = int(parts[1].strip())
    if age < 80:
        loop.append((parts[0].strip(), age))

comp = [
    (r.split(",")[0].strip(), int(r.split(",")[1]))
    for r in PEOPLE
    if int(r.split(",")[1]) < 80
]
check(7, "PARSE + FILTER: name and age, under 80", loop, comp)

print("    ^ note this one splits THREE TIMES per record. The loop split")
print("      once and reused it. That is a real cost the one-liner hides.")

# ---------------------------------------------------------------------- 8
loop = []
for word in WORDS:
    if word not in loop:
        loop.append(word)

comp = list(dict.fromkeys(WORDS))          # order-preserving dedupe
check(8, "DEDUPE, keeping order  (not a comprehension at all)", loop, comp)

print("    ^ the loop is O(n^2) — `not in loop` scans every time. The dict")
print("      version is O(n). Sometimes the answer is a different TOOL,")
print("      not a different syntax. Day 26.")

# ---------------------------------------------------------------------- 9
loop = 0
for n in NUMBERS:
    if n > 0:
        loop += n

comp = sum(n for n in NUMBERS if n > 0)
check(9, "AGGREGATE: sum the positives  (generator, no list built)", loop, comp)

# --------------------------------------------------------------------- 10
loop = []
for i, word in enumerate(WORDS, start=1):
    if len(word) > 3:
        loop.append(f"{i}:{word.upper()}")

comp = [f"{i}:{w.upper()}" for i, w in enumerate(WORDS, start=1) if len(w) > 3]
check(10, "ENUMERATE + FILTER + FORMAT", loop, comp)

print()
print("=" * WIDTH)
print(f"{'all ten pairs identical':<50}{str(all(results)):>{WIDTH - 50}}")
print("=" * WIDTH)

# ===========================================================================
# AND NOW THE TWO THAT GO BACK
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'TWO REWRITTEN BACK TO LOOPS, AND WHY':^{WIDTH}}")
print("=" * WIDTH)

# --------------------------------------------------------------------- A
print("""
A. THE ONE THAT DOES MORE THAN ONE THING

   As a comprehension it cannot report progress, cannot count what it
   skipped, and cannot log a bad record — because a comprehension produces
   a value and nothing else. The moment you need a second outcome, the
   one-liner has to become a loop, or you need a second pass over the data
   to compute the thing you already knew.
""")

parsed = []
skipped = 0
for record in PEOPLE:
    parts = record.split(",")
    if len(parts) != 3:
        skipped += 1
        continue
    name = parts[0].strip()
    age_text = parts[1].strip()
    if not age_text.isdigit():
        skipped += 1
        print(f"   warning: bad age {age_text!r} for {name!r}")
        continue
    parsed.append((name, int(age_text), parts[2].strip()))

print(f"   parsed {len(parsed)}, skipped {skipped}")
for name, age, role in parsed[:3]:
    print(f"     {name:<20}{age:>4}  {role}")

# --------------------------------------------------------------------- B
print("""
B. THE ONE THAT NEEDS TO STOP EARLY

   A comprehension always visits every item. To find the FIRST match in a
   million-row file, it does a million units of work to answer a question
   settled at row three (Day 14).
""")

BIG = list(range(1_000_000))

checked = 0
first = None
for n in BIG:
    checked += 1
    if n > 2:
        first = n
        break
print(f"   loop with break:      found {first} after {checked:,} checks")

comp_result = [n for n in BIG if n > 2][0]
print(f"   comprehension:        found {comp_result} after {len(BIG):,} checks")

lazy = next(n for n in BIG if n > 2)
print(f"   next() + generator:   found {lazy} lazily — the one-line `break`")

print("""
   `next(x for x in items if cond)` is the comprehension world's `break`,
   and it is the right answer when you want one line AND early exit. Add a
   default — next(..., None) — or it raises StopIteration on no match.
""")

print("=" * WIDTH)
print("""RULE OF THUMB

   comprehension   one input, one output, one clear expression
   loop            side effects, early exit, >2 clauses, or a line that
                   does not fit

   The honest test: IF YOU HAD TO READ IT TWICE, WRITE THE LOOP.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Number 7 splits each record three times. Fix it without a loop.
#     (Hint: a nested comprehension that names the split once —
#      [ ... for r in PEOPLE for parts in [r.split(",")] if ... ]. Then
#      decide whether that is better or worse than the loop, honestly.)
#
#   * Number 8's loop is O(n^2). Feed it 20,000 words and time both versions.
#
#   * Take pair A and try to write it as a comprehension anyway. You will
#     need two passes over PEOPLE — one for the good rows, one to count the
#     bad ones. Compare that to the single loop.
#
#   * Write a comprehension you cannot read tomorrow. Then rewrite it. That
#     exercise is the whole day.
