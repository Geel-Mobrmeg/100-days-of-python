# Day 003 — Strings

**Phase 1 · Foundations** · ~70 minutes

> **Today's build:** an initials extractor that turns any full name into a set of initials.

**Concepts:** indexing · slicing · concatenation · escape sequences · immutability

---

## The article

### Why this day exists

Most of the data you will ever handle arrives as text. Names, addresses, log lines, CSV rows,
JSON payloads, HTML, API responses — all text, all needing to be cut apart and put back
together. Strings are the type you will manipulate more than every other type combined, and the
four operations you learn today are the ones you will still be using on Day 100.

Today is deliberately about the *low-level* moves: reaching into a string by position and taking
pieces out of it. Tomorrow gives you the high-level methods that do the same jobs more
comfortably. Doing it the hard way first is what makes tomorrow's tools feel like relief instead
of magic.

### 1. A string is a sequence

That word matters. A string is an ordered run of characters, each at a numbered **index**, and
counting starts at **zero**:

```python
name = "Python"
#       012345
name[0]    # "P"
name[5]    # "n"
name[6]    # IndexError: string index out of range
```

Zero-based indexing feels arbitrary for a week and then feels obvious. The reason it wins is
that an index is really an *offset from the start* — `name[0]` is "zero characters in".

Negative indices count from the right, which saves an enormous amount of arithmetic:

```python
name[-1]   # "n"  — last character, without needing to know the length
name[-2]   # "o"
```

`name[-1]` is the idiom for "the last one", in every sequence type, for the rest of your Python
life. The alternative, `name[len(name) - 1]`, is what you write in languages that do not have it.

`len(name)` gives the number of characters — `6` here. The last valid index is always
`len(s) - 1`, which is the source of a great many off-by-one errors.

### 2. Slicing

Indexing gets one character. **Slicing** gets a run of them, with `[start:stop]`:

```python
name = "Python"
name[0:2]    # "Py"
name[2:6]    # "thon"
```

The rule that makes slices predictable — and it is the single most useful thing on this page —
is **start is included, stop is excluded**. `[0:2]` means "from 0, up to but not including 2",
so it gives you exactly `2 - 0 = 2` characters. Once you internalise "the length of a slice is
stop minus start", slicing stops being a guessing game.

Both ends are optional, and omitting them means "as far as possible in that direction":

```python
name[:3]     # "Pyt"    — from the start
name[3:]     # "hon"    — to the end
name[:]      # "Python" — a full copy
```

Slices never raise `IndexError`. Out-of-range indices are silently clamped, which is either a
convenience or a silent bug depending on the day:

```python
name[0:999]  # "Python" — no error
name[99:]    # ""       — no error, just empty
```

There is a third part, the **step**:

```python
name[::2]    # "Pto"    — every second character
name[::-1]   # "nohtyP" — the standard, slightly cryptic, string reversal
```

### 3. Concatenation and repetition

```python
"Hello, " + "world"     # "Hello, world"
"-" * 20                # "--------------------"
```

`+` joins, `*` repeats. `+` inserts nothing at all, so every space you want you must supply
yourself — the commonest small bug in this area is `"Hello," + name` producing `"Hello,Ada"`.

`+` also refuses to mix types, exactly as it did yesterday: `"Total: " + 5` is a `TypeError`.
Use `str(5)`, or wait one day for f-strings, which make the whole problem go away.

Do not build a long string by repeatedly `+`-ing in a loop. Each `+` creates a whole new string,
so the cost grows quadratically. Day 4's `"".join()` is the right tool; this is the first
performance rule of the course and one of very few worth knowing this early.

### 4. Escape sequences

Some characters cannot be typed literally inside quotes. A backslash starts an **escape
sequence**:

| Escape | Means |
|---|---|
| `\n` | newline |
| `\t` | tab |
| `\\` | a literal backslash |
| `\"` | a literal double quote |
| `\'` | a literal single quote |

```python
print("Line one\nLine two")
print("Name:\tAda")
print("She said \"hi\"")
```

