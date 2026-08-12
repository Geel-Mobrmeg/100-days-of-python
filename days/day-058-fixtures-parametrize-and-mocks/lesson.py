"""Day 058 — Fixtures, parametrize, and taking the world away.

    python3 lesson.py

Like Day 57, this file writes small test files and runs pytest on them, so
the output below is real rather than remembered.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

WIDTH = 76
WORK = Path(tempfile.mkdtemp(prefix="day058-"))


def run_pytest(source, *flags, name="test_demo.py"):
    (WORK / name).write_text(textwrap.dedent(source), encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", str(WORK / name),
         "-p", "no:cacheprovider", "--no-header", *flags],
        capture_output=True, text=True, cwd=WORK,
    )
    text = finished.stdout + finished.stderr
    return re.sub(r"^(rootdir|plugins|platform|configfile).*\n", "",
                  text, flags=re.MULTILINE)


def show(output, keep=None, indent="    "):
    for line in output.splitlines():
        if not line.strip():
            continue
        if keep and not keep(line):
            continue
        print(f"{indent}{line[:WIDTH - len(indent)]}")


# ---------------------------------------------------------------------------
# 1. A fixture is a function you ask for by name
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. ASK FOR IT BY NAME':^{WIDTH}}")
print("=" * WIDTH)
print('''
      @pytest.fixture
      def diary():
          return [Booking("ZZ-0001"), Booking("ZZ-0002")]

      def test_something(diary):        <- the PARAMETER NAME is the request
          assert len(diary) == 2

  No import, no setUp, no self. pytest reads the parameter names of every
  test, finds a fixture of that name, builds it, and passes it in.

  WHERE IT LOOKS, in order:
      the test file itself
      conftest.py in the same directory
      conftest.py in any parent directory
      installed plugins (tmp_path, monkeypatch, capsys, ...)

  conftest.py is the shared one. Nothing imports it — pytest finds it.''')


# ---------------------------------------------------------------------------
# 2. Scope, measured
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. SCOPE — HOW OFTEN IS IT BUILT?':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    import pytest

    built = {"function": 0, "module": 0, "session": 0}

    @pytest.fixture(scope="function")
    def per_function():
        built["function"] += 1
        return built["function"]

    @pytest.fixture(scope="module")
    def per_module():
        built["module"] += 1
        return built["module"]

    @pytest.fixture(scope="session")
    def per_session():
        built["session"] += 1
        return built["session"]

    @pytest.mark.parametrize("case", [1, 2, 3, 4])
    def test_uses_all_three(per_function, per_module, per_session, case):
        pass

    def test_report(per_function, per_module, per_session):
        print(f"\\nBUILT: function={built['function']} "
              f"module={built['module']} session={built['session']}")
''', "-q", "-s")

print()
show(output, keep=lambda ln: "BUILT" in ln or "passed" in ln)
print("""
  FIVE TESTS. The function-scoped fixture was built five times, the
  module-scoped one once, the session-scoped one once.

    scope="function"   (the default) fresh for every test
    scope="class"      once per test class
    scope="module"     once per file
    scope="session"    once for the whole run

  THE DEFAULT IS THE RIGHT ONE. A wider scope is a shared object, and a
  shared MUTABLE object is a test that passes alone and fails in the suite
  — or worse, passes in the suite and fails alone, which people then "fix"
  by running the tests in a particular order.

  WIDEN IT ONLY FOR SOMETHING EXPENSIVE AND READ-ONLY: a parsed fixture
  file, a compiled regex table, a database container. And if you widen it,
  hand out a COPY.""")


# ---------------------------------------------------------------------------
# 3. yield: setup and teardown
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. TEARDOWN — EVERYTHING BEFORE AND AFTER THE yield':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest("""
    import pytest

    trace = []

    @pytest.fixture(scope="module", autouse=True)
    def report():
        # autouse=True: every test in the module gets it without asking.
        # Module scope means this teardown runs LAST, so it sees
        # everything — including the final teardown of the final test.
        yield
        for number, step in enumerate(trace, 1):
            print(f"ORDER {number}. {step}")

    @pytest.fixture
    def outer():
        trace.append("outer setup")
        yield "outer"
        trace.append("outer teardown")

    @pytest.fixture
    def inner(outer):
        trace.append("inner setup")
        yield "inner"
        trace.append("inner teardown")

    def test_one(inner):
        trace.append("test one BODY")

    def test_two(inner):
        trace.append("test two BODY")
        raise AssertionError("this test FAILS on purpose")
