# Day 005 — Numbers and operators

**Phase 1 · Foundations** · ~70 minutes

> **Today's build:** a bill splitter that handles tips, uneven shares and rounds to real currency.

**Concepts:** arithmetic · `//` and `%` · `**` · precedence · the `math` module · `round()`

---

## The article

### Why this day exists

You have been doing arithmetic since Day 2 without being told the rules. Today fixes that, and
three specific items on the list are worth more than the rest combined: `%`, precedence, and
what `round()` actually does. Modulo is the operator behind every "every Nth time" and every
"does this divide evenly" you will ever write. Precedence errors are silent — the program runs
and gives the wrong answer. And `round()` does not do what you think it does.

### 1. The operators

```python
7 + 3     # 10
7 - 3     # 4
7 * 3     # 21
7 / 3     # 2.3333333333333335
7 // 3    # 2       floor division
7 % 3     # 1       remainder
7 ** 3    # 343     power
```

`/` is **true division** and it **always returns a float**, even when it divides evenly. `10 / 5`
is `5.0`, not `5`. This catches people constantly — if you need an integer index or count, `/`
is the wrong operator.

`//` is **floor division**: divide, then round *down* to a whole number. Two details that matter:

```python
7 // 2      # 3
-7 // 2     # -4    — floors toward negative infinity, NOT toward zero
7.0 // 2    # 3.0   — floor division of a float is still a float
```

`-7 // 2` being `-4` rather than `-3` surprises people from C or Java. Python floors; those
languages truncate. If you want truncation, use `int(-7 / 2)`.

### 2. `%` — the operator that earns its keep

`%` gives the remainder after floor division:

```python
7 % 3      # 1
10 % 5     # 0
```

Its value is in the four idioms it produces, all of which you will use for the rest of the
course:

```python
n % 2 == 0            # is n even?
n % 3 == 0            # does 3 divide n? (Day 14's prime finder)
seconds % 60          # seconds left over after whole minutes
(i + 1) % 10 == 0     # every tenth iteration — progress reporting
angle % 360           # wrap around a circle
```

And the pair you will reach for whenever you split one number into units:

```python
total_seconds = 3725
minutes = total_seconds // 60      # 62
seconds = total_seconds % 60       # 5
```

`//` gives how many whole ones fit, `%` gives what is left. They are two halves of one
operation, and `divmod(3725, 60)` gives you both at once.

For negatives, Python's `%` always returns a result with the **sign of the divisor**:
`-7 % 3` is `2`, not `-1`. That is deliberate and it is what makes `angle % 360` work correctly
for negative angles.

### 3. `**` and precedence

`**` is exponentiation. `2 ** 10` is 1024. It also does roots, since a square root is a
one-half power: `9 ** 0.5` is `3.0`.

Precedence, highest to lowest, for the operators you have:

1. `**`
2. unary `-`
3. `*`, `/`, `//`, `%`
4. `+`, `-`
5. comparisons
6. `not`, then `and`, then `or`

Two consequences that will bite you:

```python
-2 ** 2      # -4, not 4.   ** binds tighter than unary minus: -(2**2)
2 ** 3 ** 2  # 512, not 64. ** is RIGHT-associative: 2 ** (3 ** 2)
```

Everything at the same level evaluates left to right (except `**`). The practical rule is
simple: **when a reader would have to stop and think, add parentheses.** They cost nothing and
they are not a sign of weakness. `(a + b) / 2` is better than `a + b / 2` even when you meant
the second one, because the second one makes the reader check.

The classic bug of this kind is the average:

```python
a + b + c / 3      # divides only c. Runs fine. Wrong answer. No error.
(a + b + c) / 3    # correct
```

### 4. Augmented assignment

```python
total = 0
total += 10       # total = total + 10
total -= 3
total *= 2
total //= 4
```

These are shorthand, not new operations. `+=` on a string works too, and on a list from Day 21
it does something subtly different — a distinction that matters on Day 21 and not before.

### 5. The `math` module

Your first `import`. A module is a file of Python somebody else wrote; importing gives you its
contents under a name:

