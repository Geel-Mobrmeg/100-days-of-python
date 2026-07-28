# Day 004 — String methods and f-strings

**Phase 1 · Foundations** · ~75 minutes

> **Today's build:** a receipt printer that aligns item names, quantities and prices into clean columns.

**Concepts:** `upper` / `lower` / `strip` · `split` & `join` · `replace` · f-strings · format specs

---

## The article

### Why this day exists

Yesterday you cut strings apart by counting characters. Today you get the tools that do it by
*meaning* instead of by position — and then f-strings, which are the single most-used feature in
modern Python and the thing you will type more than any other syntax in this course.

The second half of today, format specs, is the part most people skip and then quietly need
forever. Every table you ever print, every currency figure, every aligned column, every
percentage — all of it is one small language embedded inside f-strings, and it takes about
fifteen minutes to learn.

### 1. Methods

A **method** is a function that belongs to a value and is called with a dot:

```python
"hello".upper()      # "HELLO"
```

Three things to hold onto, all of which follow from yesterday's immutability:

1. Methods on strings **return new strings**. They never modify the original.
2. Therefore the result must be assigned or used, or it evaporates.
3. Therefore methods **chain** — each returns a string, which has methods of its own.

```python
name = "  aDa LoVeLaCe  "
name.strip().title()          # "Ada Lovelace"
print(name)                   # "  aDa LoVeLaCe  " — untouched
```

### 2. Case and whitespace

```python
"ada".upper()        # "ADA"
"ADA".lower()        # "ada"
"ada lovelace".title()      # "Ada Lovelace"
"ada lovelace".capitalize() # "Ada lovelace"   — only the first word
```

`.lower()` is how you compare text that users typed. `"YES" == "yes"` is `False`; comparing
`answer.lower() == "yes"` is how the question actually gets asked. (For non-English text
`.casefold()` is the more correct version; `.lower()` is fine for this course.)

`.strip()` removes whitespace from *both* ends — spaces, tabs, newlines. It does not touch the
middle:

```python
"  hello  ".strip()      # "hello"
" a b ".strip()          # "a b"   — the inner space survives
```

`.lstrip()` and `.rstrip()` do one end each. `.rstrip()` on a line read from a file is how you
remove the trailing `\n`, which is a Day 53 problem you will meet a hundred times.

Strip *any* input a human or a file gave you, immediately, at the point you receive it. Trailing
whitespace is invisible and causes bugs that look supernatural.

### 3. `split()` and `join()` — the pair that matters most

`.split()` cuts a string into a **list** of pieces. Lists are Day 21; today just treat them as
"several strings at once".

```python
"a,b,c".split(",")            # ['a', 'b', 'c']
"Ada Augusta Byron".split()   # ['Ada', 'Augusta', 'Byron']
```

Called with no argument, `.split()` splits on *runs* of any whitespace and discards empties —
which is almost always what you want for human text:

```python
"  Ada   Byron  ".split()       # ['Ada', 'Byron']    — clean
"  Ada   Byron  ".split(" ")    # ['', '', 'Ada', '', '', 'Byron', '', ''] — not
```

That difference is the whole of yesterday's build, solved.

`.join()` is the inverse, and its calling convention surprises everybody: **the separator is the
string you call it on**, and the pieces are the argument.

```python
", ".join(["a", "b", "c"])      # "a, b, c"
"".join(["A", "B", "C"])        # "ABC"
"\n".join(["line 1", "line 2"]) # a two-line string
```

`"".join(...)` is also the correct way to build a big string from many pieces — it allocates
once, where `+=` in a loop reallocates every time.

`.splitlines()` is the one to use for multi-line text; it handles `\n`, `\r\n` and `\r` and does
not leave you a phantom empty string at the end the way `.split("\n")` does.

### 4. `replace()` and friends

```python
"2024-01-15".replace("-", "/")        # "2024/01/15"
"aaa".replace("a", "b", 1)            # "baa"  — third argument caps the count
"hello world".replace(" ", "")        # "helloworld"
```

`.replace()` is literal — no patterns, no wildcards. When you need patterns you want Day 62's
regular expressions, and you should genuinely try `.replace()` first: a chain of two replaces is
easier to read at 3am than any regex.

The predicates round it out. All return `bool`, all are worth knowing today:

```python
"file.csv".endswith(".csv")     # True
"Dr. Ada".startswith("Dr.")     # True
"42".isdigit()                  # True   — the poor man's input validation (Day 6)
"abc".isalpha()                 # True
"   ".isspace()                 # True
"Ada" in "Ada Lovelace"         # True   — membership, not a method, still essential
"l".count("l")                  # counting occurrences
```

