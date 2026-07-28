# Day 007 — Booleans and comparison

**Phase 1 · Foundations** · ~75 minutes

> **Today's build:** a password strength checker that reports which rules a password fails.

**Concepts:** truthiness · `==` vs. `is` · `and` / `or` / `not` · chained comparison · short-circuiting

---

## The article

### Why this day exists

Every decision a program will ever make reduces to a boolean. Day 11 gives you `if`, Day 12
gives you `while` — but both of those are just *plumbing* attached to the expression you write
today. The condition is the interesting part, and people who are shaky on booleans write
conditions that are technically true and semantically wrong for years.

Four things here are worth real attention: truthiness (because it makes conditions read like
English), `==` vs. `is` (because getting it wrong produces bugs that work by accident),
short-circuiting (because it is a control-flow feature disguised as an operator), and chained
comparison (because Python is one of the few languages that gets it right).

### 1. Comparison operators

```python
5 == 5       # True    equal
5 != 4       # True    not equal
5 < 6        # True
5 <= 5       # True
"a" < "b"    # True    strings compare alphabetically, by character code
```

`=` assigns, `==` compares. Python protects you here: `if x = 5` is a `SyntaxError`, not a
silent bug, which is one of the genuine improvements over C.

String comparison is by Unicode code point, so all uppercase letters sort before all lowercase
ones: `"Z" < "a"` is `True`. For human-facing sorting, compare `.lower()` on both sides. Day 27
returns to this.

Comparing different types with `<` is an error rather than a guess:

```python
5 < "6"      # TypeError: '<' not supported between instances of 'int' and 'str'
5 == "5"     # False — no error, but definitely False. Different types, different values.
```

### 2. Chained comparison

```python
18.5 <= bmi < 25
```

Python reads that as a single range test, exactly like the mathematical notation. Most languages
cannot: in C or JavaScript, `a < b < c` compares `a < b` to get a boolean and then compares
*that* to `c`, which is nonsense that happens to run.

It also short-circuits, and it evaluates the middle expression only once:

```python
0 <= expensive_function() <= 100     # called once, not twice
```

Chains work with any comparison, including `==` and `is`, and can be as long as you like:
`a < b <= c != d`. Keep them short enough to read.

### 3. Truthiness

Every Python object is either truthy or falsy. The falsy ones are a short, learnable list:

- `False`
- `None`
- zero of any numeric type: `0`, `0.0`, `0j`, `Decimal("0")`
- every empty sequence or collection: `""`, `[]`, `()`, `{}`, `set()`

**Everything else is truthy.** Including `"0"`, `"False"`, `" "`, `[0]`, and `-1`.

This is why Python conditions read the way they do:

```python
if items:            # "if there are any items"      — idiomatic
if len(items) > 0:   # same result, more machinery   — avoid
if items != []:      # same again, worse             — avoid
```

Use the short form. It works for strings, lists, dicts and sets alike, and it is what every
Python programmer expects to read.

One important exception. When `0` is a legitimate value, truthiness silently conflates it with
"missing":

```python
if count:            # WRONG when count == 0 is meaningful
if count is not None:  # right
```

That distinction — "empty" versus "absent" — is the source of a whole family of subtle bugs.
When both are possible, test explicitly.

### 4. `and`, `or`, `not` — and what they actually return

Here is the thing nobody tells beginners: **`and` and `or` do not return booleans.** They return
one of their operands.

- `a and b` → returns `a` if `a` is falsy, otherwise `b`
- `a or b` → returns `a` if `a` is truthy, otherwise `b`

```python
"" or "default"        # "default"    ← this is why Day 6's fallback worked
0 or 42                # 42
"Ada" or "default"     # "Ada"
"Ada" and "Byron"      # "Byron"
None and crash()       # None — crash() is never called
```

In a condition this makes no difference, because the result gets tested for truthiness anyway.
Everywhere else it is a feature: `name or "Anonymous"` is the standard way to supply a default.

`not` *does* always return a real `bool`: `not "Ada"` is `False`.

### 5. Short-circuiting

`and` and `or` evaluate the left side first and **stop as soon as the answer is known**:

- `False and anything` → the right side is never evaluated
- `True or anything` → the right side is never evaluated

