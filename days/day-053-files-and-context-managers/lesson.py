"""Day 053 — Files, and the `with` statement that makes them safe.

    python3 lesson.py

Everything happens in a scratch directory that is deleted at the end, so
this file can be run as many times as you like.
"""

import contextlib
import io
import locale
import os
import shutil
import sys
import tempfile
import tracemalloc

WIDTH = 76

WORK = tempfile.mkdtemp(prefix="day053-")
os.chdir(WORK)

# ---------------------------------------------------------------------------
# 1. The modes, and the one that eats your data
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. open() MODES':^{WIDTH}}")
print("=" * WIDTH)
print("""
  MODE   MEANING                            IF THE FILE EXISTS
  'r'    read (the default)                 fine — error if it does NOT
  'w'    write                              TRUNCATED TO ZERO, immediately
  'a'    append                             writes at the end
  'x'    exclusive create                   FileExistsError
  'r+'   read and write                     kept, cursor at the start
  'a+'   read and append                    kept, cursor at the end
  'rb'   / 'wb'   bytes, no decoding        for images, zips, anything binary

  THE ONE THAT BITES: 'w' truncates the moment open() returns, before you
  write a single byte. If your program then crashes, the file is empty and
  the old contents are gone.""")

with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("line one\nline two\n")

print(f"\n  wrote notes.txt        {os.path.getsize('notes.txt')} bytes")

f = open("notes.txt", "w", encoding="utf-8")     # noqa: SIM115 - the exhibit
print(f"  open(..., 'w') again   {os.path.getsize('notes.txt')} bytes"
      f"   <- nothing was written yet")
f.close()

print("""
  USE 'x' WHEN YOU MEAN "CREATE". It refuses to overwrite, which turns a
  silent data loss into a FileExistsError you can handle.""")

for attempt in (1, 2):
    try:
        with open("once.txt", "x", encoding="utf-8") as f:
            f.write("first writer wins\n")
        print(f"  attempt {attempt}: created")
    except FileExistsError:
        print(f"  attempt {attempt}: FileExistsError — refused to overwrite")


# ---------------------------------------------------------------------------
# 2. Why `with`
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. WHY `with`':^{WIDTH}}")
print("=" * WIDTH)


handles = {}


def without_with():
    f = open("risky.txt", "w", encoding="utf-8")   # noqa: SIM115 - the exhibit
    handles["no with"] = f
    f.write("half a record")
    int("boom")                                    # something goes wrong
    f.close()                                      # never reached


def with_with():
    with open("safe.txt", "w", encoding="utf-8") as f:
        handles["with"] = f
        f.write("half a record")
        int("boom")


for label, fn in [("no with", without_with), ("with", with_with)]:
    try:
        fn()
        outcome = "no exception"
    except ValueError:
        outcome = "ValueError raised"
    f = handles[label]
    print(f"  {label:<10}{outcome:<20}f.closed is {f.closed}"
          f"{'' if f.closed else '   <- still open'}")
    print(f"  {'':<10}{'':<20}{os.path.getsize(f.name)} bytes on disk")

print("""
  Both raised. Only the second CLOSED the file, and it closed it on the way
  out of the exception — no `finally` written by hand.

  WHAT "LEFT OPEN" ACTUALLY COSTS:
    * the buffer may never be flushed, so the last writes are lost
    * on Windows the file cannot be renamed or deleted by anyone
    * a loop over ten thousand files runs out of file descriptors

  CPython usually closes it when the object is garbage collected, which is
  why the bug hides in small scripts and appears in servers. Do not rely on
  it; it is not part of the language.

  MORE THAN ONE, IN ONE STATEMENT:

      with open('in.txt') as src, open('out.txt', 'w') as dst:
          ...

  ...and if you do not know how many until runtime, contextlib.ExitStack,
  which is what today's build uses.""")


# ---------------------------------------------------------------------------
# 3. Encodings
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. ENCODINGS — THE INVISIBLE PARAMETER':^{WIDTH}}")
print("=" * WIDTH)

TEXT = "café — naïve — 日本語 — 3€"

with open("utf8.txt", "w", encoding="utf-8") as f:
    f.write(TEXT)

print(f"\n  wrote (utf-8): {TEXT}")
print(f"  on disk:       {os.path.getsize('utf8.txt')} bytes for "
      f"{len(TEXT)} characters")