### 5. f-strings

Prefix a string with `f` and any `{expression}` inside it is evaluated and inserted:

```python
name = "Ada"
age = 36
print(f"{name} is {age}")            # Ada is 36
print(f"Next year: {age + 1}")       # arbitrary expressions, not just names
```

This replaces every string-building technique that came before it. Compare:

```python
"Hello, " + name + "! You are " + str(age) + "."     # concatenation: noisy, breaks on non-str
"Hello, {}! You are {}.".format(name, age)           # .format(): fine, but arguments are far away
f"Hello, {name}! You are {age}."                     # f-string: what it looks like is what it is
```

Use f-strings. The other two exist in old code and you should be able to read them, but there is
no reason to write them.

Two details worth having now. `=` inside the braces prints the expression *and* its value, which
is the fastest debugging tool in Python:

```python
print(f"{age=}")           # age=36
print(f"{age * 2 = }")     # age * 2 = 72
```

And `!r` gives you the `repr` — quoted, escapes visible — which is how you see whether a string
has whitespace hiding in it:

```python
value = " 42 "
print(f"{value}")     #  42     — is that padded? no idea
print(f"{value!r}")   # ' 42 '  — now you know
```

### 6. Format specs — the part people skip

After a colon inside the braces comes a mini-language for *how* to render the value. The full
form is `{value:[fill][align][width][,][.precision][type]}`, and you will use maybe six of them.

**Alignment and width** — this is how columns happen:

```python
f"{'Coffee':<15}"      # 'Coffee         '  left, 15 wide
f"{'Coffee':>15}"      # '         Coffee'  right
f"{'Coffee':^15}"      # '    Coffee     '  centre
f"{'Coffee':.<15}"     # 'Coffee.........'  fill with dots — the receipt leader
```

Text goes left by default, numbers go right by default, which is exactly what a table wants.

**Numbers:**

```python
f"{3.14159:.2f}"       # '3.14'      — 2 decimal places, always
f"{1234567:,}"         # '1,234,567' — thousands separators
f"{1234.5:>10,.2f}"    # '  1,234.50' — combined: width 10, commas, 2 places
f"{0.257:.1%}"         # '25.7%'     — as a percentage
f"{255:04d}"           # '0255'      — zero padded to 4
f"{255:b}"             # '11111111'  — binary. Also x, o, e.
```

`:.2f` is the one you will type most. It also *rounds*, and it always shows both decimal places
— `f"{5:.2f}"` is `'5.00'`, which is what money should look like.

**Width from a variable**, via nested braces — this is how you make columns that size themselves:

```python
w = 20
f"{'Coffee':<{w}}"     # width taken from w at runtime
```

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every method above, then f-strings, then a tour of format specs. |
| `build.py`  | The receipt printer. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Forgetting the `f`.** `print("{name}")` prints the literal text `{name}`. If your output has
braces in it, you left off the prefix.

**Calling a method and discarding it.** `text.strip()` alone does nothing. It is
`text = text.strip()`.

**`.join()` backwards.** It is `separator.join(pieces)`, not `pieces.join(separator)`.

**`TypeError: sequence item 0: expected str instance, int found`** — `.join()` only joins
strings. Convert the numbers first.

**A literal brace in an f-string.** Double it: `f"{{literal}}"` prints `{literal}`.

**`.split(" ")` on human text.** Double spaces produce empty strings. Use bare `.split()`.

**`.replace()` when you meant a pattern.** It is literal only. Two replaces, or Day 62.

---

## Exercises

1. Rewrite yesterday's initials extractor as one line using `.split()` and `.join()`. Confirm it
   works for one, two and five name parts.
2. Turn `"  ADA,byron , LOVELACE  "` into `"Ada, Byron, Lovelace"`. Chain the methods; do it in
   one expression.
3. Print a three-column table of five rows with left-aligned names, right-aligned integers and
   right-aligned money. Every column must line up exactly.
4. Print a progress bar: `[#####-----]  50%` for a given fraction, using only format specs and
   string repetition.
5. Use `f"{x=}"` to debug something. Then use `!r` on a string with trailing whitespace and see
   the thing you could not see before.
6. Explain why `f"{2/3:.2f}"` and `round(2/3, 2)` are not the same kind of operation.

---

## Checklist

- [ ] I know why `text.strip()` on its own line does nothing
- [ ] I can split on whitespace and rejoin with a separator
- [ ] I write f-strings by default and can read `.format()` in old code
- [ ] I can left-, right- and centre-align to a fixed width
- [ ] I can print money as `1,234.50` from a float
- [ ] Every column in my receipt lines up for both short and long item names
