# Day 039 — Modules and packages

**Phase 4 · Functions & modular code** · ~80 minutes

> **Today's build:** split your utilities into a proper package with submodules and a clean public surface.

**Concepts:** import mechanics · `__name__ == "__main__"` · `__init__.py` · project layout · relative imports

---

## The article

### Why this day exists

`toolkit.py` (Day 31) plus `decorators.py` (Day 37) is already two files that want to be one
thing. By Day 60 you will have a dozen. The question of *how a Python project is laid out* has a
boring standard answer, and knowing it saves you from the two failure modes: everything in one
2,000-line file, or forty files with circular imports.

### 1. What `import` actually does

```python
import json
```

Python finds the module, **executes it top to bottom exactly once**, caches the result in
`sys.modules`, and binds the name.

The "exactly once" matters. Import a module twice and the second import is a dictionary lookup —
its top-level code does not re-run. That is why module-level code should define things and not
*do* things.

The forms:

```python
import json                    # json.dumps(...)
import numpy as np             # np.array(...)
from pathlib import Path       # Path(...)        — the name only
from mypkg import a, b         # both names
from mypkg import *            # never
```

`from x import *` dumps unknown names into your namespace, shadows silently, and makes it
impossible to tell where anything came from. `__all__` limits what it takes — which is a reason to
define `__all__`, not a reason to use `import *`.

### 2. Where Python looks

`sys.path`, in order: the script's own directory, then `PYTHONPATH`, then the standard library,
then site-packages. First match wins — which is why a file called `random.py` in your project
breaks `import random` everywhere.

**Never name a file after a standard library module.** `email.py`, `json.py`, `types.py`,
`string.py`, `test.py` are all traps.

### 3. `if __name__ == "__main__":`

Every module has a `__name__`. It is `"__main__"` when run directly and the module's own name when
imported.

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

Without that guard, everything at module level runs **on import** — so importing your script to
reuse one function also runs the whole program. With it, a file can be both a library and a
command.

This is why every function in `toolkit.py` returns rather than prints (Day 31): the printing lives
under the guard, and the library part is importable.

### 4. Packages

A **package** is a directory of modules with an `__init__.py`:

```
mytoolkit/
    __init__.py       the public surface
    text.py
    numbers.py
    collections.py
    decorators.py
```

`__init__.py` runs when the package is imported. Its job is to define **what the outside world
sees**:

```python
from .text import slugify, truncate, initials
from .numbers import clamp, percent

__all__ = ["slugify", "truncate", "initials", "clamp", "percent"]
__version__ = "0.1.0"
```

Now `from mytoolkit import slugify` works, and the fact that it lives in `text.py` is an
implementation detail you are free to change.

**Keep `__init__.py` thin.** Imports and metadata, no logic. It runs on every import of anything
in the package, so slow work there slows down everything.

An empty `__init__.py` is fine — then callers write `from mytoolkit.text import slugify`, which is
more explicit and equally valid. Since 3.3 you can omit it entirely (a "namespace package"), but
for a normal library, include it.

### 5. Relative vs absolute imports

```python
from .text import slugify          # relative — same package
from ..other import thing          # relative — parent package
from mytoolkit.text import slugify # absolute
```

**Use relative imports inside a package** (they survive the package being renamed) and **absolute
imports from outside it**. PEP 8 prefers absolute for clarity; relative-within-package is the
common modern compromise, and it is what this build uses.

Relative imports only work **inside a package**. Running `python3 mytoolkit/text.py` directly fails
with `ImportError: attempted relative import with no known parent package` — because that file is
then `__main__`, not part of a package. Use `python3 -m mytoolkit.text` instead.

### 6. Circular imports

`a.py` imports `b`, `b` imports `a` → `ImportError` or a half-built module.

Fixes, best first:

1. **Move the shared thing** into a third module both can import. Usually the real fix, and it
   usually reveals that the design was muddled.
2. **Import inside the function** rather than at module level — defers it to call time.
3. **Import the module, not the name** (`import b` then `b.thing`), which tolerates partial
   initialisation.

If two modules genuinely need each other, they are one module.

### 7. Project layout

```
myproject/
    pyproject.toml
    README.md
    src/
        mytoolkit/
            __init__.py
            text.py
    tests/
        test_text.py
```

The `src/` layout is the current recommendation. Its point: your tests cannot accidentally import
the package from the working directory — they import the *installed* one, so you test what you
ship. Day 97 uses this.

`pip install -e .` installs it in editable mode, so imports work from anywhere while edits take
effect immediately.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Import mechanics, `sys.modules`, the `__main__` guard, shadowing demonstrated, circular imports. |
| `mytoolkit/` | Day 31 and Day 37's code, reorganised into a real package with four submodules. |
| `build.py` | Uses the package the way a consumer would, and shows what the layout bought. |

```bash
python3 lesson.py
python3 build.py
python3 -m mytoolkit          # the package as a command
```

---

## Common mistakes

**A file named after a stdlib module.** `random.py` breaks `import random`.

**No `__main__` guard.** Importing the file runs the program.

**Logic in `__init__.py`.** It runs on every import.

**`from x import *`.** Unknown names, silent shadowing.

**Running a package module directly.** Use `python3 -m package.module`.

**Circular imports.** Move the shared piece out.

**`__pycache__` in git.** Add it to `.gitignore`.

---

## Exercises

1. Print `__name__` in a file, run it, then import it.
2. Create `json.py` in a folder, import `json` there, and read the error.
3. Split your toolkit into three submodules and a thin `__init__.py`.
4. Show that a module's top-level code runs once, however many times you import it.
5. Create a circular import on purpose, read the error, then fix it three ways.
6. Add `__main__.py` so `python3 -m mypackage` runs something.

---

## Checklist

- [ ] I know `import` executes a module once and caches it
- [ ] Every script of mine has a `__main__` guard
- [ ] My `__init__.py` defines the public surface and nothing else
- [ ] I use relative imports inside a package
- [ ] I never name a file after a stdlib module
- [ ] `from mytoolkit import slugify` works and hides where it lives
