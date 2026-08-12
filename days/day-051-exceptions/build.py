"""Day 051 build — an input reader that cannot produce a traceback.

    python3 build.py                 # the scripted demonstration
    python3 build.py --interactive   # the demonstration, then a real prompt
    printf '8080\\ny\\n2\\n' | python3 build.py -i

THE PROBLEM WITH int(input("port: ")):

    empty input          ValueError
    'abc'                ValueError
    Ctrl-D               EOFError
    Ctrl-C               KeyboardInterrupt   <- not even an Exception
    '3.7'                ValueError
    '9' * 5000           ValueError
    'inf' via float()    NO ERROR AT ALL, and the answer is wrong

Six of those end the program with a traceback. The seventh is worse.

THE DESIGN: reading is separated from CONVERTING and from CHECKING, so a
Ctrl-C, a typo and an out-of-range number are three different outcomes with
three different responses — and the reader is a parameter, so the whole
thing can be tested without a human.
"""

import math
import sys
from dataclasses import dataclass

WIDTH = 78


# ###########################################################################
# THE ANSWER — what a read produced, and how it ended
# ###########################################################################

@dataclass(frozen=True, slots=True)
class Answer:
    """A value AND how the read ended. Both matter to the caller.

    Returning a bare value cannot distinguish "the user typed 0" from "the
    user pressed Ctrl-C and we fell back to 0". Those need different code.
    """

    value: object
    outcome: str        # ok | cancelled | eof | exhausted
    attempts: int = 1
    note: str = ""      # the last thing that was wrong, for the report

    def __bool__(self):
        """`if answer:` means "the user actually gave me this"."""
        return self.outcome == "ok"

    def __str__(self):
        return f"{self.value!r} ({self.outcome})"


# ###########################################################################
# THE READER — the only place exceptions are handled
# ###########################################################################

def ask(prompt, convert=str, check=None, default=None, attempts=3,
        reader=input, tell=lambda msg: None):
    """Read, convert and check a value. Never raises. Never tracebacks.

    convert   a callable that may raise ValueError/TypeError    (int, float)
    check     returns None if the value is acceptable, else a message
    default   what to fall back to on Ctrl-C, Ctrl-D or too many attempts
    reader    input() by default — a parameter so this is testable
    tell      where retry messages go — a parameter so this is quiet in
              tests and chatty at a terminal
    """
    used = 0
    problem = ""
    while used < attempts:
        used += 1
        try:
            raw = reader(prompt)

        # ---- the two that are NOT Exception subclasses -------------------
        except EOFError:
            # stdin closed: a pipe ran dry, or the user pressed Ctrl-D.
            # Asking again would loop forever, so stop immediately.
            tell("\n(no more input)")
            return Answer(default, "eof", used, "stdin closed")
        except KeyboardInterrupt:
            # `except Exception` would NOT catch this. That is why the
            # naive version dies on Ctrl-C with a traceback.
            tell("\n(cancelled)")
            return Answer(default, "cancelled", used, "user pressed Ctrl-C")

        # ---- the ordinary one --------------------------------------------
        try:
            value = convert(raw)
        except (ValueError, TypeError) as exc:
            # TypeError as well as ValueError: convert() may be given
            # something that is not even a string, e.g. from a test.
            problem = f"not a valid {convert.__name__}"
            tell(f"  {problem}: {exc}")
            continue
        else:
            # Only reached when convert() succeeded — so the check below
            # is never run on a value that does not exist.
            failed = check(value) if check else None
            if failed is None:
                return Answer(value, "ok", used)
            problem = failed
            tell(f"  {problem}")

    tell(f"  giving up after {attempts} attempts, using {default!r}")
    return Answer(default, "exhausted", used, problem)


# ###########################################################################
# CONVERTERS AND CHECKS — small, separate, and reusable
# ###########################################################################

def yes_no(raw):
    """Convert a human 'yes' to a bool. Raises ValueError like int() does."""
    text = raw.strip().lower()
    if text in ("y", "yes", "true", "1"):
        return True
    if text in ("n", "no", "false", "0"):
        return False
    raise ValueError(f"{raw!r} is not yes or no")


def one_of(options):
    """Build a converter that accepts a menu number OR the option's name."""
    def convert(raw):
        text = raw.strip().lower()
        for index, option in enumerate(options, 1):
            if text in (str(index), option.lower()):
                return option
        raise ValueError(f"{raw!r} is not one of {', '.join(options)}")
    convert.__name__ = "choice"
    return convert


