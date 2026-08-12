"""Day 052 — Raising, and writing your own exception types.

    python3 lesson.py

Yesterday was catching. Today is the other end: deciding that something is
wrong, saying so, and saying it in a way the caller can act on.
"""

import sys
import traceback
from pathlib import Path

WIDTH = 76


def shown(fn, limit=None):
    """Run fn, return its traceback as text. Used to SHOW real output."""
    try:
        fn()
    except BaseException:                              # noqa: BLE001
        text = "".join(traceback.format_exception(*sys.exc_info()))
        text = text.replace(str(Path(__file__).parent) + "/", "")
        lines = text.rstrip().splitlines()
        return "\n".join(f"    {ln}" for ln in (lines[:limit] if limit
                                                else lines))
    return "    (no exception)"


# ---------------------------------------------------------------------------
# 1. Which builtin to raise
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. RAISING A BUILTIN — AND CHOOSING WHICH':^{WIDTH}}")
print("=" * WIDTH)

print("""
  RIGHT TYPE                 WHEN

  ValueError                 the type is right, the VALUE is not
                             int('abc'), a negative quantity, port 99999
  TypeError                  the TYPE is wrong
                             len(3), Money + 5
  KeyError / IndexError      a lookup that is not there
  LookupError                the base of both, if you do not care which
  OSError                    the world said no (files, sockets, permissions)
  RuntimeError               nothing more specific fits, and you have tried
  NotImplementedError        an abstract method — but Day 49 showed why
                             @abstractmethod is better
  StopIteration              only from __next__. Never raise it by hand.
  AssertionError             never raise it deliberately

  THE COMMONEST MISTAKE IS `raise Exception("...")`. It forces every caller
  who wants to handle it to write `except Exception`, which then catches
  everything else too. Never raise the base class.""")


def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")     # NOT `Exception`
    return a / b


try:
    divide(1, 0)
