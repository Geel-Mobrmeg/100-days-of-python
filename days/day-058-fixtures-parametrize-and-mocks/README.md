# Day 058 — Fixtures, parametrize and mocks

**Phase 6 · Robust code** · ~90 minutes

> **Today's build:** table-driven tests for your validators, plus a mocked clock so time-based code is testable.

**Concepts:** `@pytest.fixture` · `@parametrize` · `monkeypatch` · `tmp_path` · isolating side effects

---

## The article

### Why this day exists

Day 57's suite was 146 cases of plain functions. Today is about the two things that stop a suite
from growing badly: **shared setup that does not repeat itself**, and **a way to take the world away
from code that reaches for it**.

### 1. A fixture is a function you ask for by name

```python
@pytest.fixture
def diary():
    return [Booking("ZZ-0001"), Booking("ZZ-0002")]

def test_something(diary):        # the PARAMETER NAME is the request
    assert len(diary) == 2
```

No import, no `setUp`, no `self`. pytest reads the parameter names, finds a fixture of that name,
builds it and passes it in. It looks in: the test file, `conftest.py` beside it, `conftest.py` in any
parent, then plugins.

`conftest.py` is the shared one — and **nothing imports it**. pytest finds it.

### 2. Scope, measured

```
BUILT: function=5 module=1 session=1
5 passed
```

| scope | built |
|---|---|
| `function` (default) | fresh for every test |
| `class` | once per test class |
| `module` | once per file |
| `session` | once for the whole run |

**The default is the right one.** A wider scope is a shared object, and a shared *mutable* object is
a test that passes alone and fails in the suite — or worse, passes in the suite and fails alone,
which people then "fix" by pinning the test order.

Widen only for something expensive and read-only, and hand out a copy.

### 3. `yield`: setup above, teardown below

```
ORDER 1. outer setup        ORDER  6. outer setup
ORDER 2. inner setup        ORDER  7. inner setup
ORDER 3. test one BODY      ORDER  8. test two BODY      ← this test FAILED
ORDER 4. inner teardown     ORDER  9. inner teardown
ORDER 5. outer teardown     ORDER 10. outer teardown
```

Setup runs outermost-first, teardown innermost-first, and the whole cycle repeats per test. **Steps
8–10 are the ones that matter:** test two failed and both teardowns still ran. A fixture's cleanup is
a `finally`, not a hopeful last line — Day 53's `with`, one layer up.

### 4. The built-ins

| | |
|---|---|
| `tmp_path` | a fresh empty directory, cleaned up for you |
| `monkeypatch` | set/delete an attribute, item, env var or cwd — **all undone** |
| `capsys` | what the test printed: `capsys.readouterr().out` |
| `caplog` | what it logged (Day 67) |

```python
monkeypatch.setattr(module, "name", replacement)
monkeypatch.setenv("API_KEY", "test-key")
monkeypatch.delenv("API_KEY", raising=False)
monkeypatch.chdir(tmp_path)
```

**The undoing is the point.** Assign to a module yourself and you have changed it for every test that
runs afterwards — and the failure appears in a different file.

### 5. The mistake everybody makes once

```
WRONG TARGET  is_open() -> True
RIGHT TARGET  is_open() -> False
```

Both patches are correct, targeted and undone. Only one has any effect.

```python
import datetime
datetime.datetime.now()          # patch the MODULE's attribute

from datetime import datetime
datetime.now()                   # patch YOUR module's name
```

`from X import Y` copies the reference at import time. Patching `X.Y` afterwards rebinds `X`'s
attribute and leaves your module pointing at the original object.

**Patch the name in the module that calls it, not the module that defines it.** Today's suite
asserts exactly this, because the rule is far easier to remember once you have watched it fail.

### 6. `Mock`, and what it costs

```python
notifier = Mock()
confirm(booking, notifier)

notifier.send.assert_called_once()
notifier.send.call_args.args          # the arguments, to inspect
notifier.send.side_effect = OSError   # make it fail
```

A `Mock` has **every** attribute and accepts **every** call:

```python
notifier.send_teh_thing(1, 2, 3)      # passes
notifier.a.b.c.d()                    # passes
```

So a test using a mock keeps passing after you rename the real method — the mock grows the new name
too, and now proves nothing about a class it no longer matches. That is the cost, and it is why mocks
are for things you **cannot** change: a payment provider, an SMTP server, a clock inside somebody
else's library.

**The order to reach in:**

1. a parameter (change the code)
2. a fake object you wrote (five lines, and it type-checks)
3. `monkeypatch` (for a module-level name)
4. `unittest.mock` (for a call you must assert on)

### 7. The factory fixture

A plain fixture gives every test the *same* object, so a test needing a different party size builds
the whole thing by hand. A factory returns a **function**:

```python
@pytest.fixture
def make_booking(now):
    def build(**overrides):
        defaults = {"reference": "AB-1234", ..., "party_size": 4}
        return Booking(**{**defaults, **overrides})
    return build

def test_a_party_that_is_too_large(make_booking, now):
    assert validate(make_booking(party_size=99), now=now)
```

Each test states only what it cares about, and adding a field to `Booking` changes one function
instead of thirty tests. **The most useful fixture pattern there is.**

### 8. The build: a table, and a clock you can move

```
FILE                                    FUNCTIONS    CASES    LINES
test_isolating_the_world.py                    19       28      311
test_validators.py                             15       52      213
80 passed in 0.14s
```