def in_range(low, high):
    def check(value):
        if low <= value <= high:
            return None
        return f"{value} is outside {low}–{high}"
    return check


def finite(value):
    """The check that catches what NO exception would have caught."""
    if math.isfinite(value):
        return None
    return f"{value} is not a finite number"


def non_empty(value):
    return None if value.strip() else "that was blank"


# ###########################################################################
# A TEST DOUBLE FOR input()
# ###########################################################################

class ScriptedReader:
    """Replays a list of lines, then behaves like a closed stdin.

    Because `reader` is a parameter of ask(), a Ctrl-C and an end-of-input
    are both things a test can simply ARRANGE — no signals, no subprocess,
    no waiting for a human. Day 58 does this with pytest's monkeypatch;
    the idea is identical and it is Day 46's composition again.
    """

    def __init__(self, lines, interrupt_at=None):
        self.lines = list(lines)
        self.interrupt_at = interrupt_at
        self.calls = 0
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        self.calls += 1
        if self.calls == self.interrupt_at:
            raise KeyboardInterrupt          # the user pressed Ctrl-C
        if not self.lines:
            raise EOFError                   # stdin closed
        return self.lines.pop(0)


# ###########################################################################
# 1. TWENTY-TWO HOSTILE INPUTS
# ###########################################################################

print("=" * WIDTH)
print(f"{'THE SAME INPUTS, TWO PROGRAMS':^{WIDTH}}")
print("=" * WIDTH)

HOSTILE = [
    "8080", " 42 ", "1_000", "+7", "-5",          # accepted by int()
    "٤٢",                                          # Arabic-Indic digits: 42
    "3.7", "1e5", "0x1f", "1,000", "12abc",       # rejected by int()
    "", "   ", "\t", "True", "None", "①",
    "9" * 5000,                                    # over int()'s digit limit
    "inf", "nan",                                  # float() accepts BOTH
    "99999", "0",                                  # valid ints, invalid ports
]

def show(raw):
    """A safe display form: quoted, escaped, and never wider than 18."""
    text = repr(raw)
    return text if len(text) <= 18 else f"'{raw[:5]}…' x{len(raw)}"


print(f"  {'INPUT':<20}{'int(raw)':<16}{'ask(...)':<14}{'WHY':<26}")
print("-" * WIDTH)

naive_crashes = 0
rejected_by_check = 0
port_check = in_range(1, 65535)

for raw in HOSTILE:
    try:
        naive = repr(int(raw))
        naive = naive if len(naive) <= 14 else f"{naive[:8]}…"
    except Exception as exc:                       # noqa: BLE001 - measuring
        naive = type(exc).__name__
        naive_crashes += 1

    answer = ask("", convert=int, check=port_check, default=8080,
                 attempts=1, reader=ScriptedReader([raw]))
    rejected_by_check += not answer and "not a valid" not in answer.note
    verdict = str(answer.value) if answer else f"-> {answer.value}"
    print(f"  {show(raw):<20}{naive:<16}{verdict:<14}{answer.note[:26]:<26}")

print("-" * WIDTH)
print(f"  {'':<20}{f'{naive_crashes}/{len(HOSTILE)} crash':<16}"
      f"{'0 crash':<14}{f'{rejected_by_check} rejected by the check':<26}")


# ###########################################################################
# 2. THE ONE NO EXCEPTION CATCHES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE INPUT THAT RAISES NOTHING AND IS STILL WRONG':^{WIDTH}}")
print("=" * WIDTH)

print(f"  {'INPUT':<20}{'float(raw)':<14}{'int(raw)':<14}{'with check=finite'}")
print("-" * WIDTH)
for raw in ("inf", "nan", "1e400", "9" * 5000):
    try:
        as_float = repr(float(raw))
    except ValueError:
        as_float = "ValueError"
    try:
        as_int = repr(int(raw))
    except ValueError:
        as_int = "ValueError"
    guarded = ask("", convert=float, check=finite, default=0.0,
                  attempts=1, reader=ScriptedReader([raw]))
    print(f"  {show(raw):<20}{as_float:<14}{as_int:<14}"
          f"{guarded.value} ({guarded.outcome})")

print("""
  float('inf') and float('9' * 5000) both succeed. No exception, no
  warning, and every calculation downstream is now infinite — a timeout of
  inf seconds, a price of inf, a loop that never ends.

  try/except ONLY catches what raises. Everything else is your check
  function's job. Handling exceptions is half of handling input, and it is
  the half people stop at.""")


