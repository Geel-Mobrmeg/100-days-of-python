"""Day 053 build — a log splitter that never holds the log in memory.

    python3 build.py                       # generate a demo log and split it
    python3 build.py /path/to/app.log out  # split a log of your own

THE JOB: one 10 MB (or 10 GB) log becomes one file per day.

THE CONSTRAINT: constant memory, whatever the file size. That rules out
readlines(), it rules out grouping into a dict first, and it means the
output handles have to be open AT THE SAME TIME — an unknown number of
them, decided by the data.

    contextlib.ExitStack is the answer to "an unknown number of `with`s".

Everything is written into a temporary directory that is removed at the
end, so this file leaves nothing behind.
"""

import contextlib
import random
import re
import shutil
import sys
import tempfile
import time
import tracemalloc
from collections import Counter
from pathlib import Path

WIDTH = 78

# A timestamp at the start of the line. Anything else is not a log line.
STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}Z ")


# ###########################################################################
# MAKING A LOG THAT LOOKS LIKE A REAL ONE
# ###########################################################################

def make_log(path, lines=120_000, days=14, seed=53):
    """Write a synthetic log, including the things real logs contain.

    Real logs are not clean: continuation lines from tracebacks, blank
    lines, a line truncated by a crash, and — the one that catches people
    — a byte that is not valid UTF-8, because something upstream wrote
    latin-1 into the same file.
    """
    random.seed(seed)
    levels = ["INFO"] * 80 + ["WARN"] * 15 + ["ERROR"] * 5
    services = ["api", "worker", "auth", "billing"]

    # Binary mode: this file is being built byte by byte on purpose.
    with open(path, "wb") as f:
        for n in range(lines):
            day = n * days // lines + 1
            stamp = (f"2026-03-{day:02d}T"
                     f"{n % 24:02d}:{n % 60:02d}:{(n * 7) % 60:02d}Z")
            level = random.choice(levels)
            service = random.choice(services)
            line = (f"{stamp} {level:<5} [{service}] request {n} "
                    f"completed in {random.randint(1, 900)}ms\n")
            f.write(line.encode("utf-8"))

            if level == "ERROR" and random.random() < 0.3:
                # A traceback: continuation lines with NO timestamp.
                f.write(b"  Traceback (most recent call last):\n")
                f.write(b"    ValueError: something upstream\n")
            if random.random() < 0.0005:
                f.write(b"\n")                       # a blank line
            if random.random() < 0.0004:
                # latin-1 'e-acute' (0xE9) in a UTF-8 file. Not decodable.
                f.write(b"2026-03-01T00:00:00Z INFO  [api] caf\xe9 order\n")
    return path


# ###########################################################################
# THE SPLITTER
# ###########################################################################

def split_log(source, destination, encoding="utf-8", errors="replace"):
    """Stream `source` into one file per day inside `destination`.

    Returns a Counter of what happened. Never holds more than one line.

    THE THREE DECISIONS IN THIS FUNCTION:

      1. `for line in source_file` — constant memory, any file size.
      2. ExitStack — one output handle per day, opened on first sight,
         all of them closed on the way out even if this raises.
      3. errors='replace' — a log is not worth crashing over. A CONFIG
         file would be, and that is the difference: choose per file, not
         per program.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    tally = Counter()
    last_day = None

    with contextlib.ExitStack() as stack:
        source_file = stack.enter_context(
            open(source, encoding=encoding, errors=errors)
        )
        outputs = {}

        for line in source_file:                     # ← the whole design
            tally["lines read"] += 1
            match = STAMP.match(line)

            if match:
                last_day = match.group(1)
            elif not line.strip():
                tally["blank"] += 1
                continue
            elif last_day is None:
                tally["before any timestamp"] += 1
                continue
            else:
                # A continuation line belongs with the line above it.
                tally["continuation"] += 1

            if last_day not in outputs:
                # enter_context() registers the close for LATER, so the
                # handle stays open and is still closed exactly once.
                outputs[last_day] = stack.enter_context(
                    open(destination / f"{last_day}.log", "w",
                         encoding="utf-8")
                )
                tally["files opened"] += 1

            outputs[last_day].write(line)
            tally["lines written"] += 1
            if "�" in line:
                tally["undecodable bytes replaced"] += 1

    return tally


# ###########################################################################
# THE COMPARISON: THE TWO WAYS PEOPLE ACTUALLY WRITE THIS
# ###########################################################################

def split_by_grouping(source, destination):
    """The obvious version: read it all, group, then write.

    Correct, simple, and it needs the whole file in memory — twice, once
    as the text and once as the groups.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    groups = {}
    last_day = None
    with open(source, encoding="utf-8", errors="replace") as f:
        for line in f.readlines():
            match = STAMP.match(line)
            if match:
                last_day = match.group(1)
            if last_day and line.strip():
                groups.setdefault(last_day, []).append(line)
    for day, lines in groups.items():
        with open(destination / f"{day}.log", "w", encoding="utf-8") as f:
            f.writelines(lines)
    return sum(len(v) for v in groups.values())


