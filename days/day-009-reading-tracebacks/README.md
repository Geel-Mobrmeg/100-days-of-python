# Day 009 — Reading tracebacks

**Phase 1 · Foundations** · ~75 minutes

> **Today's build:** five broken scripts, five bugs. Fix all of them and write down what each error meant.

**Concepts:** stack traces · common error types · print debugging · `breakpoint()` · rubber-ducking

---

## The article

### Why this day exists

You will spend more of your programming life reading errors than writing code. That is not a
sign of doing it badly — it is the job. The difference between someone who has been programming
for a week and someone who has been doing it for a year is almost entirely *how fast they read
an error and know where to look*.

The good news is that Python's tracebacks are unusually helpful, and modern versions have got
dramatically better: they underline the exact failing subexpression and suggest names you might
have meant. Most people never notice, because they see red text and stop reading.

Today's single most important idea, which the fifth bug exists to teach: **a traceback tells you
where the program died, not where it went wrong.** Those are frequently different lines.

### 1. Reading a traceback

```
Traceback (most recent call last):
  File "bug_2.py", line 13, in <module>
    print("Subtotal: " + SUBTOTAL)
          ~~~~~~~~~~~~~^~~~~~~~~~
TypeError: can only concatenate str (not "float") to str
```

Four parts, and you read them out of order:

1. **The last line first.** It gives the exception type and an English explanation. This is 80%
   of the information. Beginners read the first line, panic, and stop reading.
2. **The `File ... line N`.** Where it happened.
3. **The source line.** What was executing.
4. **The `~~~^^^` markers.** Python 3.11+ underlines the exact subexpression that failed. On a
   line containing `a[i] + b[j]`, this tells you *which* of the two blew up. It is enormously
   useful and almost nobody uses it.

"Most recent call last" matters once your programs have functions (Day 31). The stack is printed
oldest-call-first, so **your** code is usually near the bottom and the library frames above it
are rarely the site of your mistake. Read up from the bottom until you recognise a filename.

### 2. The exceptions you will actually meet

| Exception | Means | Typical cause |
|---|---|---|
| `SyntaxError` | Python could not parse the file | missing `)`, `:`, or quote — **nothing runs at all** |
| `IndentationError` | inconsistent indenting | mixed tabs and spaces |
| `NameError` | no such name | typo, or used before assignment |
| `TypeError` | wrong *type* for the operation | `"a" + 1`, calling a non-function |
| `ValueError` | right type, unusable *value* | `int("abc")` |
| `IndexError` | sequence index out of range | assumed a length |
| `KeyError` | no such dict key (Day 24) | assumed a key exists |
| `AttributeError` | object has no such method | wrong type, or a typo in the method name |
| `ZeroDivisionError` | divided by zero | a count that was empty |
| `FileNotFoundError` | no such file (Day 53) | wrong path, wrong working directory |

Two distinctions worth carrying:

**`TypeError` vs `ValueError`.** `int("abc")` is a `ValueError` — a string is a perfectly
reasonable thing to pass to `int()`, but *that* string is not. `int([])` is a `TypeError` — a
list is not a reasonable thing to pass at all. Right type / wrong value versus wrong type.

**`SyntaxError` is different from all the others.** It happens before your program starts. If
you see one, no line of your file ran, and the reported line number is where Python *noticed*,
which is often one line *after* the real problem — an unclosed bracket is reported at the next
line. When a `SyntaxError` points at a line that looks perfect, check the line above it.

### 3. Print debugging

Unfashionable, universally used, and genuinely correct most of the time. The technique has
exactly one modern form:

```python
print(f"{count=}")
print(f"{parts=}")
print(f"{value!r}")
```

Two rules make this a tool rather than noise:

- **Print the expression, not a label you typed.** `f"{count=}"` cannot drift out of sync with
  the code; `print("count is", n)` can, and does.
