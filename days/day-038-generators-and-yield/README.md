# Day 038 — Generators and yield

**Phase 4 · Functions & modular code** · ~85 minutes

> **Today's build:** stream a 500 MB log file and count error lines without ever loading it into memory.

**Concepts:** `yield` · lazy evaluation · generator expressions · memory footprint · `itertools`

---

## The article

### Why this day exists

Every technique so far assumes the data fits in memory. Most real data does not — a log file, a
database export, a CSV of every transaction this year, an API that pages forever.

Generators are how Python handles data larger than RAM, and the mechanism is one keyword. The
build processes half a gigabyte in a few megabytes of memory, and the difference between the two
versions is a single word.

### 1. `yield`

```python
def count_to(n):
    for i in range(n):
        yield i
```

A function containing `yield` is a **generator function**. Calling it runs *no code at all* — it
returns a **generator object**. Code runs only when you ask for a value:

```python
gen = count_to(3)      # nothing has happened yet
next(gen)              # 0  — runs until the first yield, then FREEZES
next(gen)              # 1  — resumes where it stopped
next(gen)              # 2
next(gen)              # StopIteration
```

That freezing is the whole idea. `return` destroys the function's state; **`yield` suspends it** —
locals, position, everything — and resumes on the next request.

`for x in gen:` calls `next()` for you and stops at `StopIteration`.

### 2. Laziness, and what it buys

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")
```

That function works identically on a 2 KB file and a 500 GB one, because **only one line is ever
in memory**. The list version — `return [line for line in f]` — needs the whole file.

Three consequences:

- **Constant memory**, whatever the input size.
- **Results start immediately.** A list version does all the work before returning anything; a
  generator yields the first item after doing one item's work. That matters for anything
  interactive, and for pipelines where a later stage stops early.
- **Infinite sequences are possible.** `count()` can run forever, because nobody asks for all of
  it.

### 3. What you give up

Generators are **one-shot**. Once consumed, they are empty:

```python
gen = count_to(3)
list(gen)      # [0, 1, 2]
list(gen)      # []  ← gone
```

And they have **no length and no indexing**: `len(gen)` and `gen[0]` are both `TypeError`. You
cannot know how many items there are without consuming them, which is the price of not having
computed them.

If you need the data twice, either `list()` it (and accept the memory) or call the generator
function again (and accept the work). `itertools.tee` exists but buffers, so it does not save you.

### 4. Generator expressions

```python
squares = (n * n for n in numbers)          # lazy
squares = [n * n for n in numbers]          # eager
```

Round brackets instead of square (Day 22). Inside a function call the extra brackets can be
dropped:

```python
sum(n * n for n in numbers)          # never builds the list
any(line.startswith("ERROR") for line in read_lines(path))
```

`any()` and `all()` over a generator **short-circuit** — they stop reading at the first decisive
value. `any(...)` over a 500 MB file that has an error on line 3 reads three lines.

### 5. Pipelines

This is where generators become a design tool rather than a memory trick:

```python
lines    = read_lines(path)
stripped = (line.strip() for line in lines)
errors   = (line for line in stripped if "ERROR" in line)
parsed   = (parse(line) for line in errors)

for record in parsed:
    ...
```

Nothing has been read yet. The `for` at the bottom pulls one line all the way through the chain,
then the next. Each stage holds one item.

This is the Unix pipe model, and it composes the same way: each stage does one thing, stages can
be reordered or reused, and adding a stage costs one line and no memory.

### 6. `itertools`

The standard library's generator toolkit. The ones worth knowing today:

```python
islice(gen, 10)              # the first 10 — the lazy `[:10]`
chain(a, b, c)               # several iterables as one
takewhile(pred, gen)         # stop at the first failure
dropwhile(pred, gen)         # skip until the first success
groupby(gen, key)            # group CONSECUTIVE items (Day 25's warning)
count(), cycle(), repeat()   # infinite
tee(gen, 2)                  # two independent copies (buffers!)
```

`islice` is how you look at the front of an infinite or enormous generator without consuming it
all.

### 7. Other things to know

**`yield from`** delegates to another generator — essential for recursive generators (Day 36's
tree, lazily):

```python
def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)
```

**`return` in a generator** stops it; the value becomes `StopIteration.value` and is almost never
used.

**Generators are iterators, but not all iterators are generators.** Anything with `__next__` is an
iterator; a generator is one you got from `yield`.

**Closing matters.** A generator holding an open file releases it when garbage collected, or when
you call `.close()`. Inside the generator, the `with` block's cleanup runs then — which is why the
`with` belongs *inside* the generator function, as above.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `yield` and suspension, laziness, one-shot behaviour, expressions, pipelines, `itertools`, `yield from`. |
| `build.py`  | Generates a large log file, then processes it both ways and measures the actual memory used. |

```bash
python3 lesson.py
python3 build.py             # ~60 MB log by default (fast)
python3 build.py 500         # the full 500 MB — takes a couple of minutes
```

---

## Common mistakes

**Consuming a generator twice.** The second pass is empty.

**`len()` on a generator.** `TypeError`.

**`list()`-ing it out of habit.** You just undid the point.

**Returning a list from a function that should yield.** One word's difference, whole-file memory.

**Opening the file outside the generator.** It closes before consumption, or never.

**Expecting `itertools.groupby` to group non-adjacent items.** It groups runs.

**Reading a whole file with `.read()` or `.readlines()`.** Iterate the file object instead.

---

## Exercises

1. Write `count_to(n)` and step through it with `next()` until `StopIteration`.
2. Prove a generator is one-shot.
3. Build a three-stage pipeline over a file and add a fourth stage without changing the others.
4. Use `islice` to take the first 5 of an infinite generator.
5. Compare `sum([n*n for n in range(10_000_000)])` with the generator version, watching memory.
6. Write a recursive generator that walks a nested list, using `yield from`.

---

## Checklist

- [ ] I know calling a generator function runs no code
- [ ] I can explain how `yield` differs from `return`
- [ ] I know generators are one-shot and have no length
- [ ] I write pipelines of generator expressions
- [ ] I use `islice` rather than `list()[:n]`
- [ ] My log processor's memory does not grow with the file size