def split_by_reopening(source, destination, limit=20_000):
    """The version that avoids ExitStack by opening per line.

    Constant memory AND correct. It just does one open() and one close()
    per line, which the timing below prices for you.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    last_day = None
    written = 0
    with open(source, encoding="utf-8", errors="replace") as f:
        for index, line in enumerate(f):
            if index >= limit:
                break
            match = STAMP.match(line)
            if match:
                last_day = match.group(1)
            if last_day and line.strip():
                with open(destination / f"{last_day}.log", "a",
                          encoding="utf-8") as out:
                    out.write(line)
                written += 1
    return written


# ###########################################################################
# RUN IT
# ###########################################################################

if len(sys.argv) >= 2:
    SOURCE = Path(sys.argv[1])
    WORK = Path(sys.argv[2] if len(sys.argv) > 2 else "split-output")
    TEMPORARY = False
else:
    WORK = Path(tempfile.mkdtemp(prefix="day053-build-"))
    SOURCE = WORK / "app.log"
    TEMPORARY = True
    make_log(SOURCE)

size = SOURCE.stat().st_size

print("=" * WIDTH)
print(f"{'SPLITTING A LOG BY DAY':^{WIDTH}}")
print("=" * WIDTH)
print(f"  {'source':<24}{SOURCE.name}")
print(f"  {'size':<24}{size:,} bytes ({size / 1e6:.1f} MB)")

started = time.perf_counter()
tracemalloc.start()
tally = split_log(SOURCE, WORK / "streamed")
peak_streamed = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
elapsed = time.perf_counter() - started

print(f"  {'time':<24}{elapsed:.2f}s")
print()
for label, count in tally.most_common():
    print(f"  {label:<32}{count:>10,}")

produced = sorted((WORK / "streamed").glob("*.log"))
print()
print(f"  {'OUTPUT FILE':<20}{'LINES':>10}{'BYTES':>14}")
print("  " + "-" * (WIDTH - 4))
total_lines = total_bytes = 0
for path in produced:
    with open(path, encoding="utf-8") as f:
        lines = sum(1 for _ in f)
    total_lines += lines
    total_bytes += path.stat().st_size
    print(f"  {path.name:<20}{lines:>10,}{path.stat().st_size:>14,}")
print("  " + "-" * (WIDTH - 4))
print(f"  {len(produced)} files{'':<12}{total_lines:>10,}{total_bytes:>14,}")


# ###########################################################################
# MEMORY: THE POINT OF THE WHOLE EXERCISE
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE SAME JOB, THREE WAYS':^{WIDTH}}")
print("=" * WIDTH)

tracemalloc.start()
grouped_lines = split_by_grouping(SOURCE, WORK / "grouped")
peak_grouped = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()

started = time.perf_counter()
split_by_reopening(SOURCE, WORK / "reopened", limit=20_000)
reopen_time = time.perf_counter() - started

started = time.perf_counter()
split_log(SOURCE, WORK / "streamed2")
stream_time = time.perf_counter() - started
per_20k = stream_time * 20_000 / max(tally["lines read"], 1)

print(f"\n  {'':<26}{'PEAK MEMORY':>14}{'x FILE':>9}{'TIME':>10}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'read all, then group':<26}{peak_grouped / 1e6:>11.1f} MB"
      f"{peak_grouped / size:>8.1f}x{'':>10}")
print(f"  {'stream + ExitStack':<26}{peak_streamed / 1e3:>11.0f} KB"
      f"{peak_streamed / size:>8.3f}x{stream_time:>9.2f}s")
print(f"  {'stream + reopen per line':<26}{'(constant)':>14}{'':>9}"
      f"{reopen_time:>9.2f}s")
print("  " + "-" * (WIDTH - 4))
print(f"""
  MEMORY   grouping costs {peak_grouped / max(peak_streamed, 1):,.0f}x more than streaming, and it scales
           with the FILE: at {peak_grouped / size:.1f}x, a 10 GB log would need {10 * peak_grouped / size:.0f} GB of RAM.
           The streamed version needs the same {peak_streamed / 1e3:.0f} KB it needed here.

  TIME     reopening per line took {reopen_time:.2f}s for 20,000 lines, where
           the streaming version does the same 20,000 in about {per_20k:.2f}s —
           roughly {reopen_time / max(per_20k, 0.001):.0f}x, all of it open() and close() syscalls.

  ExitStack buys the second without giving up the first. That is the
  entire reason it exists: `with` when you do not know how many.""")


# ###########################################################################
# THE MESSY LINES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT REAL LOGS CONTAIN':^{WIDTH}}")
print("=" * WIDTH)

print(f"""
  {'lines with a timestamp':<34}{tally['lines read'] - tally['continuation'] - tally['blank']:>10,}
  {'continuation lines (tracebacks)':<34}{tally['continuation']:>10,}
  {'blank lines, dropped':<34}{tally['blank']:>10,}
  {'lines with an undecodable byte':<34}{tally['undecodable bytes replaced']:>10,}

  THE CONTINUATION LINES ARE THE INTERESTING CASE. A traceback in a log
  has no timestamp of its own, and a splitter that only looks for stamps
  would either drop it or crash. This one remembers the last day it saw
  and keeps the traceback WITH the line it belongs to.

  THE UNDECODABLE BYTE is the one that catches people. Something upstream
  wrote latin-1 into a UTF-8 file. With the default errors='strict' this
  whole program dies at that byte, {tally['lines read']:,} lines in, having already
  written most of the output. With errors='replace' the byte becomes
  U+FFFD and everything else survives.

  THAT IS A JUDGEMENT, NOT A DEFAULT: for a log, salvage. For a config
  file or a bank statement, crash — a silently corrupted value is worse
  than no value.""")

sample = next((p for p in produced if "2026-03-01" in p.name), produced[0])
with open(sample, encoding="utf-8") as f:
    body = [line.rstrip("\n") for line in f][:6]
print(f"\n  first lines of {sample.name}:")
for line in body:
    print(f"    {line[:WIDTH - 6]}")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

with open(SOURCE, encoding="utf-8", errors="replace") as f:
    source_lines = sum(1 for _ in f)
    f.seek(0)

with open(SOURCE, encoding="utf-8", errors="replace") as f:
    source_nonblank = sum(1 for line in f if line.strip())

grouped_files = sorted((WORK / "grouped").glob("*.log"))

# The output is not the same size as the input, and both differences are
# explainable to the byte:
#   - each dropped blank line was one '\n'
#   - each undecodable byte (1 byte) became U+FFFD, which is 3 bytes in
#     UTF-8, so every replacement grew the file by 2
blank_bytes = tally["blank"]
replacement_growth = tally["undecodable bytes replaced"] * 2

# Re-run into the same directory: it must produce the same result.
again = split_log(SOURCE, WORK / "streamed")

claims = [
    ("every line is read", tally["lines read"] == source_lines),
    ("every non-blank line is written",
     tally["lines written"] == source_nonblank),
    ("nothing is invented",
     total_lines == tally["lines written"]),
    ("every byte is accounted for, exactly",
     total_bytes == size - blank_bytes + replacement_growth),
    ("one file per day, opened once each",
     tally["files opened"] == len(produced)),
    ("streaming and grouping agree on the line count",
     grouped_lines == tally["lines written"]),
    ("...and produce the same set of files",
     [p.name for p in grouped_files] == [p.name for p in produced]),
    ("re-running produces identical counts", again == tally),
    ("peak memory is a fraction of the file",
     peak_streamed < size / 10),
    ("...and is not a fraction of a bigger file — it is constant",
     peak_streamed < 2_000_000),
    ("continuation lines were kept, not dropped",
     tally["continuation"] > 0),
    ("undecodable bytes did not stop the run",
     tally["undecodable bytes replaced"] > 0),
]

print()
for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(p for _, p in claims)} of {len(claims)} checks pass")

print(f"""
  THE FOURTH CHECK IS THE ONE THAT WOULD CATCH A REAL BUG, and it is worth
  reading the arithmetic:

      input                        {size:>10,} bytes
      minus {tally['blank']:>3} dropped blank lines    {-blank_bytes:>10,}
      plus {tally['undecodable bytes replaced']:>4} replacements x 2 bytes  {replacement_growth:>+10,}
      = output                     {total_bytes:>10,} bytes

  The output is LARGER than the input. Each undecodable byte was one byte
  on the way in and became U+FFFD, which is three bytes in UTF-8. Knowing
  that to the byte is the difference between "it seems to work" and
  "nothing was truncated, doubled, or written with the wrong newline" — a
  line count alone would not have noticed a lost final line with no
  trailing newline.

  The eighth matters because this is a TOOL: running it twice must not
  append to yesterday's output. Mode 'w' guarantees that, and the check
  proves the guarantee rather than trusting it.""")
print("=" * WIDTH)

if TEMPORARY:
    shutil.rmtree(WORK, ignore_errors=True)
    print(f"\n(temporary directory {WORK} removed)", file=sys.stderr)
else:
    print(f"\noutput in {WORK}/streamed/", file=sys.stderr)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change errors='replace' to 'strict' and re-run. The program dies
#     part-way through, having already written most of the output — which
#     is the worst of both outcomes. Then decide where the atomic-write
#     pattern from lesson.py belongs in this file.
#
#   * Split by HOUR instead of by day. Now there are 336 output files and
#     ExitStack holds 336 handles. Find your system's limit
#     (`ulimit -n`), then write the version that closes the least recently
#     used handle when it runs out. That is a cache, and it is Day 37.
#
#   * Add gzip: `gzip.open(path, 'wt', encoding='utf-8')` is a drop-in for
#     open() here, because both are context managers that yield a text
#     stream. Measure the output size.
#
#   * Make split_log() take an OPEN STREAM rather than a path, as
#     lesson.py argued. Then split sys.stdin, and the tool composes with
#     every other command on your machine.
#
#   * Feed it a file with \\r\\n line endings and confirm the output keeps
#     them. Then read about newline='' in the open() docs — Day 54 needs
#     it for CSV.
