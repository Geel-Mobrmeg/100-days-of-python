"""Day 051 — Exceptions: try, except, else, finally.

    python3 lesson.py

Day 9 read tracebacks. Today we stop them reaching the user.

Nothing here RAISES an exception on purpose except to stand in for
something the user or the world would have done — deliberately raising your
own is tomorrow.
"""

import builtins
import timeit

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. What an unhandled exception costs
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. THE SHAPE OF THE STATEMENT':^{WIDTH}}")
print("=" * WIDTH)

raw = "twelve"
try:
    age = int(raw)
except ValueError:
    age = None

print(f"  int({raw!r}) -> handled, age is {age}")
print("""
  Without the try, that line ends the program. Not "returns None", not
  "prints a warning" — the interpreter unwinds every frame and exits.
  Everything below it, including anything that was half-written to disk,
  simply does not happen.""")


# ---------------------------------------------------------------------------
# 2. The TYPE is the whole point
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  THE TYPE YOU CATCH IS A STATEMENT ABOUT WHAT YOU EXPECTED")
print("-" * WIDTH)

data = {"port": "8080", "debug": "yes", "retries": "three"}

for key in ("port", "retries", "timeout"):
    try:
        value = int(data[key])
    except KeyError:
        outcome = "no such setting  (KeyError)"
    except ValueError:
        outcome = "not a number     (ValueError)"
    else:
        outcome = f"ok, {value}"
    print(f"  {key:<12}{outcome}")

print("""
  Three outcomes, three DIFFERENT causes, and the code says which is which.
  `except Exception` here would give one branch and a shrug.

  ORDER MATTERS: except clauses are tried top to bottom and the FIRST
  match wins, so specific types must come before general ones. Putting
  `except Exception` first makes every clause below it dead code.""")


# ---------------------------------------------------------------------------
# 3. try / except / else / finally — which parts actually run
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. FOUR BLOCKS, AND WHEN EACH RUNS':^{WIDTH}}")
print("=" * WIDTH)


def scenario(mode, log):
    """Records which blocks execute. Called three ways below."""
    try:
        log.append("try")
        if mode == "boom":
            int("x")                       # ValueError
        if mode == "return":
            return
    except ValueError:
        log.append("except")
    else:
        log.append("else")                 # only if try finished cleanly
    finally:
        log.append("finally")              # always, no exceptions
    log.append("after")


for mode in ("clean", "boom", "return"):
    log = []
    scenario(mode, log)
    print(f"  {mode:<10}{' -> '.join(log)}")

print("""
  READ THE THIRD ROW TWICE. `return` inside try still runs finally, and
  does NOT run the line after the statement. That is the entire reason
  finally exists: it is the only block that runs on the way out no matter
  how you leave — normal exit, return, or an exception on its way up.

  ELSE IS NOT DECORATION. Code that belongs after a successful try should
  go in else, not at the bottom of try, so that the try block contains ONLY
  the line that might fail:

      try:                          try:
          value = int(raw)              value = int(raw)
          total += value                total += value      <- ValueError
      except ValueError:            except ValueError:          from HERE
          ...                           ...                     is caught
                                                                by accident
  The version on the left catches exactly what it meant to.""")


# ---------------------------------------------------------------------------
# 4. Catching too much
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. CATCHING TOO MUCH':^{WIDTH}}")
print("=" * WIDTH)


def with_bare_except():
    try:
        raise KeyboardInterrupt          # stands in for the user pressing ^C
    except:                              # noqa: E722 - the exhibit
        return "swallowed"
    return "not reached"


def with_except_exception():
    try:
        raise KeyboardInterrupt
    except Exception:
        return "swallowed"


print(f"  bare `except:`        {with_bare_except()} the Ctrl-C")
try:
    with_except_exception()
    print("  `except Exception:`   swallowed the Ctrl-C")
except KeyboardInterrupt:
    print("  `except Exception:`   let the Ctrl-C through   <- correct")

print("\n  WHY: the hierarchy above Exception is not empty.")
print(f"\n  {'caught by':<8}{'':<20}ancestry")
print(f"  {'Exception?':<8}")
for name in ("ValueError", "OSError", "KeyboardInterrupt",
             "SystemExit", "GeneratorExit"):
    cls = getattr(builtins, name)
    chain = " > ".join(c.__name__ for c in reversed(cls.__mro__[:-1]))
    mark = "yes" if issubclass(cls, Exception) else "NO"
    print(f"  {mark:<8}{name:<20}{chain}")

print("""
  KeyboardInterrupt, SystemExit and GeneratorExit inherit from
  BaseException, NOT Exception. That is a deliberate design decision so
  that `except Exception` — which is what you want around a plausible
  failure — cannot accidentally trap the user's Ctrl-C, sys.exit(), or a
  generator being closed.

  A bare `except:` throws that away. It is `except BaseException:` written
  in a way that looks harmless.

  THE RULE:  catch the narrowest type that could actually happen.
             `except Exception` only at the OUTERMOST level of a program,
             where the alternative is a traceback in a user's face.
             Bare `except:` essentially never.""")


# ---------------------------------------------------------------------------
# 5. except ... as exc
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  `as exc` — and the surprise at the end of the block")
print("-" * WIDTH)

try:
    int("twelve")
except ValueError as exc:
    print(f"  message   {exc}")
    print(f"  type      {type(exc).__name__}")
    print(f"  args      {exc.args}")
    message = str(exc)                     # copy anything you need OUT

try:
    print(exc)
except NameError:
    print("  after the block: NameError — Python DELETES exc on the way out")

