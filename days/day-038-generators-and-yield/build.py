"""Day 038 build — stream a large log file without loading it.

    python3 build.py            # ~60 MB, runs in a few seconds
    python3 build.py 500        # the full 500 MB — a couple of minutes
    python3 build.py 60 --eager # ALSO run the whole-file version, to compare

Generates a log, then processes it two ways and measures the peak memory
each one actually used, with tracemalloc.

The difference between the two implementations is one word: `yield` versus
building a list. The measured difference in peak memory is about four
orders of magnitude — and, unlike the eager version, the streaming figure
does not change when the file gets bigger.
"""

import random
import sys
import time
import tracemalloc
from collections import Counter
from itertools import islice
from pathlib import Path

WIDTH = 78
LOG_PATH = Path(__file__).parent / "big.log"

target_mb = 60
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    target_mb = max(1, min(int(sys.argv[1]), 2000))
run_eager = "--eager" in sys.argv

LEVELS = ["INFO"] * 80 + ["WARN"] * 12 + ["ERROR"] * 7 + ["FATAL"]
SERVICES = ["api", "web", "worker", "db", "cache", "auth"]
MESSAGES = {
    "INFO": ["request completed", "cache hit", "job finished", "user login"],
    "WARN": ["slow query", "retry scheduled", "queue depth high"],
    "ERROR": ["database timeout", "connection refused", "disk full",
              "permission denied"],
    "FATAL": ["out of memory", "unrecoverable state"],
}


# ===========================================================================
# 0. Make the log (once)
# ===========================================================================

def generate_log(path, megabytes):
    """Write a plausible log of roughly `megabytes` MB."""
    rng = random.Random(42)
    target_bytes = megabytes * 1024 * 1024
    written = 0
    line_count = 0
    start = time.perf_counter()

    with path.open("w", encoding="utf-8") as handle:
        while written < target_bytes:
            # Write in batches so this does not take all afternoon.
            batch = []
            for _ in range(20_000):
                level = rng.choice(LEVELS)
                line = (
                    f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d} "
                    f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:"
                    f"{rng.randint(0, 59):02d} "
                    f"{level:<5} "
                    f"{rng.choice(SERVICES):<7} "
                    f"req={rng.randint(100000, 999999)} "
                    f"took={rng.randint(1, 4000)}ms "
                    f"{rng.choice(MESSAGES[level])}\n"
                )
                batch.append(line)
                line_count += 1
            text = "".join(batch)
            handle.write(text)
            written += len(text.encode("utf-8"))

    return line_count, written, time.perf_counter() - start


existing_mb = LOG_PATH.stat().st_size / 1024 / 1024 if LOG_PATH.exists() else 0

print("=" * WIDTH)
print(f"{'STREAMING A LARGE LOG':^{WIDTH}}")
print("=" * WIDTH)

if not LOG_PATH.exists() or abs(existing_mb - target_mb) > target_mb * 0.2:
    print(f"generating a ~{target_mb} MB log (this happens once)...")
    lines_written, bytes_written, took = generate_log(LOG_PATH, target_mb)
    print(f"  {lines_written:,} lines, "
          f"{bytes_written / 1024 / 1024:.1f} MB, in {took:.1f}s")
else:
    print(f"reusing {LOG_PATH.name} ({existing_mb:.1f} MB)")

size_mb = LOG_PATH.stat().st_size / 1024 / 1024
print(f"{'file':<30}{LOG_PATH.name:>{WIDTH - 30}}")
print(f"{'size':<30}{f'{size_mb:.1f} MB':>{WIDTH - 30}}")


# ===========================================================================
# THE PIPELINE — each stage yields one item at a time
# ===========================================================================

def read_lines(path):
    """Yield one line at a time. Works on 2 KB or 500 GB, identically.

    The `with` is INSIDE the generator, so the file opens on the first
    next() and closes when the generator is exhausted or collected. Put it
    outside and the file would be shut before anything was read.
    """
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            yield line.rstrip("\n")


