# Day 040 — Milestone: your own toolkit 🏁

**Phase 4 · Functions & modular code** · ~150 minutes

> **Today's build:** package your best helpers into one importable library with documentation and examples.

**Concepts:** API design · docstrings · package structure · a demo script

---

## The article

### What this milestone is testing

Not whether you can write functions. Whether you can produce something **somebody else could use
without asking you a question** — which turns out to be four artefacts and one discipline, none of
them clever.

The code has existed since Day 31. Today is about everything around it.

### 1. A public surface is a promise

```python
__all__ = ["clamp", "slugify", "chunked", "timer", ...]
```

Python has no private. `mytoolkit.text` is reachable whether you like it or not. `__all__` is
where you write down **which names you promise will keep working** — and by omission, which ones
you are free to rename tomorrow.

Without it, everything you ever wrote is public by accident and you can never change any of it.

This is also what makes `__init__.py` worth having: callers write `from mytoolkit import slugify`
and never learn it lives in `text.py`, so that file can be split or renamed without breaking
anyone.

### 2. A docstring is an interface

One imperative line saying what the function **returns**. If you cannot write it, the function
does more than one thing.

`truncate`'s docstring says the limit *includes* the suffix. The other choice is equally
defensible and the caller cannot guess — so not saying is a bug, not a documentation gap.

### 3. Examples that are also tests

```python
>>> chunked([1, 2, 3, 4, 5], 2)
[[1, 2], [3, 4], [5]]
```

Doctests are documentation, examples and tests at once — and, crucially, **they cannot go stale**,
because the suite fails the moment the documented behaviour changes. Prose rots silently; a
doctest cannot. This package has 28.

### 4. State the limits

The package README has a "Known limits" section listing five things it does badly. Writing it is
uncomfortable and it is the most useful part of the document:

- every one of those would otherwise arrive as a bug report;
- a limit you have written down is a **decision**, one you have not is an accident you will end up
  defending out of embarrassment;
- it tells a reader in thirty seconds whether this is for them, which is the README's actual job.

**Can you name three things your code does badly?** If not, you do not know it well enough to have
shipped it.

### 5. Rules you can check beat rules you can state

The package claims five design rules. `build.py` verifies every one:

| Rule | How it is checked |
|---|---|
| return, never print | captures stdout across five calls, asserts it is empty |
| never mutate an argument | passes a list, inspects it afterwards |
| raise on bugs, sentinel on expected absence | asserts `clamp()` raises and `percent(5, 0)` returns `'n/a'` |
| docstring on everything public | walks `__all__` |
| no dependencies | parses the package with `ast`, compares to `sys.stdlib_module_names` |

That last check was **wrong the first time it ran**: it grepped for lines starting with `from ` and
matched the words "from here:" inside a docstring, reporting a dependency that did not exist. A
checker that cries wolf gets switched off, and then it protects nothing — so it was rewritten to
parse the syntax tree.

The acceptance run also caught a genuine bug: `pyproject.toml` said `1.0.0` while `__init__.py`
still said `0.3.0`. Two sources of truth had drifted within a day of being created.

**A README that says "no dependencies" and a check that parses the imports are different kinds of
statement.** Only one of them is still true in six months.

### 6. Versioning is a promise about breakage

- **MAJOR** — an incompatible change to anything in `__all__`
- **MINOR** — new functionality, existing calls unaffected
- **PATCH** — a fix that changes no documented behaviour

Reaching 1.0.0 is not a celebration, it is a commitment: from here, changing what `truncate()`
counts is a 2.0.0, not a tidy-up. Which is exactly why `__all__` matters — it is the precise list
of things a major version protects.

---

## The code

| File | What it is |
|---|---|
| `mytoolkit/` | The package: 5 submodules, 16 public names, zero dependencies. |
| `mytoolkit/README.md` | The package's own documentation — install, API tables, design rules, known limits. |
| `pyproject.toml` | Makes it installable, with a console script and tool config. |
| `tests/test_toolkit.py` | 32 tests. |
| `examples/report.py` | Six functions doing one real job. |
| `lesson.py` | What separates code that works from code others can use. |
| `build.py` | 28 acceptance checks that verify every promise the package makes. |

```bash
python3 lesson.py
python3 build.py                 # the acceptance report
python3 -m mytoolkit             # the package as a command
python3 examples/report.py
python3 -m pytest tests/ -q      # 32 tests
python3 -m pytest --doctest-modules mytoolkit/ -q   # 28 doctests
pip install -e .                 # then import it from anywhere
```

---

## The brief

Build yours before reading `build.py`. It must have:

- [ ] at least ten functions you have genuinely rewritten more than once
- [ ] a package with submodules and a thin `__init__.py` defining `__all__`
- [ ] a docstring on every public function, saying what it returns
- [ ] doctests that pass
- [ ] a README with install, usage, an API table and **known limits**
- [ ] at least one runnable example
- [ ] a test suite
- [ ] a `pyproject.toml`
- [ ] `python3 -m yourpackage` doing something useful
- [ ] **zero dependencies**, or a written reason for each one

---

## Common mistakes

**No `__all__`.** Everything is public forever.

**Logic in `__init__.py`.** It runs on every import.

**Documentation that promises what the code does not do.** Check it mechanically.

**A README with no limits section.** Every limit becomes a bug report.

**Two sources of truth for the version.** They drift — this one drifted in a day.

**Examples that no longer run.** Run them in the acceptance check.

**Shipping without a test.** "It worked when I wrote it" is not a claim anyone can act on.

---

## Extend it

1. **Break a promise on purpose** — make `slugify()` print, or add a dependency — and confirm the
   acceptance report catches it. If it does not, the check is decorative.
2. Add a function of your own with a docstring, doctests, a README row and a test. Count how many
   places a new public name has to appear — that number is what a public surface costs.
3. `pip install -e .`, then import it from your home directory. That is the moment it stops being
   a folder and starts being a library.
4. Write the CHANGELOG a 1.0.0 implies, then decide what would make it 2.0.0.

---

## Phase 4 checklist

You are leaving Functions & modular code. Before you do:

- [ ] I return by default and print only at the edges
- [ ] I never use a mutable default argument
- [ ] I can write a wrapper that forwards any signature
- [ ] I understand closures and can say when one should be a class
- [ ] I choose comprehensions, loops or functional tools deliberately
- [ ] I reach for recursion on trees and loops on sequences
- [ ] I can write a decorator that takes arguments
- [ ] I use generators for anything large or streamed
- [ ] I can lay out a package and define its public surface
- [ ] **My library passes its own acceptance checks, and I broke one to prove they work**

Tomorrow: classes. Everything you built with closures and dicts gets a second, roomier form —
and Day 46 is about when *not* to use it.
