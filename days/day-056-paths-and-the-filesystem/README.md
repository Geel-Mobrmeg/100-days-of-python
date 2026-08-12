# Day 056 — Paths and the filesystem

**Phase 6 · Robust code** · ~80 minutes

> **Today's build:** a bulk renamer with a dry-run mode that shows every change before it touches anything.

**Concepts:** `pathlib.Path` · globbing · `exists` & `mkdir` · `shutil` · cross-platform paths

---

## The article

### Why this day exists

Days 53–55 read and wrote files you already had a path to. Today is about *finding* them, *naming*
them and *moving* them — which is where a program stops being able to lose only its own output and
starts being able to lose the user's data.

### 1. A path is an object

| the old way | the pathlib way |
|---|---|
| `os.path.join(a, b, c)` | `Path(a) / b / c` |
| `os.path.basename(p)` | `p.name` |
| `os.path.splitext(p)[0]` | `p.stem` |
| `os.path.dirname(p)` | `p.parent` |
| `os.makedirs(p, exist_ok=True)` | `p.mkdir(parents=True, exist_ok=True)` |

The `/` operator is not cuteness — it uses the right separator on every platform, so string
concatenation of paths never appears in your code again.

The part that surprises people:

```
/home/ada/docs/report.final.tar.gz
  .name        report.final.tar.gz
  .stem        report.final.tar        ← everything before the LAST dot
  .suffix      .gz                     ← only the LAST extension
  .suffixes    ['.final', '.tar', '.gz']
```

`with_suffix()`, `with_stem()` and `with_name()` return *new* paths — a `Path` is immutable, like a
string.

### 2. Relative to what?

A relative path resolves against the **working directory** — where the user ran the command, not
where your script lives. This is the commonest "works on my machine" there is:

```python
Path("data.csv")                       # depends on the caller's shell
Path(__file__).parent / "data.csv"     # always next to the script
```

Use the second for files that ship *with* your code, the first for files the user points you at.

`.resolve()` removes `..` and `.`, follows symlinks and makes the path absolute. Do it **before** you
compare two paths or check that one is inside another:

```python
target = (root / user_supplied).resolve()
if not target.is_relative_to(root.resolve()):
    raise ValueError(...)
```

That is the line that stops `../../etc/passwd`. String comparison on unresolved paths is how
directory-traversal bugs happen.

### 3. Finding things

```
iterdir()                 .hidden, archive, notes.txt, photo.JPG, sub
glob('*.txt')             notes.txt
glob('*')                 .hidden, archive, notes.txt, photo.JPG, sub
rglob('*.txt')            archive/old.txt, notes.txt, sub/file.txt
glob.glob(work + '/*')    archive, notes.txt, photo.JPG, sub
```

Three things worth knowing:

- **`pathlib`'s `glob('*')` returns dotfiles. The `glob` module's does not.** Opposite defaults —
  code converted from one to the other silently changes which files it touches.
- `rglob(p)` is `glob("**/" + p)`.
- **Glob is case-sensitive on Linux and not on macOS/Windows.** `*.jpg` finds one file here and two
  on a Mac. Filter on `p.suffix.lower()` if it matters.

And it returns an iterator in arbitrary order — `sorted()` it, or your output changes between runs.

### 4. The operation that bites

```
a.txt contains 'AAA', b.txt contains 'BBB'
a.txt.rename(b.txt)
b.txt now contains 'AAA' and BBB IS GONE
```

`rename()` **silently overwrites** an existing file on POSIX. On Windows it raises instead — so the
same code behaves differently on two platforms, which is worse than either.

