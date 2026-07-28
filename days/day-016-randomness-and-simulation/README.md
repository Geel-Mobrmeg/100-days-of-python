# Day 016 — Randomness and simulation

**Phase 2 · Control flow** · ~75 minutes

> **Today's build:** a dice simulator that rolls ten thousand times and plots the distribution as text bars.

**Concepts:** the `random` module · `randint` & `choice` · `shuffle` · seeding for reproducibility

---

## The article

### Why this day exists

Randomness makes programs interesting: games, tests, sampling, shuffling, simulations. It also
makes them *unrepeatable*, which is a serious problem the first time a bug only appears one run
in fifty.

So today has two halves. The first is the four functions you will use. The second is **seeding**,
which is the thing that separates people who use randomness from people who can debug it.

### 1. The functions

```python
import random

random.randint(1, 6)          # 1..6 INCLUSIVE, both ends
random.randrange(1, 7)        # 1..6 — stop excluded, like range()
random.random()               # float, 0.0 <= x < 1.0
random.uniform(1.5, 3.5)      # float in a range
random.choice(["a","b","c"])  # one item from a sequence
random.choices(pop, k=5)      # k items, WITH replacement
random.sample(pop, k=5)       # k items, WITHOUT replacement
random.shuffle(my_list)       # reorders IN PLACE — returns None
```

Two of those have sharp edges that catch everybody:

**`randint` includes both ends.** This is the *only* range-like thing in Python that does.
`randint(1, 6)` is a die; `range(1, 6)` is 1–5. When you mean "index into a list", `randrange` is
the safer habit because it matches everything else.

**`shuffle` mutates and returns `None`.**

```python
cards = shuffle(cards)      # WRONG — cards is now None
random.shuffle(cards)       # right — cards is shuffled where it sits
cards = random.sample(cards, len(cards))   # if you want a shuffled COPY
```

`x = list.method()` returning `None` is a shape you will meet again on Day 21 with `.sort()` and
`.append()`. Python's convention: **methods that change a thing in place return `None`**, so that
you cannot accidentally believe you got a copy.

`choices` vs `sample`: `choices` can return the same item twice (rolling a die five times);
`sample` cannot (dealing five cards). Picking the wrong one produces a subtle, plausible bug.

### 2. Seeding — the important half

Python's randomness is **pseudo**-random: a deterministic sequence produced from a starting
number called the **seed**. Same seed, same sequence, every time, on every machine.

```python
random.seed(42)
print(random.randint(1, 6))    # 6, on any machine, forever
print(random.randint(1, 6))    # 1
random.seed(42)
print(random.randint(1, 6))    # 6 again — the sequence restarted
```

By default Python seeds from the system entropy pool, so each run differs. That is right for a
game and wrong for almost everything else you will do this year:

- **Debugging.** A bug that appears one run in fifty is nearly impossible to fix. Seed it, and
  the failing run happens every time.
- **Tests** (Day 57). A test that sometimes fails is worse than no test.
- **Reproducible results.** Anyone re-running your simulation should get your numbers.

The rule: **seed when you need to reproduce, do not seed when you need unpredictability.** And
never use the `random` module for anything security-related — passwords, tokens, session ids.
It is fast and predictable by design, and given a few outputs an attacker can compute the rest.
Use `secrets` instead:

```python
import secrets
secrets.token_hex(16)
secrets.randbelow(100)
```

Prefer a private generator over the module-level functions when it matters, because the module
level ones share one global state that any library can reseed under you:

```python
rng = random.Random(42)
rng.randint(1, 6)
```

### 3. Simulation, and what "random" actually looks like

A simulation answers a question by running the thing many times and counting. It is the tool for
problems where the maths is hard or you do not trust your maths.

The core loop:

```python
hits = 0
for _ in range(TRIALS):
    if experiment():
        hits += 1
print(hits / TRIALS)
```

Three things worth knowing about the results:

**Small samples lie.** Ten coin flips giving 7 heads is completely normal. A hundred giving 70 is
suspicious. The error shrinks with **√n**, which means *a hundred times the trials for ten times
the accuracy* — the reason simulations run for millions of iterations rather than thousands.

**Real randomness clumps.** In 100 flips, a run of six identical results is more likely than not.
Humans asked to fake a random sequence produce too few long runs, and this is exactly how faked
data gets caught.

**Two dice are not one die twice.** Rolling one d6 gives a flat distribution. Rolling two and
summing gives a triangle peaking at 7, because there are six ways to make 7 and one way to make
2. Today's build plots both, and the difference between them is the whole reason board games use
2d6.

### 4. Drawing a histogram in text

You have everything you need from Day 4:

```python
bar = "#" * int(count / max_count * bar_width)
print(f"{label:>4} {count:>6,} {percent:>6.2%} {bar}")
```

Scale to the **largest count**, not to the total, or every bar will be one character long. And
put the numbers next to the bar — a bar chart with no figures is decoration.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every function, the `shuffle` trap, seeding, `choices` vs `sample`, and how sample size affects error. |
| `build.py`  | The dice simulator: 1d6, 2d6, 3d6, a fairness check, and a seeded run that reproduces exactly. |

```bash
python3 lesson.py
python3 build.py
python3 build.py 1000000
python3 build.py 10000 42     # seeded — identical output every time
```

---

## Common mistakes

**`cards = random.shuffle(cards)`** — now `None`. It shuffles in place.

**`randint(0, len(items))`** — off the end by one. `randint` includes both ends; use
`randrange(len(items))` or `random.choice(items)`.

**Using `choices` where you meant `sample`** — duplicates appear, and the bug looks like bad
data rather than bad code.

**Seeding inside a loop.** `random.seed(42)` on every pass produces the same "random" value every
time. Seed once, at the start.

**Concluding anything from 20 trials.** Run more.

**`random` for passwords or tokens.** Use `secrets`.

**Expecting no repeats.** In 23 people there is a better-than-even chance two share a birthday.
Clumping is what random looks like.

---

## Exercises

1. Roll a d6 ten times, then a thousand. Compare each face's share to 16.67%.
2. Seed with 42, print five numbers, reseed with 42, print five more. Confirm they match.
3. Shuffle a deck of 52 with `shuffle`, then produce a shuffled copy without touching the
   original. Two different tools.
4. Simulate the birthday problem: how many people before two share a birthday? Run it 10,000
   times and take the average. The answer is near 23.
5. Estimate π by throwing darts at a square and counting those inside the inscribed circle.
   How many darts to get 3.14 reliably? (It is more than you expect — √n is brutal.)
6. Simulate the Monty Hall problem, both strategies, 100,000 times each. Believe the numbers.

---

## Checklist

- [ ] I know `randint` includes both endpoints and nothing else does
- [ ] I know `shuffle` returns `None`
- [ ] I can choose between `choices` and `sample` correctly
- [ ] I seed when I need reproducibility and not when I need unpredictability
- [ ] I use `secrets`, not `random`, for anything security-related
- [ ] My 2d6 histogram peaks at 7 and is symmetric
