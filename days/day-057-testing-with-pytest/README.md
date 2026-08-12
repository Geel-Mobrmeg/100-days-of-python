# Day 057 — Testing with pytest

**Phase 6 · Robust code** · ~90 minutes

> **Today's build:** write a real test suite for the toolkit you built on Day 40 and find at least one bug.

**Concepts:** `assert` · test discovery · arrange-act-assert · `pytest.raises` · test naming

---

## The article

### Why this day exists

Day 40's package shipped with a README, examples, 28 acceptance checks and 28 doctests. All of them
passed. Today's suite found **four bugs in it**, and understanding why the earlier checks missed
them is worth more than the bugs are.

### 1. `assert` is the whole API

```python
def test_totals():
    assert totals([1, 2, 3]) == {"count": 3, "sum": 7}
```

```
E       AssertionError: assert {'count': 3, 'sum': 6} == {'count': 3, 'sum': 7}
E         Differing items:
E         {'sum': 6} != {'sum': 7}
```

There is no `assertEqual`, `assertIn`, `assertGreater` or `assertAlmostEqual` to learn. pytest
**rewrites the assert statement** as it imports your file, so a bare `==` reports both sides and a
dict comparison names the differing key. `unittest` prints `AssertionError` and nothing else. That
difference is most of why pytest won.

### 2. Discovery is four lines of rules

| | |
|---|---|
| files | `test_*.py` or `*_test.py` |
| functions | `test_*` |
| classes | `Test*` (with no `__init__`) |
| where | the directory you point it at, recursively |

No registration, no suite object, no base class. A file of functions named `test_something` **is** a
test suite.

Keep tests *out* of the package — they are not something a user installs, and they should import the
package the way a user would, which is also how you find out that your package cannot be imported.

### 3. The shape of one test

```python
def test_clamp_pulls_a_value_above_the_range_down_to_the_top():
    value, low, high = 15, 0, 10        # ARRANGE
    result = clamp(value, low, high)    # ACT   — exactly one call
    assert result == 10                 # ASSERT — exactly one claim
```

1. **The name is a sentence.** When it fails, the report tells you what broke before you have opened
   anything. `test_clamp_2` tells you nothing.
2. **One act.** Three calls to the thing under test, and a failure does not say which.
3. **One claim.** Six asserts means the first failure hides the other five, and you fix them one run
   at a time.

**A test has no branches.** No `if`, no loop over cases, no `try`. If a test needs logic to decide
what is correct, that logic can be wrong, and nothing tests it.

### 4. Errors and floats

```python
with pytest.raises(ValueError):                       # it raised, and the type
with pytest.raises(ValueError, match=r"low \(10\)"):  # ...and the message
with pytest.raises(ValueError) as caught:             # ...and its attributes
    ...
assert "10" in str(caught.value)

assert 0.1 + 0.2 == pytest.approx(0.3)                # never == on floats
```

`match` takes a **regular expression** and searches, so escape your brackets. Testing the message is
testing the contract — Day 52 argued the message is part of the interface, and this is where that
claim gets enforced.

### 5. `parametrize`, not a loop

```python
@pytest.mark.parametrize("seconds, expected", [
    (0, "0:00"), (59, "0:59"), (60, "1:00"), (3600, "1:00:00"), (-5, "-0:05"),
])
def test_duration(seconds, expected):
    assert duration(seconds) == expected
```

```
test_demo.py::test_duration[0-0:00] PASSED
test_demo.py::test_duration[3600-1:00:00] PASSED
test_demo.py::test_duration[-5--0:05] FAILED
1 failed, 5 passed
```

Five independent tests, each named after its own inputs. The loop people write instead reports **one**
failure and hides the rest.

Stack the decorator to get a grid — which is how today's suite runs the same four bug assertions
against two different modules.

### 6. `xfail(strict=True)`

```python
@pytest.mark.xfail(strict=True, reason="known bug, ticket #412")
def test_a_known_bug():
    ...
```

If the test starts passing, pytest reports the run as **FAILED** — `[XPASS(strict)]` — telling you
to delete the marker. A non-strict xfail on a bug somebody has since fixed stays green forever and
the marker rots into a lie.

- `skip` — this cannot run here (a missing dependency)
- `skipif` — the same, conditionally
- `xfail` — this *should* pass and does not, and I know why

**Never skip a test because it fails.** That is deleting the test with extra steps.

### 7. The flags

```
pytest -k "slug"       every test whose name matches
pytest -x              stop at the first failure
pytest --lf            only what failed last time
pytest --tb=short      shorter tracebacks
pytest -s              let print() through
```

The loop that works: `pytest -x --lf` until green, then plain `pytest`.

### 8. What to test, in order

1. **The happy path**, once. Cheapest, and least likely to find anything.
2. **The boundaries.** 0, 1, the limit, the limit ± 1.
3. **The empty case.** Empty list, empty string, zero, `None`.
4. **The error case.** What should raise, and with what message.
5. **The property.** Not three examples — the *rule*.

### 9. The four bugs, and what they had in common

| | as shipped (1.0.0) | expected |
|---|---|---|
| `human_bytes(1024*1024 - 1)` | `'1024.0 KB'` | `'1.0 MB'` |
| `duration(-5)` | `'-1:59:55'` | `'-0:05'` |
| `slugify('Café')` | `'café'` | `'cafe'` |
| `dig({'a': None}, 'a', default='MISSING')` | `'MISSING'` | `None` |

