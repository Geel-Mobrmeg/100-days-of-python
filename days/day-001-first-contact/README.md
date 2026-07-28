# Day 001 — First contact

**Phase 1 · Foundations** · ~60 minutes

> **Today's build:** a program that prints your name inside an ASCII frame it draws to fit.

**Concepts:** installing Python · the REPL vs. a script · `print()` · running a `.py` file · your editor

---

## The article

### Why this day exists

Almost everyone who quits programming quits in the first week, and almost none of them quit
because loops were too hard. They quit because they never got a clean loop between *typing
something* and *seeing what it did*. Today is entirely about building that loop. By the end of
the hour you should be able to go from an idea to a running program without stopping to look
anything up — not because you know much Python yet, but because the mechanics are out of the way.

There are only four moving parts, and you will use all four every single day for the next
ninety-nine.

### 1. Installing Python

Python is a program that reads your files and does what they say. You need version **3.11 or
newer** for this course — Day 17 uses `match`, which arrived in 3.10, and the type syntax on
Day 59 assumes 3.9+.

Check what you already have:

```bash
python3 --version
```

If that prints `Python 3.11.x` or higher, you are done. If it prints 3.8, or errors, install a
current version:

- **macOS** — `brew install python@3.12`, or the installer from [python.org](https://python.org).
- **Windows** — the installer from python.org. **Tick "Add python.exe to PATH"** on the first
  screen. Nearly every "python is not recognized" question on the internet is that unticked box.
- **Linux** — you almost certainly have it. `sudo apt install python3` if not.

One footnote that saves confusion later: on macOS and Linux the command is usually `python3`,
on Windows it is usually `python`. Wherever this course writes `python`, use whichever one
works on your machine.

### 2. Two ways to run Python: the REPL and a script

This is the distinction most beginners are never told explicitly, and it causes weeks of
low-grade confusion.

**The REPL** is Python's interactive prompt. Type `python3` with no filename:

```
$ python3
Python 3.12.1
>>> 2 + 2
4
>>> print("hi")
hi
>>> exit()
```

REPL stands for Read–Eval–Print Loop: it reads a line, evaluates it, prints the result, and
loops. Notice that `2 + 2` printed `4` **without** you asking it to. That is the REPL being
helpful, and it is unique to the REPL. It is a workbench: a place to test one small thing, check
what a function does, confirm you remember a method name. Nothing you type in it is saved.

**A script** is a file of Python that runs top to bottom and then exits:

```bash
python3 hello.py
```

A script prints *only* what you explicitly tell it to print. A file containing just `2 + 2`
outputs nothing at all — Python computes 4, finds nobody wants it, and throws it away. This
surprises everyone once. If you want to see a value from a script, you must `print()` it.

Rule of thumb for the whole course: **explore in the REPL, keep in a script.** The `lesson.py`
in each folder is the script; try the same lines in the REPL to see the difference.

### 3. `print()`

`print` is a *function*. You call it by putting parentheses after its name, and you put its
input — its **arguments** — inside them:

```python
print("Hello, world!")
```

The quotes matter. `"Hello"` is a piece of text (a **string**); `Hello` without quotes is a
*name*, and Python will go looking for something called `Hello`, fail to find it, and stop.
Single and double quotes work identically — `'Hello'` and `"Hello"` are the same string — so
pick one and stay consistent. This course uses double.

`print` takes as many arguments as you like, and joins them with a space:

```python
print("Ada", "Lovelace")      # Ada Lovelace
print("2 + 2 =", 2 + 2)       # 2 + 2 = 4
```

Two keyword arguments are worth meeting on day one, because you will want them within the week:

```python
print("a", "b", "c", sep="-")   # a-b-c   — what goes BETWEEN the arguments
print("no newline", end="")     # what goes AFTER the last one; default is "\n"
```

`print()` with nothing in it prints a blank line. That is the normal way to space out output.

### 4. Your editor

Use whatever you like, as long as it does three things: syntax highlighting, an integrated
terminal, and showing you the file extension. **VS Code** with the official Python extension is
the default recommendation and what most of this course's screenshots would look like if it had
any. PyCharm, Sublime, Neovim, Zed — all fine.

Two settings to change now, once, forever:

- **Insert spaces instead of tabs, width 4.** Python cares about indentation, and mixing tabs
  with spaces is a real error with a confusing message. Every editor has this setting.
- **Show whitespace / render control characters**, if it's on offer. Invisible problems become
  visible problems.

Create a folder for this course and open the *folder* in your editor, not individual files. Your
terminal should be in the same folder — in VS Code, `` Ctrl-` `` opens one that already is.

### 5. Borrowed from tomorrow

Today's build needs three things a day early. They are explained properly on Days 2 and 3; for
now, take them on trust:

```python
name = "Ada Lovelace"    # a name pointing at a value          (Day 2)
len(name)                # how many characters that value has  (Day 3)
"-" * 12                 # a string repeated: "------------"   (Day 3)
```

That last one is the trick the whole build hangs on. A frame that "draws to fit" is just a line
of dashes whose length you compute from the name instead of typing by hand — which is the entire
idea of programming, arriving on day one and never leaving.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every concept above, runnable and annotated. Run it, then change lines and run it again. |
| `build.py`  | Today's build, finished. Write your own first. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`SyntaxError: Missing parentheses in call to 'print'`** — you wrote Python 2. It is
`print("x")`, not `print "x"`.

**`NameError: name 'Hello' is not defined`** — you forgot the quotes. Python thought `Hello` was
a name and went looking for it.

**Your file is called `hello.py.txt`.** Windows hides extensions by default. Turn that off in
Explorer (View → File name extensions) or you will fight this for days.

**`python: command not found`** — try `python3`. If neither works, PATH wasn't set during
install; re-run the installer with the PATH box ticked.

**Running the file from the wrong folder.** `python3 hello.py` means "run `hello.py` *in this
directory*". `cd` to where the file is, or pass the full path.

---

## Exercises

1. Open the REPL and evaluate `2 + 2`, `"a" + "b"`, and `len("python")`. Now put those same
   three lines in a file and run it. Explain out loud why the file printed nothing.
2. Print a three-line address block — name, street, city — using exactly one `print()` call.
   (Hint: `\n` inside a string is a newline. Day 3 covers this properly.)
3. Use `sep` to print `2024-01-15` from the three numbers `2024`, `1`, `15`. Notice what happens
   to the zero padding, and leave it broken; Day 4 fixes it.
4. Make Python raise an error on purpose. Read the last line of the traceback and write down, in
   your own words, what it told you. You will do this a lot on Day 9.

---

## Checklist

- [ ] `python3 --version` prints 3.11 or higher
- [ ] I can start the REPL and exit it without closing the terminal
- [ ] I can run a `.py` file from my terminal
- [ ] I can explain why a script containing only `2 + 2` prints nothing
- [ ] My editor inserts 4 spaces when I press Tab
- [ ] The build runs and the frame fits my name exactly