readings = [
    ("utf-8", "strict"),
    ("latin-1", "strict"),
    ("ascii", "strict"),
    ("ascii", "replace"),
    ("ascii", "ignore"),
]

print(f"\n  {'READ AS':<12}{'errors=':<10}RESULT")
for encoding, errors in readings:
    try:
        with open("utf8.txt", encoding=encoding, errors=errors) as f:
            result = f.read()[:34]
    except UnicodeDecodeError as exc:
        result = f"UnicodeDecodeError at byte {exc.start}"
    print(f"  {encoding:<12}{errors:<10}{result}")

print(f"""
  latin-1 NEVER raises — it maps all 256 byte values — so it silently
  produces mojibake and you find out three systems later. That is worse
  than the exception ascii gave you.

  ALWAYS PASS encoding=. Without it, Python 3.11 uses the LOCALE's
  encoding, which here is {locale.getpreferredencoding(False)!r} and on somebody else's machine is
  something else. The same script then reads the same file differently on
  two computers, which is a bug that cannot be reproduced.

  encoding='utf-8' unless you have a reason. errors='strict' (the default)
  unless you would genuinely rather have wrong text than an exception.""")


# ---------------------------------------------------------------------------
# 4. Reading: three ways, and their cost
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. READ IT ALL, OR A LINE AT A TIME':^{WIDTH}}")
print("=" * WIDTH)

LINES = 200_000
with open("big.txt", "w", encoding="utf-8") as f:
    for n in range(LINES):
        f.write(f"2026-03-{n % 28 + 1:02d} INFO  request {n} completed\n")

size = os.path.getsize("big.txt")


def whole_file():
    with open("big.txt", encoding="utf-8") as f:
        return sum(1 for _ in f.read().splitlines())


def all_lines():
    with open("big.txt", encoding="utf-8") as f:
        return len(f.readlines())


def streamed():
    with open("big.txt", encoding="utf-8") as f:
        return sum(1 for _ in f)


print(f"\n  the file: {LINES:,} lines, {size / 1e6:.1f} MB\n")
print(f"  {'HOW':<28}{'LINES':>10}{'PEAK MEMORY':>16}{'x FILE SIZE':>14}")
print("  " + "-" * (WIDTH - 4))
for label, fn in [(".read().splitlines()", whole_file),
                  (".readlines()", all_lines),
                  ("for line in f", streamed)]:
    tracemalloc.start()
    count = fn()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    shown = (f"{peak / 1e6:.1f} MB" if peak > 1e6 else f"{peak / 1e3:.0f} KB")
    print(f"  {label:<28}{count:>10,}{shown:>16}{peak / size:>13.3f}x")

print("""
  Same answer, three memory profiles. `for line in f` reads a buffer at a
  time and forgets each line as it goes, so it does not care whether the
  file is 8 MB or 8 GB.

  A FILE OBJECT IS AN ITERATOR. That is why `for line in f` works, and why
  it is the default way to read anything you did not create yourself.

  The lines keep their '\\n'. Use .rstrip('\\n'), not .strip(), unless you
  are sure leading whitespace is meaningless.""")


# ---------------------------------------------------------------------------
# 5. Writing safely
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. WRITING WITHOUT DESTROYING THE OLD VERSION':^{WIDTH}}")
print("=" * WIDTH)

with open("config.txt", "w", encoding="utf-8") as f:
    f.write("the good version\n")


def naive_rewrite(fail):
    """Truncates first, then fails. The old contents are gone."""
    try:
        with open("config.txt", "w", encoding="utf-8") as f:
            f.write("new ")
            if fail:
                raise RuntimeError("network died mid-write")
            f.write("version\n")
    except RuntimeError:
        pass


def atomic_rewrite(fail):
    """Writes a temporary file, then REPLACES in one atomic step."""
    temporary = "config.txt.tmp"
    try:
        with open(temporary, "w", encoding="utf-8") as f:
            f.write("new ")
            if fail:
                raise RuntimeError("network died mid-write")
            f.write("version\n")
        os.replace(temporary, "config.txt")        # atomic on POSIX and NT
    except RuntimeError:
        with contextlib.suppress(FileNotFoundError):
            os.remove(temporary)


