"""Day 019 — Time and pacing.

    python3 lesson.py

This one takes about 12 seconds to run, because several sections are
demonstrating waiting. That is the point.
"""

import time

# ---------------------------------------------------------------------------
# 1. The three clocks, and why the choice is not cosmetic
# ---------------------------------------------------------------------------

print(f"time.time()          {time.time():.3f}   seconds since 1970")
print(f"time.perf_counter()  {time.perf_counter():.3f}   from an ARBITRARY origin")
print(f"time.monotonic()     {time.monotonic():.3f}   also arbitrary, never backwards")
print(f"time.process_time()  {time.process_time():.3f}   CPU used by this process")

print("""
  perf_counter()  measure DURATIONS. Highest resolution available.
  monotonic()     timeouts and schedulers. Cannot go backwards.
  time()          record WHEN something happened. Convertible to a date.
  process_time()  CPU only — ignores sleeping and waiting for I/O.

  time() is the WALL CLOCK, and wall clocks move: NTP corrections, daylight
  saving, a user setting the date. `end - start` with time() can come out
  NEGATIVE. That is a real bug that surfaces about twice a year.
""")

# The absolute value of perf_counter() is meaningless. Only differences are.
start = time.perf_counter()
total = sum(range(1_000_000))
elapsed = time.perf_counter() - start
print(f"summing a million ints took {elapsed:.4f}s (total={total:,})")


# ---------------------------------------------------------------------------
# 2. sleep measures a LOWER bound, not an exact one
# ---------------------------------------------------------------------------

print("\nasking for 0.001s of sleep, 200 times:")
start = time.perf_counter()
for _ in range(200):
    time.sleep(0.001)
actual = time.perf_counter() - start
print(f"  asked for {200 * 0.001:.3f}s, actually took {actual:.3f}s "
      f"({actual / 0.2:.1f}x)")
print("  sleep() guarantees AT LEAST that long. The OS decides the rest.")


# ---------------------------------------------------------------------------
# 3. process_time vs perf_counter — the difference IS the waiting
# ---------------------------------------------------------------------------

wall_start = time.perf_counter()
cpu_start = time.process_time()
time.sleep(0.5)
print(f"\nsleeping 0.5s:")
print(f"  wall clock: {time.perf_counter() - wall_start:.3f}s")
print(f"  CPU time:   {time.process_time() - cpu_start:.3f}s")
print("  Sleeping costs wall time and no CPU. That gap is exactly how you")
print("  tell an I/O-bound program from a CPU-bound one — all of Day 91.")


# ---------------------------------------------------------------------------
# 4. Printing over the same line with \r
# ---------------------------------------------------------------------------

print("\nspinner (3 seconds):")
FRAMES = "|/-\\"
start = time.perf_counter()
i = 0
while time.perf_counter() - start < 3:
    print(f"\r  working {FRAMES[i % len(FRAMES)]}", end="", flush=True)
    i += 1
    time.sleep(0.1)
print("\r  working done   ")          # padded, then a real newline

# THREE THINGS, all of which you will get wrong once:
#
#   end=""       otherwise the newline moves you down and \r does nothing
#   flush=True   output is buffered; with no newline to trigger a flush the
#                text may not appear until the program ends. Every "my
#                progress bar only shows at the end" question is this line.
#   PADDING      \r overwrites, it does not erase. Going from "100 items" to
#                "99 items" leaves a stray "s".

print("\nunpadded, going from a long line to a short one:")
print("\r  counting 100 items", end="", flush=True)
time.sleep(0.6)
print("\r  counting 9", end="", flush=True)
time.sleep(0.6)
print("       <- the leftover characters are still there")

print("\npadded properly:")
print(f"\r  {'counting 100 items':<30}", end="", flush=True)
time.sleep(0.6)
print(f"\r  {'counting 9':<30}", end="", flush=True)
time.sleep(0.6)
print("\n  clean.")


# ---------------------------------------------------------------------------
# 5. A progress bar
# ---------------------------------------------------------------------------

print("\nprogress bar:")
STEPS = 30
for step in range(STEPS + 1):
    fraction = step / STEPS
    filled = int(fraction * 24)
    bar = "#" * filled + "." * (24 - filled)
    print(f"\r  [{bar}] {fraction:>4.0%}", end="", flush=True)
    time.sleep(0.02)
print()


# ---------------------------------------------------------------------------
# 6. DRIFT — the mistake that makes a 25-minute timer late
# ---------------------------------------------------------------------------

print("\ncounting sleeps vs reading the clock, with slow work in the loop:")

# WRONG: each pass costs one interval PLUS the work PLUS sleep's overshoot,
# and the errors accumulate.
start = time.perf_counter()
for _ in range(10):
    sum(range(200_000))            # stand-in for "the loop does something"
    time.sleep(0.05)
drifting = time.perf_counter() - start

# RIGHT: derive the remaining time from a FIXED START. sleep now only
# controls how often you redraw, not how long the whole thing takes.
start = time.perf_counter()
TARGET = 0.5
while True:
    elapsed = time.perf_counter() - start
    if elapsed >= TARGET:
        break
    sum(range(200_000))
    time.sleep(min(0.05, TARGET - elapsed))
corrected = time.perf_counter() - start

print(f"  target                 {TARGET:.3f}s")
print(f"  counting sleeps        {drifting:.3f}s   "
      f"({drifting - TARGET:+.3f}s)")
print(f"  reading the clock      {corrected:.3f}s   "
      f"({corrected - TARGET:+.3f}s)")
print("""
  DERIVE STATE FROM A SOURCE OF TRUTH, DO NOT ACCUMULATE IT.
  A slow pass then makes the display stutter instead of making the timer
  wrong. The same principle reappears in animation, in billing, and in
  anything that integrates a value over time.
""")


# ---------------------------------------------------------------------------
# 7. Formatting a duration, and the bell
# ---------------------------------------------------------------------------

seconds = 3725
print(f"3725 seconds is {seconds // 3600:02d}:"
      f"{seconds % 3600 // 60:02d}:{seconds % 60:02d}")
print(f"the time now is {time.strftime('%H:%M:%S')}")

print("\a  <- a terminal bell, if your terminal allows it (many do not,")
print("      and it is always silent when output is redirected to a file)")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Remove flush=True from the progress bar and run it piped into `cat`.
#   * Remove end="" and watch \r stop mattering.
#   * Time time.sleep(0.001) a thousand times and work out the real overhead.
#   * Use time.time() for the drift comparison instead of perf_counter() and
#     confirm it agrees — then read section 1 again about why you still
#     should not.
