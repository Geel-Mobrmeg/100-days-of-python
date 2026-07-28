# Day 010 — Milestone: command-line quiz 🏁

**Phase 1 · Foundations** · ~150 minutes

> **Today's build:** a ten-question quiz that asks, scores, gives feedback per answer and prints a final grade.

**Concepts:** combining everything so far · program structure · scoring · user feedback

---

## The article

### What a milestone day is

Every tenth day is longer, and it has no new syntax in it. The job is to take the ten days you
just did and build one thing that needs all of them at once — which is a completely different
skill from following a lesson, and the one that actually transfers.

You have, as of last night: values and types, strings and their methods, f-strings and format
specs, arithmetic, input, booleans, and the ability to read an error. That is genuinely enough to
write a real program. Today proves it.

### The constraint, and why it is a gift

You do not have `if`. You do not have loops. You do not have functions or lists.

That sounds like it makes a *scored quiz* impossible. It does not — and working out why is the
most valuable two hours in this phase, because it forces you to learn the two techniques that
experienced programmers reach for *instead of* a conditional, long after they have one.

**Technique 1: a bool is an index.**

`True` is `1` and `False` is `0` (Day 2). Sequences are indexed by integers (Day 3). Therefore:

```python
VERDICT = ("WRONG", "RIGHT")
print(VERDICT[correct])       # picks one, no `if` anywhere
```

**Technique 2: a lookup table replaces a chain of comparisons.**

Instead of ten `elif`s deciding a grade, one string where position *N* holds the grade for a
score of *N*:

```python
GRADES = "FFFFFDDCBAA"
#         0    5 7 9 10
grade = GRADES[score]
```

Read that carefully, because this is the point of the day. The version you would write tomorrow
with `if`/`elif` is six lines, and the policy is *spread across* those six lines. The table
version puts the entire grading policy on **one line, where it can be read, checked and changed
by someone who does not read Python.** That is not a workaround for missing syntax. It is
frequently the better design, and it stays better after Day 11.

**Technique 3: a string times a bool appears or vanishes.**

```python
print(("    " + explanation + "\n") * (not correct), end="")
```

`"abc" * False` is `""`. So the explanation prints when the answer was wrong and produces
*nothing at all* when it was right. Note the newline is inside the multiplied string and
`end=""` turns off print's own — otherwise the "nothing" case still emits a blank line.

### Program structure

This is the other half of a milestone: the code has to survive being read. Use the four-part
shape, and keep the parts apart:

```
CONFIGURE   constants at the top, named, in one place
INPUT       gather everything from the outside world
COMPUTE     pure arithmetic on what you gathered — no printing
REPORT      print. Nothing here calculates anything.
```

The discipline that matters is keeping COMPUTE and REPORT separate. A value computed *inside* a
`print()` call cannot be checked, reused, or tested (Day 57). Every build from here on separates
them, and today is where the habit starts.

### Scoring and comparing answers

**Never compare raw input.** Normalise both sides identically:

```python
ok = given.strip().lower() in ACCEPTED.split("|")
```

Note `.split("|")` rather than a bare `in` against the string. `"ru" in "true|yes"` is `True` —
a substring match — and that bug will silently mark wrong answers correct. Splitting into whole
options fixes it. This is a real bug that ships regularly.

**Accept more than one right answer.** `7` and `seven` are the same answer. So are `%` and
`modulo`. A quiz that rejects a correct answer on a formatting technicality teaches the student
nothing except that the quiz is broken.

**Score with `sum` over bools.** `ok_1 + ok_2 + ...` is the count of correct answers, because
bools are ints. `all()` and `any()` collapse them further.

### Feedback that is worth reading

The difference between a quiz and a scored quiz is that a scored quiz **tells you why**. Three
rules:

1. **Report every question**, not just the failures. Seeing nine ticks is the reward.
2. **Show what the user actually typed**, with `!r` so whitespace is visible. Half of all "that
   was right!" complaints are a trailing space.
3. **Explain only the wrong ones.** An explanation next to a correct answer is noise.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The four-part program shape, bool-as-index, lookup tables, and safe answer comparison. |
| `build.py`  | The full quiz. Ten questions, per-answer feedback, grade, and a closing line chosen by score. |

```bash
python3 lesson.py
python3 build.py

# score 6/10 without typing:
printf 'cairo\nParis\n7\ntrue\nzero\nfalse\n1969\nlist\n42\npython\n' | python3 build.py

# perfect paper:
printf 'cairo\nParis\nseven\ntrue\n0\nfalse\n%%\nstr\n512\nValueError\n' | python3 build.py
```

---

## The brief

Build it yourself before opening `build.py`. It must:

- [ ] ask ten questions, one at a time
- [ ] accept answers case-insensitively and ignore surrounding whitespace
- [ ] accept more than one phrasing for at least three questions
- [ ] mark each answer right or wrong **without using `if`**
- [ ] show what the user typed, and explain only the wrong answers
- [ ] print a score, a percentage and a letter grade
- [ ] use a lookup table for the grade, not a comparison chain
- [ ] never crash, whatever is typed — including an empty answer

---

## Common mistakes

**`"ru" in "true|yes"` is `True`.** Split into options first. This is the bug most likely to be
in your version.

**Comparing raw input.** `"Cairo " == "cairo"` is `False`. Normalise both sides.

**Computing inside `print()`.** Then you cannot reuse or check the value.

**`print("")` when you wanted nothing.** It emits a blank line. Put the `\n` inside the
multiplied string and use `end=""`.

**A grade chain that is wrong at the boundary.** With a lookup table this class of bug cannot
happen, which is the argument for it.

**Ten copies of a line, edited nine times.** Ask yourself how confident you are that copy seven
is right. This is what tomorrow and Day 13 are for.

---

## Extend it

1. Count the repetition. Roughly 60 lines expressing 3 ideas — the honest cost of having no loop.
2. **On Day 13**, put the questions in a list and collapse the whole thing to about twelve lines.
   Keep both versions and diff them. That diff is the clearest argument for loops you will ever
   see.
3. **On Day 11**, add feedback that differs in *structure*, not just content. Then notice the
   `GRADES` table is still better than an `if` chain, and leave it alone. Knowing which to
   convert is the skill.
4. **On Day 24**, move the questions into a dict. **On Day 55**, into a JSON file — at which
   point the program contains no quiz content at all and you have written a quiz *engine*.

---

## Phase 1 checklist

You are about to leave Foundations. Before you do:

- [ ] I can write and run a Python file from the terminal without thinking about it
- [ ] I know what type every value in my program is
- [ ] I can slice a string and format one into a column
- [ ] I know why `input()` needs converting and how that conversion fails
- [ ] I can write a compound boolean condition and predict its value
- [ ] I read the last line of a traceback first
- [ ] `ruff check` is silent on my code
- [ ] **My quiz runs, scores correctly, and does not crash on any input**

Tomorrow you get `if`. It will feel like being handed a power tool.