This is not an optimisation, it is a guarantee you are meant to rely on. It is how you write a
guard and the thing it guards in one expression:

```python
if count > 0 and total / count > 10:      # division never happens when count is 0
if text and text[0] == "#":               # indexing never happens on an empty string
```

Reverse either of those and you get a `ZeroDivisionError` or an `IndexError`. **Order your
conditions so the cheap, protective test comes first.**

Precedence, lowest to highest: `or`, then `and`, then `not`, then comparisons. So
`a or b and c` means `a or (b and c)`. Parenthesise anything that makes a reader pause.

### 6. `==` vs. `is`

- `==` asks **"are these equal?"** — same value.
- `is` asks **"are these the same object?"** — same identity, same place in memory.

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b       # True  — equal contents
a is b       # False — two separate lists
c = a
c is a       # True  — one list, two names (Day 2's labels)
```

**Use `is` for exactly three things: `None`, `True`, `False`.** Use `==` for everything else.

The reason this matters is that Python caches small integers and short strings, so `is`
sometimes appears to work on values:

```python
x = 256; y = 256; x is y      # True  — cached
x = 257; y = 257; x is y      # False — not cached (in most contexts)
```

A test that passes for 256 and fails for 257 is a genuinely horrible bug to find. Modern Python
warns you: `SyntaxWarning: "is" with a literal`. Listen to it.

`is None` is preferred over `== None` partly by convention and partly because `==` can be
redefined by a class (Day 43) while `is` cannot be — so `is None` is the only check that cannot
lie to you.

### 7. `any()`, `all()` and counting bools

Because `True` is `1` and `False` is `0` (Day 2), booleans add up:

```python
rules_passed = rule_a + rule_b + rule_c      # how many passed
```

And two builtins collapse many bools into one, both short-circuiting:

```python
all([rule_a, rule_b, rule_c])    # True if every one is truthy
any([rule_a, rule_b, rule_c])    # True if at least one is
```

`all([])` is `True` and `any([])` is `False`. That looks arbitrary and is in fact the only
consistent choice — "none of the zero rules failed" is true.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Comparison, chaining, truthiness, the real return values of `and`/`or`, short-circuiting, `is`. |
| `build.py`  | The password checker: eight independent rules, each reported. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`if x = 5`** — `SyntaxError`. Assignment is `=`, comparison is `==`.

**`if x == True`** — redundant; write `if x`. And it is subtly wrong for truthy non-`True`
values: `"Ada" == True` is `False`.

**`is` on values.** `if name is "Ada"` works by accident for short literals and fails for long
ones. Use `==`.

**`if count:` when `0` is meaningful.** Use `is not None`.

**Guard in the wrong order.** `total / count > 10 and count > 0` crashes. Cheap test first.

**`if a == 1 or 2:`** — always `True`. `2` is truthy on its own. You meant
`a == 1 or a == 2`, or better, `a in (1, 2)`.

**Assuming `and` returns a bool.** `"" and 5` is `""`, not `False`. Harmless in a condition,
surprising in an assignment.

---

## Exercises

1. Predict then check: `bool("0")`, `bool([])`, `bool([0])`, `bool(" ")`, `bool(0.0)`,
   `bool(None)`, `bool("False")`.
2. Predict the *value* (not just the truthiness) of: `"" or 0`, `0 or ""`, `"a" and 0`,
   `None or "x"`, `[] or {} or "last"`.
3. Write one expression that is `True` for a leap year. Then rewrite it with the operands
   reordered so the cheapest test runs first, and say whether it matters here.
4. Write a condition that safely checks whether the first character of a possibly-empty string
   is a digit. Then write the version that crashes, and confirm it does.
5. Use `is` to prove that two equal lists are different objects and that two names for one list
   are not.
6. Count how many of five conditions are true, using `+`. Then decide whether `sum()` and a list
   would read better.

---

## Checklist

- [ ] I can list every falsy value from memory
- [ ] I write `if items:` rather than `if len(items) > 0:`
- [ ] I know `and`/`or` return an operand, not a bool
- [ ] I put the protective test on the left of `and`
- [ ] I use `is` only for `None`, `True` and `False`
- [ ] My checker reports each rule independently, with no rule hiding another