Eighty cases from thirty-four functions — and a failure names the rule *and* the row:

```
FAILED test_validators.py::test_one_bad_field_is_reported[overrides11-party_size]
```

**Two design decisions in `bookings.py` do most of the work**, and both are decisions rather than
techniques:

- **Nothing calls `datetime.now()`.** Every function that needs the time takes it as an argument. A
  function that asks the world what time it is can only be tested at that time.
- **Nothing reads a database.** `existing` is a plain sequence the caller supplies. Tests pass a
  list; production passes a query result; neither knows about the other.

Those two turn *"we need a mocking framework"* into *"we need an argument"*:

```python
@pytest.mark.parametrize("minutes, expired", [(0, False), (14, False), (15, True)])
def test_hold_expires_after_fifteen_minutes(valid, later, minutes, expired):
    assert hold_expired(valid, now=later(minutes=minutes)) is expired
```

`legacy.py` has the same rule written the other way, tested with the same four cases and the same
assertions — and it needs a `datetime` subclass, a `monkeypatch`, and knowing which module to patch.
The machinery is what breaks when somebody reorganises an import six months from now.

### 9. Thirteen seconds of backoff, in a quarter of one

```
delay configured across the retry tests                     23.0s
time those tests actually took                               0.26s
speed-up                                                       89x
```

```python
@pytest.fixture
def no_waiting(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    return slept
```

And it does more than save time: the fake **records** what it was asked to wait for, so the backoff
schedule becomes data.

```python
assert no_waiting == [0.5, 1.0, 2.0]
```

Without the patch that assertion cannot be written — you can only observe that the whole thing took
roughly three and a half seconds, which is not the same claim.

A suite that takes a minute is one people run before lunch. A suite that takes a second is one they
run before every commit.

### 10. Test both sides of every boundary

`build.py` sabotages the validator — changing the minimum booking length from fifteen minutes to ten
— and the table catches it, because it tests both sides:

```python
(14, "ends_at"),         # under the minimum: must be rejected
(15, None),              # exactly the minimum: must be accepted
```

A table with only the failing side would have stayed green. It is one more row.

*(That sabotage check was itself flaky until it cleared `__pycache__`: Python validates a `.pyc`
against the source's mtime **and size**, and `"15"` → `"10"` changes neither if both writes land
inside one filesystem timestamp tick.)*

---

## The code

| File | What it is |
|---|---|
| `bookings.py` | The validator under test. Seven rules, `now` as a parameter, no I/O. |
| `legacy.py` | The same two rules written the way that needs a mock. |
| `conftest.py` | `now`, `later`, `make_booking` (factory), `valid`, `diary`. |
| `tests/test_validators.py` | The table: 15 functions → 52 cases, both sides of every boundary. |
| `tests/test_isolating_the_world.py` | `monkeypatch` on the clock, the env and `time.sleep`; `tmp_path`; `capsys`; `Mock`; and the same rule needing none of them. |
| `lesson.py` | Fixture scope counted, teardown order traced through a failure, and the wrong patch target demonstrated. |
| `build.py` | The report, the timing, and a sabotage the table catches. |

```bash
python3 lesson.py
python3 build.py
python3 -m pytest tests/ -q      # 80 passed
python3 -m pytest tests/ -v      # every case, by name
```

---

## Common mistakes

**A module- or session-scoped fixture holding something mutable.** Order-dependent tests.

**Building the same object by hand in twenty tests.** Use a factory fixture.

**Patching where the name is defined instead of where it is used.**

**Assigning to a module instead of using `monkeypatch`.** It leaks into every later test.

**Mocking code you own.** Pass an argument instead.

**Asserting a mock was called, and nothing else.** That tests your test.

**Real `time.sleep` in tests.** A slow suite is an unrun suite.

**Real files outside `tmp_path`.** Passes once, fails the second time.

**A table with only the failing side of a boundary.**

**`autouse=True` everywhere.** A test that does not name its fixtures does not say what it depends on.

---

## Exercises

1. Replace three tests that build the same object with a factory fixture. Count the lines deleted.
2. Make a module-scoped fixture return a list, append to it in one test, and watch a later test see
   it. Then run the later test alone and watch it pass.
3. Patch the wrong module on purpose and spend two minutes not understanding why. Worth the two
   minutes.
4. Monkeypatch `time.sleep` in a test of retrying code, and compare the suite's runtime.
5. Write the same test twice — once with `mock.patch`, once by passing an argument. Rename the
   method being mocked and see which one notices.
6. Convert a function that calls `datetime.now()` into one that takes `now`, then delete the fixture
   that used to freeze it.
7. Use `tmp_path` and `capsys` in one test of something that writes a file and prints a summary.

---

## Checklist

- [ ] I request fixtures by parameter name and share them in `conftest.py`
- [ ] I leave the scope at `function` unless I can justify widening it
- [ ] I use `yield` for teardown and know it runs after a failure
- [ ] I reach for `tmp_path`, `monkeypatch` and `capsys` before writing my own
- [ ] I patch where the name is used
- [ ] I prefer a parameter to a mock for code I own
- [ ] I use factory fixtures instead of fixed objects
- [ ] My tests never really sleep, hit the network, or write outside `tmp_path`
- [ ] My tables test both sides of every boundary
