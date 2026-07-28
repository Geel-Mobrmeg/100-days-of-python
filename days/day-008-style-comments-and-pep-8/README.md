# Day 008 — Style, comments and PEP 8

**Phase 1 · Foundations** · ~60 minutes

> **Today's build:** take a deliberately ugly 60-line script and refactor it until ruff is silent.

**Concepts:** naming conventions · docstrings · line length · `black` · `ruff`

---

## The article

### Why this day exists

You have written seven days of code. Some of it you could not read back today. That is not a
character flaw, it is the normal result of writing code with no conventions — and it compounds,
because every hour spent re-reading your own work is an hour not spent learning.

Style is not about being tidy. It is about **making the shape of the code carry information**, so
that a reader — including you, in a fortnight — spends attention on the logic instead of on the
formatting. The industry settled this argument years ago, and the settlement has a name.

### 1. PEP 8

PEP 8 is the official Python style guide. It is worth reading once, end to end; it is shorter
than you expect. The parts you will use every day:

**Naming.**

| Thing | Convention | Example |
|---|---|---|
| variable, function | `lower_snake_case` | `weight_kg`, `parse_row` |
| constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| class | `CapWords` | `BankAccount` |
| "internal, don't touch" | leading underscore | `_cache` |

Three single-character names are **banned outright**: `l`, `O` and `I`. In most fonts they are
indistinguishable from `1`, `0` and `1`. This is not pedantry; `l = 1` is a genuinely unreadable
line of code.

**Whitespace.** Four spaces per indent, never tabs. Spaces around binary operators and after
commas, none inside brackets, none before a call's parenthesis:

```python
x = a + b            # not  x=a+b
f(a, b)              # not  f( a,b )
items[0]             # not  items [ 0 ]
```

An exception worth knowing, because `black` does it and it looks wrong at first: around an
operator of *higher* priority you may drop the spaces to show the grouping — `bmi = w / h**2`.

**Line length.** PEP 8 says 79; most modern projects use 88 (the `black` default) or 100. Pick
one and let the tool enforce it. The point is not the number — it is that a line long enough to
need scrolling is a line hiding something.

**Imports.** One per line, at the top, grouped: standard library, then third party, then your
own, with a blank line between the groups.

```python
import json          # not  import os, sys
import os

import requests

from mypackage import helper
```

Never `from module import *`. It dumps unknown names into your file, shadows things silently,
and makes it impossible to tell where a name came from.

### 2. Comments and docstrings

The rule that matters: **comments explain *why*, code explains *what*.**

```python
x = x + 1                 # increment x        ← worthless, says what the code says
x = x + 1                 # compensate for the 0-based index in the report  ← useful
```

A comment that restates the code is worse than no comment, because it is a second thing to keep
in sync and it will drift. When you feel the urge to explain *what* a line does, the better fix
is usually a name: `is_plausible = ...` needs no comment.

Commented-out code should be deleted. Git remembers it (Day 69). Leaving it means every future
reader has to wonder whether it matters.

A **docstring** is a string literal as the first statement of a module, function or class. It is
not a comment — it is stored on the object and shown by `help()`:

```python
"""Parse one delimited user record and report it."""
```

Use triple quotes even for one line. One-line docstrings say what the thing does, in the
imperative, ending in a full stop. Day 31 covers function docstrings properly.

### 3. `black` — formatting, decided

`black` is an *opinionated* formatter: it reformats your file and offers you almost no options.
That sounds obnoxious and is its entire value. Once a team adopts it, formatting arguments stop,
because there is nothing left to argue about.

```bash
pip install black
black .              # reformat everything, in place
black --check .      # report, change nothing — this is what CI runs
black --diff file.py # show me what you would do
```

Run it, look at what it changed, and get used to writing code that it will not have to touch.
You will find your own style converging on it within a week.

### 4. `ruff` — the linter

A formatter fixes how code *looks*. A **linter** finds things that are wrong: unused imports,
undefined names, shadowed builtins, comparisons to `True`, mutable default arguments. `ruff` is
the modern one — it replaces `flake8`, `isort`, `pyupgrade` and a dozen others, and it is fast
enough that there is no excuse not to run it on save.

