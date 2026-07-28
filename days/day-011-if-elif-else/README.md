# Day 011 — if, elif, else

**Phase 2 · Control flow** · ~65 minutes

> **Today's build:** a grade calculator that turns any percentage into a letter, with boundary cases handled.

**Concepts:** branching · nesting · guard clauses · the ternary expression

---

## The article

### Why this day exists

Yesterday you built a scored quiz without a single conditional. You should have found it
uncomfortable — that discomfort is the argument for today.

Everything you have written so far runs every line, in order, every time. `if` is the first
thing that changes that, and it is the foundation of every program that reacts to anything.

The syntax takes ten minutes. The rest of the day is about the two things that actually go
wrong: **boundaries** and **nesting**.

### 1. The syntax

```python
if temperature > 30:
    print("hot")
elif temperature > 20:
    print("warm")
else:
    print("cold")
```

Three mechanical points, all of which produce errors on your first day:

- **The colon.** Every `if`, `elif` and `else` ends with one. Forgetting it is a `SyntaxError`.
- **The indentation is the block.** Python has no braces; the indented lines *are* the body.
  Four spaces, consistently. Mixing tabs and spaces is an `IndentationError` with a famously
  unhelpful message.
- **`else` has no condition.** `else something:` is a syntax error. `else` is "everything not
  already matched", by definition.

You can have any number of `elif`s and at most one `else`, and the `else` is optional.

The condition is evaluated for **truthiness** (Day 7), so it does not have to be a comparison:

```python
if items:              # "if there are any items"
if not name:           # "if the name is empty"
```

### 2. Order matters, and this is where the bugs are

`elif` chains are evaluated **top to bottom, and stop at the first match.** That single fact
causes more grading bugs than anything else in this course:

```python
# WRONG
if score >= 50:
    grade = "D"       # everything ≥ 50 stops here. Nobody ever gets an A.
elif score >= 90:
    grade = "A"
```

The rule: **order your branches from most specific to least specific**, which for numeric bands
means from the highest threshold down.

Because the chain stops at the first match, you never need to re-test what an earlier branch
already excluded:

```python
if score >= 90:
    grade = "A"
elif score >= 80:            # already known to be < 90. Do NOT write `and score < 90`.
    grade = "B"
```

Writing that redundant upper bound is not just noise — it is a second thing that can be wrong,
and it hides the actual boundary.

### 3. Boundaries — the whole difficulty of today

Every threshold has an edge, and the edge is where the bug lives. For "80 and above is a B":

| Written | 79.9 | 80 | 80.1 |
|---|---|---|---|
| `score > 80` | B? no | **no — bug** | yes |
| `score >= 80` | no | **yes** | yes |

**`>` versus `>=` at a boundary is the single most common off-by-one in real software.** The
defence is not care, it is testing the boundary specifically: for every threshold *N*, check
*N−1*, *N*, and *N+1*. Today's build does exactly that, in the file, so you can see it fail.

Two related traps:

- **Gaps.** If one branch is `score >= 80` and the next is `score < 79`, then 79.5 matches
  nothing and your variable is never assigned — a `NameError` far away from the cause.
- **Floats.** `if total == 0.3` is a coin flip (Day 5). Compare with a tolerance, or use
  `Decimal`.

### 4. Nesting, and guard clauses

Conditionals nest:

```python
if logged_in:
    if is_admin:
        show_admin_panel()
    else:
        show_user_panel()
else:
    show_login()
```

That is already at the edge of readable, and it is only two levels. Deep nesting — the
"arrow anti-pattern" — is the most common way ordinary code becomes unreadable:

```python
if a:
    if b:
        if c:
            do_the_thing()          # the actual work, four levels in
```

The fix is a **guard clause**: handle the exceptional cases first, leave, and let the main path
sit unindented at the bottom.

```python
if not a:
    return          # or continue / raise / print-and-exit
if not b:
    return
if not c:
    return
do_the_thing()      # the point of the function, at indent level zero
```

Guard clauses need something to leave *with*. You have `continue` and `break` from Day 14, and
`return` from Day 31. For now, use the flattening ideas you can: combine conditions with `and`
(Day 7), and compute a boolean first with a name that explains it:

```python
can_proceed = a and b and c
if can_proceed:
    do_the_thing()
```

**Naming the condition is usually the biggest readability win available.** `if is_eligible:`
beats a three-line boolean expression every time, and it can be printed when you are debugging.

### 5. The ternary expression

For choosing between two *values*, Python has a one-line conditional:

```python
status = "adult" if age >= 18 else "child"
```

Read it in the middle first: *the condition, then what you get if it holds, then otherwise.* It
is an **expression** — it produces a value — so it can go anywhere a value can, including inside
an f-string:

```python
print(f"You are an {'adult' if age >= 18 else 'child'}")
```

Use it when both branches are short values. Do not use it for side effects, do not nest it, and
do not use it when the branches are complicated. The moment you have to read it twice, it should
have been a normal `if`.

### 6. When *not* to use `if`

Yesterday's techniques do not stop being good today:

```python
grade = GRADES[score]                    # lookup table beats 6 elifs
verdict = ("WRONG", "RIGHT")[correct]    # bool as index
```

The rule of thumb: if your `if`/`elif` chain is doing nothing but *mapping an input to an
output*, a table is usually clearer, and it puts the whole policy in one place. If the branches
do genuinely different *work*, use `if`.

Today's build has both, side by side, so you can judge.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Syntax, ordering, boundaries, nesting, guard clauses, ternary. |
| `build.py`  | The grade calculator — two implementations, and a boundary test that proves them equivalent. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Missing colon.** `if x > 5` → `SyntaxError: expected ':'`.

**`IndentationError: unexpected indent`** — inconsistent spacing, or tabs mixed with spaces.

**`elif` chain in the wrong order.** Test the highest threshold first, or everyone gets a D.

**`>` where you meant `>=`.** Test `N-1`, `N`, `N+1` for every threshold.

**`if x = 5`** — `SyntaxError`. Assignment, not comparison.

**`if x == 1 or 2:`** — always true. Write `x in (1, 2)`.

**A variable assigned in only some branches.** If no branch matches, it is never defined, and
the `NameError` appears far from the cause. Assign a default first.

**`else if`** — that is C. Python spells it `elif`.

---

## Exercises

1. Write the grade chain with the branches in the wrong order and confirm nobody gets an A.
   Understanding *why* takes ten seconds and inoculates you for good.
2. For every threshold in your grade calculator, print the result at `N-1`, `N` and `N+1`. Any
   surprise is a bug.
3. Rewrite this without nesting: `if a: if b: print("yes")`. Two ways.
4. Convert three of yesterday's bool-as-index expressions to `if`, then decide honestly which
   version you prefer for each. They will not all go the same way.
5. Write a FizzBuzz for 1–20 using an `if`/`elif` chain. Get the ordering right first time by
   thinking about which condition is most specific.
6. Write a condition that classifies a number as negative, zero, or positive. Then write it as
   a nested ternary, look at it, and change it back.

---

## Checklist

- [ ] I never forget the colon or the indent
- [ ] I order numeric bands from the highest threshold down
- [ ] I do not re-test what an earlier branch already excluded
- [ ] I test `N-1`, `N` and `N+1` at every boundary
- [ ] I name complicated conditions instead of inlining them
- [ ] I can say when a lookup table beats an `if` chain
