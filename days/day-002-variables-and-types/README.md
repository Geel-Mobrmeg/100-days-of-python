# Day 002 — Variables and types

**Phase 1 · Foundations** · ~60 minutes

> **Today's build:** a temperature converter that handles Celsius, Fahrenheit and Kelvin in both directions.

**Concepts:** assignment · `int`, `float`, `str`, `bool` · dynamic typing · `type()` · `None`

---

## The article

### Why this day exists

Yesterday every value you used was written where it was used. That does not scale past about
four lines. Today you learn to give values names, which is what lets a program be *about*
something rather than just being a list of literals.

The second half of the day is types. Python will happily let you write `"3" + 4` and then stop
with an error, and the error will make no sense unless you understand that `"3"` and `3` are
different kinds of thing that merely look similar. Nearly every confusing error in your first
month traces back to a value being a different type than you assumed.

### 1. Assignment

```python
temperature = 21.5
```

Read the `=` as **"gets"**, never as "equals". This is not an equation being stated; it is an
instruction being carried out: *make the name `temperature` refer to the value `21.5`*. Python
evaluates the right-hand side first, then attaches the name to the result. That ordering is why
this works and isn't circular:

```python
count = 0
count = count + 1     # right side first: 0 + 1 → 1. Then count gets 1.
```

A useful mental model: a variable is a **label stuck on a value**, not a box containing one.
Assigning again just moves the label:

```python
x = "first"
x = "second"      # the label moved; "first" is now unreachable and gets cleaned up
```

Two labels can sit on the same value. This is harmless for the simple types today, and becomes
extremely important on Day 21 when values start being mutable:

```python
a = 5
b = a         # both names point at 5
a = 6         # only a moved. b is still 5.
```

**Naming rules:** letters, digits and underscores; cannot start with a digit; case matters
(`age` and `Age` are different names). **Naming conventions**, which matter more: use
`lower_snake_case`, use words not abbreviations, and let the length of the name track how far
apart its definition and its use are. `n` is fine inside a two-line calculation; the thing your
whole program is about deserves `celsius`, not `c`. Day 8 makes this formal.

Avoid names that shadow builtins: `list`, `str`, `type`, `sum`, `id`, `input`, `max`. Python
lets you, and then the builtin is gone for the rest of the program.

### 2. The four types you meet today

| Type | What it is | Literals |
|---|---|---|
| `int` | whole number, unlimited size | `0`, `-7`, `1_000_000` |
| `float` | number with a fractional part | `3.14`, `-0.5`, `2.0`, `1e-3` |
| `str` | text | `"hello"`, `'hello'`, `""` |
| `bool` | true or false | `True`, `False` |

Three things worth noticing straight away:

- `2` and `2.0` are **not the same type**, though they compare equal. Any arithmetic that
  involves a float produces a float: `10 / 2` is `5.0`, not `5`.
- Underscores in numbers are legal and purely for your eyes: `1_000_000` is a million.
- `True` and `False` are capitalised. `true` is a `NameError`.

Floats are binary approximations of decimal numbers, which produces the single most reported
"bug" in every language:

```python
0.1 + 0.2      # 0.30000000000000004
```

This is not a Python flaw, it is how binary fractions work — 0.1 is no more finitely
representable in binary than 1/3 is in decimal. Never compare floats with `==`, and never use
floats for money. Day 44 builds a `Money` type properly; for now, `round()` is your patch.

### 3. Dynamic typing

Python is **dynamically typed**: names have no declared type, values do. The same name can point
at a string and later at a number, and Python will not object:

```python
x = 42        # x is currently pointing at an int
x = "hello"   # now at a str. Perfectly legal.
```

It is also **strongly typed**, which is the other half and is often forgotten. Python will not
silently guess across types:

```python
"3" + 4       # TypeError: can only concatenate str (not "int") to str
```

JavaScript would have returned `"34"`. Python refuses, and that refusal is a feature: the error
happens at the mistake instead of five functions later. To combine them you must be explicit
about which one you meant:

```python
int("3") + 4       # 7    — text to number
"3" + str(4)       # "34" — number to text
```

`int()`, `float()`, `str()` and `bool()` are **conversions**, not casts: they build a new value
of the requested type. `int("3.7")` raises — it wants an integer, and `"3.7"` is not one.
`int(3.7)` gives `3`, truncating toward zero rather than rounding. Day 6 covers this in anger.

### 4. `type()` and truthiness

`type(value)` tells you what something actually is. It is a debugging tool, not something you
put in finished code:

```python
type(42)        # <class 'int'>
type(3.0)       # <class 'float'>
type("42")      # <class 'str'>
type(True)      # <class 'bool'>
```

One curiosity that will confuse you exactly once: `bool` is a subclass of `int`, so `True == 1`
and `True + True == 2`. This is a historical accident and occasionally useful for counting.

`bool(x)` asks "is this value truthy?" Every Python value answers:

- **Falsy:** `0`, `0.0`, `""`, `None`, and every empty container.
- **Truthy:** everything else — including `"0"` and `"False"`, which are non-empty strings.

Day 7 builds on this heavily. Today, just know that emptiness is falsiness.

### 5. `None`

`None` is Python's "no value here" value. It is not `0`, not `""`, not `False` — it is a
distinct thing meaning *nothing has been set*:

```python
result = None
```

You will meet it constantly whether or not you write it: a function with no `return` returns
`None`, `dict.get()` returns it for a missing key, and `print()` itself returns it. Test for it
with `is`, never `==`:

```python
if result is None:      # correct
```

The reason is Day 7's material, but the habit starts today.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Assignment, all four types, conversion, `type()`, truthiness and `None`. |
| `build.py`  | The temperature converter. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`TypeError: can only concatenate str (not "int") to str`** — you tried `"Age: " + 30`. Either
convert (`str(30)`) or, better, let `print` do it: `print("Age:", 30)`.

**`NameError: name 'x' is not defined`** — you used the name before assigning it, or you typed
it with different capitalisation than you defined it.

**`SyntaxError: cannot assign to literal`** — you wrote `5 = x`. Assignment always goes
name-on-the-left.

**`0.1 + 0.2 != 0.3`** — expected. Round for display, and never store money as a float.

**Naming a variable `str` or `list`.** Everything works until the moment you try to use the
builtin, and then the error is baffling. Restart your REPL; in a script, rename the variable.

---

## Exercises

1. Assign `a = 5` and `b = a`, then change `a`. Print both. Now explain what the `=` did in
   each of the three statements, using the word "label".
2. Predict the type of each before running: `7 / 2`, `7 // 2`, `7 % 2`, `2 ** 10`, `2.0 ** 10`.
   Check with `type()`. One of these will surprise you.
3. Write one line that prints `0.1 + 0.2` and one that prints it rounded to 2 places, and
   convince yourself the underlying value did not change.
4. Predict `bool()` for each: `0`, `""`, `"0"`, `" "`, `None`, `-1`, `0.0`. Then check.
5. Store your age as a string and try to add 1 to it. Read the error carefully, then fix it in
   two different ways.

---

## Checklist

- [ ] I read `=` as "gets", not "equals"
- [ ] I can name the four types and produce a literal of each
- [ ] I can explain why `"3" + 4` is an error but `int("3") + 4` is not
- [ ] I know why `0.1 + 0.2` prints what it prints
- [ ] I know which values are falsy without checking
- [ ] My converter agrees with a search engine for 0°C, 100°C and −40°C