# ###########################################################################
# 3. THE THREE WAYS A READ CAN END BADLY
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'CTRL-C, CTRL-D, AND GIVING UP':^{WIDTH}}")
print("=" * WIDTH)

situations = [
    ("user types a valid port",
     ScriptedReader(["8080"])),
    ("user mistypes twice, then gets it right",
     ScriptedReader(["", "abc", "443"])),
    ("user presses Ctrl-C at the prompt",
     ScriptedReader(["8080"], interrupt_at=1)),
    ("user mistypes, then presses Ctrl-C",
     ScriptedReader(["abc", "8080"], interrupt_at=2)),
    ("stdin closes (Ctrl-D, or a dry pipe)",
     ScriptedReader([])),
    ("piped input runs out mid-question",
     ScriptedReader(["abc"])),
    ("three wrong answers in a row",
     ScriptedReader(["abc", "-1", "99999"])),
]

print(f"  {'SITUATION':<40}{'RESULT':<22}{'TRIES':>6}")
print("-" * WIDTH)

escaped = 0
for label, reader in situations:
    try:
        answer = ask("port? ", convert=int, check=port_check,
                     default=8080, reader=reader)
        result = str(answer)
    except BaseException as exc:              # noqa: BLE001 - the measurement
        result = f"ESCAPED {type(exc).__name__}"
        answer = Answer(None, "escaped", 0)
        escaped += 1
    print(f"  {label:<40}{result:<22}{answer.attempts:>6}")

print("-" * WIDTH)
print(f"  {'exceptions that escaped ask()':<40}{escaped:>28}")
print("""
  The `except BaseException` in that loop is the MEASUREMENT, not the
  design — it is there to prove nothing gets past ask(). It caught nothing,
  which is the claim this file is making.

  Note that Ctrl-C is caught SEPARATELY and reported as `cancelled`, not
  merged into the errors. A user who cancels has not made a mistake, and a
  program that says "invalid input" to a deliberate Ctrl-C is lying.""")


# ###########################################################################
# 4. FINALLY, AT A PROMPT
# ###########################################################################

print()
print("-" * WIDTH)
print("  WHERE `finally` ACTUALLY EARNS ITS KEEP")
print("-" * WIDTH)

trace = []


def guarded_session(reader):
    """A prompt loop with something that must happen on every exit path."""
    trace.append("open resource")
    try:
        answer = ask("name? ", check=non_empty, default="anonymous",
                     reader=reader)
        trace.append(f"read {answer.outcome}")
        return answer
    finally:
        trace.append("CLOSE resource")


for label, reader in [("normal", ScriptedReader(["Ada"])),
                      ("Ctrl-C", ScriptedReader(["Ada"], interrupt_at=1)),
                      ("no input", ScriptedReader([]))]:
    trace.clear()
    answer = guarded_session(reader)
    print(f"  {label:<10}{' -> '.join(trace):<46}{answer.outcome:>20}")

print("""
  Three different exits — a value, a cancel, an empty stdin — and
  "CLOSE resource" happens on all three. `return` inside try does not skip
  finally. That is the guarantee Day 53 turns into `with`.""")


# ###########################################################################
# 5. A WHOLE FORM, WITH NO WAY TO CRASH IT
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'A FORM THAT CANNOT TRACEBACK':^{WIDTH}}")
print("=" * WIDTH)

MODES = ["development", "staging", "production"]


def configure(reader, tell=lambda msg: None):
    """Six questions. Returns settings and whether the user completed them."""
    questions = [
        ("name", dict(prompt="service name: ", check=non_empty,
                      default="unnamed")),
        ("port", dict(prompt="port [1-65535]: ", convert=int,
                      check=in_range(1, 65535), default=8080)),
        ("mode", dict(prompt=f"mode {MODES}: ", convert=one_of(MODES),
                      default="development")),
        ("workers", dict(prompt="workers [1-64]: ", convert=int,
                         check=in_range(1, 64), default=4)),
        ("timeout", dict(prompt="timeout seconds: ", convert=float,
                         check=finite, default=30.0)),
        ("debug", dict(prompt="debug? [y/n]: ", convert=yes_no,
                       default=False)),
    ]
    settings, defaulted = {}, []
    for key, spec in questions:
        answer = ask(reader=reader, tell=tell, **spec)
        settings[key] = answer.value
        if answer.outcome == "cancelled":
            return settings, "cancelled", defaulted
        if not answer:
            defaulted.append(key)
    return settings, "complete", defaulted


