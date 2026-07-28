# Day 028 — Nested data

**Phase 3 · Data structures** · ~80 minutes

> **Today's build:** read a deeply nested config structure and answer five questions about it without crashing.

**Concepts:** dicts of lists of dicts · safe traversal · flattening · shape-first thinking

---

## The article

### Why this day exists

Everything that arrives from outside your program is nested: JSON from an API (Day 66), a config
file (Day 55), a scraped page (Day 67), a database result. It arrives shaped like a tree, and it
arrives *with holes in it* — optional fields, empty lists, nulls, and occasionally a string where
you expected a list.

Today is about not crashing on any of that, and about a habit — **look at the shape before you
write the traversal** — which sounds too obvious to state and which almost nobody does.

### 1. Shape-first thinking

Before writing any code that touches nested data, be able to say its shape out loud:

> "A dict whose keys are region names, whose values are dicts with `manager` (a string) and
> `stores` (a list of dicts, each with `name`, `staff` and an optional `hours`)."

If you cannot say it, you cannot traverse it, and you will find out one `TypeError` at a time.

Three tools for finding out:

```python
type(data)                  # dict? list?
list(data.keys())           # what fields
data[0] if data else None   # one sample element
import json; print(json.dumps(data, indent=2)[:2000])   # look at it
```

`json.dumps(..., indent=2)` is the fastest way to make a nested structure legible, and it works
on any dict/list/str/number tree. Use it constantly.

### 2. The access ladder

Four levels, in increasing order of tolerance:

```python
d["a"]["b"]["c"]                          # 1. raises on any missing key
d.get("a", {}).get("b", {}).get("c")      # 2. never raises, returns None
d.get("a", {}).get("b", {}).get("c", 0)   # 3. with your own default
```

Level 2 is the chained-default idiom, and the trick is that **the default is the same type as the
thing you would have got** — an empty dict for a dict, so the next `.get()` still works.

It has two limits:
- **Lists.** `.get()` does not exist on a list. `d["items"][0]` needs an index check.
- **Wrong types.** If `d["a"]` is a *string*, `.get()` raises `AttributeError`, not `KeyError`.

For anything past two or three levels, write a helper — level 4:

```python
def dig(data, *keys, default=None):
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, ...)
        elif isinstance(data, list) and isinstance(key, int) and -len(data) <= key < len(data):
            data = data[key]
        else:
            return default
    return data

dig(config, "regions", "north", "stores", 0, "name", default="-")
```

Twelve lines, written once, and every traversal in the program becomes readable and unable to
crash. This is worth having in your Day 40 toolkit.

### 3. `try/except` is the other answer

Day 51 covers it properly, but the shape is worth knowing now:

```python
try:
    name = data["regions"]["north"]["stores"][0]["name"]
except (KeyError, IndexError, TypeError):
    name = "-"
```

The trade: `.get()` chains say what happens *inline*, `try/except` keeps the happy path clean and
catches every failure mode including the type errors. For one deep access, `try` is often
clearer. For a dozen, a `dig()` helper wins.

### 4. Iterating nested data

The natural shape is a nested `for`, and the discipline is to guard each level:

```python
for region, info in config.get("regions", {}).items():
    for store in info.get("stores", []):
        for member in store.get("staff", []):
            ...
```

Every default is *the empty version of the thing that should be there*, so a missing key simply
means zero iterations rather than an exception. That is the single most useful habit on this
page.

**Flattening** turns a tree into a flat list of rows, and it is usually the right move before
analysis, because flat data is what sorting, counting and (on Day 73) pandas all want:

```python
rows = [
    {"region": region, "store": store["name"], "staff": len(store.get("staff", []))}
    for region, info in config.get("regions", {}).items()
    for store in info.get("stores", [])
]
```

### 5. Depth is a smell

Two levels of nesting is comfortable. Three is tolerable. Four means you are modelling something
that wants to be a class (Day 41), or a flat list of records with keys, or a database (Day 78).

The signal: when your code is full of `["a"]["b"]["c"]["d"]`, the *structure* has become the
problem rather than the data.

### 6. Copying nested data

Day 21's warning, now with real consequences:

```python
config.copy()            # SHALLOW — inner dicts and lists are shared
copy.deepcopy(config)    # a genuinely independent tree
```

Modifying a "copy" of a nested config and finding the original changed is a bug that costs an
afternoon. If you are going to mutate, `deepcopy` first — it is slow, and correctness comes
first.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Shape inspection, the access ladder, `dig()`, guarded iteration, flattening, deep copy. |
| `build.py`  | A deliberately hostile config, five questions answered, and every failure mode survived. |

```bash
python3 lesson.py
python3 build.py
```

---

## Common mistakes

**`KeyError` three levels down.** Chain `.get()` with typed defaults, or use `dig()`.

**`.get()` on a list.** Lists have no `.get()`.

**`AttributeError: 'str' object has no attribute 'get'`** — the value was not the type you
assumed. `.get()` chains do not protect against this; `try/except TypeError` does.

**`.get("items")` returning `None`, then iterating it.** Default to `[]`, not `None`.

**Assuming a list is non-empty.** `data["items"][0]` on `[]` is `IndexError`.

**Shallow-copying a config and mutating it.**

**Four levels of nesting.** Reshape the data.

---

## Exercises

1. Print an unknown structure with `json.dumps(..., indent=2)` and write its shape in one
   sentence before touching it.
2. Write `dig()` and use it for five accesses of varying depth, including through a list index.
3. Take a working traversal and delete a key from the data. Fix it so it returns a default.
4. Flatten a three-level structure into rows and sort them (Day 27).
5. Shallow-copy a nested config, mutate the copy, and prove the original changed.
6. Write a recursive function that finds every value for a given key at any depth. (Recursion is
   Day 36 — try it anyway.)

---

## Checklist

- [ ] I look at the shape before writing the traversal
- [ ] My `.get()` defaults are the empty version of the right type
- [ ] I know `.get()` chains do not protect against wrong types
- [ ] I have a `dig()` helper for deep access
- [ ] I flatten before analysing
- [ ] My config reader survives every missing, empty and wrong-typed field