```bash
pip install ruff
ruff check .              # find problems
ruff check --fix .        # fix the safely-fixable ones
ruff format .             # it also formats, black-compatibly
```

Configure it once, in `pyproject.toml` at the root of your project:

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "N", "UP", "C4", "SIM", "B"]
```

Those eight codes are a good default: pycodestyle errors and warnings, pyflakes, naming,
pyupgrade, comprehensions, simplification, and bugbear. Add rules as you meet them; do not start
with everything switched on or you will spend a day arguing with it.

**The linter is not always right.** When it flags something you meant, silence that one line
with a reason:

```python
import config  # noqa: F401  — imported for its side effects
```

A bare `# noqa` with no code and no reason is how a codebase goes quiet and stays broken.

### 5. What a refactor is

The build is the point of the day, and it has one rule: **the output must not change.**

Refactoring means improving the structure of code without altering its behaviour. If the output
changes, you did not refactor, you rewrote — and the commit message claiming otherwise is how
"tiny cleanup" PRs take down production.

So the exercise is verified mechanically:

```bash
python3 ugly.py  > /tmp/before.txt
python3 build.py > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt      # must be empty
ruff check build.py                       # must be silent
```

`ugly.py` in this folder runs correctly and produces the right answer. It has thirteen ruff
violations and roughly ten more problems ruff cannot see. Fix it yourself before reading
`build.py`, and keep the diff empty the whole way.

---

## The code

| File | What it does |
|---|---|
| `ugly.py` | The starting point: works perfectly, reads terribly. 13 ruff errors. |
| `lesson.py` | Every convention above, shown as before/after pairs. |
| `build.py`  | The finished refactor — identical output, ruff-silent, black-clean. |

```bash
python3 lesson.py
ruff check --isolated --select E,F,W,N,UP,C4,SIM,B ugly.py    # 13 errors
ruff check --isolated --select E,F,W,N,UP,C4,SIM,B build.py   # silent
diff <(python3 ugly.py) <(python3 build.py) && echo "behaviour unchanged"
```

If `ruff` is not installed: `pip install ruff black`.

---

## Common mistakes

**Fixing style and logic in one commit.** Now nobody can review either. Separate commits, always.

**Running `black` on a repo that has never had it.** One enormous diff that buries real history.
Do it as its own commit, and record the hash in `.git-blame-ignore-revs`.

**Naming a variable `list`, `str`, `id`, `type` or `sum`.** Ruff's builtin rules catch this.

**`from decimal import *`.** You now have `Context`, `Clamped`, `getcontext` and forty other
names in your file, and no reader can tell where any of them came from.

**Treating the linter as an authority.** It is a very fast, very literal colleague. Sometimes it
is wrong. Silence it with a reason, not with a bare `# noqa`.

**Comments that restate the code.** `# add one to x` above `x += 1`. Delete it.

---

## Exercises

1. Refactor `ugly.py` yourself without looking at `build.py`. Keep the diff empty at every step.
2. Run `ruff check --fix` on a copy of `ugly.py`. How many of the thirteen does it fix by itself?
   Why can it not fix the rest?
3. Run `black --diff ugly.py` and read the output. Note everything it changed that ruff had not
   complained about — formatting and linting are different jobs.
4. Go back to your Day 5 or Day 7 build and run ruff on it. Fix what it finds.
5. Write a `pyproject.toml` in the repository root with the config from the article, then confirm
   `ruff check` picks it up without the `--isolated` flag.
6. Find one comment in your own earlier code that explains *what* instead of *why*. Delete it and
   improve a name until the comment is unnecessary.

---

## Checklist

- [ ] I use `lower_snake_case` for variables and `UPPER_SNAKE_CASE` for constants
- [ ] I never use `l`, `O` or `I` as names
- [ ] My imports are one per line, at the top, and none is `*`
- [ ] My comments say why, and I deleted the ones that said what
- [ ] `ruff check` is silent on my refactor
- [ ] `diff` between the old and new output is empty
