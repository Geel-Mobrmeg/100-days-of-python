"""Day 012 build — a number guessing game.

Higher/lower hints, attempt counting, input that cannot crash the game, and
a demonstration at the end that proves the optimal strategy is what you think
it is.

    python3 build.py
    printf '50\\n25\\n37\\n43\\n40\\n41\\n' | python3 build.py

The counting rule that catches people: THE WINNING GUESS COUNTS. If you find
it on your fourth guess, that is four attempts, not three.
"""

import random

LOW = 1
HIGH = 100
WIDTH = 56

# Ceiling of log2(100) — the number of guesses binary search always needs.
PERFECT_PLAY = 7

random.seed()          # Day 16 covers seeding; this just varies the answer
secret = random.randint(LOW, HIGH)

print("=" * WIDTH)
print(f"{'GUESS THE NUMBER':^{WIDTH}}")
print("=" * WIDTH)
print(f"I am thinking of a whole number from {LOW} to {HIGH}.")
print(f"Halving the range each time finds it in at most {PERFECT_PLAY} goes.")
print("Type 'quit' to give up.")
print()

# ---------------------------------------------------------------------------
# Loop state. All three parts of a while loop, set up before it starts.
# ---------------------------------------------------------------------------

attempts = 0
found = False
gave_up = False

# The range the player can still logically be considering. Tracking it lets
# the game notice a guess that contradicts a hint already given.
known_low = LOW
known_high = HIGH

while not found and not gave_up:
    raw = input(f"[{known_low}-{known_high}] Your guess: ").strip().lower()

    # --- the escape hatch, first: a validation loop with no way out is a trap
    if raw in ("quit", "q", "exit", ""):
        gave_up = True
        break

    # --- validate before converting (Day 6). No traceback can reach the user.
    negative = raw.startswith("-")
    digits = raw[1:] * negative or raw
    if not digits.isdigit():
        print(f"  {raw!r} is not a whole number. Try again.")
        continue          # Day 14 — skip to the next pass without counting it

    guess = int(raw)

    # --- an out-of-range guess is not an attempt, it is a typo
    if guess < LOW or guess > HIGH:
        print(f"  {guess} is outside {LOW}-{HIGH}. That one is free.")
        continue

    # --- THIS is where the attempt counts: a real, in-range, whole guess
    attempts += 1

    if guess < known_low or guess > known_high:
        print(f"  (that contradicts a hint — {guess} is already ruled out)")

    if guess == secret:
        found = True
    elif guess < secret:
        print(f"  {guess} is too LOW.")
        known_low = max(known_low, guess + 1)
    else:
        print(f"  {guess} is too HIGH.")
        known_high = min(known_high, guess - 1)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
if gave_up:
    print(f"The number was {secret}. You made {attempts} guess(es).")
else:
    print(f"Correct — the number was {secret}.")
    print(f"You found it in {attempts} guess{'es' * (attempts != 1)}.")
    print()
    print(f"{'your guesses':<32}{attempts:>22}")
    print(f"{'perfect play needs at most':<32}{PERFECT_PLAY:>22}")
    if attempts < PERFECT_PLAY:
        print(f"{'verdict':<32}{'lucky':>22}")
    elif attempts == PERFECT_PLAY:
        print(f"{'verdict':<32}{'optimal':>22}")
    else:
        wasted = attempts - PERFECT_PLAY
        print(f"{'verdict':<32}{f'{wasted} more than needed':>22}")
print("=" * WIDTH)

# ===========================================================================
# The computer plays itself — proof that the strategy is what it claims
# ===========================================================================
#
# Binary search: always guess the middle of what is still possible. Every
# guess halves the range, so 100 candidates take at most 7 guesses. This
# runs the strategy against every possible secret from 1 to 100 and reports
# the worst case — which should be exactly PERFECT_PLAY.

print()
print("=" * WIDTH)
print(f"{'BINARY SEARCH, AGAINST ALL 100 SECRETS':^{WIDTH}}")
print("=" * WIDTH)

target = LOW
worst = 0
worst_secret = LOW
total_guesses = 0

while target <= HIGH:
    lo = LOW
    hi = HIGH
    tries = 0
    while True:
        mid = (lo + hi) // 2          # // keeps it an int (Day 5)
        tries += 1
        if mid == target:
            break
        elif mid < target:
            lo = mid + 1
        else:
            hi = mid - 1
    total_guesses += tries
    if tries > worst:
        worst = tries
        worst_secret = target
    target += 1

print(f"{'secrets tested':<38}{HIGH - LOW + 1:>16}")
print(f"{'worst case':<38}{worst:>16}")
print(f"{'worst secret':<38}{worst_secret:>16}")
print(f"{'average guesses':<38}{total_guesses / (HIGH - LOW + 1):>16.2f}")
print(f"{'matches the claimed bound?':<38}{str(worst == PERFECT_PLAY):>16}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change HIGH to 1000 and PERFECT_PLAY to 10. The proof at the bottom
#     should still agree. If it does not, one of the two numbers is wrong —
#     and the code will tell you which.
#
#   * The inner `while True` in the proof has no explicit stop condition. Why
#     can it not hang? Write the argument down: it is that the range strictly
#     shrinks every pass and the target is always inside it. That argument is
#     what you should be able to make about EVERY while loop you write.
#
#   * Add a hint after three failed guesses: "it is even", or "it is a
#     multiple of 7". You have % from Day 5.
#
#   * Give the player a fixed budget of guesses and a score. Then, on Day 21,
#     keep a list of past guesses and refuse to accept a repeat.
