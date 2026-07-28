# Day 006 — Input and type conversion

**Phase 1 · Foundations** · ~70 minutes

> **Today's build:** an interactive BMI calculator that refuses nonsense input instead of crashing.

**Concepts:** `input()` · casting · why input is always a string · basic validation

---

## The article

### Why this day exists

Until now every value in your programs was written by you, in the file, correct by construction.
Today the outside world gets in, and the outside world types `"twenty"` into a box labelled
*age*, pastes a value with a trailing space, hits Enter on an empty line, and pastes `70kg` into
a field that wanted a number.

The single most important sentence of this day: **`input()` always returns a string.** Always.
Even when the user typed digits. Even when the prompt said "enter a number". Every crash on this
day traces back to forgetting it.

### 1. `input()`

```python
name = input("What is your name? ")
print(f"Hello, {name}")
```

`input()` prints its prompt (with no automatic newline — put a trailing space in the prompt
yourself), waits for the user to press Enter, and returns everything they typed **as a string,
without the newline**.

That last detail is a small gift: you do not have to strip `\n` the way you will when reading
files on Day 53. You *do* have to strip everything else, because people paste text with spaces
on it constantly.

`input()` with no prompt still works, and still waits. A program that appears to hang is often
one sitting on a bare `input()`.

### 2. Why "always a string" is the whole day

```python
age = input("Age: ")     # user types 30
age + 1                  # TypeError: can only concatenate str (not "int") to str
age * 2                  # "3030"  ← no error! Just silently wrong.
```

Look at those two lines carefully. The first fails loudly, which is fine — you find out
immediately. The second **succeeds and is wrong**, because `"30" * 2` is a perfectly legal
string repetition. That is the dangerous shape: a type error that does not raise.

So convert, explicitly, at the boundary:

```python
age = int(input("Age: "))
```

This one-liner is the standard idiom and you will write it hundreds of times. It also crashes on
anything that is not a whole number, which is the rest of today's material.

### 3. Conversions and how they fail

```python
int("30")        # 30
int("  30  ")    # 30      — surrounding whitespace is tolerated
int("30.5")      # ValueError: invalid literal for int() with base 10: '30.5'
int("thirty")    # ValueError
int("")          # ValueError
int(30.5)        # 30      — from a FLOAT it truncates; from a STRING it raises
float("30.5")    # 30.5
float("3e2")     # 300.0   — scientific notation is accepted
float("")        # ValueError
```

The asymmetry in the middle catches everyone: `int("30.5")` raises, `int(30.5)` does not.
`int()` on a string demands an integer *literal*; `int()` on a number truncates. When user input
might have a decimal point, go via float: `int(float("30.5"))`.

The exception you will see is `ValueError` — the type was right (a string), the *value* was not.
Compare with `TypeError`, which means the type itself was wrong. Day 9 makes that distinction
properly; noticing it today will save you time then.

### 4. Validating before you convert

You have two families of tools, and both are from Day 4.

**Predicates**, which return `bool`:

```python
"30".isdigit()       # True
"30.5".isdigit()     # False  ← the dot is not a digit
"-30".isdigit()      # False  ← nor is the minus sign
"".isdigit()         # False  ← empty is not digits, which is convenient
"٣٠".isdigit()       # True   ← Arabic-Indic digits. int() handles them too.
```

`.isdigit()` is a decent first gate for whole non-negative numbers and *nothing else*. For
anything with a sign or a decimal point it says False, which means using it alone silently
rejects `-5` and `1.5`. Know its limits.

**Cleaning**, which changes the string into something convertible:

```python
raw = "  70.5 kg \n"
cleaned = raw.strip().lower().replace("kg", "").replace(",", "").strip()
float(cleaned)      # 70.5
```

Strip first, strip again at the end, and normalise case before you compare or replace. This
chain is the shape of nearly all real input handling.

### 5. Today's honest limitation

The build brief says "refuses nonsense input instead of crashing", and there are two halves to
that:

- **Not crashing** — achievable today, by cleaning the input so that whatever survives is always
  convertible, with a fallback for when nothing does.
- **Refusing** — as in *stop, tell the user, ask again* — needs a branch (`if`, Day 11) and a
  loop (`while`, Day 12). You do not have them yet.

So today you build the part that comes first and that most people skip: **deciding, precisely,
whether an input is acceptable, and being able to say why.** The build prints a verdict for each
rule. On Day 11 you will act on that verdict; on Day 12 you will re-ask until it passes; on
Day 51 you will learn `try/except`, which is the grown-up version of all of it.

That ordering is deliberate. Validation logic is the hard part and it is independent of the
control flow you wrap around it.

### 6. Multiple values, and a note on scripts that ask questions

Each `input()` is one line from the user. To collect several values, call it several times — or
take one line and split it (Day 4):

```python
raw = input("Enter width and height: ")     # user types: 10 20
parts = raw.split()                          # ['10', '20']
```

Finally: a script that calls `input()` needs somebody at a keyboard. Run it in a terminal, not
by clicking Run in a preview pane that has no stdin. You can also feed it from a file or a pipe:

```bash
echo "1.75
70" | python3 build.py
```

That trick is how you test an interactive program without typing, and it is worth knowing now.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | `input()`, the conversions, how each fails, and the cleaning chain. Asks you a few questions. |
| `build.py`  | The BMI calculator: clean, validate, report, compute — and never crash. |

```bash
python3 lesson.py
python3 build.py

# or feed it without typing:
printf '1.75\n70\n' | python3 build.py
```

---

## Common mistakes

**`TypeError: can only concatenate str (not "int") to str`** — you forgot `int()` around an
`input()`.

**`"30" * 2` giving `"3030"`.** No exception, wrong answer. The worst kind.

**`ValueError: invalid literal for int() with base 10: '30.5'`** — use `int(float(x))`, or
decide that decimals are invalid and say so.

**`ValueError` on empty input.** The user pressed Enter. `""` converts to nothing. Always a case.

**Forgetting `.strip()`.** A pasted value with a trailing space fails comparisons in ways that
are invisible on screen. `print(f"{value!r}")` shows you.

**A mismatched prompt.** `input("Age:")` with no trailing space puts the cursor against the
colon. Small, but every user notices.

**Running an interactive script where there is no stdin.** You get `EOFError`. Use a terminal.

---

## Exercises

1. Ask for a number, then print it, `type()` of it, and `type(int(...))` of it. Confirm out loud
   that `input()` gave you a string.
2. Write the cleaning chain that turns each of these into `70.5`: `" 70.5 "`, `"70.5kg"`,
   `"70,5"` (European decimal comma), `"70.5 KG"`.
3. Find three strings where `.isdigit()` disagrees with "can `int()` handle this". Two are easy;
   the third needs you to look up `.isdecimal()` and `.isnumeric()`.
4. Ask for two numbers on one line and print their sum. Handle the case where the user typed
   only one.
5. Write a one-line expression that converts user input to a float and yields `0.0` for empty
   input, without any conditional. (Hint: `or` on an empty string. It is Day 7's material and it
   will work today.)
6. Feed your build a deliberately awful input — `"  -0 kg  "`, `"1.2.3"`, `"٧٠"`, an empty line
   — and check it does something defensible with each.

---

## Checklist

- [ ] I can say, without hesitating, what type `input()` returns
- [ ] I convert at the boundary, in the same line I read
- [ ] I know why `int("30.5")` raises but `int(30.5)` does not
- [ ] I know what `.isdigit()` says about `"-5"` and `"1.5"`
- [ ] I strip every string a human gave me, immediately
- [ ] My build survives empty input, text, and a number with units attached