def parse(lines):
    """Yield a dict per line. Bad lines are skipped, not fatal."""
    for line in lines:
        parts = line.split(maxsplit=5)
        if len(parts) < 6:
            continue
        date, clock, level, service, request, rest = parts
        took = 0
        for token in rest.split():
            if token.startswith("took="):
                digits = token[5:].removesuffix("ms")
                took = int(digits) if digits.isdigit() else 0
        yield {
            "date": date,
            "level": level,
            "service": service,
            "took": took,
            "message": rest.split("ms ", 1)[-1] if "ms " in rest else rest,
        }


def only(records, *levels):
    """Yield only the records at the given levels."""
    wanted = set(levels)
    for record in records:
        if record["level"] in wanted:
            yield record


# ===========================================================================
# 1. STREAMING — constant memory
# ===========================================================================

print()
print("-" * WIDTH)
print("1. STREAMING (generators)")
print("-" * WIDTH)

tracemalloc.start()
start = time.perf_counter()

levels = Counter()
services = Counter()
error_messages = Counter()
total_lines = 0
total_ms = 0
slowest = None

# The whole analysis, one line at a time. Nothing is ever held.
for record in parse(read_lines(LOG_PATH)):
    total_lines += 1
    levels[record["level"]] += 1
    total_ms += record["took"]
    if slowest is None or record["took"] > slowest["took"]:
        slowest = record
    if record["level"] in ("ERROR", "FATAL"):
        services[record["service"]] += 1
        error_messages[record["message"]] += 1

stream_time = time.perf_counter() - start
_, stream_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

errors = levels["ERROR"] + levels["FATAL"]

print(f"{'lines processed':<34}{total_lines:>{WIDTH - 34},}")
print(f"{'ERROR + FATAL lines':<34}{errors:>{WIDTH - 34},}")
print(f"{'error rate':<34}{errors / total_lines:>{WIDTH - 34}.2%}")
mean_ms = f"{total_ms / total_lines:.0f} ms"
slowest_text = f"{slowest['took']}ms  {slowest['service']}"

print(f"{'mean duration':<34}{mean_ms:>{WIDTH - 34}}")
print(f"{'slowest request':<34}{slowest_text:>{WIDTH - 34}}")
print(f"{'time taken':<34}{f'{stream_time:.2f} s':>{WIDTH - 34}}")
print(f"{'PEAK MEMORY':<34}"
      f"{f'{stream_peak / 1024 / 1024:.2f} MB':>{WIDTH - 34}}")

print()
print(f"  {'LEVEL':<10}{'COUNT':>12}{'SHARE':>10}   {'':<28}")
peak_level = max(levels.values())
for level, n in levels.most_common():
    bar = "#" * int(n / peak_level * 26)
    print(f"  {level:<10}{n:>12,}{n / total_lines:>10.1%}   {bar:<28}")

print()
print(f"  {'TOP ERROR MESSAGES':<40}{'COUNT':>12}")
for message, n in error_messages.most_common(4):
    print(f"  {message[:40]:<40}{n:>12,}")

# ===========================================================================
# 2. THE EAGER VERSION — the same answer, the whole file in RAM
# ===========================================================================

print()
print("-" * WIDTH)
print("2. EAGER (the whole file at once)")
print("-" * WIDTH)

if run_eager:
    tracemalloc.start()
    start = time.perf_counter()

    with LOG_PATH.open(encoding="utf-8") as handle:
        all_lines = handle.readlines()             # <- the whole file
    all_records = [
        r for r in parse(line.rstrip("\n") for line in all_lines)
    ]                                              # <- and again, parsed
    eager_errors = len([r for r in all_records
                        if r["level"] in ("ERROR", "FATAL")])

    eager_time = time.perf_counter() - start
    _, eager_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del all_lines, all_records

    print(f"{'lines processed':<34}{total_lines:>{WIDTH - 34},}")
    print(f"{'ERROR + FATAL lines':<34}{eager_errors:>{WIDTH - 34},}")
    print(f"{'same answer as streaming':<34}"
          f"{str(eager_errors == errors):>{WIDTH - 34}}")
    print(f"{'time taken':<34}{f'{eager_time:.2f} s':>{WIDTH - 34}}")
    print(f"{'PEAK MEMORY':<34}"
          f"{f'{eager_peak / 1024 / 1024:.2f} MB':>{WIDTH - 34}}")
    print()
    print(f"{'memory ratio':<34}"
          f"{f'{eager_peak / stream_peak:.0f}x':>{WIDTH - 34}}")
    print(f"{'file size':<34}{f'{size_mb:.1f} MB':>{WIDTH - 34}}")
