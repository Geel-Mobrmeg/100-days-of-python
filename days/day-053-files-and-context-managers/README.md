# Day 053 — Files and context managers

**Phase 6 · Robust code** · ~80 minutes

> **Today's build:** a log splitter that breaks one large file into daily files without loading it all at once.

**Concepts:** `open()` modes · `with` statements · encodings · reading line by line · writing safely

---

## The article

### Why this day exists

Everything so far has lived and died inside one process. Today your programs start touching data
that outlives them — and the filesystem is where beginners lose data for real, not hypothetically.

Three things do it: `'w'` truncating before you write, a missing `encoding=`, and a file left open
when an exception went past.

### 1. The modes

| Mode | Meaning | If the file exists |
|---|---|---|
| `'r'` | read (default) | fine — error if it does *not* |
| `'w'` | write | **truncated to zero, immediately** |
| `'a'` | append | writes at the end |
| `'x'` | exclusive create | `FileExistsError` |
| `'r+'` | read and write | kept, cursor at the start |
| `'rb'` / `'wb'` | bytes, no decoding | for images, zips, anything binary |

`'w'` truncates the moment `open()` returns, before a single byte is written. `lesson.py` shows it:
18 bytes on disk, `open(..., 'w')`, 0 bytes — and nothing has been written yet. Crash there and the
old contents are gone.

**Use `'x'` when you mean "create".** It turns a silent overwrite into a `FileExistsError` you can
handle.

### 2. Why `with`, measured

```python
def without_with():
    f = open("risky.txt", "w", encoding="utf-8")
    f.write("half a record")
    int("boom")          # something goes wrong
    f.close()            # never reached
```

```
no with   ValueError raised   f.closed is False   <- still open
                              0 bytes on disk
with      ValueError raised   f.closed is True
                              13 bytes on disk
```

Both raised. Only the second closed the file — and it closed it *on the way out of the exception*,
with no hand-written `finally`. The first also lost the write, because the buffer was never flushed.

What "left open" actually costs: unflushed buffers, files that cannot be renamed or deleted on
Windows, and a loop over ten thousand files that runs out of file descriptors. CPython usually
closes it at garbage-collection time, which is exactly why the bug hides in small scripts and
appears in servers.

Several at once:

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    ...
```

...and when you do not know how many until runtime, `contextlib.ExitStack` — which is what today's
build is built around.

### 3. `encoding=` is not optional

```
READ AS     errors=   RESULT
utf-8       strict    café — naïve — 日本語 — 3€
latin-1     strict    cafÃ© â€” naÃ¯ve â€” æ—¥æœ¬èªž
ascii       strict    UnicodeDecodeError at byte 3
ascii       replace   caf�� ��� na��ve ���
ascii       ignore    caf  nave    3
```

**`latin-1` never raises.** It maps all 256 byte values, so it silently produces mojibake and you
find out three systems later. That is worse than the exception `ascii` gave you.

Without `encoding=`, Python 3.11 uses the *locale's* encoding — so the same script reads the same
file differently on two machines, which is a bug that cannot be reproduced. Pass `encoding="utf-8"`
unless you have a reason.

`errors=` is a judgement, per file, not per program: `'strict'` for a config file or a bank
statement, `'replace'` for a log where salvaging 99.99% beats crashing.

### 4. Read a line at a time

`lesson.py` reads the same 8.3 MB file three ways:

| how | lines | peak memory | × file size |
|---|---:|---:|---:|
| `.read().splitlines()` | 200,000 | 27.8 MB | 3.355× |
| `.readlines()` | 200,000 | 19.7 MB | 2.380× |
| `for line in f` | 200,000 | **22 KB** | **0.003×** |

Same answer, three memory profiles. `for line in f` reads a buffer at a time and forgets each line
as it goes, so it does not care whether the file is 8 MB or 8 GB.

**A file object is an iterator.** That is why the loop works, and why it is the default way to read
anything you did not create yourself.

Lines keep their `\n`. Use `.rstrip("\n")`, not `.strip()`, unless you are sure leading whitespace is
meaningless.

### 5. Writing without destroying the old version

```python
with open("config.txt.tmp", "w", encoding="utf-8") as f:
    f.write(new_contents)
os.replace("config.txt.tmp", "config.txt")     # atomic
```

```
naive     after a crash mid-write, config.txt is 'new'
atomic    after a crash mid-write, config.txt is 'the good version'
```

`os.replace()` is atomic: at every instant the path points at the whole old file or the whole new
one, never at half of either. Any other reader sees one or the other.

**Write to `path.tmp`, then `os.replace(path.tmp, path)`.** Memorise it — it is the difference
between a config file that survives a power cut and one that does not.

### 6. `with` is a protocol

```python
class Section:
    def __enter__(self):
        return self                        # what `as x` receives
    def __exit__(self, exc_type, exc_value, traceback):
        return False                       # False = let the exception through
```

```python
@contextlib.contextmanager
def section(name):
    ...setup...
    try:
        yield name
    finally:
        ...cleanup...
