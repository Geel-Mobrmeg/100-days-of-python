# Day 012 — while loops

**Phase 2 · Control flow** · ~70 minutes

> **Today's build:** a number guessing game that gives higher/lower hints and counts attempts.

**Concepts:** loop conditions · accumulators · sentinel values · avoiding infinite loops

---

## The article

### Why this day exists

`if` lets a program choose. `while` lets it *keep going*. Between them they can express any
procedure a human could carry out by hand — which is not a figure of speech, it is a theorem, and
after today you have the whole set.

`while` is also the loop that can hang. Learning where the hang comes from, on purpose, on the
day you meet it, is much cheaper than learning it at midnight in three weeks.

### 1. The shape

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

Three parts, and **every `while` loop has all three**. Naming them is the whole skill:

1. **Setup** — the variable exists and has a starting value, *before* the loop.
2. **Condition** — checked *before every pass*, including the first. If it is false at the start,
   the body never runs at all.
3. **Progress** — something in the body changes a value the condition depends on.

Miss the setup and you get a `NameError`. Miss the progress and the loop never ends. That is the
entire failure surface, and it is worth checking those three things explicitly every time you
write one until it becomes automatic.

### 2. Infinite loops

```python
count = 0
while count < 5:
    print(count)          # count never changes. This runs forever.
```

**`Ctrl-C` stops a runaway program.** Learn it now, before you need it. It raises
`KeyboardInterrupt`, which you will handle properly on Day 51.

The three ways loops fail to end:

```python
while count < 5:
    count -= 1            # progress in the WRONG DIRECTION

while total != 100:
    total += 3            # STEPS OVER the target: 99, 102, 105... never equal

while count < 5:
    if x:
        count += 1        # progress only on SOME paths
```

The second one is the subtle one and it is why **`<` and `>` are safer loop conditions than
`!=` and `==`**. `while total != 100` requires hitting 100 exactly; `while total < 100` cannot
miss.

There is one *deliberate* infinite loop, and it is idiomatic:

```python
while True:
    answer = input("> ")
    if answer == "quit":
        break
```

`while True` with a `break` inside is the standard shape for "loop until something happens" —
especially for input validation, where you cannot know the condition before you have asked once.
Day 14 covers `break` properly; today you may use it in this one pattern.

### 3. Accumulators

The single most common loop shape in programming: a variable outside the loop that collects
something from each pass.

```python
total = 0                       # 0 is the identity for addition
while ...:
    total += value

product = 1                     # 1 is the identity for multiplication
count = 0
lines = []                      # Day 21
```

**Start the accumulator at the value that means "nothing yet".** Zero for a sum, one for a
product, empty for a collection. Starting a sum at 1 is a bug that produces a *plausible* wrong
answer, which is the worst kind.

For running minimum and maximum, there is a trap:

```python
lowest = 0                      # WRONG — no positive number will ever beat it
lowest = None                   # right: "nothing yet", and test for it
lowest = float("inf")           # also right, and often neater
```

Day 18 goes deeper into loop patterns. Today, get the initial value right.

### 4. Sentinel values

A **sentinel** is a value that means "stop", mixed in with the data:

```python
while True:
    line = input("Enter a value (or 'done'): ").strip()
    if line.lower() == "done":
        break
    total += float(line)
```

Choose a sentinel that **cannot be a real value**. `"done"` is safe for numbers; `0` is not safe
for a list of numbers that might legitimately contain zero; `-1` is not safe for temperatures.
Using a real value as a sentinel is a classic bug in data-processing code, and the classic
symptom is a file that stops being read halfway through because row 400 happened to be `-1`.

Empty input — the user just pressing Enter — is a good sentinel for interactive prompts, because
it is easy to type and it is rarely meaningful data.

### 5. Validation loops

This is the pattern Day 6 was missing:

```python
while True:
    raw = input("Height in metres: ").strip()
    if raw.replace(".", "", 1).isdigit():
        height = float(raw)
        break
    print("  Please enter a number, like 1.75.")
```

Ask, test, break on success, complain and go round again on failure. Three lines of structure
that turn a program that crashes on bad input into one that cannot be broken by typing.

Give the user a way out. A validation loop with no escape is a trap: accept an empty line, or a
`quit`, or count the attempts and give up.

### 6. `while` versus `for`

Tomorrow you get `for`, and you should then use it almost always. The division:

- **`for`** — you know what you are iterating over: a sequence, a range, a file. This is 90% of
  loops.
- **`while`** — you are looping until a *condition changes*, and you cannot know in advance how
  many passes that takes: user input, a game loop, a retry, a convergence.

If you find yourself writing `i = 0; while i < len(items): ... i += 1`, that is a `for` loop with
extra opportunities for bugs. Tomorrow.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The three parts, the three ways to hang, accumulators, sentinels, validation loops. |
| `build.py`  | The guessing game — plus a computer-plays-itself mode that proves the strategy. |

```bash
python3 lesson.py
python3 build.py
printf '50\n25\n37\n43\n40\n41\n' | python3 build.py
```

---

## Common mistakes

**Forgetting the progress step.** The loop runs forever. `Ctrl-C`.

**`while` with `!=` on a stepped value.** `while n != 100` with `n += 3` never stops. Use `<`.

**The accumulator declared inside the loop.** It resets every pass and always ends up holding
one item's worth.

**`lowest = 0` for a running minimum.** Nothing positive will ever be lower. Use `None` or
`float("inf")`.

**A sentinel that is also valid data.** `-1` stops a temperature log early on a cold day.

**Off-by-one from `<` vs `<=`.** `while i < 5` runs five times; `while i <= 5` runs six.

**A validation loop with no escape.** Always give the user a way to quit.

---

## Exercises

1. Write a countdown from 10 to 1 then "Liftoff". Now do it with `<` instead of `>` and note how
   the loop simply never runs, rather than erroring.
2. Sum the numbers 1 to 100 with a `while` loop. Check against `n * (n + 1) / 2`.
3. Write a loop that ends with `!=` and a step of 3 aiming at 100. Watch it hang. `Ctrl-C`. Fix
   it by changing one character.
4. Ask for numbers until the user types `done`, then report count, total, mean, min and max. Get
   the initial values for min and max right.
5. Write a validation loop for an integer between 1 and 10 that gives up after 3 attempts and
   tells the user why.
6. Collatz: from any positive integer, halve it if even, else `3n + 1`, until it reaches 1. Count
   the steps. Try 27 — it takes 111.

---

## Checklist

- [ ] I can name the setup, condition and progress in any loop I write
- [ ] I know `Ctrl-C` stops a runaway program
- [ ] I prefer `<` and `>` to `!=` in loop conditions
- [ ] My accumulators start at the value meaning "nothing yet"
- [ ] My sentinels cannot collide with real data
- [ ] My guessing game counts attempts correctly — including the winning one
