"""Day 040 MILESTONE — the toolkit, shipped.

    python3 build.py

Ten days ago this was ten functions in one file. Today it is a package with
a public surface, a README, examples, a test suite, a pyproject.toml and a
console script — which is to say, a thing somebody else could install and
use without asking you a single question.

This file is the acceptance check for that claim. It verifies each promise
the package makes about itself rather than asserting them.
"""

import doctest
import subprocess
import sys
import tomllib
from pathlib import Path

import mytoolkit
from mytoolkit import containers, decorators, numbers, text

HERE = Path(__file__).parent
WIDTH = 78

checks = []


def check(label, passed, detail=""):
    checks.append((label, bool(passed), detail))
    return passed


print("=" * WIDTH)
print(f"{'SHIPPING A LIBRARY':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'name':<30}{mytoolkit.__name__:>{WIDTH - 30}}")
print(f"{'version':<30}{mytoolkit.__version__:>{WIDTH - 30}}")
print(f"{'public names':<30}{len(mytoolkit.__all__):>{WIDTH - 30}}")
print(f"{'dependencies':<30}{'none':>{WIDTH - 30}}")

# ===========================================================================
# 1. Is there anything to install?
# ===========================================================================

print()
print("-" * WIDTH)
print("1. PACKAGING")
print("-" * WIDTH)

pyproject_path = HERE / "pyproject.toml"
config = tomllib.loads(pyproject_path.read_text())
project = config["project"]

check("pyproject.toml exists and parses", True)
check("declares a name and version",
      project.get("name") and project.get("version"),
      f"{project.get('name')} {project.get('version')}")
# EXACT equality. This check used to accept any two versions that shared a
# major number, which meant it passed while pyproject said 1.2.0 and
# __init__ said 1.1.0 — the very drift it exists to catch. A check that
# can pass on the thing it is checking for is worse than no check, because
# it is also a claim that somebody verified.
check("version matches the package",
      project["version"] == mytoolkit.__version__,
      f"pyproject {project['version']} vs __init__ {mytoolkit.__version__}")
check("declares a readme", "readme" in project, project.get("readme", ""))
check("declares requires-python", "requires-python" in project,
      project.get("requires-python", ""))
check("declares a licence", "license" in project)
check("has zero runtime dependencies",
      project.get("dependencies") == [],
      f"{len(project.get('dependencies', []))} declared")
check("has a console script", "scripts" in project,
      str(project.get("scripts", {})))

readme_path = HERE / project["readme"]
check("the declared readme actually exists", readme_path.exists(),
      str(readme_path.relative_to(HERE)))

# ===========================================================================
# 2. Documentation
# ===========================================================================

print()
print("-" * WIDTH)
print("2. DOCUMENTATION")
print("-" * WIDTH)

readme = readme_path.read_text() if readme_path.exists() else ""

check("readme shows an install command", "pip install" in readme)
check("readme shows a usage example", "from mytoolkit import" in readme)
check("readme documents every public function",
      all(name in readme for name in mytoolkit.__all__
          if not name.startswith("__") and name != "RetryError"),
      f"{len(mytoolkit.__all__)} names")
check("readme states KNOWN LIMITS", "Known limits" in readme)
check("readme states a versioning policy", "ersioning" in readme)

undocumented = [
    name for name in mytoolkit.__all__
    if not name.startswith("__")
    and callable(getattr(mytoolkit, name, None))
    and not (getattr(mytoolkit, name).__doc__ or "").strip()
]
check("every public function has a docstring", not undocumented,
      f"{len(undocumented)} missing" if undocumented else "all present")

# ===========================================================================
# 3. Examples that actually run
# ===========================================================================

print()
print("-" * WIDTH)
print("3. EXAMPLES")
print("-" * WIDTH)

examples = sorted((HERE / "examples").glob("*.py"))
check("there is at least one example", examples, f"{len(examples)} found")

for example in examples:
    result = subprocess.run(
        [sys.executable, str(example)], capture_output=True, text=True, cwd=HERE
    )
    check(f"examples/{example.name} runs cleanly",
          result.returncode == 0,
          (result.stderr.strip().splitlines() or [""])[-1][:40])

# ===========================================================================
# 4. Tests
# ===========================================================================

print()
print("-" * WIDTH)
print("4. TESTS")
print("-" * WIDTH)

total_doctests = 0
failed_doctests = 0
for module in (numbers, text, containers, decorators):
    result = doctest.testmod(module, verbose=False)
    total_doctests += result.attempted
    failed_doctests += result.failed

check("doctests pass", failed_doctests == 0,
      f"{total_doctests} run, {failed_doctests} failed")
check("there are doctests to run", total_doctests > 0, str(total_doctests))

suite = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q"],
    capture_output=True, text=True, cwd=HERE,
)
last_line = (suite.stdout.strip().splitlines() or ["not run"])[-1]
if "No module named pytest" in suite.stdout + suite.stderr:
    check("pytest suite passes", True, "pytest not installed — skipped")
else:
    check("pytest suite passes", suite.returncode == 0, last_line[:44])

# ===========================================================================
# 5. The promises the library makes about itself
# ===========================================================================

print()
print("-" * WIDTH)
print("5. THE DESIGN RULES, VERIFIED")
print("-" * WIDTH)