```

`__exit__` receives the exception, and its **return value decides what happens next**: `False`/`None`
lets it continue, `True` **swallows** it. Return `True` only when suppressing is the manager's whole
purpose — that is what `contextlib.suppress` does, and doing it by accident is how exceptions vanish.

In `@contextmanager` the `finally` is not optional: without it, an exception in the body skips your
cleanup entirely.

### 7. Take a stream, not a path

```python
def count_errors(stream):
    return sum(1 for line in stream if "ERROR" in line)
```

That function works on a file, an `io.StringIO`, `sys.stdin`, a decompressed stream, or a list of
strings — and it needs no temporary file to test. Half the fixtures you would otherwise write on
Day 58 disappear.

### 8. Today's build: `ExitStack`

Splitting a log by day has a shape that forces the issue. You need one output file per day, you do
not know how many days there are until you have read the file, and you refuse to hold the file in
memory. Three constraints, and `ExitStack` is what satisfies all three:

```python
with contextlib.ExitStack() as stack:
    source = stack.enter_context(open(path, encoding="utf-8", errors="replace"))
    outputs = {}
    for line in source:                            # constant memory
        ...
        if day not in outputs:
            outputs[day] = stack.enter_context(open(dest / f"{day}.log", "w",
                                                    encoding="utf-8"))
        outputs[day].write(line)
```

`enter_context()` registers each close for later, so the handle stays open and is still closed
exactly once — including if the loop raises. The build measures the alternatives:

| | peak memory | × file | time |
|---|---:|---:|---:|
| read all, then group | 16.4 MB | 2.0× | |
| stream + `ExitStack` | **261 KB** | 0.031× | 0.12s |
| stream + reopen per line | (constant) | | 0.26s / 20k lines |

Grouping costs 63× the memory and scales with the file — a 10 GB log would want 20 GB of RAM.
Reopening per line keeps the memory but pays for an `open()` and a `close()` syscall per line, about
14× slower. `ExitStack` gets both.

### 9. Real logs are not clean

The build's synthetic log contains what real ones do, and each needs a decision:

- **continuation lines** — a traceback has no timestamp of its own. A splitter that only looks for
  stamps drops it. This one remembers the last day it saw and keeps the traceback with the line it
  belongs to.
- **blank lines** — dropped, and counted.
- **an undecodable byte** — something upstream wrote latin-1 into a UTF-8 file. With
  `errors='strict'` the program dies 120,000 lines in, having already written most of the output —
  the worst of both outcomes.

### 10. Checking to the byte

The build's most useful check is not the line count:

```
input                         8,288,049 bytes
minus  76 dropped blank lines           -76
plus   50 replacements x 2 bytes        +100
= output                      8,288,073 bytes
```

**The output is larger than the input.** Each undecodable byte was one byte on the way in and became
U+FFFD, which is three bytes in UTF-8. Being able to account for that to the byte is the difference
between "it seems to work" and knowing nothing was truncated, doubled, or written with the wrong
newline — a line count would not have noticed a lost final line with no trailing newline.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Modes, `with` proved with `f.closed`, five encodings on one file, memory of three read styles, atomic replace, `__enter__`/`__exit__`, streams instead of paths. |
| `build.py`  | The splitter: 120k lines into 14 daily files, three implementations compared on memory and time, and 12 checks including byte-exact accounting. |

```bash
python3 lesson.py
python3 build.py                        # generates a demo log and splits it
python3 build.py /path/to/app.log out   # your own log
```

Both files work in a temporary directory and clean up after themselves.

---

## Common mistakes

**No `with`.** The file stays open when an exception goes past, and the buffer may never flush.

**No `encoding=`.** Works on your machine, fails on someone else's.

**`errors='ignore'` to make a problem go away.** It makes the *message* go away.

**`'w'` when you meant `'a'` or `'x'`.** Truncation happens before you write.

**`.readlines()` on something large.** Ask what happens when the file is 100× bigger.

**`.strip()` when you meant `.rstrip("\n")`.** Leading whitespace is often data.

**Writing in place.** A crash mid-write leaves half a file where a good one used to be.

**`__exit__` returning `True` by accident.** Exceptions vanish.

**Taking a path where a stream would do.** Every caller now needs a real file, and so does every
test.

---

## Exercises

1. Write a file with `with`, and again with an exception before `close()`. Compare `f.closed` and
   the byte counts.
2. Write UTF-8, read it as latin-1, and read it as ascii. One lies and one raises.
3. Read a large file three ways and measure the peak with `tracemalloc`.
4. Implement the write-to-temp-then-`os.replace` pattern and interrupt it halfway.
5. Write a context manager with `__enter__`/`__exit__`, then the same one with `@contextmanager`.
6. Make `__exit__` return `True` and watch an exception disappear.
7. Use `ExitStack` to open a number of files decided at runtime.
8. Rewrite a function that takes a path so it takes a stream, then test it with `io.StringIO`.

---

## Checklist

- [ ] I always use `with`
- [ ] I always pass `encoding=`
- [ ] I know `'w'` truncates immediately and `'x'` refuses to
- [ ] I read line by line unless I have a reason not to
- [ ] I write to a temporary file and `os.replace` it
- [ ] I can write a context manager both ways
- [ ] I know what returning `True` from `__exit__` does
- [ ] I take streams instead of paths where I can
