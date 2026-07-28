# Day 021 — Lists

**Phase 3 · Data structures** · ~75 minutes

> **Today's build:** a to-do list you can add to, complete, reorder and delete from, all in memory.

**Concepts:** creation & indexing · slicing · `append` / `insert` / `pop` · mutability · aliasing vs. copying

---

## The article

### Why this day exists

Yesterday's adventure held its world in five parallel lists that had to stay the same length
forever, with nothing enforcing it. Every program you have written has had a moment where you
wanted "several of these" and had to write `item_1`, `item_2`, `item_3`.

Lists are the fix, and they are the container you will use more than all the others combined.
They are also the first **mutable** thing you have met, and mutability brings one genuinely
dangerous behaviour with it — aliasing — which is the real subject of today.

### 1. Creating and indexing

```python
tasks = ["write", "test", "ship"]
empty = []
mixed = [1, "two", 3.0, True, None]      # legal, and usually a bad idea
```

A list can hold anything, including other lists. In practice, keep one *kind* of thing in a list;
mixed lists mean every reader has to check types.

Indexing and slicing work exactly as they did for strings (Day 3), and for the same reasons:

```python
tasks[0]        # "write"
tasks[-1]       # "ship"
tasks[0:2]      # ["write", "test"]   — a NEW list
tasks[::-1]     # reversed copy
len(tasks)      # 3
"test" in tasks # True
```

**A slice of a list is a new list.** That matters more here than it did for strings, and it is
the basis of the copying section below.

### 2. The methods, and which ones return `None`

```python
tasks.append("deploy")       # add one, at the end            -> None
tasks.insert(0, "plan")      # add one, at an index           -> None
tasks.extend(["a", "b"])     # add MANY (list += list)        -> None
tasks.remove("test")         # delete by VALUE, first match   -> None
tasks.sort()                 # reorder in place               -> None
tasks.reverse()              # in place                       -> None
tasks.clear()                # empty it                       -> None

tasks.pop()                  # remove and RETURN the last
tasks.pop(0)                 # remove and RETURN by index
tasks.index("ship")          # position, raises if absent
tasks.count("ship")          # how many
```

The pattern from Day 16's `shuffle` is now a rule: **methods that change a list in place return
`None`.** So `tasks = tasks.append("x")` sets `tasks` to `None`, and the mistake surfaces
somewhere else entirely.

Where you want a result instead of a mutation, use the function form:

```python
tasks.sort()                 # changes tasks
new = sorted(tasks)          # leaves tasks alone         (Day 27)
tasks.reverse()              # changes tasks
new = list(reversed(tasks))  # leaves tasks alone
```

`append` vs `extend` catches everyone once: `append` adds *one item*, so
`tasks.append(["a","b"])` gives you a list containing a list.

`.remove()` deletes the **first** match only and raises `ValueError` if absent. To delete by
position use `del tasks[i]` or `.pop(i)`.

### 3. Mutability — the actual subject of today

Strings are immutable; every "change" made a new one. Lists are **mutable**: they change in
place, and every name pointing at them sees the change.

```python
a = [1, 2, 3]
b = a               # NOT a copy — a second label on the SAME list (Day 2)
b.append(4)
print(a)            # [1, 2, 3, 4]   ← a changed too
```

This is **aliasing**, and it is the single most common source of "impossible" bugs for people new
to Python. Nothing is wrong with the code above; it does exactly what it says. The problem is
that `b = a` reads like a copy and is not one.

`is` tells you the truth (Day 7): `b is a` is `True`.

**Four ways to actually copy:**

```python
b = a.copy()        # clearest
b = a[:]            # idiomatic, older
b = list(a)         # also works, and converts other iterables
import copy; b = copy.deepcopy(a)     # for NESTED lists — see below
```

The first three are **shallow**: they copy the outer list, and the items inside are still shared.
For a flat list of numbers or strings that is completely fine. For a list of lists it is a trap:

```python
grid = [[0, 0], [0, 0]]
shallow = grid.copy()
shallow[0][0] = 9
print(grid)         # [[9, 0], [0, 0]]   ← the inner lists were shared
```

Use `copy.deepcopy()` when the nesting matters. Day 28 goes further.

And the related trap, which is worth committing to memory today:

```python
grid = [[0] * 3] * 3        # WRONG — three references to ONE row
grid[0][0] = 9              # changes every row
grid = [[0] * 3 for _ in range(3)]   # right (Day 22)
```

### 4. Never mutate what you are iterating

From Day 13, now with teeth:

```python
for task in tasks:
    if task.done:
        tasks.remove(task)      # skips items, silently
```

Build a new list instead — which is tomorrow's comprehension — or iterate over a copy
(`for task in tasks[:]`).

### 5. Lists vs. what comes next

- **Fast:** indexing, appending to the end, iterating.
- **Slow:** `in` and `.index()` on a big list (they scan), and inserting or deleting near the
  front (everything after it shifts).

If you find yourself writing `if x in big_list` inside a loop, that is a nested loop in disguise,
and Day 26's `set` makes it instant. Day 29 measures all of this properly.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Every method, the `None` returns, aliasing shown with `is`, shallow vs deep, and the `[[0]*3]*3` trap. |
| `build.py`  | The to-do list: add, complete, reorder, delete, undo — with the aliasing bug demonstrated and fixed. |

```bash
python3 lesson.py
python3 build.py
printf 'add buy milk\nadd write day 21\ndone 1\nlist\nquit\n' | python3 build.py
```

---

## Common mistakes

**`tasks = tasks.append(x)`** — `tasks` is now `None`.

**`b = a` believing it copies.** It aliases. Use `.copy()`.

**`.copy()` on a nested list.** Shallow. Inner lists are shared.

**`[[0] * 3] * 3`** — one row, three times.

**`append` where you meant `extend`.** A list inside your list.

**Removing while iterating.** Silently skips.

**`.remove()` on an absent value.** `ValueError`. Check with `in` first.

**`.index()` on a huge list in a loop.** O(n) each time.

---

## Exercises

1. Show with `is` that `b = a` aliases and `b = a[:]` does not.
2. Write a function-free "swap two items" and "move item to front" using slicing and `pop`.
3. Build `[[0]*3]*3`, change one cell, and print it. Then build it correctly.
4. Remove every even number from a list — first the buggy way, then two correct ways.
5. Shallow-copy a list of lists, change an inner value, and prove the original changed. Then fix
   it with `deepcopy`.
6. Implement a stack (`append`/`pop`) and a queue (`append`/`pop(0)`). Time the queue at 100,000
   items and look up `collections.deque`.

---

## Checklist

- [ ] I know which list methods return `None`
- [ ] I can explain aliasing and prove it with `is`
- [ ] I know the difference between shallow and deep copying
- [ ] I never write `[[x] * n] * m`
- [ ] I never remove from a list while iterating it
- [ ] My to-do list survives every command in any order without crashing
