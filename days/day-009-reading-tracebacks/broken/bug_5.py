"""BUG 5 — average response time from a log.

This is the important one.

The traceback will point at the division. The division is not the bug. The
bug is four lines above it, and it is silent. Fix the line the traceback
names and you will have a program that reports a wrong answer instead of
crashing, which is strictly worse.

Find out WHY the divisor is zero before you touch it.
"""

LOG = """GET /home 200 118ms
GET /about 200 92ms
POST /login 302 240ms
GET /assets/app.css 200 12ms
GET /missing 404 8ms"""

lines = LOG.splitlines()

# Keep only the successful requests: status 200.
# (`[... for ... if ...]` is a comprehension — Day 22. Read it as "the lines
#  where the condition holds".)
successful = [line for line in lines if " 200ms " in line]

total_ms = 0
count = len(successful)

print(f"log lines:        {len(lines)}")
print(f"successful:       {count}")

durations = [int(line.split()[-1].replace("ms", "")) for line in successful]
total_ms = sum(durations)

average = total_ms / count

print(f"average response: {average:.1f}ms")