- **Use `!r` for anything textual.** `f"{value!r}"` shows `' 42 '` where `f"{value}"` shows `42`.
  The difference between those two is a bug you will otherwise stare through.

The method: **walk backwards from the crash**, printing each value on the way, until one of them
is not what you assumed. That line is the real bug. Bug 5 in this folder is exactly this shape,
and a single `print(f"{count=}")` finds it in ten seconds.

### 4. `breakpoint()`

When there are too many values to print, put `breakpoint()` on a line and run the script
normally. Python stops there and gives you a prompt with all locals live:

```
n     next line (step over)
s     step into the call
c     continue
l     list source around here
p x   print x
q     quit
```

Type any expression to evaluate it against the live state — that is the thing prints cannot do.
`PYTHONBREAKPOINT=0` disables every `breakpoint()` in a run without editing files.

### 5. Rubber-ducking

Explain the broken code out loud, line by line, to something that cannot help you. The sentence
you cannot finish is the bug.

This works because reading silently lets you skim the line you *assume* is fine, and speaking
forces you to evaluate it. Most people find the bug partway through and never finish the
sentence. Corollary: write the help request before you send it, and half the time you will not
need to.

### 6. Today's real lesson

Bug 5 crashes on a division. The division is not the bug. Four lines earlier, a filter tested for
a string that appears nowhere in the data, matched nothing, and produced an empty result —
silently. The emptiness travelled downstream until something finally objected.

If you "fix" the line the traceback names — say, by guarding the division — you get a program
that prints a **wrong answer instead of crashing**, which is strictly worse. The crash was the
only thing telling you something was broken.

So: find out *why* a value is wrong before you make the symptom go away.

---

## The code

| File | What it does |
|---|---|
| `broken/bug_1.py` … `bug_5.py` | Five programs that crash, five different exceptions. Fix these. |
| `lesson.py` | Runs all five and prints their **real** tracebacks, annotated, plus print-debugging and `pdb`. |
| `build.py` | The five fixes, each with what the traceback said and why. |

```bash
python3 lesson.py                 # the annotated tour
python3 broken/bug_1.py           # crash it yourself
python3 build.py                  # the fixes
```

---

## Common mistakes

**Reading the first line and stopping.** The information is at the bottom.

**Fixing the line the traceback names, when the cause is elsewhere.** See bug 5.

**Silencing an error instead of understanding it.** A guard that turns a crash into a wrong
number is a downgrade.

**Assuming a `SyntaxError`'s line number is right.** Check the line above — an unclosed bracket
is reported one line late.

**Ignoring "Did you mean:".** Python 3.10+ suggests the name you meant. It is usually correct.

**Debugging by shuffling code.** Changing things at random until it works produces a program
nobody understands, including you. Print the values.

---

## Exercises

1. Fix all five bugs without reading `build.py`. For each, write one sentence: *what the
   exception type means*, not what you changed.
2. Cause each of these deliberately, in the REPL, in one line: `TypeError`, `ValueError`,
   `IndexError`, `AttributeError`, `ZeroDivisionError`.
3. Write a `SyntaxError` by leaving a bracket unclosed on line 3 of a 10-line file. Note which
   line Python blames.
4. Take bug 5 and find the bug using only `print(f"{...=}")` — no reading ahead. Time yourself.
5. Put `breakpoint()` in bug 3 just before the failing line, then use `p parts_3` and
   `p len(parts_3)` to see the problem, and `q` to exit.
6. Explain bug 1 out loud to an object in the room. Notice where you hesitate.

---

## Checklist

- [ ] I read the last line of a traceback first
- [ ] I can explain the difference between `TypeError` and `ValueError`
- [ ] I look at the `^^^` markers to find the failing subexpression
- [ ] I use `f"{x=}"` and `!r` rather than bare prints
- [ ] I know how to start `pdb` and the six commands that matter
- [ ] I fixed the *cause* of bug 5, not the line that crashed