- **`human_bytes`** compared the value *before* formatting it, so 1023.99902 KB printed as
  `1024.0 KB` — a quantity that does not exist.
- **`duration`** hit `divmod`'s flooring: `divmod(-5, 3600)` is `(-1, 3595)`, so minus five seconds
  rendered as minus one hour fifty-nine.
- **`slugify`** promised "URL-safe" and used `str.isalnum()`, which is `True` for every letter in
  every script. The package README *also* described this wrongly, claiming `"Café"` became `"caf"` —
  which the code never did. Two wrong answers about one function.
- **`dig`** ended `return default if data is None else data`, making "the key is absent" and "the key
  holds null" the same answer — the exact question a caller uses `dig()` to ask, and it matters the
  moment the data came from JSON (Day 55).

**Not one is in the happy path.** Three are boundaries — the value just below a unit change, zero
going negative, the first non-ASCII character — and the fourth is a value the author never wrote a
docstring example for.

### 10. Why 28 doctests and 28 acceptance checks found none of them

**Doctests test the examples the author chose.** Every one passed, because `human_bytes(2048)` really
is `'2.0 KB'`. An author who had thought of 1048575 would have written the code correctly.

**Acceptance checks tested the package's promises** — return rather than print, no mutation, a
docstring on everything public, zero dependencies. All true, and none of them about whether the
answers are right.

A test suite is different in one specific way: it is written by somebody asking *how could this be
wrong?* rather than *does this work?*. The two questions produce different files.

The four tests that found these are all **properties**:

```python
def test_human_bytes_never_prints_a_value_of_1024_or_more():
    for exponent in range(0, 40):
        for offset in (-1, 0, 1):
            number = float(human_bytes(2 ** exponent + offset).split()[0])
            assert abs(number) < 1024
```

120 inputs across 40 decades, and it would have caught the bug without anybody thinking of 1048575.

> **Write examples to document. Write properties to find bugs.**

### 11. Fixing, and proving the fix

Two things happened after the bugs were confirmed, and both matter as much as the fix:

**A regression table.** Every doctest example run against both versions, checking that the answers
that were already right did not change. A fix that changes an answer nobody asked you to change is a
second bug.

**A version bump, 1.0.0 → 1.1.0, not 1.0.1.** All four fixes change *documented* behaviour: somebody's
filenames used to contain `café` and now contain `cafe`. A patch release promises nothing changes.
(Day 40's own versioning rule, applied to Day 40's own package.)

### 12. The check that proves a suite is worth having

`build.py` breaks the package on purpose — one character, in one `return` — runs the tests, confirms
they go red, and puts it back.

**A test suite that has never failed is a suite nobody has checked.** Do this to your own once. If it
stays green, you have written something that costs time to run and finds nothing.

---

## The code

| File | What it is |
|---|---|
| `lesson.py` | Writes small test files, runs pytest on them, and shows the real output: assertion rewriting, `raises`, `parametrize`, and `xfail(strict=True)` catching an XPASS. |
| `tests/test_numbers.py` | 14 test functions, 7 parametrised — including the property test that found bug 1. |
| `tests/test_text_and_containers.py` | 19 test functions — the URL-safety property, the chunking property, the `dig` null case. |
| `tests/test_bugs_before_and_after.py` | The four bugs asserted against **both** versions, with `xfail(strict=True)` on the old one. |
| `as_shipped.py` | The four functions exactly as Day 40 shipped them. A museum piece, so the failure is reproducible. |
| `conftest.py` | Puts Day 40's package on `sys.path`. |
| `build.py` | Runs the suite, reproduces each bug, shows the regression table, and sabotages the package to prove the tests bite. |

```bash
python3 lesson.py
python3 build.py                  # the report
python3 -m pytest tests/ -q       # 146 passed, 4 xfailed
python3 -m pytest tests/ -v       # one line per case
```

---

## Common mistakes

**Testing only the happy path.** All four bugs were outside it.

**A loop over cases instead of `parametrize`.** One failure reported, the rest hidden.

**Several asserts per test.** You learn one problem per run.

**Vague names.** `test_clamp_2` in a failure report is a starting point, not information.

**`assert` on floats with `==`.**

**Skipping a failing test.** Deleting it with extra steps.

**`xfail` without `strict=True`.** The marker outlives the bug.

**Logic inside a test.** Nothing tests the test.

**Tests that depend on each other, on dict order, on the clock or on the network.** They fail when the
code is right, and then people stop reading them.

**Never watching a test fail.** You do not know it can.

---

## Exercises

1. Take a function you wrote before Day 40 and write four tests: happy path, boundary, empty, error.
2. Convert a loop-over-cases test to `@parametrize` and break one case. Compare the reports.
3. Write a property test — a rule over many inputs, not an example — for something you have written.
4. Add `xfail(strict=True)` to a known bug, fix the bug without touching the test, and watch your
   suite go red.
5. Test an error message with `pytest.raises(..., match=...)`.
6. Break your own code on purpose and confirm the suite catches it. Time how long it takes to notice.
7. Run `pytest -k` with a substring and watch it select across files.

---

## Checklist

- [ ] I write plain `assert` and read the rewritten failure report
- [ ] My test names are sentences
- [ ] One act and one claim per test
- [ ] I use `parametrize` instead of loops
- [ ] I use `pytest.raises` with `match` for error messages
- [ ] I use `pytest.approx` for floats
- [ ] I mark known bugs `xfail(strict=True)` and never skip them
- [ ] I test boundaries, empties, errors and properties
- [ ] **I have watched my suite fail on purpose**
