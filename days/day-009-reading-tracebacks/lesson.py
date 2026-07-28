"""Day 009 — Reading tracebacks.

This lesson runs the five broken scripts for you and prints their real
tracebacks, annotated. Nothing here is a mock-up; every traceback below came
out of Python a fraction of a second before you read it.

    python3 lesson.py

(It uses `subprocess` to launch the broken files as separate processes. That
 is the lesson's plumbing, not its content — you meet subprocess properly
 much later. It is used because you do not have try/except until Day 51, and
 a lesson about crashes has to be able to survive one.)
"""

import subprocess
import sys
from pathlib import Path

BROKEN = Path(__file__).parent / "broken"
WIDTH = 74


def run(script):
    """Run a broken script and return whatever it printed, stdout and stderr."""
    result = subprocess.run(
        [sys.executable, str(BROKEN / script)],
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


# ---------------------------------------------------------------------------
# 1. The anatomy of a traceback
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("1. ANATOMY — read it from the BOTTOM")
print("=" * WIDTH)
print("""
    Traceback (most recent call last):     <- a header. Skip it.
      File "bug_2.py", line 13, in <module>   <- WHERE
        print("Subtotal: " + SUBTOTAL)        <- the failing line
              ~~~~~~~~~~~~~^~~~~~~~~~         <- the exact subexpression
    TypeError: can only concatenate ...       <- WHAT. Read this FIRST.

Three habits, in order of how much time they save:

  1. READ THE LAST LINE FIRST. It names the exception type and explains it
     in English. Beginners read the first line, panic, and stop.

  2. THEN read upward for the file and line number. In a stack of calls,
     "most recent call last" means YOUR code is usually near the bottom;
     library frames above it are rarely where the mistake is.

  3. LOOK AT THE ^^^ MARKERS. Python 3.11+ underlines the exact
     subexpression that failed, which distinguishes `a[i]` from `b[j]` on a
     line that has both.
""")

# ---------------------------------------------------------------------------
# 2-6. The five bugs, live
# ---------------------------------------------------------------------------

CASES = [
    (
        "bug_1.py",
        "ValueError — right type, wrong value",
        "The message quotes the offending value: '3.0'. int() on a string\n"
        "wants an integer literal; int() on a float truncates. Day 6.",
    ),
    (
        "bug_2.py",
        "TypeError — wrong type entirely",
        "Compare with ValueError above. TypeError means the operation does\n"
        "not apply to that kind of thing at all. Python refuses to guess\n"
        "what 'text plus number' should mean.",
    ),
    (
        "bug_3.py",
        "IndexError — the sequence was shorter than you assumed",
        "Note the ^^^ under parts_3[1] specifically. The data is not\n"
        "malformed; it is a person with one name. Your assumption was the\n"
        "bug, and it was never written down.",
    ),
    (
        "bug_4.py",
        "NameError — and Python tells you the fix",
        "'Did you mean: celsius_reading?' Python 3.10+ suggests the closest\n"
        "name in scope. A linter finds this without running anything (F821).",
    ),
    (
        "bug_5.py",
        "ZeroDivisionError — where it DIED, not where it went WRONG",
        "The traceback points at the division. The bug is the filter four\n"
        "lines earlier, matching ' 200ms ' instead of ' 200 '. It matched\n"
        "nothing, silently, and the emptiness travelled downstream.\n"
        "A traceback is the scene of the crash, not the scene of the crime.",
    ),
]

for number, (script, title, note) in enumerate(CASES, start=2):
    print()
    print("=" * WIDTH)
    print(f"{number}. {title}")
    print("=" * WIDTH)
    output = run(script)
    for line in output.splitlines()[-6:]:
        print("   " + line)
    print()
    for line in note.splitlines():
        print("   >> " + line)

# ---------------------------------------------------------------------------
# 7. Print debugging
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print("7. PRINT DEBUGGING — unfashionable, and what everybody actually does")
print("=" * WIDTH)

log = "GET /home 200 118ms"
parts = log.split()

# The f-string `=` form (Day 4) is the whole technique. It prints the
# EXPRESSION as well as the value, so a screen of these stays readable.
print(f"{log=}")
print(f"{parts=}")
print(f"{len(parts)=}")
print(f"{parts[-1]=}")
print(f"{parts[-1].replace('ms', '')=}")

print("""
   >> Two rules that make this work instead of becoming noise:
   >>   * Print the EXPRESSION, not a label you typed. f"{count=}" cannot
   >>     drift out of sync with the code the way print("count", n) can.
   >>   * Print !r for anything textual. f"{value!r}" shows ' 42 ' where
   >>     f"{value}" shows 42, and the difference is the bug.
   >>
   >> Walk BACKWARDS from the crash, printing each value, until one of them
   >> is not what you assumed. That value's line is the real bug.
""")

# ---------------------------------------------------------------------------
# 8. breakpoint()
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print("8. breakpoint() — when prints are not enough")
print("=" * WIDTH)
print("""
Put `breakpoint()` on any line and run the script normally. Python stops
there and gives you an interactive prompt (pdb) with every local variable
live. The six commands that cover almost everything:

    n     next line (step over)
    s     step INTO the call on this line
    c     continue until the next breakpoint or the end
    l     list the source around here
    p x   print x        (pp x for pretty-print)
    q     quit

Type a bare variable name to see it. Type any Python expression to evaluate
it against the live state — that is the part prints cannot do.

Set PYTHONBREAKPOINT=0 in the environment to disable every breakpoint()
in a file without deleting them. Ship code with none of them anyway.
""")

print("=" * WIDTH)
print("9. RUBBER-DUCKING")
print("=" * WIDTH)
print("""
Explain the broken code, out loud, line by line, to something that cannot
help you. The sentence you cannot finish is the bug.

This is not a joke and it is not a metaphor for asking a colleague. It works
because reading code silently lets you skim the line you assume is correct,
and speaking it forces you to actually evaluate it. Most people find the bug
partway through the explanation and never finish the sentence.

Corollary: write the bug report before you ask for help. Half the time you
will not need to send it.
""")