for label, rewrite in [("naive", naive_rewrite), ("atomic", atomic_rewrite)]:
    with open("config.txt", "w", encoding="utf-8") as f:
        f.write("the good version\n")
    rewrite(fail=True)
    with open("config.txt", encoding="utf-8") as f:
        after = f.read().strip()
    print(f"  {label:<10}after a crash mid-write, config.txt is {after!r}")

print("""
  os.replace() is ATOMIC: at every instant the path points either at the
  whole old file or at the whole new one, never at half of either. Any
  other reader sees one or the other.

  THE PATTERN, worth memorising:
      write to path.tmp  ->  os.replace(path.tmp, path)

  contextlib.suppress(FileNotFoundError) above is `try/except/pass` with a
  name that says the omission was deliberate.""")


# ---------------------------------------------------------------------------
# 6. Writing your own context manager
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. `with` IS A PROTOCOL, NOT A FILE FEATURE':^{WIDTH}}")
print("=" * WIDTH)

events = []


class Section:
    """The two-method protocol, in full."""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        events.append(f"enter {self.name}")
        return self                       # what `as x` receives

    def __exit__(self, exc_type, exc_value, traceback):
        events.append(f"exit {self.name}"
                      f"{' (' + exc_type.__name__ + ')' if exc_type else ''}")
        return False                      # False = let the exception through


@contextlib.contextmanager
def section(name):
    """The same thing in six lines. Everything before yield is __enter__."""
    events.append(f"enter {name}")
    try:
        yield name
    finally:
        events.append(f"exit {name}")


with Section("outer"):
    with section("inner"):
        events.append("body")

print(f"\n  {' -> '.join(events)}")

events.clear()
try:
    with Section("guarded"):
        int("boom")
except ValueError:
    events.append("caught outside")
print(f"  {' -> '.join(events)}")

print("""
  __exit__ receives the exception, and its RETURN VALUE decides what
  happens next: False (or None) lets it continue, True SWALLOWS it. Return
  True only when suppressing is the manager's whole purpose — that is what
  contextlib.suppress does, and doing it by accident is how exceptions
  vanish.

  @contextmanager is the version you will actually write. The `finally` is
  not optional: without it, an exception in the body skips your cleanup.""")


# ---------------------------------------------------------------------------
# 7. Files that are not files
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  ANY FILE-LIKE OBJECT WORKS — WHICH IS WHY YOU CAN TEST THIS")
print("-" * WIDTH)


def count_errors(stream):
    """Takes a STREAM, not a path. Now it can be tested without a file."""
    return sum(1 for line in stream if "ERROR" in line)


with open("big.txt", encoding="utf-8") as f:
    from_disk = count_errors(f)

from_memory = count_errors(io.StringIO("ok\nERROR one\nERROR two\n"))

print(f"  from a real file      {from_disk}")
print(f"  from io.StringIO      {from_memory}   <- no file was created")
print(f"  from a list of lines  {count_errors(['ERROR x'])}")
print("""
  TAKE A STREAM, NOT A PATH, wherever you reasonably can. The caller can
  then hand you a file, a StringIO, stdin, a decompressed stream or a test
  fixture — and Day 58's tmp_path stops being necessary for half your
  tests.""")

print()
print("=" * WIDTH)
print("""  1. `with` always. It closes on the exception too.
  2. encoding='utf-8' always. The default is the LOCALE's.
  3. 'w' truncates immediately. 'x' refuses to overwrite.
  4. `for line in f` — constant memory, any file size.
  5. Write to .tmp, then os.replace(). Atomic.
  6. __exit__ returning True swallows the exception. Almost never do that.
  7. Take a stream, not a path.""")
print("=" * WIDTH)

os.chdir("/")
shutil.rmtree(WORK, ignore_errors=True)
print(f"\n(scratch directory {WORK} removed)", file=sys.stderr)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Open a file 'w', write, and kill the program before close() — with
#     and without `with`. Compare the file sizes.
#
#   * Write utf-8 and read it with encoding='latin-1'. Then do the reverse.
#     One raises and one lies; decide which you would rather debug.
#
#   * Make __exit__ return True and put an exception in the body. Watch it
#     disappear, and imagine finding that in somebody else's code.
#
#   * Read a 1 GB file with .readlines(). Then don't.
#
#   * Replace `os.replace` with `os.rename` and read the docs on what
#     happens when the destination exists on Windows.