forms = [
    ("everything typed correctly",
     ScriptedReader(["api", "8080", "production", "8", "30", "y"])),
    ("typos, then corrections",
     ScriptedReader(["", "api", "seventy", "443", "prod", "3", "8", "", "1e400",
                     "2.5", "yep", "yes"])),
    ("answers three, then walks away",
     ScriptedReader(["api", "8080", "2"])),
    ("cancels at the third question",
     ScriptedReader(["api", "8080", "production"], interrupt_at=3)),
]

for label, reader in forms:
    settings, outcome, defaulted = configure(reader)
    print(f"\n  {label}")
    print(f"    {'result':<12}{outcome}"
          f"{'' if not defaulted else '  (defaulted: ' + ', '.join(defaulted) + ')'}")
    for key, value in settings.items():
        typed = "" if key in defaulted or outcome == "cancelled" else "typed"
        print(f"      {key:<10}{value!r:<16}{typed}")

print("""
  Six wrong answers out of the twelve lines typed into the second form,
  three abandoned questions in the third, a Ctrl-C in the fourth — and four
  usable settings dictionaries, no tracebacks, and a caller that can tell
  which values the user actually chose and which were filled in.

  THAT LAST PART IS THE DESIGN. `settings['port'] == 8080` does not say
  whether the user typed it. `outcome` and `defaulted` do.""")


# ###########################################################################
# WHAT THIS FILE CLAIMS, AND HOW IT CHECKED
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

claims = [
    ("no input can make ask() raise",
     escaped == 0),
    ("the naive version crashes on most of them",
     naive_crashes >= 12),
    ("Ctrl-C is reported as cancelled, not as an error",
     ask("", reader=ScriptedReader(["x"], interrupt_at=1)).outcome
     == "cancelled"),
    ("an empty stdin stops instead of looping",
     ask("", reader=ScriptedReader([]), attempts=99).attempts == 1),
    ("a bad value retries exactly `attempts` times",
     ask("", convert=int, attempts=4,
         reader=ScriptedReader(["a", "b", "c", "d", "e"])).attempts == 4),
    ("the value is returned on the first good attempt",
     ask("", convert=int, reader=ScriptedReader(["7", "8"])).attempts == 1),
    ("check() never runs on a failed conversion",
     ask("", convert=int, check=lambda v: 1 / 0, attempts=1,
         reader=ScriptedReader(["abc"])).outcome == "exhausted"),
    ("float('inf') is rejected by the check, not by an exception",
     ask("", convert=float, check=finite, attempts=1,
         reader=ScriptedReader(["inf"])).outcome == "exhausted"),
    ("a real value that is falsy is still `ok`",
     ask("", convert=int, reader=ScriptedReader(["0"])).outcome == "ok"),
]

for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")

print("-" * WIDTH)
print(f"  {sum(passed for _, passed in claims)} of {len(claims)} checks pass")
print("""
  The seventh is the subtle one. `check=lambda v: 1 / 0` would raise
  ZeroDivisionError if it ever ran — and the conversion failed, so it never
  did. That is what putting the check in the `else:` block BUYS: it cannot
  run on a value that does not exist.""")
print("=" * WIDTH)


# ###########################################################################
# INTERACTIVE
# ###########################################################################

if {"--interactive", "-i"} & set(sys.argv):
    print("\nNow for real. Type nonsense. Press Ctrl-C. Press Ctrl-D.\n")
    settings, outcome, defaulted = configure(input, tell=print)
    print(f"\n  outcome   {outcome}")
    print(f"  defaulted {defaulted or 'nothing'}")
    for key, value in settings.items():
        print(f"  {key:<10}{value!r}")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change `except (ValueError, TypeError)` to `except Exception` and
#     re-run. Every check passes — and now a bug inside YOUR converter
#     looks exactly like the user typing "abc", so you would debug it by
#     staring at the input. Change it back.
#
#   * Change it to a bare `except:` instead. The Ctrl-C row of the second
#     table changes from `cancelled` to a retry, because you are now
#     catching the interrupt as if it were a typo.
#
#   * Delete the `check=finite` from the timeout question and pass 'inf'.
#     Nothing raises. Find where the wrong answer first becomes visible.
#
#   * Give ask() a `history` list so the reader can offer the previous
#     answer as the default. Notice that nothing about the exception
#     handling changes — the separation is doing its job.
#
#   * On Day 52, replace `check` returning a message with a check that
#     RAISES a ValidationError carrying the field name. Then ask() has one
#     failure path instead of two.
