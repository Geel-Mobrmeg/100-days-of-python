# Day 015 — Nested loops

**Phase 2 · Control flow** · ~80 minutes

> **Today's build:** an ASCII art generator: pyramids, diamonds and a chessboard, all from nested loops.

**Concepts:** loops inside loops · row and column thinking · cost of nesting · 2D grids

---

## The article

### Why this day exists

Everything with two dimensions — a table, a grid, an image, a chessboard, a spreadsheet, every
pairing of one list against another — is a nested loop. You already wrote one on Day 13 without
much ceremony. Today is about the two things that make them hard: **thinking in rows and
columns**, and **knowing what they cost**.

The cost part is not academic. A nested loop over 1,000 items is a million operations. Three
levels is a billion. The difference between a program that finishes and one that appears to hang
is very often a loop you did not notice was nested.

### 1. The shape

```python
for row in range(3):
    for col in range(4):
        print(f"({row},{col})", end=" ")
    print()                    # end of row — OUTSIDE the inner loop
```

**The outer loop is rows; the inner loop is columns.** The inner loop runs *completely* for each
single pass of the outer one — 3 rows × 4 columns = 12 passes of the inner body.

The `print()` at the end is the detail everyone gets wrong once. It belongs to the *outer* loop
— one newline per row, after all that row's columns are done. Indent it one level further and
you get a newline after every cell; leave it out and the whole grid is one long line.

That is the whole mental model:

- outer pass = one row
- inner pass = one cell
- after the inner loop = finish the row

### 2. Row and column thinking

The trick with any shape is to answer one question: **for a cell at (row, col), what decides
what goes there?**

Work out the rule, then write the loop. Do not write the loop and fiddle until it looks right —
that produces code you cannot modify.

A chessboard: a square is dark when `(row + col)` is even. That single expression is the whole
board, and it is why the colours alternate along both axes at once.

```python
for row in range(8):
    for col in range(8):
        print("##" if (row + col) % 2 == 0 else "  ", end="")
    print()
```

A left-aligned triangle of height *n*: row *i* has *i + 1* stars.

```python
for i in range(n):
    print("*" * (i + 1))
```

Notice that one does not need an inner loop at all — string repetition (Day 3) does the inner
loop's job. **When each row is a simple repeat, `*` beats a nested loop** for both readability
and speed. Use the inner loop when cells differ from each other.

A centred pyramid needs two things per row: leading spaces, then stars.

| row | spaces | stars |
|---|---|---|
| 0 | n−1 | 1 |
| 1 | n−2 | 3 |
| 2 | n−3 | 5 |
| i | n−1−i | 2i+1 |

Write that table out before writing the code. Every pyramid bug is a wrong entry in that table,
and the table takes thirty seconds.

### 3. Ranges that depend on the outer variable

The inner range does not have to be constant, and this is where nested loops get interesting:

```python
for i in range(rows):
    for j in range(i, cols):       # starts where the outer loop is
        ...
```

That gives the upper triangle — you used it on Day 13 to print each multiplication fact once.
The general pattern for "every unordered pair, once" is `for j in range(i + 1, n)`, and it comes
up constantly: comparing every item with every other item, finding duplicates, computing
distances.

### 4. `break` and `continue` in nested loops

**`break` leaves only the innermost loop.** This is the single most common surprise.

```python
for row in grid:
    for cell in row:
        if cell == target:
            break              # leaves the INNER loop only
    # ...and the outer loop carries on to the next row
```

Three ways to leave both:

```python
# 1. A flag
found = False
for row in grid:
    for cell in row:
        if cell == target:
            found = True
            break
    if found:
        break

# 2. for...else — Day 14, and the neatest
for row in grid:
    for cell in row:
        if cell == target:
            break
    else:
        continue          # inner finished with no break -> next row
    break                 # inner DID break -> leave outer too

# 3. Put it in a function and `return`   (Day 31 — and this is the right answer)
```

Option 3 is genuinely the best one, and when you meet `return` on Day 31 you should come back
and rewrite any two-level search you have written. Option 2 is clever and a little too clever;
option 1 always works and everybody understands it.

### 5. The cost of nesting

```python
for i in range(n):          # n
    for j in range(n):      # n × n
        do_something()      # runs n² times
```

| n | n² | at ~10M ops/sec |
|---|---|---|
| 100 | 10,000 | instant |
| 1,000 | 1,000,000 | ~0.1 s |
| 10,000 | 100,000,000 | ~10 s |
| 100,000 | 10,000,000,000 | ~17 minutes |

Ten times the data is a hundred times the work. This is the first performance idea in the
course, it is called **O(n²)**, and Day 29 gives it a proper name and Day 95 the tools to
measure it.

The practical warning: nesting is not always visible. A loop that calls `if item in other_list:`
is a nested loop — `in` on a list scans it. On Day 26 you will learn that a `set` turns that scan
into a single step, and the same program goes from minutes to milliseconds without a loop being
deleted.

### 6. 2D grids

Storing a grid needs a list of lists (Day 21), but you can already *print* one, and the indexing
convention is worth meeting now: `grid[row][col]`, row first. It reads like "which line, then how
far along", and mixing up the order is a classic bug that produces a transposed image.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | The shape, the row/col rule, triangles, dependent ranges, breaking out, and a measured cost demo. |
| `build.py`  | The art generator: triangles, pyramids, diamonds, chessboard, borders and a multiplication grid. |

```bash
python3 lesson.py
python3 build.py
python3 build.py 12
```

---

## Common mistakes

**`print()` in the wrong place.** Inside the inner loop, or missing. One newline per row, after
the inner loop, at the outer loop's indentation.

**Reusing the loop variable.** `for i` inside `for i` — the inner one clobbers the outer.

**Expecting `break` to leave both loops.** It leaves one.

**Off-by-one in a pyramid.** Write the spaces/stars table before the code.

**Accidental O(n²).** `if x in list` inside a loop over another list.

**Building output with `+=` in a nested loop.** Quadratic on top of quadratic. Collect and join.

---

## Exercises

1. Print a 5×5 grid of `(row,col)` coordinates. Move the `print()` inside the inner loop and then
   delete it, to see both failure modes.
2. Print a left triangle, a right-aligned triangle, an inverted triangle, and a centred pyramid
   of height 6. Write the spaces/stars table for each first.
3. Print an 8×8 chessboard with `##` and spaces. Then add rank and file labels around it.
4. Print a hollow square of size *n*: border only. The rule is "row or col is at an edge".
5. Print every unordered pair from `"ABCDE"` exactly once. There should be 10.
6. Time a nested loop at n = 100, 1,000 and 3,000 and confirm the time grows with the square.

---

## Checklist

- [ ] I know which loop is rows and which is columns
- [ ] My `print()` for the row end is at the outer indentation
- [ ] I write the per-row rule down before writing the loop
- [ ] I know `break` leaves only the inner loop, and three ways around it
- [ ] I can state what n² means for n = 10,000
- [ ] My diamond is symmetric at both odd and even sizes
