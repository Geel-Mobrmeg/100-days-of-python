"""Day 012 — while loops.

    python3 lesson.py

Nothing in this file hangs. The infinite loops are all in comments, and you
should uncomment them one at a time and press Ctrl-C.
"""

# ---------------------------------------------------------------------------
# 1. Every while loop has exactly three parts
# ---------------------------------------------------------------------------

count = 0                 # 1. SETUP     — exists, and has a starting value
while count < 5:          # 2. CONDITION — checked BEFORE every pass
    print(count, end=" ")
    count += 1            # 3. PROGRESS  — changes what the condition tests
print()

# Miss the setup  -> NameError.
# Miss the progress -> it never ends.
# That is the entire failure surface. Check all three, every time, until it
# is automatic.

# The condition is checked BEFORE the first pass, so a loop can run zero times:
n = 10
while n < 5:
    print("this never prints")
print("a while loop can run zero times")


# ---------------------------------------------------------------------------
# 2. The three ways a loop fails to end
# ---------------------------------------------------------------------------
#
# Uncomment ONE at a time and press Ctrl-C to stop it.
#
#   (a) no progress at all
#         count = 0
#         while count < 5:
#             print(count)
#
#   (b) progress in the wrong direction
#         count = 0
#         while count < 5:
#             count -= 1
#
#   (c) stepping OVER the target — the subtle one
#         total = 0
#         while total != 100:
#             total += 3        # 99, 102, 105 ... never exactly 100
#
# (c) is why `<` and `>` are safer loop conditions than `!=` and `==`.
# `while total < 100` cannot miss. `while total != 100` must hit it exactly.

total = 0
while total < 100:
    total += 3
print(f"stopped at {total} — < cannot overshoot into an infinite loop")


# ---------------------------------------------------------------------------
# 3. The one deliberate infinite loop
# ---------------------------------------------------------------------------

# `while True` with a `break` is idiomatic, not a smell. It is the shape for
# "loop until something happens", especially when you cannot evaluate the
# condition until after the first pass.

countdown = 3
while True:
    print(f"  tick {countdown}")
    countdown -= 1
    if countdown == 0:
        break
print("done")


# ---------------------------------------------------------------------------
# 4. Accumulators — the most common loop shape there is
# ---------------------------------------------------------------------------

# The accumulator lives OUTSIDE the loop. Declared inside, it would reset on
# every pass and end up holding one item's worth.

total = 0             # 0 is the identity for addition
product = 1           # 1 is the identity for multiplication
n = 1
while n <= 5:
    total += n
    product *= n
    n += 1
print(f"sum 1..5 = {total}, product 1..5 = {product}")

# START AT THE VALUE THAT MEANS "NOTHING YET". Starting a sum at 1 produces a
# plausible wrong answer, which is worse than a crash.

# Running min/max have a trap. This is WRONG:
#     lowest = 0        <- no positive number will ever beat it
# These are right:
lowest = float("inf")
highest = float("-inf")

readings = "18.2 21.7 15.9 24.1 19.8"
i = 0
parts = readings.split()
while i < len(parts):
    value = float(parts[i])
    if value < lowest:
        lowest = value
    if value > highest:
        highest = value
    i += 1
print(f"lowest {lowest}, highest {highest}")

# Note the shape of that loop: i = 0 ... while i < len(...) ... i += 1.
# That is a `for` loop wearing a disguise, with three extra chances to get it
# wrong. Tomorrow you delete all three lines.


# ---------------------------------------------------------------------------
# 5. Sentinel values
# ---------------------------------------------------------------------------

# A sentinel is a value meaning "stop", mixed in with the data. It MUST be
# something that cannot be a real value.
#
#   "done"  safe for a list of numbers
#   0       NOT safe — a list of numbers may legitimately contain zero
#   -1      NOT safe for temperatures, bank balances, or coordinates
#
# The classic bug: a data file that stops being read halfway through because
# row 400 happened to hold the sentinel.

DATA = "12 8 30 -1 45 7"          # -1 chosen badly on purpose
values = DATA.split()
i = 0
running = 0
while i < len(values):
    v = int(values[i])
    if v == -1:
        break
    running += v
    i += 1
print(f"sum stopped early at {running} — it should be 101, and -1 was data")


# ---------------------------------------------------------------------------
# 6. The validation loop — what Day 6 was missing
# ---------------------------------------------------------------------------

# Ask, test, break on success, complain and go round again on failure.
# ALWAYS give a way out: this one accepts an empty line.

attempts = 0
MAX_ATTEMPTS = 3
height = None

while attempts < MAX_ATTEMPTS:
    raw = input("Height in metres (Enter to skip): ").strip()
    if not raw:
        print("  skipped")
        break
    if raw.replace(".", "", 1).isdigit():
        height = float(raw)
        break
    attempts += 1
    remaining = MAX_ATTEMPTS - attempts
    print(f"  {raw!r} is not a number. {remaining} attempt(s) left.")

if height is None:
    print("No height recorded.")
else:
    print(f"Recorded {height} m.")

# A validation loop with no escape is a trap. Accept an empty line, or a
# 'quit', or count attempts and give up — but always something.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Uncomment each infinite loop in section 2. Ctrl-C each one.
#   * Change `while count < 5` to `<= 5` and count the iterations.
#   * Move `total = 0` inside a loop and watch the answer collapse.
#   * Collatz: from n, halve if even else 3n+1, until 1. Count the steps for
#     27. It is 111, and there is no way to know that without running it —
#     which is exactly when you need `while` rather than `for`.
