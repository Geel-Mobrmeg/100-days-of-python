# Day 052 — Raising and custom exceptions

**Phase 6 · Robust code** · ~80 minutes

> **Today's build:** a validation layer for your inventory system with domain-specific error types.

**Concepts:** `raise` · exception hierarchies · `raise ... from` · error messages people can act on

---

## The article

### Why this day exists

Yesterday was the catching end. Today is the raising end, and it is the one that decides how good
yesterday's code can possibly be.

Day 50's inventory system raised `ValueError`, `KeyError` and `TypeError`. Honest, and useless to a
caller: you cannot tell "the supplier sent a price of −3" from "there is a bug in my code", and you
cannot put either next to the field it belongs to on a form.

### 1. Pick the type. Never `raise Exception(...)`

| Type | When |
|---|---|
| `ValueError` | the type is right, the **value** is not |
| `TypeError` | the **type** is wrong |
| `KeyError` / `IndexError` | a lookup that is not there (`LookupError` is the base of both) |
| `OSError` | the world said no — files, sockets, permissions |
| `RuntimeError` | nothing more specific fits, and you have tried |
| `NotImplementedError` | an abstract method — though Day 49 showed `@abstractmethod` is better |
| `StopIteration` | only from `__next__`. Never by hand. |
| `AssertionError` | never raise it deliberately |

`raise Exception("...")` forces every caller who wants to handle it to write `except Exception`,
which then catches everything else too. It is the raising equivalent of a bare `except:`.

### 2. The message is an interface

```
Error                                               says nothing
Invalid input                                       which input? invalid how?
Invalid port                                        still not saying what I gave
Invalid port: 99999                                 now I can see my mistake
port must be 1-65535, got 99999                     and now I know the rule
port must be 1-65535, got 99999 (from PORT in .env) ...and where to fix it
```

Four things, and the last is the one people forget:

1. **what** is wrong — `port`
2. **what was given** — `got 99999`
3. **what was expected** — `must be 1-65535`
4. **where it came from** — `from PORT in .env`

Write it for the person reading it at 3am who did not write the code and cannot see your variables.
Every message that makes them open your source is a message that failed.

### 3. A class of your own — and when not to bother

```python
class ValidationError(InventoryError, ValueError):
    def __init__(self, field, value, expected=None, source=None):
        self.field = field
        self.value = value
        self.expected = expected or type(self).expected
        self.source = source
        super().__init__(str(self))
```

Three things that buys, all of them concrete:

- `except InventoryError` catches all of yours **and nothing else**;
- the caller reads `exc.field` instead of parsing your message with a regular expression;
- the traceback says `OutOfRange`, not `ValueError`, so the log is searchable.

Note the second base class. `ValidationError` is **also a `ValueError`**, so code written before
these types existed and says `except ValueError` keeps working. That is how you add precise
exception types to a library people already use — `build.py` checks both clauses catch it, and
checks that `InsufficientStock` (a different branch) is *not* a `ValueError`.

**When not to bother:** if the caller would do the same thing for your exception as for the builtin,
use the builtin. A custom class whose body is `pass` and which nobody catches separately is noise.

### 4. A hierarchy is a set of choices you offer the caller

```
InventoryError                    "something in my domain went wrong"
  ├── ValidationError             "...an incoming field is unusable"
  │     ├── MissingField
  │     ├── BadType
  │     ├── OutOfRange
  │     └── UnknownReference
  ├── StockError
  │     └── InsufficientStock
  └── DuplicateSku
```

Each level is a decision somebody might make. If nobody would ever catch `BadType` separately from
`OutOfRange`, do not split them — every level is a level every reader has to learn. Two or three
deep is almost always enough.

### 5. `raise ... from` — one word, and the reader's first guess changes

```
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

The above exception was the direct cause of the following exception:

BadType: cost must be a decimal amount, got 'free' (from feed line 3)
```

| | what the traceback says | how it reads |
|---|---|---|
| no `from` | "During handling of the above exception, **another** exception occurred" | your handler looks buggy |
| `from exc` | "The above exception was the **direct cause**" | deliberate translation |
| `from None` | the original is hidden entirely | correct when internals are noise, wrong when they are the clue |

Python keeps the context (`__context__`) either way. `from exc` sets `__cause__` and changes the
wording — from *the library is broken* to *my input was wrong*.

**Default to `from exc`** whenever you convert somebody else's exception into yours.

### 6. Re-raising: `raise` and `raise exc` are not the same

```python
except ConfigError:
    log.warning("config failed, using defaults")
    raise            # keeps the ORIGINAL traceback
```