""", "-q", "-s", "--tb=no")

print()
show("\n".join(ln.lstrip(".FEsx") if ln.startswith((".", "F"))
                 and "ORDER" in ln else ln
                 for ln in output.splitlines()),
     keep=lambda ln: "ORDER" in ln or " failed" in ln)
print("""
  READ THE ORDER. Setup runs outermost-first, teardown innermost-first,
  and the whole cycle repeats for the second test because the default
  scope is per-function.

  STEPS 8 TO 10 ARE THE ONES THAT MATTER: test two FAILED, and both
  teardowns still ran. A fixture's cleanup is a `finally`, not a hopeful
  last line — Day 53's `with`, one layer up.

  A fixture that uses another just asks for it by name; pytest builds the
  graph in dependency order. And `autouse=True` on the reporting fixture
  means every test in the module got it without mentioning it — useful for
  setup that must happen everywhere, and easy to overuse, because a test
  that does not name its fixtures does not say what it depends on.""")


# ---------------------------------------------------------------------------
# 4. The built-in fixtures
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. THE ONES YOU DID NOT WRITE':^{WIDTH}}")
print("=" * WIDTH)
print("""
  tmp_path          a fresh empty directory, cleaned up for you
  tmp_path_factory  the same, at session scope
  monkeypatch       set/delete an attribute, an item, an env var, or the
                    working directory — ALL UNDONE when the test ends
  capsys            what the test printed:  capsys.readouterr().out
  caplog            what the test logged (Day 67)
  request           metadata about the running test
  recwarn           warnings that were raised

  monkeypatch's methods:

      monkeypatch.setattr(module, "name", replacement)
      monkeypatch.setattr("package.module.name", replacement)
      monkeypatch.setitem(config, "key", value)
      monkeypatch.setenv("API_KEY", "test-key")
      monkeypatch.delenv("API_KEY", raising=False)
      monkeypatch.chdir(tmp_path)
      monkeypatch.syspath_prepend(path)

  THE UNDOING IS THE POINT. Assign to a module yourself and you have
  changed it for every test that runs afterwards — and the failure appears
  in a different file, which is a bad afternoon.""")


# ---------------------------------------------------------------------------
# 5. Patch where it is USED
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. THE MISTAKE EVERYBODY MAKES ONCE':^{WIDTH}}")
print("=" * WIDTH)

output = run_pytest('''
    import datetime as datetime_module
    from datetime import datetime

    import pytest

    # This is what `from datetime import datetime` does in a real module:
    # it binds THIS module's own name to the class object.

    def is_open():
        return 8 <= datetime.now().hour < 22

    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 3, 18, 3, 0)     # 3am: closed

    def test_patching_the_source_module_does_nothing(monkeypatch):
        monkeypatch.setattr(datetime_module, "datetime", Frozen)
        print("\\nWRONG TARGET  is_open() ->", is_open())

    def test_patching_where_it_is_used_works(monkeypatch):
        monkeypatch.setattr(__name__ + ".datetime", Frozen)
        print("RIGHT TARGET  is_open() ->", is_open())
''', "-q", "-s")

print()
show(output, keep=lambda ln: "TARGET" in ln or "passed" in ln)
print("""
  Both patches are correct, targeted and undone. Only one has any effect.

      import datetime;  datetime.datetime.now()    patch the MODULE
      from datetime import datetime;  datetime.now()
                                                   patch YOUR module's name

  `from X import Y` copies the reference at import time. Patching X.Y
  afterwards rebinds X's attribute and leaves your module pointing at the
  original object.

  THE RULE: patch the name in the module that CALLS it, not the module
  that defines it. Today's tests/ has a test asserting exactly this,
  because the rule is much easier to remember once you have watched it
  fail.""")


# ---------------------------------------------------------------------------
# 6. Mock
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. Mock — AND WHAT IT COSTS':^{WIDTH}}")
print("=" * WIDTH)
print("""
      notifier = Mock()
      confirm(booking, notifier)

      notifier.send.assert_called_once()
      notifier.send.assert_called_with(address, subject, body)
      notifier.send.call_args.args          the arguments, to inspect
      notifier.send.call_count              how many times
      notifier.send.return_value = "queued" what it should give back
      notifier.send.side_effect = OSError   ...or raise

  A Mock has EVERY attribute and accepts EVERY call:

      notifier.send_teh_thing(1, 2, 3)      passes
      notifier.a.b.c.d()                    passes

  So a test using a mock keeps passing after you rename the real method —
  the mock grows the new name too, and the test now proves nothing about
  a class it no longer matches. That is the cost, and it is why mocks are
  a tool for things you CANNOT change:

      a payment provider, an SMTP server, a clock in somebody else's
      library, a filesystem that is full

  For code you own, an ARGUMENT is cheaper. Day 51's reader=input, Day
  46's Warehouse(pricing=..., audit=...), and today's validate(booking,
  now=...) are all the same move, and none of them needs a library.

  THE ORDER TO REACH IN:
      1. a parameter                     (change the code)
      2. a fake object you wrote         (5 lines, and it type-checks)
      3. monkeypatch                     (for a module-level name)
      4. unittest.mock                   (for a call you must assert on)""")


# ---------------------------------------------------------------------------
# 7. Parametrising the fixture
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. THE FACTORY FIXTURE':^{WIDTH}}")
print("=" * WIDTH)
print('''
  A PLAIN FIXTURE gives every test the same object:

      @pytest.fixture
      def booking():
          return Booking("AB-1234", "ada@example.com", ...)

  ...and then a test that needs a different party size has to build the
  whole thing by hand, with all twelve fields, in the test.

  A FACTORY FIXTURE returns a FUNCTION:

      @pytest.fixture
      def make_booking(now):
          def build(**overrides):
              defaults = {"reference": "AB-1234", ..., "party_size": 4}
              return Booking(**{**defaults, **overrides})
          return build

      def test_a_party_that_is_too_large(make_booking, now):
          assert validate(make_booking(party_size=99), now=now)

  Each test states ONLY what it cares about, and adding a field to Booking
  changes one function instead of thirty tests. This is the single most
  useful fixture pattern there is.

  AND params= MAKES A FIXTURE RUN EVERY TEST THAT USES IT, ONCE PER VALUE:

      @pytest.fixture(params=["sqlite", "postgres"])
      def database(request):
          return connect(request.param)

  Every test taking `database` now runs twice. Use it for a dimension that
  applies to a whole FILE; use @parametrize for cases that apply to one
  test.''')

print()
print("=" * WIDTH)
print("""  1. A fixture is requested by parameter name. conftest.py shares it.
  2. Default scope is function. Widen only for expensive, read-only things.
  3. yield: setup above, teardown below — and it runs even on failure.
  4. tmp_path, monkeypatch, capsys before you write your own.
  5. monkeypatch undoes itself. Assigning to a module does not.
  6. Patch where the name is USED.
  7. Mock what you cannot change. Pass an argument to what you can.
  8. A factory fixture beats a fixed one.""")
print("=" * WIDTH)

shutil.rmtree(WORK, ignore_errors=True)


# ---------------------------------------------------------------------------
# Now write some
# ---------------------------------------------------------------------------
#
#   * Take three tests that build the same object and replace it with a
#     factory fixture. Count the lines deleted.
#
#   * Make a module-scoped fixture return a list, append to it in one test,
#     and watch a later test see the change. Then run that later test on
#     its own and watch it pass.
#
#   * Patch the wrong module on purpose and spend two minutes not
#     understanding why the test fails. It is worth the two minutes.
#
#   * Monkeypatch time.sleep in a test of something that retries, and
#     compare the suite's runtime before and after.
#
#   * Write the same test twice: once with mock.patch and once by passing
#     an argument. Then rename the method being mocked, and see which test
#     notices.
