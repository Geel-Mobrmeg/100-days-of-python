# Day 055 — JSON

**Phase 6 · Robust code** · ~80 minutes

> **Today's build:** a settings store that loads defaults, merges user overrides and saves changes to disk.

**Concepts:** `dumps` & `loads` · `dump` & `load` · nested structures · custom encoders · config files

---

## The article

### Why this day exists

CSV is a table. JSON is a *shape* — and almost everything you will exchange with another program
has a shape: an API response, a config file, a cached result, a message on a queue.

The module has four functions and takes about ten minutes to learn. The rest of today is the dozen
things it does that people do not expect.

### 1. Four functions, one letter

```
json.dumps(obj)      -> a STRING            "s" for string
json.loads(text)     -> a Python object
json.dump(obj, f)    -> writes to a FILE
json.load(f)         -> reads from a file
```

The pair without the `s` take a *file object*, not a path — so they work on anything file-like,
which is Day 53's argument arriving again.

### 2. What survives the round trip — and what does not

| Python | JSON | back as | same? |
|---|---|---|---|
| `dict`, `list`, `str`, `int`, `float`, `bool`, `None` | as expected | same type | yes |
| `tuple` | `[1, 2, 3]` | **`list`** | NO |
| `{1: "one"}` | `{"1": "one"}` | **string keys** | NO |
| `set` | — | `TypeError` | no |

`json.loads(json.dumps(x)) == x` is **false** for a great many `x`, and that assumption is what most
JSON bugs are made of. Only the `set` is honest enough to raise.

The worst case, from `lesson.py`:

```
you wrote       {1: 'one', True: 'TRUE', None: 'nothing'}   3 entries
the dict is     {1: 'TRUE', None: 'nothing'}                2 keys
the JSON is     {"1": "TRUE", "null": "nothing"}            2 keys
```

Two separate collapses, neither of which raised. Python merged `1` and `True` before `json` was
involved (`1 == True`, same hash), so `'one'` was already gone. Then `json` turned the remaining int
and `None` keys into the strings `"1"` and `"null"`.

**Keep JSON keys as strings in Python too.** Then what you send is what you meant.

### 3. Python writes JSON that is not JSON

```python
json.dumps({"rate": float("inf"), "ratio": float("nan")})
# -> {"rate": Infinity, "ratio": NaN}
```

`NaN` and `Infinity` are not in the JSON specification. Python emits and reads them happily; every
other parser rejects the file. So it is a bug you find in a *different language*, in production, at
the boundary.

```python
json.dumps(data, allow_nan=False)     # ValueError, at your desk instead
```

Duplicate keys are the same shape of problem in reverse: `json.loads('{"a": 1, "a": 2}')` gives
`{'a': 2}`. Valid JSON, last one wins, silently.

### 4. How it is written

| option | bytes | when |
|---|---:|---|
| default | 67 | |
| `indent=2` | 89 | anything a human opens or a git diff shows |
| `sort_keys=True` | 89 | **always for files** — a no-op save then gives an empty diff |
| `separators=(",",":")` | 59 | anything on a network |
| `ensure_ascii=False` | 62 | files you own; writes real UTF-8 instead of `\uXXXX` |

`sort_keys=True` is not cosmetic. Without it, dict ordering leaks into the file, re-saving an
unchanged config produces a diff, and a config file in git becomes unreviewable.

### 5. Types of your own

`datetime`, `date`, `Decimal`, `Path` and `set` all raise `TypeError`. Two hooks fix that:

```python
json.dumps(record, default=encode)          # called only for what json can't handle
json.loads(text, object_hook=decode)        # called on every decoded object
```

The **tagged-object** pattern round-trips a type JSON does not have:

```json
{"__type__": "decimal", "value": "19.99"}
```

And the choice of *which* fields to tag is the actual content. In `lesson.py`, `created`, `due` and
`price` are tagged and come back as `datetime`, `date` and `Decimal`; `path` and `tags` are written
as a plain string and a plain array and come back as `str` and `list` — because those two are
consumed by other systems that want exactly that.

The one you cannot compromise on:

```
Decimal('19.99') as a float, tripled:  59.969999999999999
the exact answer:                      59.97
```

JSON has no decimal type. A price written as a JSON number is a rounding bug you cannot see.

### 6. Reading somebody else's JSON

```
not JSON at all     JSONDecodeError: line 1 col 2
trailing comma      JSONDecodeError: line 1 col 9
single quotes       JSONDecodeError: line 1 col 2
a bare number       ok -> int
null                ok -> NoneType
nested 1000 deep    RecursionError
```

**JSON is not Python.** Single quotes, trailing commas and unquoted keys are all invalid, and all
are things a human hand-editing a config will write. `JSONDecodeError` carries `.lineno`, `.colno`
and `.pos` — put them in your message (Day 52) and the person fixing the file knows where to look.

**A bare number, string or `null` is valid JSON.** `json.load(f)` can return `42` or `None`, and code
that immediately does `data["key"]` gets a `TypeError` rather than the `KeyError` it was ready for.

**`json.loads` is safe on untrusted text** — it builds data, never code. That is its one advantage
over `pickle` and `eval`, and it is not small: never unpickle or eval data from outside your program.
But safe is not unlimited: 1000 levels of nesting is 24 bytes of input and a `RecursionError`. Cap
the *size* of anything that came off a network before you parse it.

### 7. JSON, or something else