except ValueError as exc:
    print(f"  caught precisely: {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# 2. The message is the interface
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. AN ERROR MESSAGE PEOPLE CAN ACT ON':^{WIDTH}}")
print("=" * WIDTH)

messages = [
    ("Error", "says nothing at all"),
    ("Invalid input", "which input? invalid how?"),
    ("Invalid port", "closer — still does not say what was given"),
    ("Invalid port: 99999", "now I can see my mistake"),
    ("port must be 1-65535, got 99999",
     "and now I know the rule"),
    ("port must be 1-65535, got 99999 (from PORT in .env)",
     "...and where to go and fix it"),
]

print()
for message, note in messages:
    print(f"  {message:<52}{note[:22]}")

print("""
  FOUR THINGS, AND THE LAST ONE IS THE ONE PEOPLE FORGET:

    1. WHAT is wrong          "port"
    2. WHAT WAS GIVEN         "got 99999"
    3. WHAT WAS EXPECTED      "must be 1-65535"
    4. WHERE IT CAME FROM     "from PORT in .env"

  Write the message for the person who will read it at 3am, who did not
  write this code, and who cannot see your variables. Every message that
  makes them open your source is a message that failed.

  AND SAY IT IN THE ORDER THEY THINK: subject first, not "Error occurred
  while processing the value provided for the configuration option port".""")


# ---------------------------------------------------------------------------
# 3. Your own exception class
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. YOUR OWN TYPE':^{WIDTH}}")
print("=" * WIDTH)


class ConfigError(Exception):
    """The base for everything this module raises.

    ITS ONLY JOB is to let a caller write one clause:

        except ConfigError:      -> all of my failures
        except Exception:        -> mine, plus every bug in the program

    A base class per library or per module. Not per function.
    """


class MissingSetting(ConfigError):
    """A required setting was absent."""


class BadSetting(ConfigError):
    """A setting was present and unusable.

    Carries DATA, not just a message — so a caller can build its own
    message, put the field name in a form, or count failures by field.
    """

    def __init__(self, field, value, expected):
        self.field = field
        self.value = value
        self.expected = expected
        super().__init__(f"{field} must be {expected}, got {value!r}")


def load(settings):
    if "port" not in settings:
        raise MissingSetting("port is required (set PORT in .env)")
    try:
        port = int(settings["port"])
    except ValueError as exc:
        raise BadSetting("port", settings["port"], "a whole number") from exc
    if not 1 <= port <= 65535:
        raise BadSetting("port", port, "1-65535")
    return port


for settings in ({}, {"port": "http"}, {"port": "99999"}, {"port": "8080"}):
    try:
        result = f"loaded {load(settings)}"
    except BadSetting as exc:
        result = f"{type(exc).__name__}  field={exc.field!r} value={exc.value!r}"
    except MissingSetting as exc:
        result = f"{type(exc).__name__}  {exc}"
    print(f"  {str(settings):<24}{result}")

print("""
  THREE THINGS THAT BOUGHT:

    * `except ConfigError` catches all three and nothing else
    * the caller can read exc.field WITHOUT parsing the message
    * the type name appears in the traceback, so the log says
      `BadSetting` and not `ValueError`

  WHEN NOT TO BOTHER: if the caller would do the same thing for your
  exception as for a builtin, use the builtin. A custom class whose only
  content is `pass` and which nobody catches separately is noise.""")


# ---------------------------------------------------------------------------
# 4. Hierarchies
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  A HIERARCHY IS A SET OF CHOICES YOU GIVE THE CALLER")
print("-" * WIDTH)
print("""
      ConfigError                      "something in config went wrong"
        ├── MissingSetting             "...and it is absent"
        ├── BadSetting                 "...and it is unusable"
        │     ├── BadType
        │     └── OutOfRange
        └── SourceUnreadable           "...and I could not even look"

  Each level is a DECISION a caller might make. If nobody would ever catch
  BadType separately from OutOfRange, do not split them — every level you
  add is a level every reader has to learn.

  TWO OR THREE LEVELS IS ALMOST ALWAYS ENOUGH.

  INHERIT FROM A BUILTIN WHEN THE MEANING MATCHES:

      class BadSetting(ConfigError, ValueError): ...

  Now old code that says `except ValueError` keeps working, and new code
  can be precise. Useful when adding types to a library people already use;
  confusing if overdone.""")


# ---------------------------------------------------------------------------
# 5. raise ... from
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. raise ... from — THREE DIFFERENT TRACEBACKS':^{WIDTH}}")
print("=" * WIDTH)


def implicit():
    try:
        int("http")
    except ValueError:
        raise BadSetting("port", "http", "a whole number")


def explicit():
    try:
        int("http")
    except ValueError as exc:
        raise BadSetting("port", "http", "a whole number") from exc


def suppressed():
    try:
        int("http")
    except ValueError:
        raise BadSetting("port", "http", "a whole number") from None


for label, fn in [("no `from` at all", implicit),
                  ("`from exc`", explicit),
                  ("`from None`", suppressed)]:
    print(f"\n  {label}")
    print(shown(fn))

print("""
  ALL THREE keep working code working. The difference is what the log says
  at 3am.

    no `from`      "During handling of the above exception, ANOTHER
                   exception occurred" — which reads like your handler
                   itself is buggy. Python keeps the context automatically
                   (exc.__context__) whether you ask or not.

    `from exc`     "The above exception was the DIRECT CAUSE" — this is
                   deliberate translation, one layer wrapping another.
                   Sets exc.__cause__.

    `from None`    hides the original entirely. Correct when the internals
                   are noise (a caller does not care that your config
                   loader uses json underneath) — and a mistake when they
                   are the actual clue.

  DEFAULT TO `from exc`. It is one word, and it is the difference between a
  reader thinking "the library is broken" and "my input was wrong".""")


# ---------------------------------------------------------------------------
# 6. Re-raising
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  RE-RAISING: `raise` AND `raise exc` ARE NOT THE SAME")
print("-" * WIDTH)

attempts = []


def inner():
    int("http")                        # the real origin, line ~N


def bare_reraise():
    try:
        inner()
    except ValueError:
        attempts.append("logged")
        raise                          # keeps the ORIGINAL traceback


def reraise_by_name():
    try:
        inner()
    except ValueError as exc:
        attempts.append("logged")
        raise exc                      # traceback now starts HERE


for label, fn in [("bare `raise`", bare_reraise),
                  ("`raise exc`", reraise_by_name)]:
    frames = shown(fn).count("File ")
    print(f"  {label:<20}{frames} frames in the traceback")

print("""
  Bare `raise` re-raises the exception that is being handled, with its
  traceback intact, so the report still points at the line that failed.
  `raise exc` re-raises it from the handler, and the original line is gone.

  USE BARE `raise` when you want to log and let it continue upward:

      except ConfigError:
          log.warning("config failed, using defaults")
          raise""")


# ---------------------------------------------------------------------------
# 7. assert is not error handling
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  assert IS NOT ERROR HANDLING")
print("-" * WIDTH)
print("""
      assert port > 0, "port must be positive"

  python3 -O removes that line entirely. Every assert in your program
  becomes a no-op, and validation you thought you had is gone.

  ASSERT     a claim about YOUR OWN code that should be impossible to
             break — an internal invariant, a sanity check in a test.
  RAISE      anything about input, the world, or a caller's mistake.

  A useful test: could a user cause this? Then it is a raise.""")


# ---------------------------------------------------------------------------
# 8. Exception groups (3.11+)
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. MORE THAN ONE THING WRONG AT ONCE':^{WIDTH}}")
print("=" * WIDTH)


def validate_all(settings):
    """Collect every problem, then raise them together."""
    problems = []
    for field, expected, ok in [
        ("port", "a whole number in 1-65535",
         str(settings.get("port", "")).isdigit()),
        ("host", "a non-empty name", bool(settings.get("host", "").strip())),
        ("workers", "a whole number", str(settings.get("workers", "")).isdigit()),
    ]:
        if not ok:
            problems.append(BadSetting(field, settings.get(field), expected))
    if problems:
        raise ExceptionGroup(f"{len(problems)} settings are wrong", problems)
    return settings


broken = {"port": "http", "host": "  ", "workers": "many"}

try:
    validate_all(broken)
except* BadSetting as group:
    print(f"  one raise, {len(group.exceptions)} problems:")
    for exc in group.exceptions:
        print(f"    {exc}")

print("""
  Python 3.11's ExceptionGroup, and `except*` to unpack it.

  WHY IT MATTERS: raising on the FIRST problem makes fixing three mistakes
  take three runs. A form that reports one field at a time is the same bug
  with a nicer font.

  USE A GROUP when the failures are independent and the caller wants all of
  them: validation, a batch of parallel tasks (Day 92), a set of files.

  USE A PLAIN RAISE when the first failure makes the rest meaningless —
  there is no point checking the port of a config file you could not
  open.""")

print()
print("=" * WIDTH)
print("""  1. Never `raise Exception(...)`. Pick the type.
  2. The message says what, what was given, what was expected, from where.
  3. One base class per library so callers get one clause.
  4. Carry data on the exception, not only in the message.
  5. `raise ... from exc` when you translate; `from None` to hide noise.
  6. Bare `raise` to re-raise; `raise exc` throws the traceback away.
  7. assert is for your bugs. raise is for everyone else's.
  8. Report all the problems at once when the caller could fix them all.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Change BadSetting to inherit ValueError as well and confirm that
#     `except ValueError` starts catching it. That is how a library adds
#     precise types without breaking anyone.
#
#   * Delete `from exc` in load() and read the traceback again. Decide
#     which version you would rather be paged about.
#
#   * Write `assert` validation, then run the file with python3 -O.
#
#   * Turn validate_all() into a first-failure version and count how many
#     runs it takes to fix the three-field config above.
#
#   * Give BadSetting a `.suggestion` — "did you mean 8080?" — and a
#     __str__ that includes it. Error messages can do arithmetic.