```python
import math

math.sqrt(16)      # 4.0
math.floor(3.7)    # 3      — always down
math.ceil(3.2)     # 4      — always up
math.pi            # 3.141592653589793
math.inf           # infinity
math.isclose(0.1 + 0.2, 0.3)   # True — the correct way to compare floats
```

`math.isclose()` deserves attention. Day 2 told you never to compare floats with `==`; this is
what to do instead. It asks "are these two numbers the same to within a sensible tolerance",
which is the question you actually meant.

`math.floor()` and `//` agree for positives and are both floors, so prefer `//` when you are
dividing. `int()` is different again — it truncates toward zero. For `-3.7`: `int()` gives `-3`,
`math.floor()` gives `-4`, `round()` gives `-4`.

### 6. `round()` and money

`round(x, n)` rounds to `n` decimal places, and it does **banker's rounding**: exact halves go
to the nearest *even* number.

```python
round(2.5)     # 2   ← not 3
round(3.5)     # 4
round(0.5)     # 0
```

This is not a bug. Always rounding halves up biases sums upward; rounding to even cancels out
over many values, which is why financial standards specify it. But it is not what a shopkeeper
does, and if you need "always up on a half" you have to say so explicitly.

The deeper problem is that **floats cannot represent most decimal fractions**, so `round()`
sometimes appears to misbehave:

```python
round(2.675, 2)    # 2.67, not 2.68 — because 2.675 is really 2.67499999...
```

For money, the correct answer is `decimal.Decimal`, which stores decimal digits exactly:

```python
from decimal import Decimal, ROUND_HALF_UP

Decimal("0.1") + Decimal("0.2")            # Decimal('0.3') — exactly
Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # 2.68
```

Note `Decimal("0.1")` from a **string**. `Decimal(0.1)` inherits the float's error and defeats
the point.

Today's build uses `Decimal` for exactly this reason. It is one of the few places this early in
the course where the naive answer is genuinely wrong rather than merely clumsy — a bill split
three ways must add back up to the bill, and with floats it sometimes will not.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every operator, precedence traps, `math`, `round()` and `Decimal`. |
| `build.py`  | The bill splitter — even split, uneven shares, and a remainder that goes somewhere. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**Using `/` where you needed `//`.** `list[len(x) / 2]` is a `TypeError`; indices must be `int`.

**`-2 ** 2` giving `-4`.** Precedence. Write `(-2) ** 2`.

**`a + b + c / 3`.** No error, wrong answer. Parenthesise anything a reader would have to think
about.

**Expecting `round(2.5) == 3`.** Banker's rounding. Expected behaviour.

**`ZeroDivisionError`.** Both `/` and `%` raise on a zero divisor. Anywhere a divisor comes from
data, it can be zero.

**Money in floats.** Three people splitting £100.00 can end up owing £99.99 or £100.01. Use
`Decimal` and decide explicitly where the odd penny goes.

---

## Exercises

1. Convert 10,000 seconds into hours, minutes and seconds using only `//` and `%`. Then do it
   again with `divmod()`.
2. Predict then check: `-7 // 2`, `-7 % 2`, `7 % -2`, `int(-3.7)`, `math.floor(-3.7)`,
   `round(-3.5)`. Three of these will surprise you.
3. Write an expression that is `True` when a year is a leap year. (Divisible by 4, except
   centuries, except centuries divisible by 400.) You have `%`, `and`, `or` and `not`.
4. Prove that `0.1 + 0.2 == 0.3` is `False`, then make the correct comparison two different ways
   — `math.isclose` and `Decimal`.
5. Add up `0.1` ten times and compare against `1.0`. Now do it with `Decimal("0.1")`.
6. Split £100 three ways so the shares add back to exactly £100. Decide who gets the extra penny
   and defend the choice.

---

## Checklist

- [ ] I know `/` always returns a float and `//` floors rather than truncates
- [ ] I can use `%` for even/odd, divisibility, wrapping and unit splitting
- [ ] I know `-2 ** 2` is `-4` and why
- [ ] I never compare floats with `==`
- [ ] I can explain banker's rounding to somebody else
- [ ] My split shares sum to exactly the total, at every share count I try
