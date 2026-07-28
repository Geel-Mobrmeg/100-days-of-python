"""Day 027 build — a leaderboard: score DESC, then time ASC, then name ASC.

That requirement is deliberately awkward, because the directions are mixed.
A single tuple key with reverse=True cannot express it, and finding that out
is the point.

Both correct techniques are implemented, and the build asserts they agree.

    python3 build.py
"""

from operator import itemgetter

WIDTH = 74

# ---------------------------------------------------------------------------
# The data. Ties are deliberate and they are where all the interest is:
#
#   * Turing and Hopper both scored 950  -> the time must break the tie
#   * Lovelace and Liskov both scored 875 with the SAME time
#                                        -> the name must break that
#   * Borg has no time recorded (None)   -> must not crash the sort
# ---------------------------------------------------------------------------

PLAYERS = [
    {"name": "Hopper",    "score": 950, "time": 214.5},
    {"name": "Turing",    "score": 950, "time": 187.2},
    {"name": "Liskov",    "score": 875, "time": 201.0},
    {"name": "Lovelace",  "score": 875, "time": 201.0},
    {"name": "Johnson",   "score": 875, "time": 190.8},
    {"name": "Babbage",   "score": 640, "time": 301.4},
    {"name": "Borg",      "score": 640, "time": None},
    {"name": "Antonelli", "score": 640, "time": 288.1},
]


def show(title, rows):
    print()
    print("=" * WIDTH)
    print(f"{title:^{WIDTH}}")
    print("=" * WIDTH)
    print(f"{'#':>3}  {'NAME':<14}{'SCORE':>8}{'TIME':>10}   {'':<30}")
    print("-" * WIDTH)
    best = max(r["score"] for r in rows) or 1
    for rank, row in enumerate(rows, start=1):
        time_text = f"{row['time']:.1f}" if row["time"] is not None else "  --"
        bar = "#" * int(row["score"] / best * 26)
        print(f"{rank:>3}. {row['name']:<14}{row['score']:>8}"
              f"{time_text:>10}   {bar:<30}")


# ===========================================================================
# THE WRONG WAYS, first — because seeing them fail is the lesson
# ===========================================================================

# WRONG 1: sort by score only. The 950s and 875s come out in input order,
# which is not random and is not the tie-break anybody asked for.
wrong_1 = sorted(PLAYERS, key=itemgetter("score"), reverse=True)
show("WRONG 1 — score only (ties fall back to input order)", wrong_1)
print("  Turing and Hopper both have 950. Hopper is first only because she")
print("  appears first in the source data. That is stability doing exactly")
print("  what it promises — and it is not the requirement.")

# WRONG 2: a tuple key with reverse=True. Now the TIME is descending too,
# so the slowest player wins the tie-break. Backwards.
wrong_2 = sorted(
    [p for p in PLAYERS if p["time"] is not None],
    key=itemgetter("score", "time"),
    reverse=True,
)
show("WRONG 2 — tuple key + reverse=True (reverses EVERY level)", wrong_2)
print("  Among the 950s, Hopper (214.5s) now beats Turing (187.2s). The")
print("  slower player is winning, because reverse=True reversed the time")
print("  as well as the score. One flag cannot express two directions.")

# ===========================================================================
# THE TWO CORRECT WAYS
# ===========================================================================

# A missing time should not win a tie and must not crash the comparison.
# `t is None` is a bool; False sorts before True, so real times come first.
NO_TIME = float("inf")


def sort_key(row):
    """score DESC (negated), time ASC (missing last), name ASC."""
    time = row["time"]
    return (-row["score"], time if time is not None else NO_TIME, row["name"])


# TECHNIQUE A — one pass, negating the number that goes the other way.
by_tuple = sorted(PLAYERS, key=sort_key)

# TECHNIQUE B — successive stable sorts, LEAST significant first.
# This one needs no negation, so it works for fields you cannot negate:
# strings, dates, anything.
by_passes = PLAYERS.copy()
by_passes.sort(key=itemgetter("name"))                                  # 3rd
by_passes.sort(key=lambda r: r["time"] if r["time"] is not None else NO_TIME)  # 2nd
by_passes.sort(key=itemgetter("score"), reverse=True)                   # 1st