There is no atomic "rename only if absent" in the standard library. You check, you know the check is
not atomic (Day 51's LBYL gap), and you say so.

### 5. Other people's machines

| | what differs |
|---|---|
| **case** | Linux: `File.txt` and `file.txt` are two files. macOS/Windows: usually one |
| **illegal characters** | Windows forbids `< > : " \| ? *` and trailing dots/spaces; Linux forbids only `/` and NUL |
| **reserved names** | `CON`, `PRN`, `AUX`, `NUL`, `COM1–9`, `LPT1–9` — with *any* extension |
| **length** | historically 260 characters on Windows |

If your tool names files, sanitise for the strictest platform even when you are not on it. It is
eight lines.

### 6. The line to be frightened of

```python
shutil.rmtree(path)
```

No confirmation, no recycle bin, no undo. Four habits: resolve first and assert the target is where
you think; never build a destructive path by concatenation; **dry run by default**; and check
explicitly for the empty string, because `Path("")` is `Path(".")`.

### 7. The build: dry run is the default

That is the whole design. Doing the work requires `--apply`. A tool that renames files is a tool that
can lose them, and the difference between "shows you the plan" and "shows you the plan unless you
forget a flag" is the difference between a tool people trust and one they run once.

```
BEFORE                            AFTER
  leading and trailing  .txt      leading-and-trailing.txt          ->
....dots....txt                   dots.txt                          ->
2019 Invoice #7 (paid).csv        2019-invoice-7-paid.csv           ->
CON.txt                           con-file.txt                      ->
Holiday Photo 01.JPEG             holiday-photo-01.jpg              ->
Report Draft.txt                  report-draft.txt                  !!
                                  2 files want 'report-draft.txt'
café menu (final).PDF             cafe-menu-final.pdf               ->
report:draft.txt                  report-draft.txt                  !!

would rename 10, unchanged 2, refused 2
```

The dry run is only trustworthy because `plan()` and `apply()` share **one pure naming function**. A
preview computed by different code from the action is a lie waiting to happen — and the build
*checks* that the dry run changed no names and no modification times, rather than asserting it.

### 8. The four problems a naive renamer gets wrong

**Collisions.** Two files that normalise to the same name. Both are refused, loudly. Auto-numbering
them is a defensible alternative — and it would make the result depend on the order the operating
system happened to list the directory in, which is not stable.

**Cycles.** This is the one that costs a file:

```
                a.txt               b.txt                  FILES
one pass        I am A              -- GONE --                 1
two phases      I am B              I am A                     2
```

Given `a → b` and `b → a`, renaming in *any* order destroys one of them, because `rename()`
overwrites. The fix is two passes: move every source to a unique temporary name, then move each
temporary to its target. No target is ever occupied when it is written to, so no order is wrong. Six
extra lines, and not optional.

**Overwrites** of files that are not part of the plan — checked before acting.

**Case-only renames**, which are a no-op on one filesystem and a conflict on another.

### 9. The bug this file shipped with

The build's first version used the textbook accent-folding recipe — decompose with NFKD, drop every
combining mark. It turns `café` into `cafe`, and it turns Russian `Другой файл` into
`другои-фаил`, because `й` decomposes to `и` plus a combining breve.

Two different letters, silently merged, in every file a Russian speaker owns. And the version before
*that* was worse: an ASCII-only `[a-z0-9]` slug renamed every Cyrillic, Greek, Arabic, Hebrew, Hindi,
Chinese and Japanese filename to `unnamed` — identically, so they then collided with each other.

Folding is a *Latin* convenience. It is now applied only where the base character is ASCII, and there
are two checks for it, because the failure is invisible to anyone testing in English.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Path anatomy, `resolve` and `is_relative_to`, five glob queries compared, the `rename` overwrite demonstrated, and the cross-platform table. |
| `build.py`  | The renamer: a 14-file sample tree with every awkward case, a dry run proved to touch nothing, two-phase apply, a swap that a one-pass renamer loses, and 21 checks. |

```bash
python3 lesson.py
python3 build.py                      # the demonstration
python3 build.py ~/Downloads          # DRY RUN on a folder of your own
python3 build.py ~/Downloads --apply  # ...and actually do it
```

---

## Common mistakes

**Building paths with `+` or f-strings.** Wrong separator, and no `.parent`.

**Assuming `.stem` strips every extension.** `archive.tar.gz` → `archive.tar`.

**Opening a relative path from a script.** It resolves against the caller's shell.

**Comparing unresolved paths.** `..` and symlinks make string comparison meaningless.

**Trusting a user-supplied filename.** `.resolve().is_relative_to(root)` or nothing.

**`rename()` onto a path that might exist.** Silent data loss on POSIX.

**Renaming in one pass.** Any swap loses a file.

**Glob without `sorted()`.** Non-deterministic output.

**ASCII-only slugs.** Every non-Latin name becomes the same name.

**`shutil.rmtree` on a path you did not resolve and check.**

---

## Exercises

1. Print `.stem` and `.suffix` for `archive.tar.gz`, then write the loop that strips every suffix.
2. Run a script that opens `Path("data.csv")` from a different working directory, then fix it.
3. Glob a folder containing `a.JPG` with `*.jpg` and compare with a colleague on a Mac.
4. `rename()` a file onto an existing one, then read the other file.
5. Write the traversal check and try `../../etc/passwd` against it.
6. Write a renamer with a dry run, and check *in code* that the dry run changed no timestamps.
7. Make two files swap names. Do it in one pass, then in two.
8. Sanitise a filename for Windows: illegal characters, reserved names, trailing dots.

---

## Checklist

- [ ] I use `Path` and `/`, never string joining
- [ ] I know `.suffix` is only the last extension
- [ ] I use `Path(__file__).parent` for files that ship with my code
- [ ] I `.resolve()` before comparing, and use `.is_relative_to()` for safety
- [ ] I `sorted()` my globs and know they skip nothing in pathlib
- [ ] I know `rename()` overwrites on POSIX
- [ ] I sanitise names for the strictest platform
- [ ] My destructive tools dry-run by default
- [ ] I rename in two phases