| | for |
|---|---|
| **JSON** | nested structure, config, APIs, anything with a shape |
| **CSV** | a flat table, and anything a spreadsheet must open |
| **JSON Lines** | one object per line — streamable and appendable; the right answer for logs |
| **TOML** | human-*edited* config. `tomllib` reads it (3.11+); Python cannot write it |
| **pickle** | Python objects, trusted source, same version. Never over a network |

Plain JSON is a poor log format: you cannot append to an array without rewriting the file, and you
cannot read it without holding all of it.

### 8. The build: the merge everybody gets wrong

Every real configuration system has the same shape:

```
defaults (in code)  <-  a file  <-  environment  <-  command line
least specific                                      most specific
```

Each layer overrides the one before it — **and only the keys it mentions.** That last clause is the
whole problem:

```
SETTING                     DEFAULT       SHALLOW       DEEP
service.name                unnamed       billing-api   billing-api
service.port                8080          443           443
service.host                localhost     GONE          localhost    <-
service.workers             4             GONE          4            <-
features.metrics            True          GONE          True         <-
billing.currency            GBP           GONE          GBP          <-

settings destroyed by the shallow merge: 5
```

`{**defaults, **user}` replaced three whole *sections* with the fragments the user wrote. It looks
correct, it passes any test whose fixture mentions every key, and it silently deletes five settings
the moment a real user writes a three-line config file.

`deep_merge` is nine lines. It merges dicts key by key and lets anything else replace — which is also
a decision: a user who sets `tags` means *these* tags, and appending would make an empty list
impossible to express.

### 9. The defaults are the schema

Every key that may exist is in `DEFAULTS`, with a value of the type it must have. That one decision
pays three times:

```
service.port: expected a number, got '8080'
service.hots: unknown setting; did you mean 'host'?
limits.timeout_seconds: expected a number, got 'thirty'
features.beta_ui: expected true/false, got 'yes'
loging: unknown setting; did you mean 'logging'?
```

- **wrong types** are caught before the program starts, rather than at the arithmetic two hundred
  lines later;
- **typos** are caught at all — without an unknown-key check, `hots` and `loging` are completely
  silent and somebody spends an afternoon on it;
- **environment variables**, which are always strings, are converted using the type of the default
  they override — the schema doing a second job for free.

`'yes'` deserves its own note: it is truthy, so the feature turns **on** — and `'no'` would have
turned it on too.

Beware `isinstance(True, int)`, which is `True` in Python: check `bool` before `int` or every
boolean setting accepts `7`.

### 10. Saving

```python
with open(path.with_suffix(".json.tmp"), "w", encoding="utf-8") as f:
    json.dump(settings, f, default=encode, indent=2,
              sort_keys=True, ensure_ascii=False, allow_nan=False)
os.replace(temporary, path)
```

Day 53's atomic write, plus `sort_keys` for stable diffs and `allow_nan=False` so an accidental
infinity fails here rather than in whatever reads the file. The build checks both: saving twice gives
byte-identical output, and a crash mid-save leaves the old file intact.

And a habit worth forming: **never print a settings object raw.** A `redacted()` view that replaces
anything named like a secret costs six lines and keeps API keys out of your logs.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The four functions, the lossy round trips, the key collision, `NaN`, formatting options, `default=`/`object_hook=`, and eight kinds of malformed input. |
| `build.py`  | The settings store: shallow vs deep merge measured, validation against the defaults, four layers of override, atomic save, redaction, and 16 checks. |

```bash
python3 lesson.py
python3 build.py                    # the demonstration
python3 build.py my-config.json     # validate a file of your own
```

---

## Common mistakes

**`{**defaults, **user}` for nested config.** Deletes whole sections.

**Assuming the round trip is lossless.** Tuples become lists; int keys become strings.

**Leaving `allow_nan` alone.** You write JSON other parsers reject.

**No `sort_keys`.** Every save is a diff.

**Writing money as a float.** `19.99` is not 19.99.

**No unknown-key check.** A typo in a config file is completely silent.

**Checking `int` before `bool`.** `isinstance(True, int)` is `True`.

**`data["key"]` straight after `json.load`.** It might be a list, a number or `None`.

**Printing or logging a config object.** That is how keys leak.

**`pickle` or `eval` on anything from outside.** Arbitrary code execution.

---

## Exercises

1. Round-trip a dict with tuple values and check `isinstance`.
2. Round-trip `{1: 'a', '1': 'b'}` and count the keys.
3. `dumps` with a NaN, then parse the file with `jq` or another language.
4. Write a `Decimal` as a float, triple it, and compare to the exact answer.
5. Hand-write a config with a trailing comma and print `exc.lineno` and `exc.colno`.
6. Serialise a class of your own with `default=`, restore it with `object_hook=`, and decide which
   fields deserve a `__type__` tag.
7. Write `deep_merge` from scratch, then break it with `dict.update` and watch which settings vanish.
8. Add environment-variable overrides that convert using the default's type.

---

## Checklist

- [ ] I know which of `dump`/`dumps`/`load`/`loads` I want
- [ ] I know tuples become lists and int keys become strings
- [ ] I use `allow_nan=False` for anything leaving Python
- [ ] I use `sort_keys=True` and `indent=2` for files
- [ ] I can write `default=` and `object_hook=` for my own types
- [ ] I never store money as a JSON number
- [ ] I merge configuration deeply, not shallowly
- [ ] I validate unknown keys and wrong types against the defaults
- [ ] I save atomically and redact secrets before printing
