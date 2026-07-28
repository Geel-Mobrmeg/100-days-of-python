"""Day 019 build — a Pomodoro timer that counts down in place.

    python3 build.py                # 25 min work / 5 min break, 4 cycles
    python3 build.py --demo         # 6-second intervals, to watch it work
    python3 build.py 1 1 2          # 1 min work, 1 min break, 2 cycles

The timer NEVER counts sleeps. Every frame recomputes the remaining time
from a fixed start, so a slow redraw makes the display stutter instead of
making a 25-minute interval finish at 25:04.

Ctrl-C stops it and still prints the session summary.
"""

import sys
import time

WIDTH = 58
BAR = 34

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

work_minutes = 25.0
break_minutes = 5.0
cycles = 4
tick = 0.25                # how often to redraw, NOT how long anything takes

if "--demo" in sys.argv:
    work_minutes = 6 / 60
    break_minutes = 3 / 60
    cycles = 2
    tick = 0.1
else:
    numbers = [a for a in sys.argv[1:] if a.replace(".", "", 1).isdigit()]
    if len(numbers) >= 1:
        work_minutes = float(numbers[0])
    if len(numbers) >= 2:
        break_minutes = float(numbers[1])
    if len(numbers) >= 3:
        cycles = int(float(numbers[2]))


def clock(seconds):
    """Format a number of seconds as MM:SS, rounding up so 0.1s shows 00:01."""
    seconds = max(0, int(seconds + 0.999))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def countdown(label, minutes, symbol):
    """Count down in place. Returns the real elapsed seconds.

    The only thing `tick` controls is the redraw rate. `remaining` is
    always derived from perf_counter(), so this cannot drift.
    """
    duration = minutes * 60
    start = time.perf_counter()

    while True:
        elapsed = time.perf_counter() - start
        remaining = duration - elapsed
        if remaining <= 0:
            break

        done = elapsed / duration
        filled = int(done * BAR)
        bar = symbol * filled + "." * (BAR - filled)

        # \r + end="" + flush=True + a fixed width. All four are needed.
        frame = f"  {label:<7} [{bar}] {clock(remaining)} left"
        print(f"\r{frame:<{WIDTH}}", end="", flush=True)

        # Never sleep past the end, or the last frame overshoots.
        time.sleep(min(tick, remaining))

    finished = f"  {label:<7} [{symbol * BAR}] {clock(0)} — done"
    print(f"\r{finished:<{WIDTH}}")
    print("\a", end="", flush=True)          # bell, if the terminal allows it
    return time.perf_counter() - start


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'POMODORO TIMER':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'work interval':<28}{f'{work_minutes:g} min':>30}")
print(f"{'break interval':<28}{f'{break_minutes:g} min':>30}")
print(f"{'cycles':<28}{cycles:>30}")
print(f"{'started at':<28}{time.strftime('%H:%M:%S'):>30}")
print("=" * WIDTH)
print("Ctrl-C to stop early — the summary still prints.")
print()

session_start = time.perf_counter()
session_wall_start = time.time()
completed_work = 0
completed_breaks = 0
worked_seconds = 0.0
rested_seconds = 0.0
interrupted = False

try:
    for cycle in range(1, cycles + 1):
        print(f"-- cycle {cycle} of {cycles} " + "-" * (WIDTH - 18))

        worked_seconds += countdown("WORK", work_minutes, "#")
        completed_work += 1

        # No break after the final work interval — the session is over.
        if cycle < cycles:
            rested_seconds += countdown("BREAK", break_minutes, "~")
            completed_breaks += 1

except KeyboardInterrupt:
    # try/except is Day 51. It is borrowed here because a timer that loses
    # your session when you press Ctrl-C is not a timer anybody would use,
    # and Ctrl-C raises KeyboardInterrupt rather than just stopping.
    interrupted = True
    print("\r" + " " * WIDTH + "\r", end="")
    print("  stopped early.")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

session_seconds = time.perf_counter() - session_start
accounted = worked_seconds + rested_seconds

print()
print("=" * WIDTH)
print(f"{'SESSION SUMMARY':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'work intervals completed':<34}{f'{completed_work} / {cycles}':>24}")
print(f"{'breaks completed':<34}{completed_breaks:>24}")
print(f"{'time worked':<34}{clock(worked_seconds):>24}")
print(f"{'time on breaks':<34}{clock(rested_seconds):>24}")
print(f"{'total session':<34}{clock(session_seconds):>24}")
print("-" * WIDTH)

# The accuracy check. This is the part that justifies the whole design:
# the sum of the intervals should match the wall clock to within a redraw.
requested = completed_work * work_minutes * 60 + completed_breaks * break_minutes * 60
drift = accounted - requested

print(f"{'time requested':<34}{f'{requested:.2f}s':>24}")
print(f"{'time actually taken':<34}{f'{accounted:.2f}s':>24}")
print(f"{'drift':<34}{f'{drift:+.3f}s':>24}")
print(f"{'drift per interval':<34}"
      f"{f'{drift / max(1, completed_work + completed_breaks):+.3f}s':>24}")
print("-" * WIDTH)
print(f"{'started':<34}{time.strftime('%H:%M:%S', time.localtime(session_wall_start)):>24}")
print(f"{'finished':<34}{time.strftime('%H:%M:%S'):>24}")
print(f"{'completed normally':<34}{str(not interrupted):>24}")
print("=" * WIDTH)

if not interrupted and abs(drift) < 0.5:
    print("Drift under half a second across the whole session — because every")
    print("frame recomputed the remaining time instead of counting sleeps.")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 build.py --demo` and watch the drift line. Now change
#     countdown() to the naive version:
#
#         for remaining in range(int(duration), 0, -1):
#             ...
#             time.sleep(1)
#
#     and run it again. The drift becomes visible immediately, and it is
#     proportional to how much work each frame does.
#
#   * Add `time.sleep(0.05)` inside the redraw loop to simulate a slow
#     terminal. The correct version absorbs it; the naive one does not.
#
#   * Make the long break (15 minutes) happen after every fourth work
#     interval, which is what the real Pomodoro technique specifies.
#
#   * Log each completed interval to a file with a timestamp (Day 53), so
#     the session survives closing the terminal. Note that THIS is where
#     time.time() belongs — recording when something happened — while
#     perf_counter() stays for measuring how long it took.
