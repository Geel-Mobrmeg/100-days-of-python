# Day 019 — Time and pacing

**Phase 2 · Control flow** · ~70 minutes

> **Today's build:** a Pomodoro timer that counts down in place and rings when the interval ends.

**Concepts:** `time.sleep()` · `perf_counter()` · loop timing · carriage-return output

---

## The article

### Why this day exists

Two separate skills share a module today.

The first is **making a program wait** — for pacing an animation, throttling requests to an API
(Day 66), or simply making output readable. The second is **measuring how long something took**,
which is the beginning of every performance conversation you will ever have (Day 95).

There is also one small trick — printing over the same line — that turns a wall of scrolling
output into something that looks like software.

### 1. `time.sleep()`

```python
import time
time.sleep(1.5)        # pause this thread for 1.5 seconds
```

It takes a float, so `sleep(0.05)` is fine. It blocks *everything* in the program — nothing else
runs, no input is read, no display updates. That is acceptable in a script and completely
unacceptable in a UI or a server, which is why `asyncio.sleep` exists (Day 94).

`sleep()` guarantees *at least* that long, not exactly that long. The OS may take longer. This
matters for the accumulation problem in section 4.

### 2. The three clocks

Python has several, and picking the wrong one is a real bug.

| Function | Measures | Use for |
|---|---|---|
| `time.perf_counter()` | elapsed real time, highest resolution | **timing code** |
| `time.monotonic()` | elapsed time, never goes backwards | timeouts, schedulers |
| `time.time()` | seconds since 1970 (the "epoch") | **timestamps**, dates |
| `time.process_time()` | CPU time used by this process | ignoring sleep and I/O |

The rule: **`perf_counter()` to measure durations, `time.time()` to record when something
happened.**

Why it matters: `time.time()` is the wall clock, and the wall clock can *move*. NTP corrections,
daylight saving, a user changing the system clock — any of these can make `end - start` negative.
`perf_counter()` and `monotonic()` cannot go backwards, by definition. Using `time.time()` for a
timeout is a bug that shows up twice a year.

Both `perf_counter()` and `monotonic()` return seconds from an **arbitrary** origin. The absolute
value is meaningless; only the difference has any meaning.

```python
start = time.perf_counter()
do_the_work()
elapsed = time.perf_counter() - start
print(f"took {elapsed:.3f}s")
```

`time.process_time()` is the interesting one for later: it counts CPU time only, so a program
that sleeps for ten seconds uses almost no process time. That is exactly how you tell an
I/O-bound program from a CPU-bound one, which is the whole of Day 91.

### 3. Printing over the same line

`\r` is a **carriage return**: move the cursor to the start of the line without advancing.
Combine it with `end=""` and each write overwrites the previous one.

```python
print(f"\r{remaining} seconds left", end="", flush=True)
```

Three details, all of which you will get wrong once:

- **`end=""`** — otherwise the newline moves you down and `\r` achieves nothing.
- **`flush=True`** — output is buffered, and without a newline to trigger a flush the text may
  not appear until much later. Every "my progress bar only shows up at the end" question is this.
- **Pad the line.** `\r` overwrites, it does not erase. Going from `100 seconds` to `99 seconds`
  leaves a stray `s`. Pad to a fixed width, or clear with `"\r" + " " * 40 + "\r"`.

Finish with a real newline when you are done, or the next output lands on top of your last frame.

This works in a terminal. It does not work in most notebook or IDE output panes, where the
output is a log rather than a screen.

### 4. Loop timing, and the drift problem

The obvious countdown is wrong:

```python
for remaining in range(60, 0, -1):
    print(remaining)
    time.sleep(1)           # drifts
```

Each pass takes *one second plus however long the printing took*, and `sleep` guarantees only a
lower bound. Over 60 passes the error accumulates, and a 25-minute timer can be seconds late.

The fix is to **compute from a fixed start time** rather than counting passes:

```python
start = time.perf_counter()
while True:
    elapsed = time.perf_counter() - start
    remaining = DURATION - elapsed
    if remaining <= 0:
        break
    ...
    time.sleep(0.1)
```

Now `sleep` only controls *how often you redraw*. The remaining time is always derived from the
clock, so a slow pass makes the display stutter instead of making the timer wrong.

This is a general principle worth keeping: **derive state from a source of truth, do not
accumulate it.** The same idea reappears in animation, in billing, and in anything that
integrates a value over time.

### 5. Making a noise

`print("\a")` emits the terminal bell. Whether anything happens depends entirely on the
terminal — many silence it by default, and it does nothing when output is redirected to a file.
Treat it as a bonus, and always print a visible message too.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The clocks compared, `\r` demonstrated, and drift measured against a fixed start. |
| `build.py`  | The Pomodoro timer: work/break cycles, in-place countdown, progress bar, session log. |

```bash
python3 lesson.py
python3 build.py                  # the real thing: 25 min work, 5 min break
python3 build.py --demo           # 6-second intervals, so you can watch it work
python3 build.py 1 1 2            # 1 min work, 1 min break, 2 cycles
```

---

## Common mistakes

**Missing `flush=True`.** Your progress bar appears all at once at the end.

**Missing `end=""`.** `\r` does nothing useful.

**Not padding.** Leftover characters from the longer previous line.

**`time.time()` for durations.** Can go backwards. Use `perf_counter()`.

**Counting `sleep`s instead of reading the clock.** Drift.

**`sleep()` in anything interactive.** It blocks everything.

**Assuming the bell works.** Often silenced, always silent when redirected.

---

## Exercises

1. Print a spinner (`| / - \`) that rotates in place for three seconds.
2. Print a progress bar that fills over five seconds. Get `flush`, `end` and padding right.
3. Time an empty loop of a million passes with `perf_counter()`. Then time
   `time.sleep(0.5)` with both `perf_counter()` and `process_time()` and explain the difference.
4. Build a 10-second countdown by counting `sleep(1)`s and another from a fixed start. Compare
   the total elapsed time for each. Then add a slow operation inside the loop and compare again.
5. Show a clock updating in place every second, using `time.strftime("%H:%M:%S")`.
6. Measure how long `time.sleep(0.001)` actually takes, a thousand times over. It is not 1 ms.

---

## Checklist

- [ ] I use `perf_counter()` for durations and `time.time()` for timestamps
- [ ] I know why `time.time()` can go backwards
- [ ] My in-place output uses `\r`, `end=""`, `flush=True` and padding
- [ ] My countdown derives remaining time from a fixed start, not from a count
- [ ] I finish in-place output with a real newline
- [ ] My timer is still accurate after 25 minutes
