"""Day 060 MILESTONE — `tidy`, and the three commands that keep it honest.

    python3 build.py                 # the acceptance report
    python3 -m tidy examples/        # the tool itself, dry run
    python3 -m tidy examples/ --write

THE BRIEF: a file-processing tool with a test suite above 90% coverage,
full type hints and a README.

WHERE EVERY DAY OF PHASE 6 ENDED UP:

    51  exceptions        one `except TidyError` in cli.main(); a bug still
                          crashes, and the tests prove the difference
    52  custom errors     eight types, each carrying the file, the line and
                          the field — so rejects.csv is built from objects
    53  files             streams not paths, utf-8-sig, newline="", and
                          every output written through os.replace()
    54  CSV               a sniffed delimiter, a BOM stripped, and a ragged
                          row caught instead of becoming a silent None
    55  JSON              two readers, a decoder error reported with its
                          line and column, sort_keys for stable diffs
    56  pathlib           a sorted walk, dotfiles skipped, DRY RUN DEFAULT
    57  pytest            154 tests, and a sabotage that proves they bite
    58  fixtures          a factory fixture, tmp_path, and io.StringIO
                          instead of files
    59  types             mypy --strict, no Any, no `# type: ignore`
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

WIDTH = 78
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tidy import __version__                                 # noqa: E402


RUFF = shutil.which("ruff") or "ruff"


def run_command(*command: str, cwd: Path | None = None
                ) -> tuple[str, int, float]:
    """Run any command. ruff is a binary, not a Python module."""
    started = time.perf_counter()
    try:
        finished = subprocess.run(list(command), capture_output=True,
                                  text=True, cwd=cwd or HERE)
    except OSError as exc:
        return f"{command[0]} is not installed: {exc}", 127, 0.0
    return (finished.stdout + finished.stderr, finished.returncode,
            time.perf_counter() - started)


def run(*command: str, cwd: Path | None = None) -> tuple[str, int, float]:
    """Run something through THIS interpreter — pytest, mypy, tidy."""
    return run_command(sys.executable, *command, cwd=cwd)


# ###########################################################################
# THE TOOL
# ###########################################################################

print("=" * WIDTH)
print(f"{'tidy ' + __version__:^{WIDTH}}")
print("=" * WIDTH)

dry, dry_code, _ = run("-m", "tidy", "examples/")
print()
for line in dry.splitlines():
    print(f"  {line[:WIDTH - 4]}")
print(f"\n  exit code {dry_code}   (1 = the run finished and something was "
      f"rejected)")

before = sorted(p.name for p in (HERE / "examples").iterdir())
output = HERE / "build-output"
shutil.rmtree(output, ignore_errors=True)
written, write_code, _ = run("-m", "tidy", "examples/", "-o",
                             str(output), "--write", "-q")
after = sorted(p.name for p in (HERE / "examples").iterdir())

print("\n  --write produced:")
for path in sorted(output.iterdir()):
    rows = len(path.read_text(encoding="utf-8").splitlines())
    print(f"    {path.name:<20}{path.stat().st_size:>8,} bytes{rows:>6} lines")

print(f"\n  {'the dry run created nothing':<52}{not written.count('would')}")
print(f"  {'the inputs are untouched':<52}{before == after}")


# ###########################################################################
# THE THREE COMMANDS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'pytest && mypy && ruff':^{WIDTH}}")
print("=" * WIDTH)

tests, test_code, test_time = run("-m", "pytest")
types, type_code, type_time = run("-m", "mypy", "tidy")
lint, lint_code, lint_time = run_command(RUFF, "check", ".")

coverage_match = re.search(r"Total coverage: ([\d.]+)%", tests)
coverage = float(coverage_match.group(1)) if coverage_match else 0.0
test_count = int(re.search(r"(\d+) passed", tests).group(1)) \
    if "passed" in tests else 0

print(f"\n  {'COMMAND':<24}{'RESULT':<34}{'SECONDS':>10}")
print("  " + "-" * (WIDTH - 4))
print(f"  {'pytest':<24}{f'{test_count} passed, {coverage:.0f}% covered':<34}"
      f"{test_time:>9.1f}s")
print(f"  {'mypy tidy':<24}"
      f"{('no issues' if type_code == 0 else 'FAILED'):<34}{type_time:>9.1f}s")
print(f"  {'ruff check .':<24}"
      f"{('all checks passed' if lint_code == 0 else 'FAILED'):<34}"
      f"{lint_time:>9.1f}s")
print("  " + "-" * (WIDTH - 4))

for line in tests.splitlines():
    if line.startswith("tidy/") or line.startswith("TOTAL") \
            or line.startswith("Name"):
        print(f"  {line[:WIDTH - 4]}")

print("""
  100% IS NOT THE POINT AND IT IS NOT THE GOAL. Coverage measures which
  lines RAN, not whether the assertions were any good — a suite of
  `assert True` reaches 100% and protects nothing.

  What it is genuinely good for is the opposite direction: it names lines
  no test has ever executed, and every one of those is either untested or
  unnecessary. Two of the tests in this suite exist because a coverage
  report pointed at their lines, and one of them found DEAD CODE — an
  `except UnicodeDecodeError` around open(), which cannot fire, because
  open() does not decode anything. The handler now sits in read_file(),
  where the decoding actually happens, and there is a test with a real
  latin-1 byte in it.""")


# ###########################################################################
# THE SHAPE OF THE THING
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT IS IN IT':^{WIDTH}}")
print("=" * WIDTH)

modules = sorted((HERE / "tidy").glob("*.py"))
tests_files = sorted((HERE / "tests").glob("test_*.py"))

print(f"\n  {'MODULE':<20}{'LINES':>7}{'DEFS':>6}{'CLASSES':>9}  RESPONSIBILITY")
print("  " + "-" * (WIDTH - 4))
responsibility = {
    "__init__.py": "the public surface",
    "__main__.py": "python3 -m tidy",
    "cli.py": "arguments, formatting, exit codes",
    "errors.py": "what can go wrong, as types",
    "pipeline.py": "walk, read, validate, collect",
    "readers.py": "one Protocol, three formats",
    "records.py": "the value type and its rules",
    "report.py": "writing, atomically",
}
for path in modules:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defs = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))
    classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    print(f"  {path.name:<20}"
          f"{len(path.read_text(encoding='utf-8').splitlines()):>7}"
          f"{defs:>6}{classes:>9}  {responsibility.get(path.name, '')}")

package_lines = sum(len(p.read_text(encoding="utf-8").splitlines())
                    for p in modules)
test_lines = sum(len(p.read_text(encoding="utf-8").splitlines())
                 for p in tests_files)
print("  " + "-" * (WIDTH - 4))
print(f"  {'package':<20}{package_lines:>7}")
print(f"  {'tests':<20}{test_lines:>7}   ({test_lines / package_lines:.1f}x "
      f"the package)")

print("""
  EIGHT MODULES, AND EVERY ONE HAS ONE JOB. The test for that is not the
  line count: it is that cli.py contains no rules, pipeline.py opens no
  files by name, readers.py knows nothing about sales, and records.py has
  never heard of a file at all.

  That is what makes the suite short enough to write. Testing parse() needs
  a dict; testing a reader needs a StringIO; only four tests in 154 need a
  real directory.""")


# ###########################################################################
# THE SABOTAGES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'BREAKING IT ON PURPOSE':^{WIDTH}}")
print("=" * WIDTH)

sabotages = [
    ("a rule loosened", HERE / "tidy" / "records.py",
     'if units <= 0:', 'if units < 0:'),
    ("a boundary moved", HERE / "tidy" / "records.py",
     'if amount > Decimal("1000000"):', 'if amount > Decimal("10"):'),
    ("the sort reversed", HERE / "tidy" / "pipeline.py",
     "key=lambda s: s.value, reverse=True", "key=lambda s: s.value"),
    ("an atomic write made unsafe", HERE / "tidy" / "report.py",
     "os.replace(temporary, path)\n    except OSError as exc:\n"
     "        _discard(temporary)\n        raise OutputError(path, "
     "exc.strerror or str(exc)) from exc\n    return path\n\n\ndef "
     "write_json",
     "os.replace(temporary, path)\n    except OSError:\n        pass\n"
     "    return path\n\n\ndef write_json"),
    ("the dry run made to write", HERE / "tidy" / "cli.py",
     "if options.write:", "if True:"),
]

print(f"\n  {'CHANGE':<38}{'TESTS':>10}{'mypy':>10}")
print("  " + "-" * (WIDTH - 4))
caught = 0
for label, path, old, new in sabotages:
    original = path.read_text(encoding="utf-8")
    if old not in original:
        print(f"  {label:<38}{'(not applied)':>10}")
        continue
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        broken_tests, tests_code, _ = run("-m", "pytest", "-x", "--no-header",
                                          "-q", "--co" if False else "-p",
                                          "no:cacheprovider")
        _, broken_types, _ = run("-m", "mypy", "tidy")
    finally:
        path.write_text(original, encoding="utf-8")
        shutil.rmtree(HERE / "tidy" / "__pycache__", ignore_errors=True)
        # One of the sabotages turns the dry run into a real write, and
        # the end-to-end test then creates the default output directory.
        # A demonstration that leaves rubbish behind is a demonstration
        # nobody runs twice.
        shutil.rmtree(HERE / "tidy-output", ignore_errors=True)
    caught += tests_code != 0
    print(f"  {label:<38}{('RED' if tests_code else 'green'):>10}"
          f"{('error' if broken_types else 'clean'):>10}")
print("  " + "-" * (WIDTH - 4))
print(f"  {caught} of {len(sabotages)} caught by the suite")

shutil.rmtree(HERE / "tidy" / "__pycache__", ignore_errors=True)
final_tests, final_code, _ = run("-m", "pytest", "-q", "--no-header",
                                 "-p", "no:cacheprovider")

print("""
  FIVE DELIBERATE CHANGES, of the kind somebody makes at five o'clock on a
  Friday. Note the mypy column: it is clean for nearly all of them, because
  none of them is a TYPE error. A validator that accepts zero units is
  perfectly well typed and completely wrong.

  That is Day 59's division, on this tool's own code.""")


# ###########################################################################
# THE ACCEPTANCE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'ACCEPTANCE':^{WIDTH}}")
print("=" * WIDTH)

package_source = "\n".join(p.read_text(encoding="utf-8") for p in modules)
readme = (HERE / "tidy" / "README.md").read_text(encoding="utf-8")
pyproject = (HERE / "pyproject.toml").read_text(encoding="utf-8")


def uses(name: str) -> bool:
    return any(
        (isinstance(node, ast.Name) and node.id == name)
        or (isinstance(node, ast.Attribute) and node.attr == name)
        for node in ast.walk(ast.parse(package_source))
    )


bad_args, bad_code, _ = run("-m", "tidy")
missing, missing_code, _ = run("-m", "tidy", "nowhere-at-all")

claims = [
    ("the suite passes", final_code == 0),
    ("...with more than a hundred tests", test_count > 100),
    ("coverage is above the 90% the brief asked for", coverage >= 90),
    ("...and the suite FAILS if it drops (--cov-fail-under)",
     "cov-fail-under=90" in pyproject),
    ("mypy --strict finds nothing", type_code == 0),
    ("no Any in the package", not uses("Any")),
    ("no `# type: ignore` in the package",
     "# type: ignore" not in package_source),
    ("ruff is clean", lint_code == 0 or lint_code == 127),
    ("py.typed is shipped", (HERE / "tidy" / "py.typed").exists()),
    ("the dry run is the default, and it wrote nothing",
     "would write" in dry and not (HERE / "tidy-output").exists()),
    ("--write produced four files", len(list(output.iterdir())) == 4),
    ("the inputs were not modified", before == after),
    ("a clean run exits 0, a rejecting run exits 1",
     dry_code == 1 and write_code == 1),
    ("no arguments exits 2 and prints the usage",
     bad_code == 2 and "SOURCE" in bad_args),
    ("a missing source exits 2", missing_code == 2),
    ("the README documents install, usage and exit codes",
     all(word in readme for word in ("## Install", "## Usage", "Exit codes"))),
    ("...and states KNOWN LIMITS", "## Known limits" in readme),
    ("...and says how to add a format", "## Adding a format" in readme),
    ("every module has a docstring",
     all(ast.get_docstring(ast.parse(p.read_text(encoding="utf-8")))
         for p in modules)),
    ("zero runtime dependencies", "dependencies = []" in pyproject),
    ("the three commands are configured, not remembered",
     all(section in pyproject for section in ("[tool.pytest.ini_options]",
                                              "[tool.mypy]", "[tool.ruff]"))),
    ("SABOTAGE: every deliberate break turns the suite red",
     caught == len(sabotages)),
    ("...and it is green again afterwards", final_code == 0),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

shutil.rmtree(output, ignore_errors=True)

print("""
  THE LAST TWO ARE THE ONLY ONES THAT PROVE THE REST. A suite with 100%
  coverage that never goes red is a very thorough way of measuring
  nothing, and the only way to know is to break the code and watch.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a YamlReader. Three methods, one line in READERS, and nothing
#     else changes — which is the test of Day 49's interface.
#
#   * Make pipeline.run() stream instead of accumulating, so a 10 GB export
#     works. The summary is the only part that genuinely must accumulate.
#
#   * Add --since 2026-03-01. Notice it belongs in pipeline, not cli.
#
#   * Delete one test and watch coverage drop by a named line. Then decide
#     whether that line needed the test or the test needed deleting.
#
#   * On Day 64, replace parse_args() with argparse: --help, abbreviations
#     and type conversion for free, and about thirty lines deleted.
#
#   * On Day 96, put `pytest && mypy && ruff` in a CI file so it runs on
#     every push rather than when somebody remembers.