Bare `raise` re-raises what is being handled with its traceback intact, so the report still points
at the line that failed. `raise exc` re-raises it *from the handler*, and the original line is gone
— `lesson.py` counts the frames to show the difference.

### 7. `assert` is not error handling

```python
assert port > 0, "port must be positive"
```

`python3 -O` removes that line entirely. Every assert becomes a no-op and the validation you thought
you had is gone.

- **assert** — a claim about *your own* code that should be impossible to break; an internal
  invariant; a check in a test.
- **raise** — anything about input, the world, or a caller's mistake.

A useful test: *could a user cause this?* Then it is a `raise`.

### 8. More than one thing wrong at once

```python
if problems:
    raise ExceptionGroup(f"{len(problems)} problems", problems)
...
except* ValidationError as group:
    for exc in group.exceptions:
        ...
```

Python 3.11's `ExceptionGroup`, and `except*` to unpack it. Today's build validates a seven-record
supplier feed and reports **10 problems across 5 records in one pass**. Raising on the first would
have meant one round trip per problem — a form that reports one field at a time is the same bug with
a nicer font.

Use a group when the failures are **independent** and the caller wants all of them. Use a plain
`raise` when the first failure makes the rest meaningless: there is no point checking the port of a
config file you could not open.

### 9. Why carrying data matters, in one demonstration

The build takes the same three exception objects and produces three outputs:

```
1. FOR A PERSON      cost must be greater than 0, got '-48' (from feed line 4)
2. FOR A LOG         OutOfRange  field=cost  value='-48'
3. FOR AN API        {"field": "cost", "problem": "OutOfRange",
                      "expected": "greater than 0", "got": "-48"}
```

Nobody re-typed the field name and nobody parsed a message to get it back out. An exception class is
a place to keep everything you knew at the moment it went wrong — most of which is unrecoverable one
frame later, which is exactly why it has to be captured where it is raised.

`UnknownReference` carries a `suggestion`, so a mistyped `premuim` produces *"did you mean
premium?"*. That is only possible because there was somewhere to put it.

### 10. And your own bugs still crash

The build runs five operations through one `except InventoryError` clause. Four are handled. The
fifth is a deliberate typo in the catalogue's own code, and it goes straight past into an
`AttributeError` — which is what should happen, because no amount of retrying fixes a typo.

That separation is the entire reason for a domain base class. `except Exception` would have swallowed
the bug and reported it to the user as an inventory problem.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Choosing the type, message anatomy, hierarchies, the three `raise ... from` tracebacks side by side, re-raise frame counts, `assert` under `-O`, and `ExceptionGroup`. |
| `build.py`  | The validation layer: 8 error types, a 7-record supplier feed producing 10 problems in one pass, the same errors as prose/log/JSON, and 12 checks. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`raise Exception("...")`.** Nobody can catch it precisely.

**A message with no value in it.** "Invalid input" cannot be acted on.

**Only a message, no attributes.** The caller ends up parsing your prose.

**Converting an exception without `from exc`.** The traceback blames your handler.

**`raise exc` instead of bare `raise`.** Throws away the line that actually failed.

**A hierarchy nobody catches at.** Levels are for decisions, not for tidiness.

**`assert` as validation.** Gone under `-O`.

**Stopping at the first problem** when the caller could have fixed them all in one go.

**Catching your own exception right where you raised it.** If you handle it immediately, do not
raise — just return the other value.

---

## Exercises

1. Take three `raise ValueError(...)` calls in your own code and give each the right type and a
   four-part message.
2. Write a two-level hierarchy for a domain you know, and justify every level by naming a caller who
   would catch at it.
3. Convert a library exception into yours with `from exc`, then without, and compare tracebacks.
4. Add data to an exception (`field`, `value`, `expected`) and build a JSON error response from it
   without touching the message.
5. Turn a first-failure validator into an `ExceptionGroup` one, and count the round trips it saves
   on a record with four bad fields.
6. Add `exc.add_note(...)` (3.11) and see where it appears.
7. Write validation with `assert`, then run the file under `python3 -O`.

---

## Checklist

- [ ] I never raise the base `Exception`
- [ ] My messages say what, what was given, what was expected, and from where
- [ ] I have one base class per package so callers get one clause
- [ ] My exceptions carry data, not only prose
- [ ] I use `raise ... from exc` when I translate an exception
- [ ] I use bare `raise` to re-raise
- [ ] I know `assert` disappears under `-O`
- [ ] I report independent failures together
- [ ] My own bugs still crash
