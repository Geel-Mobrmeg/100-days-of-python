# Day 034 — Scope and closures

**Phase 4 · Functions & modular code** · ~80 minutes

> **Today's build:** a counter factory and a memo cache, both built from closures instead of classes.

**Concepts:** LEGB rule · `global` & `nonlocal` · functions returning functions · captured state

---

## The article

### Why this day exists

Yesterday you wrote a function that returned a function without dwelling on why that works. Today
is the why — and it turns out to be the mechanism behind decorators (Day 37), callbacks, and a
surprising amount of "how does this library do that".

The payoff sentence: **a closure is an object with one method.** Once you see that, Day 41's
classes stop looking like a new idea and start looking like the same idea with more room.

### 1. LEGB — how a name is resolved

When Python meets a name, it looks in four places, in order, and stops at the first hit:

| | Scope | Where |
|---|---|---|
| **L** | Local | inside the current function |
| **E** | Enclosing | inside any function wrapped around it |
| **G** | Global | the module (file) level |
| **B** | Built-in | `len`, `print`, `str`, … |

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)        # local
    inner()
```

Delete the innermost assignment and the same `print(x)` finds the enclosing one, then the global,
then a `NameError`.

This is also why shadowing a builtin is dangerous (Day 8): `list = [1,2]` puts a name in **G**,
which is searched before **B**, so `list()` stops working everywhere below it.

### 2. Reading is free; assigning creates a local

The rule that produces the most confusing error in this topic:

> **If a function assigns to a name anywhere in its body, that name is local for the whole
> function — including before the assignment.**

```python
count = 0

def broken():
    print(count)        # UnboundLocalError, not 0
    count = count + 1
```

Python decides scope at *compile* time by scanning for assignments, not at run time. Because
`count = ...` appears somewhere in the body, `count` is local throughout — so the `print` reads a
local that has not been assigned yet.

`+=` counts as an assignment, which is why counters break in exactly this way.

### 3. `global` and `nonlocal`

```python
def with_global():
    global count
    count += 1          # now assigns to the module-level name

def outer():
    total = 0
    def inner():
        nonlocal total
        total += 1      # assigns to outer's `total`
    inner()
    return total
```

- `global` — reach the module level.
- `nonlocal` — reach the nearest *enclosing function* scope. Not the global one.

**Avoid `global`.** A function that mutates module state cannot be tested in isolation, cannot be
reasoned about locally, and cannot be run twice safely. Pass values in, return values out.

`nonlocal` is different: it is the tool that makes closures able to *remember*, and it is used
deliberately rather than as a shortcut.

### 4. Closures

A **closure** is a function that remembers the variables from where it was defined, even after
that outer call has finished.

```python
def make_multiplier(factor):
    def multiply(value):
        return value * factor      # `factor` comes from the enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
double(5)      # 10
triple(5)      # 15
```

`make_multiplier(2)` has returned — its frame is gone — and yet `double` still knows `factor` is
2. Python kept the variable alive because the inner function referred to it. You can see the
evidence:

```python
double.__closure__[0].cell_contents      # 2
```

`double` and `triple` are separate objects with separate captured state. That is the whole idea.

### 5. Captured state, and the loop trap

To *change* captured state you need `nonlocal`:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
```

And the classic trap, which catches everyone once:

```python
functions = []
for i in range(3):
    functions.append(lambda: i)
[f() for f in functions]       # [2, 2, 2] — not [0, 1, 2]
```

**Closures capture the variable, not its value.** All three lambdas share the same `i`, and by
the time they run, the loop has finished and `i` is 2.

The fix is to bind the value at definition time, with a default argument (Day 32 — evaluated
once, at definition, which is exactly what you want here):

```python
functions.append(lambda i=i: i)     # [0, 1, 2]
```

or with a factory function, which is clearer.

### 6. A closure *is* an object

```python
def make_counter():            class Counter:
    count = 0                      def __init__(self):
    def increment():                   self.count = 0
        nonlocal count             def increment(self):
        count += 1                     self.count += 1
        return count                   return self.count
    return increment
```

Same behaviour, same encapsulation, same private state. The difference:

| Closure | Class |
|---|---|
| one behaviour | many methods |
| state is genuinely private | `obj.count` is reachable |
| lighter, faster | introspectable, subclassable, picklable |

**Use a closure for one behaviour with a little state. Use a class when there are several
operations on the same state.** A closure with three inner functions returned in a tuple is a
class that has not admitted it yet.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | LEGB, `UnboundLocalError` demonstrated, `global` vs `nonlocal`, closures, the loop trap and its fix. |
| `build.py`  | A counter factory and a memoising cache, both closures — then the same cache as a class, compared. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`UnboundLocalError`.** You assigned to the name somewhere in the function.

**Using `global` to share state.** Untestable, unrepeatable. Pass and return.

**`nonlocal` at module level.** `SyntaxError` — there is no enclosing function.

**Late binding in a loop.** All closures see the final value. Bind with a default argument.

**Expecting `nonlocal` to reach globals.** It only reaches enclosing *functions*.

**A closure with four inner functions.** That is a class.

---

## Exercises

1. Write the `UnboundLocalError` version, then fix it three ways: `global`, passing in, returning.
2. Write `make_multiplier` and inspect `__closure__[0].cell_contents`.
3. Reproduce the loop trap and fix it both ways.
4. Write a closure holding a running average that never stores the list of values.
5. Write `make_counter` and prove two counters are independent.
6. Rewrite one closure as a class, then decide which you prefer and why.

---

## Checklist

- [ ] I can recite LEGB and say which scope wins
- [ ] I know why assigning makes a name local for the whole function
- [ ] I use `nonlocal` deliberately and `global` almost never
- [ ] I know closures capture the variable, not the value
- [ ] I can explain when a closure should be a class
- [ ] My counters are independent and my cache reports its own hit rate