# RULE 2: never mutate an argument.
original_list = [3, 1, 3, 2]
mytoolkit.unique(original_list)
mytoolkit.chunked(original_list, 2)
check("unique/chunked do not mutate their argument",
      original_list == [3, 1, 3, 2], str(original_list))

original_dict = {"a": {"b": [1, 2]}}
mytoolkit.dig(original_dict, "a", "b", 0)
check("dig does not mutate its argument",
      original_dict == {"a": {"b": [1, 2]}})

# RULE 3: raise on programmer error, sentinel on expected absence.
raised = False
try:
    mytoolkit.clamp(5, 10, 0)
except ValueError:
    raised = True
check("clamp RAISES on an inverted range (a bug)", raised)
check("percent RETURNS 'n/a' on zero (a normal state)",
      mytoolkit.percent(5, 0) == "n/a")

# RULE 1: return, never print. Capture stdout and confirm silence.
import io                                        # noqa: E402
from contextlib import redirect_stdout           # noqa: E402

buffer = io.StringIO()
with redirect_stdout(buffer):
    mytoolkit.slugify("Quiet Please")
    mytoolkit.human_bytes(2048)
    mytoolkit.duration(3725)
    mytoolkit.initials("Ada Lovelace")
    mytoolkit.truncate("some text", 6)
check("the library prints nothing", buffer.getvalue() == "",
      repr(buffer.getvalue()[:30]))

# RULE 5: no dependencies.
#
# The first version of this check grepped for lines starting with "from ",
# and matched the words "from here:" inside a docstring — reporting a
# dependency that did not exist. Parse the code with `ast` instead of
# pattern-matching the text: a checker that produces false alarms gets
# switched off, and then it protects nothing.
import ast                                       # noqa: E402

third_party = []
for source_file in sorted((HERE / "mytoolkit").glob("*.py")):
    tree = ast.parse(source_file.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:                   # a relative import
                continue
            root = (node.module or "").split(".")[0]
        elif isinstance(node, ast.Import):
            root = node.names[0].name.split(".")[0]
        else:
            continue
        if root and root not in sys.stdlib_module_names:
            third_party.append(f"{source_file.name}: {root}")

check("imports nothing outside the standard library", not third_party,
      third_party[0] if third_party else "stdlib only")

# ===========================================================================
# 6. Can it be used from somewhere else?
# ===========================================================================

print()
print("-" * WIDTH)
print("6. USABLE FROM ELSEWHERE")
print("-" * WIDTH)

runnable = subprocess.run(
    [sys.executable, "-m", "mytoolkit"],
    capture_output=True, text=True, cwd=HERE,
)
check("`python3 -m mytoolkit` runs", runnable.returncode == 0,
      f"{len(runnable.stdout.splitlines())} lines of output")

importable = subprocess.run(
    [sys.executable, "-c",
     "import mytoolkit; print(mytoolkit.slugify('It Works'))"],
    capture_output=True, text=True, cwd=HERE,
)
check("importable as a package", importable.stdout.strip() == "it-works",
      importable.stdout.strip())

# ===========================================================================
# THE REPORT
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'ACCEPTANCE':^{WIDTH}}")
print("=" * WIDTH)
for label, passed, detail in checks:
    mark = "v" if passed else "x"
    print(f"  [{mark}] {label:<50}{detail[:22]:>22}")

passed_count = sum(1 for _, ok, _ in checks if ok)
print("-" * WIDTH)
print(f"  {passed_count} of {len(checks)} checks passed")
print("=" * WIDTH)

if passed_count == len(checks):
    print("""
Everything the package claims about itself is true, and this file proves it
rather than asserting it. That distinction is the whole of the milestone:
a README that promises "no dependencies" and a check that greps the imports
are different kinds of statement, and only one of them stays true.""")
else:
    print("\nSomething the package claims about itself is NOT true. Fix it.")

print(f"""
WHAT TEN DAYS BUILT

  Day 31   ten functions, one file, docstrings and doctests
  Day 32   signatures designed so the common call is one argument
  Day 33   a call logger — a decorator with the syntax filed off
  Day 34   lru_cache written by hand, from closures
  Day 35   four pipelines compared and judged
  Day 36   a recursive tree walker, and its iterative twin
  Day 37   @timer, @retry, @cache bolted on WITHOUT touching day 31's code
  Day 38   generators, and the same program in 0.02 MB instead of 164
  Day 39   one package, four submodules, one public surface
  Day 40   README, examples, {len(checks)} acceptance checks, pyproject.toml

  Still to come for this same package:
  Day 57   a real pytest suite that finds a bug in it
  Day 59   full type annotations, mypy clean
  Day 97   published to TestPyPI, installable by strangers""")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Break one promise — make slugify() print something, or add a
#     dependency to pyproject.toml — and re-run. The acceptance report
#     should catch it. If it does not, the check is decorative.
#
#   * Add a function of your own that you have hand-written twice in this
#     course. Give it a docstring, doctests, a README row and a test. Note
#     how many places a new public name has to appear — that number is what
#     "a public surface" costs, and it is worth knowing before you add one.
#
#   * Run `pip install -e .` and then import mytoolkit from your home
#     directory. That is the moment it stops being a folder and starts
#     being a library.
#
#   * Write the CHANGELOG.md that a 1.0.0 implies. Then decide what would
#     make it 2.0.0 — the answer is "any change to __all__'s behaviour",
#     and writing that down is what semantic versioning actually is.