show("CORRECT — score DESC, time ASC, name ASC", by_tuple)

print()
print("-" * WIDTH)
print(f"{'technique A (negated tuple key) == technique B (three passes)':<58}"
      f"{str(by_tuple == by_passes):>{WIDTH - 58}}")
print("-" * WIDTH)

# ---------------------------------------------------------------------------
# Prove each tie-break actually fired
# ---------------------------------------------------------------------------

order = [p["name"] for p in by_tuple]

checks = [
    ("score beats everything: 950s first",
     order[:2] == ["Turing", "Hopper"] or order[:2] == ["Hopper", "Turing"]),
    ("Turing (187.2s) beats Hopper (214.5s) on TIME",
     order.index("Turing") < order.index("Hopper")),
    ("Johnson (190.8s) leads the 875s on TIME",
     order.index("Johnson") < order.index("Liskov")),
    ("Liskov before Lovelace — same score AND time, so NAME decides",
     order.index("Liskov") < order.index("Lovelace")),
    ("Borg (no time) sinks below Antonelli and Babbage",
     order.index("Borg") > order.index("Antonelli")),
    ("no row was lost", len(by_tuple) == len(PLAYERS)),
]

print()
print("=" * WIDTH)
print(f"{'DID EACH TIE-BREAK FIRE?':^{WIDTH}}")
print("=" * WIDTH)
for label, ok in checks:
    print(f"  {label:<62}{str(ok):>8}")
print("-" * WIDTH)
print(f"  {'all tie-breaks correct':<62}{str(all(ok for _, ok in checks)):>8}")
print("=" * WIDTH)

# ---------------------------------------------------------------------------
# Which technique to use
# ---------------------------------------------------------------------------

print("""
WHICH TECHNIQUE?

  Negated tuple key      one pass, one expression, and the whole ordering
                         is visible in a single place. ONLY WORKS ON
                         NUMBERS — you cannot negate a name or a date.

  Successive sorts       works for ANY mix of directions and types. Costs
                         one pass per key, and the passes read backwards
                         (least significant first), which needs a comment.

Reach for the tuple key when every descending field is numeric. Reach for
successive sorts the moment one is not — for example "newest first, then
name A-Z", where the date cannot be negated.

A third option exists for the hard cases: give the objects an ordering of
their own with __lt__ and functools.total_ordering. That is Day 44.""")

# ---------------------------------------------------------------------------
# Ranking with ties — a different question from sorting
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'COMPETITION RANKING (equal scores share a rank)':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'RANK':>5}  {'NAME':<14}{'SCORE':>8}{'TIME':>10}")
print("-" * WIDTH)

rank = 0
previous_score = None
for i, row in enumerate(by_tuple, start=1):
    if row["score"] != previous_score:
        rank = i                       # 1224 ranking: skip after a tie
        previous_score = row["score"]
    time_text = f"{row['time']:.1f}" if row["time"] is not None else "  --"
    print(f"{rank:>5}  {row['name']:<14}{row['score']:>8}{time_text:>10}")
print("=" * WIDTH)
print("Note the ranks skip after a tie (1,1,3) — 'standard competition")
print("ranking'. Dense ranking would give 1,1,2. Sorting is one question;")
print("assigning ranks is a second one, and it needs deciding separately.")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change the requirement to "newest first, then name A-Z" with a date
#     field. The negated tuple key stops working immediately — you cannot
#     negate a date — and technique B carries on unchanged.
#
#   * Borg's missing time currently sinks to the bottom of her score group.
#     Should a missing time instead be treated as "not yet ranked" and
#     excluded? Decide, write it down, then implement it.
#
#   * Implement DENSE ranking (1,1,2) alongside the competition ranking, and
#     print both columns.
#
#   * Add 100,000 players and time sorted() against heapq.nlargest(10) with
#     the same key. For a top-10 board you never needed the full sort.