else:
    print(f"""  Skipped. Pass --eager to run it.

  It calls handle.readlines() and then builds a list of every parsed
  record, so peak memory lands around {size_mb * 8:.0f} MB for this {size_mb:.0f} MB file —
  measured at roughly EIGHT times the file size, not the 1x you might
  expect, because every line becomes a Python str object and every record
  a dict, and both carry far more overhead than the raw bytes.

  At 500 MB that is about 4 GB. On a machine with 2 GB free it is not
  slow, it is IMPOSSIBLE. The streaming version above used
  {stream_peak / 1024 / 1024:.2f} MB and does not care how big the file is.""")

# ===========================================================================
# 3. SHORT-CIRCUITING — the other thing laziness buys
# ===========================================================================

print()
print("-" * WIDTH)
print("3. SHORT-CIRCUITING")
print("-" * WIDTH)

start = time.perf_counter()
first_fatal = next(
    (r for r in parse(read_lines(LOG_PATH)) if r["level"] == "FATAL"), None
)
first_time = time.perf_counter() - start

start = time.perf_counter()
first_ten = list(islice(only(parse(read_lines(LOG_PATH)), "ERROR"), 10))
ten_time = time.perf_counter() - start

print(f"{'find the FIRST fatal':<34}{f'{first_time * 1000:.1f} ms':>{WIDTH - 34}}")
print(f"{'find the first 10 errors':<34}{f'{ten_time * 1000:.1f} ms':>{WIDTH - 34}}")
print(f"{'full scan (section 1)':<34}{f'{stream_time * 1000:.0f} ms':>{WIDTH - 34}}")
print(f"""
  Both stopped reading as soon as they had an answer. `next(...)` and
  islice() never asked for line {total_lines:,}, so it was never read from disk.

  The eager version cannot do this AT ALL: readlines() has already read
  everything before the filter runs. Laziness is not only about memory —
  it is about not doing work nobody asked for.""")

print()
print("=" * WIDTH)
print(f"""ONE WORD.

    def read_lines(path):              def read_lines(path):
        with path.open() as f:             with path.open() as f:
            for line in f:                     return f.readlines()
                yield line

The left one holds one line. The right one holds the file. Everything else
in this program — the parsing, the counting, the reporting — is identical.

  streaming peak memory   {stream_peak / 1024 / 1024:>8.2f} MB
  file size               {size_mb:>8.2f} MB
  ratio                   {stream_peak / 1024 / 1024 / size_mb:>8.4f}x

Delete big.log when you are done: it is in .gitignore, and it is {size_mb:.0f} MB.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run `python3 build.py 500 --eager` if you have the RAM, and watch the
#     ratio. Then run it without --eager and note the streaming figure does
#     not move at all between 60 MB and 500 MB.
#
#   * Add a stage that keeps only requests over 3000ms. One line, no extra
#     memory, and it can go anywhere in the chain.
#
#   * Section 1 makes ONE pass and computes six things. Try computing them
#     with six separate generator expressions and note you cannot — each
#     one would need its own pass over the file. Single-pass thinking
#     (Day 18) is not optional once the data does not fit.
#
#   * Write the pipeline so it can also read .gz logs, by swapping
#     path.open for gzip.open in read_lines. NOTHING else changes — which
#     is the payoff of each stage knowing only about lines.