Two ways to avoid escaping altogether. Use the *other* quote character:

```python
print('She said "hi"')      # no escaping needed
```

Or use a **raw string** with an `r` prefix, where backslashes are literal. This is essential for
Windows paths and for the regexes on Day 62:

```python
print(r"C:\Users\new")      # C:\Users\new  — without the r, \n is a newline
```

**Triple-quoted strings** span lines and keep their formatting, which makes them the tool for
banners, help text, and — as of Day 31 — docstrings:

```python
message = """Dear Ada,

    Thank you for the algorithm.
"""
```

### 5. Immutability

Strings **cannot be changed in place**. Ever.

```python
name = "Python"
name[0] = "J"       # TypeError: 'str' object does not support item assignment
```

Every operation that looks like it modifies a string actually builds a new one and leaves the
original alone:

```python
name = "Python"
name.upper()        # "PYTHON" — a NEW string
print(name)         # "Python" — unchanged!
```

This is the mistake everybody makes at least once, usually with `.strip()`. The result is
returned, not applied. If you want to keep it, assign it:

```python
name = name.upper()
```

The reason for immutability: it makes strings safe to share and cheap to hash, which is what
lets them be dictionary keys on Day 24. The cost is the loop-concatenation problem above. To
"edit" a string, slice around the part you want to replace and reassemble:

```python
name = "Python"
name = "J" + name[1:]      # "Jython"
```

### 6. Where slicing runs out

Today's build asks for initials from *any* name. With indexing and slicing, the first initial is
easy — `name[0]` — and the rest are not, because you do not know where the spaces are. You can
find one with `name.index(" ")`, which is the inverse of indexing: give it a character, it gives
you the position.

That handles two names. Three names need two searches. An arbitrary number needs a loop, and you
do not have loops until Day 13. So today you will feel the limit, and that is on purpose:
tomorrow's `.split()` exists precisely because this is annoying, and it will land much harder
having felt the annoyance.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Indexing, slicing, concatenation, escapes and immutability, runnable. |
| `build.py`  | The initials extractor — slicing first, then the preview of tomorrow. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`IndexError: string index out of range`** — the last valid index is `len(s) - 1`, not
`len(s)`. Or the string was shorter than you assumed, possibly empty.

**`TypeError: 'str' object does not support item assignment`** — you tried to edit a string in
place. Build a new one by slicing and concatenating.

**Calling a method and throwing away the result.** `name.strip()` on its own line does nothing
useful. It has to be `name = name.strip()`.

**Off-by-one in slices.** `s[0:3]` gives three characters, not four. Say "stop minus start" out
loud until it is automatic.

**`\U` or `\N` in a Windows path.** `"C:\Users"` and `"C:\New"` both raise or misbehave. Use a
raw string or forward slashes.

**`ValueError: substring not found`** from `.index()`. It raises when the thing is not there.
`.find()` returns `-1` instead, which is quieter and sometimes worse.

---

## Exercises

1. For `s = "programming"`, write slices that produce: `"pro"`, `"ming"`, `"gram"`, the whole
   string reversed, and every second character. Predict each before running it.
2. Write an expression that gives the last three characters of *any* string without using
   `len()`. Then one that works even if the string is only two characters long.
3. Explain in one sentence why `s[99:]` returns `""` rather than raising, while `s[99]` raises.
4. Take `"  Ada Lovelace  "` and produce `"Ada Lovelace"` using only slicing and `len()` — no
   methods. Now note how much you want `.strip()`.
5. Turn `"Python"` into `"Pythonic"` and then into `"Jython"`, in both cases reassigning the
   same name. Prove the original string was never modified.

---

## Checklist

- [ ] I can index from the front and the back without counting on my fingers
- [ ] I can say why `[2:5]` gives three characters
- [ ] I know what `s[::-1]` does and why
- [ ] I can produce a literal backslash, a literal quote and a newline in a string
- [ ] I can explain why `name.upper()` alone changes nothing
- [ ] My extractor produces correct initials for a two-part and a three-part name
