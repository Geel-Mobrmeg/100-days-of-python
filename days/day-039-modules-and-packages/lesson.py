"""Day 039 — Modules and packages.

    python3 lesson.py

Sections 3 and 5 write throwaway files into a temporary directory and run
them as separate processes, because "what happens when you shadow the
standard library" cannot be demonstrated safely inside a running program.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

WIDTH = 72


def run_in(directory, filename, source):
    """Write a file into `directory` and run it, returning its output."""
    path = Path(directory) / filename
    path.write_text(source)
    result = subprocess.run(
        [sys.executable, str(path)], capture_output=True, text=True,
        cwd=directory,
    )
    return (result.stdout + result.stderr).strip()


# ---------------------------------------------------------------------------
# 1. import executes a module ONCE and caches it
# ---------------------------------------------------------------------------

print(f"{'modules already loaded':<34}{len(sys.modules):>{WIDTH - 34}}")
print(f"{'is json loaded?':<34}{str('json' in sys.modules):>{WIDTH - 34}}")

import json                                    # noqa: E402 - to show the effect

print(f"{'after import json':<34}{str('json' in sys.modules):>{WIDTH - 34}}")
print(f"{'same object every time':<34}"
      f"{str(json is sys.modules['json']):>{WIDTH - 34}}")

print("""
Python FINDS the module, EXECUTES it top to bottom exactly once, CACHES it
in sys.modules, and BINDS the name. Import it again and the second import
is a dictionary lookup — the top-level code does NOT re-run.

Which is why module-level code should DEFINE things and not DO things.""")


# ---------------------------------------------------------------------------
# 2. Where Python looks
# ---------------------------------------------------------------------------

print("sys.path, in order (first match wins):")
for entry in sys.path[:5]:
    print(f"  {entry or '(the script directory)'}")
print("  ...")
print("""
  1. the running script's own directory      <- this is the dangerous one
  2. PYTHONPATH
  3. the standard library
  4. site-packages

FIRST MATCH WINS, and your own directory is first.""")


# ---------------------------------------------------------------------------
# 3. SHADOWING — a file named after a stdlib module
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "random.py").write_text("VALUE = 'this is not the stdlib'\n")
    output = run_in(tmp, "app.py", """
import random
try:
    print("randint gave", random.randint(1, 6))
except AttributeError as e:
    print("AttributeError:", e)
print("what got imported:", random.__file__)
""")

print("with a file called random.py sitting next to the script:")
for line in output.splitlines():
    print(f"  {line}")

print("""
  Python found YOUR random.py first and imported it instead. Every library
  in the process that uses `random` now breaks, and the traceback points
  at THEIR code, not yours.

  NEVER name a file after a stdlib module: random.py, json.py, email.py,
  types.py, string.py, test.py, collections.py, io.py, code.py.

  That is why this package's collections module is called containers.py.""")


# ---------------------------------------------------------------------------
# 4. __name__ and the __main__ guard
# ---------------------------------------------------------------------------

print(f"__name__ in this file, run directly: {__name__!r}")

with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "greeter.py").write_text('''
print(f"    greeter.py top level ran, __name__ = {__name__!r}")

def greet(name):
    return f"Hello, {name}"

if __name__ == "__main__":
    print("    ...and the __main__ block ran too")
''')
    print("\nrunning greeter.py directly:")
    print(run_in(tmp, "run_it.py",
                 "import subprocess, sys; "
                 "subprocess.run([sys.executable, 'greeter.py'])"))

    print("\nIMPORTING greeter.py instead:")
    print(run_in(tmp, "importer.py",
                 "import greeter\n"
                 "print('    imported. greet(\"Ada\") =', greeter.greet('Ada'))"))

print("""
  Same file. Run directly, __name__ is "__main__" and the block fires. On
  import, __name__ is "greeter" and it does not — so you can reuse greet()
  without running the program.

  Without the guard, importing your script to borrow one function runs the
  whole thing. WITH it, a file is both a library and a command.

  This is why every function in Day 31's toolkit RETURNS rather than
  prints: the printing lives under the guard, the library part is
  importable.""")


# ---------------------------------------------------------------------------
# 5. CIRCULAR IMPORTS
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "alpha.py").write_text(
        "from beta import beta_thing\n"
        "def alpha_thing():\n    return 'alpha'\n"
    )
    Path(tmp, "beta.py").write_text(
        "from alpha import alpha_thing\n"
        "def beta_thing():\n    return 'beta'\n"
    )
    output = run_in(tmp, "circular.py", "import alpha\n")

print("alpha imports beta, beta imports alpha:")
for line in output.splitlines()[-3:]:
    print(f"  {line}")

print("""
  THE FIXES, best first:

  1. MOVE THE SHARED THING into a third module both import. Usually the
     real fix, and it usually reveals the design was muddled.
  2. IMPORT INSIDE THE FUNCTION, deferring it to call time.
  3. IMPORT THE MODULE, NOT THE NAME — `import beta` then `beta.thing`,
     which tolerates a partially initialised module.

  If two modules genuinely need each other, they are one module.""")


# ---------------------------------------------------------------------------
# 6. The package in this folder
# ---------------------------------------------------------------------------

import mytoolkit                               # noqa: E402 - the demonstration

print(f"{'mytoolkit version':<34}{mytoolkit.__version__:>{WIDTH - 34}}")
print(f"{'public names':<34}{len(mytoolkit.__all__):>{WIDTH - 34}}")
print(f"{'slugify actually lives in':<34}"
      f"{mytoolkit.slugify.__module__:>{WIDTH - 34}}")
print(f"{'but you import it from':<34}{'mytoolkit':>{WIDTH - 34}}")

print("""
  mytoolkit/
      __init__.py     the PUBLIC SURFACE — imports and metadata only
      numbers.py      clamp, percent, human_bytes, duration
      text.py         truncate, slugify, initials
      containers.py   chunked, unique, dig
      decorators.py   timer, retry, cache, validated
      __main__.py     makes `python3 -m mytoolkit` work

  Callers write `from mytoolkit import slugify`. That it lives in text.py
  is an implementation detail, and text.py could be split in two tomorrow
  without breaking anyone. THAT is what __init__.py buys.

  Relative imports (`from .text import slugify`) inside the package;
  absolute imports from outside it. Relative ones survive a rename.""")


# ---------------------------------------------------------------------------
# 7. Layout
# ---------------------------------------------------------------------------

print("""
THE STANDARD LAYOUT (Day 97 ships one)

    myproject/
        pyproject.toml
        README.md
        src/
            mytoolkit/
                __init__.py
                text.py
        tests/
            test_text.py

The src/ layout exists for one reason: your tests CANNOT accidentally
import the package from the working directory. They import the INSTALLED
one, so you test what you ship. `pip install -e .` makes edits take effect
immediately.""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Create json.py in a folder and import json there.
#   * Delete the __main__ guard from a script and import it.
#   * Add `print("loading")` to mytoolkit/__init__.py and import three
#     different submodules. It prints once.
#   * Build the circular import yourself and fix it all three ways.
#   * Run `python3 mytoolkit/__main__.py` directly and read the
#     ImportError. Then `python3 -m mytoolkit`, which works. (text.py runs
#     fine either way — it has no relative imports to resolve, so there is
#     nothing to fail. The error is about relative imports, not about
#     package files in general.)
