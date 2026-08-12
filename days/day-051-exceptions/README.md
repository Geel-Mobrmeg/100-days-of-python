# Day 051 — Exceptions

**Phase 6 · Robust code** · ~80 minutes

> **Today's build:** a safe input reader that survives bad types, empty input and Ctrl-C without a traceback.

**Concepts:** `try` / `except` · `else` & `finally` · exception types · catching too much

---

## The article

### Why this day exists

Day 9 taught you to *read* a traceback. Fifty days later, every program you have written still ends
in one the moment reality disagrees with it.

That is the line between a script and software. A script may crash; the person who runs it wrote it
and can read the traceback. Software has users, and to a user a traceback means "this is broken and
I did nothing wrong".

### 1. The shape of the statement

```python
try:
    value = int(raw)          # only the line that can fail
except ValueError:
    value = 0                 # what to do when it does
else:
    log(value)                # runs only if try finished cleanly
finally:
    close()                   # runs on every way out
```

Four blocks, and `build.py`/`lesson.py` both trace which ones actually execute:

| what happened | try | except | else | finally | line after |
|---|:-:|:-:|:-:|:-:|:-:|
| nothing failed | ✓ | | ✓ | ✓ | ✓ |
| ValueError | ✓ | ✓ | | ✓ | ✓ |
| `return` inside try | ✓ | | | ✓ | — |

**Read the third row twice.** `return` runs `finally` and skips everything after the statement.
That is the entire reason `finally` exists: it is the only block that runs no matter how control
leaves — normal exit, `return`, or an exception on its way up the stack.

### 2. `else` is not decoration

```python
try:                              try:
    value = int(raw)                  value = int(raw)
    total += value                    total += value     # ← if THIS raises
except ValueError:                except ValueError:     #   ValueError, it is
    ...                               ...                #   caught by mistake
else:
    total += value
```

Keeping the `try` block down to the one line that can fail is how you make sure the handler catches
what you meant. Everything else goes in `else`.

Today's build uses this for a specific guarantee: the validation function lives in the `else`, so it
**cannot run on a value that failed to convert.** `build.py` proves it by passing
`check=lambda v: 1/0` alongside input that fails conversion — the `ZeroDivisionError` never happens.

### 3. The type you catch is a claim about what you expected

```python
try:
    value = int(data[key])
except KeyError:            # no such setting
    ...
except ValueError:          # present, but not a number
    ...
```

Two causes, two responses, and the code says which is which. `except Exception` collapses them into
one branch and a shrug.

Clauses are tried top to bottom and the **first match wins**, so specific types go above general
ones. Python will not warn you that a clause below `except Exception` is unreachable.

Use a tuple — `except (ValueError, TypeError)` — when the *response* is the same. Use two clauses
when it differs. The shape of the code should match the shape of your intent.

### 4. Catching too much

This is the part that is worth getting exactly right, because the failure is invisible.

```
caught by
Exception?          ancestry
yes     ValueError          BaseException > Exception > ValueError
yes     OSError             BaseException > Exception > OSError
NO      KeyboardInterrupt   BaseException > KeyboardInterrupt
NO      SystemExit          BaseException > SystemExit
NO      GeneratorExit       BaseException > GeneratorExit
```

`KeyboardInterrupt`, `SystemExit` and `GeneratorExit` deliberately sit *outside* `Exception`, so
that `except Exception` — which is what you want around a plausible failure — cannot swallow the
user's Ctrl-C, a `sys.exit()`, or a generator being closed.

A bare `except:` throws that guarantee away. It is `except BaseException:` written in a way that
looks harmless, and it makes Ctrl-C stop working.

**The rule:**

- catch the **narrowest type that could actually happen**;
- `except Exception` only at the outermost level of a program, where the alternative is a traceback
  in a user's face;
- bare `except:` essentially never.

### 5. `except: pass` is worse than a crash

```python
for record in records:
    try:
        total += int(record["qty"])
    except:
        pass
```

`lesson.py` runs this over four records and gets **11** where the answer is **16**. One record was
dropped for bad data; the other for a typo in the *key*, which is a bug in the code. Both vanished,
and the program reported success.

`except: pass` does not handle an error. It converts a loud failure into a quiet wrong answer, and
the loud one is the one that gets fixed. If you genuinely mean to continue, say so:

```python
except ValueError:
    skipped.append(record)      # ...and report len(skipped) at the end
```

Now "we ignored 1 of 4 rows" is a fact the caller can see — and the `KeyError` still crashes,
correctly, because that one is *your* bug.