print(f"  the copy survives: {message!r}")
print("""
  Python deletes the name at the end of the except block (it would keep the
  whole traceback, and every frame's locals, alive). If you need the detail
  later, copy it into your own variable — as above.""")


# ---------------------------------------------------------------------------
# 6. Catching several at once
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  ONE CLAUSE, SEVERAL TYPES")
print("-" * WIDTH)

for raw in ("42", "abc", None, [1]):
    try:
        n = int(raw)
    except (TypeError, ValueError) as exc:
        n = f"{type(exc).__name__}"
    print(f"  int({raw!r:<6}) -> {n}")

print("""
  A tuple, not two clauses, when the RESPONSE is the same. Two clauses when
  the response differs. The shape of the code should match the shape of
  your intent.""")


# ---------------------------------------------------------------------------
# 7. EAFP vs LBYL
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. ASK FORGIVENESS, NOT PERMISSION':^{WIDTH}}")
print("=" * WIDTH)

settings = {"host": "localhost", "port": 8080}


def lbyl(key):
    """Look Before You Leap."""
    if key in settings:
        return settings[key]
    return "default"


def eafp(key):
    """Easier to Ask Forgiveness than Permission."""
    try:
        return settings[key]
    except KeyError:
        return "default"


runs = 200_000
results = []
for label, fn, key in [("hit  (key present)", None, "host"),
                       ("miss (key absent)", None, "nope")]:
    t_lbyl = timeit.timeit(lambda: lbyl(key), number=runs)
    t_eafp = timeit.timeit(lambda: eafp(key), number=runs)
    results.append((label, t_lbyl, t_eafp))

print(f"  {'':<22}{'LBYL':>10}{'EAFP':>10}{'':>6}{runs:,} calls")
for label, t_lbyl, t_eafp in results:
    faster = "EAFP" if t_eafp < t_lbyl else "LBYL"
    print(f"  {label:<22}{t_lbyl:>9.3f}s{t_eafp:>9.3f}s   {faster} wins")

print("""
  A try that does not fire is nearly free; one that fires is expensive.
  So EAFP wins when the failure is RARE and loses when it is common — which
  is a statement about your data, not about style.

  THE STRONGER ARGUMENT IS NOT SPEED. It is that LBYL has a gap between the
  check and the act:

      if path.exists():        <- true here...
          open(path)           <- ...and the file is gone here

  Nothing can close that gap — not more checks — because the world changes
  between two lines. `try: open(path) except FileNotFoundError:` has no
  gap, because the check and the act are the same operation. (Day 53.)

  USE LBYL when the check is cheap, total and local: `if items:` before
  indexing, `if n != 0` before dividing.""")


# ---------------------------------------------------------------------------
# 8. The one to never write
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. THE ANTI-PATTERN':^{WIDTH}}")
print("=" * WIDTH)

records = [{"qty": "3"}, {"qty": "x"}, {"quantity": "5"}, {"qty": "8"}]

total = 0
for record in records:
    try:
        total += int(record["qty"])
    except:                                # noqa: E722 - the exhibit
        pass

print(f"  total with `except: pass`   {total}")
print("""
  The answer is 11 and it should be 16. Two records were dropped — one for
  a typo in the DATA and one for a typo in the KEY, which is a bug in this
  code — and the program reported success either way.

  `except: pass` does not handle an error. It converts a loud failure into
  a quiet wrong answer, which is strictly worse, because the loud one gets
  fixed.

  IF YOU GENUINELY WANT TO CONTINUE, SAY SO IN THE CODE:

      except ValueError:
          skipped.append(record)     <- and report len(skipped) at the end

  Now "we ignored 1 of 4 rows" is a fact the caller can see.""")

skipped = []
total = 0
crashed = None
try:
    for index, record in enumerate(records):
        try:
            total += int(record["qty"])
        except ValueError:
            skipped.append(record)         # bad DATA — expected, recorded
except KeyError as exc:                    # my BUG — caught only to print it
    crashed = f"record {index}: KeyError {exc}"

print(f"  {'total before it stopped':<32}{total}")
print(f"  {'rows skipped as bad data':<32}{len(skipped)} of {len(records)}")
print(f"  {'stopped at':<32}{crashed}")
print("""
  The ValueError is HANDLED, because bad data in a feed is a thing I
  expected and can describe. The KeyError is not, so it stopped the run —
  correctly, because a record with no 'qty' key means MY assumption about
  the data's shape is wrong, and no amount of skipping fixes that.

  (The outer try above exists only so this file can print the crash and
  keep going. In real code there is no outer try, and the program dies.)

  HANDLE WHAT YOU EXPECTED. LET YOUR OWN BUGS CRASH.""")

print()
print("=" * WIDTH)
print("""  1. Catch the narrowest type that can actually occur.
  2. Put ONLY the risky line in try; the rest goes in else.
  3. finally for cleanup — it runs on return and on the way up.
  4. Never bare `except:`; `except Exception` only at the top level.
  5. `except: pass` turns a crash into a wrong answer.
  6. Handle what you expected. Let your own bugs crash.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Put `except Exception` above `except ValueError` and find out that
#     Python does not warn you the second clause is unreachable.
#
#   * Add a `return` to the finally block of scenario(). It swallows the
#     exception that was on its way out — silently. Work out why that is
#     almost never what you want.
#
#   * Time eafp() on a dict where 90% of lookups miss, and again where 1%
#     miss. The advice reverses.
#
#   * Wrap a loop body in try/except and then move the try OUTSIDE the
#     loop. One version processes the remaining items; the other stops.
#     That choice is the whole design, and it is invisible in the diff.
