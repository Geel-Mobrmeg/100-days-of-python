"""Day 026 build — a duplicate finder and a tag comparison.

    python3 build.py

Two jobs that look similar and are not:

  DUPLICATES   needs COUNTS, so a set alone cannot do it. A set knows what
               is present, never how many times. Counter does the counting;
               the set does the "which ones repeat" in one expression.

  COMPARISON   is pure set algebra. Four operators answer every question
               anyone asks about two collections, and each replaces a
               nested loop.
"""

from collections import Counter

WIDTH = 72

# ===========================================================================
# PART 1 — DUPLICATES
# ===========================================================================

EMAILS = [
    "ada@example.com", "alan@example.com", "grace@example.com",
    "ada@example.com", "katherine@example.com", "alan@example.com",
    "ada@example.com", "bjarne@example.com", "grace@example.com",
]

print("=" * WIDTH)
print(f"{'DUPLICATE FINDER':^{WIDTH}}")
print("=" * WIDTH)

unique = set(EMAILS)
counts = Counter(EMAILS)

# The one-expression version of "which ones repeat":
duplicates = {item for item, n in counts.items() if n > 1}

print(f"{'entries':<32}{len(EMAILS):>{WIDTH - 32}}")
print(f"{'distinct':<32}{len(unique):>{WIDTH - 32}}")
print(f"{'duplicated values':<32}{len(duplicates):>{WIDTH - 32}}")
print(f"{'redundant entries':<32}{len(EMAILS) - len(unique):>{WIDTH - 32}}")

print()
print("-" * WIDTH)
print(f"{'VALUE':<40}{'TIMES':>8}{'EXTRA':>10}")
print("-" * WIDTH)
for value, n in counts.most_common():
    if n > 1:
        print(f"{value:<40}{n:>8}{n - 1:>10}")
print("-" * WIDTH)

# WHY A SET IS NOT ENOUGH ON ITS OWN:
print(f"""
A set can tell you THAT there were duplicates:

    len(EMAILS) != len(set(EMAILS))     ->  {len(EMAILS) != len(unique)}

but never HOW MANY, because a set holds each value exactly once by
definition. The counts come from Counter (Day 25); the set comprehension
above just picks out the values whose count is above one.""")

# Order-preserving deduplication, since a set throws order away:
first_seen = list(dict.fromkeys(EMAILS))
print(f"""
Deduplicated, keeping first-seen order:
  {chr(10).join('    ' + e for e in first_seen)}

  set(EMAILS) would give the same VALUES in an arbitrary order.""")

# ===========================================================================
# PART 2 — COMPARING TWO COLLECTIONS
# ===========================================================================

ada = {"python", "sql", "git", "linux", "maths", "assembly"}
alan = {"python", "git", "maths", "logic", "cryptography"}

print()
print("=" * WIDTH)
print(f"{'TAG COMPARISON':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'ada':<10}{', '.join(sorted(ada))}")
print(f"{'alan':<10}{', '.join(sorted(alan))}")
print()

comparisons = [
    ("in both", "ada & alan", ada & alan,
     "the overlap — 'who has both?'"),
    ("ada only", "ada - alan", ada - alan,
     "what alan is missing — 'what is the gap?'"),
    ("alan only", "alan - ada", alan - ada,
     "what ada is missing — note it is NOT symmetric"),
    ("in one only", "ada ^ alan", ada ^ alan,
     "everything not shared — 'what differs?'"),
    ("in either", "ada | alan", ada | alan,
     "the combined vocabulary"),
]

print(f"{'QUESTION':<14}{'OPERATOR':<14}{'RESULT':<44}")
print("-" * WIDTH)
for label, op, result, _ in comparisons:
    print(f"{label:<14}{op:<14}{', '.join(sorted(result))[:42]:<44}")

print("-" * WIDTH)
for label, op, result, why in comparisons:
    print(f"  {op:<14}{why}")

print()
print(f"{'ada is a superset of alan?':<40}{str(ada >= alan):>{WIDTH - 40}}")
print(f"{'any overlap at all?':<40}{str(not ada.isdisjoint(alan)):>{WIDTH - 40}}")
print(f"{'overlap as a share of the union':<40}"
      f"{len(ada & alan) / len(ada | alan):>{WIDTH - 40}.1%}")

# That last figure is the Jaccard index — the standard measure of how alike
# two sets are, and it is one expression.

# ===========================================================================
# PART 3 — THREE-WAY, WHICH IS WHERE LOOPS REALLY GIVE UP
# ===========================================================================

grace = {"cobol", "compilers", "maths", "linux", "navy"}

print()
print("=" * WIDTH)
print(f"{'THREE-WAY':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'grace':<10}{', '.join(sorted(grace))}")
print()

everyone = ada & alan & grace
anyone = ada | alan | grace
only_ada = ada - alan - grace

print(f"{'known by all three':<40}"
      f"{', '.join(sorted(everyone)) or '(none)':>{WIDTH - 40}}")
print(f"{'known by at least one':<40}{len(anyone):>{WIDTH - 40}}")
print(f"{'unique to ada':<40}"
      f"{', '.join(sorted(only_ada)):>{WIDTH - 40}}")

# Exactly-one-of-three is NOT a ^ b ^ c — that gives things in an odd number
# of sets, so something in all three would be included. Say what you mean:
exactly_one = (
    (ada - alan - grace) | (alan - ada - grace) | (grace - ada - alan)
)
print(f"{'known by exactly one person':<40}{len(exactly_one):>{WIDTH - 40}}")
print(f"{'  a ^ b ^ c would give':<40}{len(ada ^ alan ^ grace):>{WIDTH - 40}}")
print()
print("  Those two differ whenever something is in ALL THREE sets: ^ counts")
print("  membership in an ODD number of sets, which is three as well as one.")
print("  A classic subtle bug. Write what you mean, not what is shortest.")

# A membership grid, which is the readable way to present all of this:
print()
print("-" * WIDTH)
print(f"{'SKILL':<18}{'ada':>7}{'alan':>7}{'grace':>7}{'COUNT':>8}")
print("-" * WIDTH)
for skill in sorted(anyone):
    marks = [skill in ada, skill in alan, skill in grace]
    row = "".join(f"{('x' if m else '-'):>7}" for m in marks)
    print(f"{skill:<18}{row}{sum(marks):>8}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Write the "in both" calculation as a nested loop over two lists and
#     count the comparisons. Then do it at 10,000 skills each and time both.
#     The set version does not get noticeably slower; the loop does.
#
#   * `ada - alan` and `alan - ada` are different answers. Find a real
#     question where reversing them would be a serious bug (hint: "which
#     permissions must I GRANT" versus "which must I REVOKE").
#
#   * Add a fourth person and see which parts of this file needed changing.
#     The set expressions did not; only the presentation did.
#
#   * Use frozenset to group people by their EXACT skill set, so two people
#     with identical skills land together regardless of order.
#
#   * The duplicate finder reports duplicate VALUES. Extend it to find
#     near-duplicates — emails differing only in case or surrounding space.
#     Normalise before building the set, and notice that the choice of
#     normalisation IS the definition of "duplicate".