> **Handle what you expected. Let your own bugs crash.**

### 6. EAFP, and the gap LBYL cannot close

Python's convention is *easier to ask forgiveness than permission*: try it, handle the failure —
rather than checking first. `lesson.py` times both, 200,000 calls each:

| | LBYL | EAFP |
|---|---:|---:|
| key present | 0.032s | **0.018s** |
| key absent | **0.022s** | 0.043s |

A `try` that does not fire is nearly free; one that fires is expensive. So EAFP wins when failure is
*rare* — a statement about your data, not about style.

The stronger argument is not speed:

```python
if path.exists():      # true here...
    open(path)         # ...and the file is gone here
```

Nothing closes that gap, because the world changes between two lines. `try: open(path)` has no gap:
the check and the act are the same operation.

Use LBYL when the check is cheap, total and local — `if items:` before indexing, `if n != 0` before
dividing.

### 7. `as exc` disappears

```python
except ValueError as exc:
    message = str(exc)      # copy out anything you need
print(exc)                  # NameError — Python deleted it
```

Python deletes the name at the end of the block; otherwise the exception would keep its whole
traceback, and every frame's local variables, alive. Copy what you need into your own variable.

### 8. What today's build is really about

The reader has three separate jobs, and separating them is the design:

| job | what it is | what it catches |
|---|---|---|
| read | `reader(prompt)` | `EOFError`, `KeyboardInterrupt` |
| convert | `int`, `float`, `yes_no` | `ValueError`, `TypeError` |
| check | `in_range(1, 65535)`, `finite` | **things no exception would catch** |

That third row is the one people skip. `float("inf")` and `float("9" * 5000)` both succeed — no
exception, no warning — and every calculation downstream is now infinite. `int("١٢٣")` returns 123,
because Python accepts any Unicode decimal digit. `int("1_000")` returns 1000.

**`try`/`except` only catches what raises.** Handling exceptions is half of handling input, and it
is the half people stop at.

The reader is also a *parameter*, defaulting to `input`. That one decision is what lets `build.py`
test a Ctrl-C, a closed stdin and twelve typos without a human being present — and it is Day 46's
composition, arriving where you needed it.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Which blocks run when, why bare `except:` breaks Ctrl-C, `as exc` vanishing, EAFP timed, and `except: pass` producing a wrong answer. |
| `build.py`  | The reader: 22 hostile inputs, 7 ways a prompt can end badly, a 6-question form that cannot traceback, and 9 checks. |

```bash
python3 lesson.py
python3 build.py                 # the report
python3 build.py --interactive   # then a real prompt — try Ctrl-C and Ctrl-D
```

---

## Common mistakes

**Bare `except:`.** Catches Ctrl-C and `sys.exit()`. Your program can no longer be stopped.

**`except Exception` everywhere.** Fine at the top of a program, wrong inside a function that knows
what can go wrong.

**`except: pass`.** A wrong answer, delivered quietly.

**Too much inside `try`.** The handler starts catching failures from lines you never meant it to.

**Catching `Exception` to hide a bug you have not diagnosed.** It is still there, and now it is
silent.

**Assuming a successful conversion is a valid value.** `inf`, `nan`, `-1`, `0`, 5,000 digits.

**Catching an exception and losing the detail.** At minimum record `str(exc)`; Day 52 does it
properly.

**Retrying forever.** A closed stdin never becomes open. Count attempts, and treat `EOFError` as
final.

---

## Exercises

1. Write a `try` with all four blocks, and print from each. Then add `return` to the `try` and run
   it again.
2. Take a function that crashes on bad input and make it survive without changing what it returns
   for good input.
3. Write the bare-`except:` version of a prompt loop, then try to Ctrl-C out of it.
4. Time EAFP against LBYL on a dictionary where 90% of lookups miss, then where 1% miss.
5. Write a converter that raises `ValueError` (like `int` does) and pass it to today's `ask()`.
6. Add a check that rejects an input no exception would have caught.
7. Put `except Exception` above `except ValueError` and confirm Python says nothing.

---

## Checklist

- [ ] I catch the narrowest type that can actually occur
- [ ] I know why `KeyboardInterrupt` is not an `Exception`
- [ ] I never write a bare `except:`
- [ ] I put only the risky line in `try`, and the rest in `else`
- [ ] I use `finally` for cleanup and know it runs on `return`
- [ ] I never write `except: pass` without recording what was skipped
- [ ] I know that a successful conversion is not a valid value
- [ ] I let my own bugs crash
