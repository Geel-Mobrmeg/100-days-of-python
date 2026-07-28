# Day 025 — Counting and grouping

**Phase 3 · Data structures** · ~80 minutes

> **Today's build:** a word frequency analyser that reports the top twenty words in any text file.

**Concepts:** dict comprehensions · `collections.Counter` · `defaultdict` · inverting a dict

---

## The article

### Why this day exists

Counting things and grouping things are, between them, most of what data processing actually is.
"How many of each?" and "which ones belong together?" are the two questions behind every report,
every log analysis and every dashboard you will ever build.

You can do both with a plain dict, and you should write it that way once. Then `collections`
hands you the versions that are shorter, faster and harder to get wrong.

### 1. Counting by hand, three ways

```python
counts = {}
for word in words:
    if word in counts:              # 1. the obvious way
        counts[word] += 1
    else:
        counts[word] = 1

    counts[word] = counts.get(word, 0) + 1        # 2. with .get()
    counts.setdefault(word, 0)                    # 3. with setdefault
    counts[word] += 1
```

All three are correct. The `.get(k, 0) + 1` form is the one to remember, because it is one line
and reads as what it does. And all three exist to work around the same thing: **you cannot `+= 1`
a key that is not there yet.**

### 2. `defaultdict`

```python
from collections import defaultdict

counts = defaultdict(int)
counts[word] += 1              # a missing key becomes int() == 0 first
```

`defaultdict(factory)` calls `factory()` to create a value whenever a **missing key is accessed**.
`int` gives `0`, `list` gives `[]`, `set` gives `set()`.

For grouping, this is the one that matters:

```python
groups = defaultdict(list)
for name in names:
    groups[name[0]].append(name)         # no setdefault, no check
```

One line, and the "does this key exist yet" question disappears entirely.

The catch, and it is a real one: **merely looking at a missing key creates it.**

```python
d = defaultdict(list)
if d["nope"]:          # you just added "nope": [] to the dict
    ...
print(len(d))          # 1
```

Use `d.get(k)` to check without creating, or `k in d`.

### 3. `Counter`

```python
from collections import Counter

counts = Counter(words)               # the entire counting loop
counts.most_common(20)                # top 20 as (word, count) pairs
counts["missing"]                     # 0, not KeyError
```

`Counter` is a dict subclass, so everything you know still works. What it adds:

```python
Counter("hello")                      # counts characters
counts.most_common()                  # all, most frequent first
counts.most_common(3)                 # top 3
counts.total()                        # sum of counts (3.10+)
sum(counts.values())                  # same, works everywhere
counts.update(more_words)             # add more
a + b, a - b, a & b, a | b            # combine counters arithmetically
```

`.most_common()` is what makes it worth importing — sorting a dict by value is fiddly enough
that having it built in is a genuine saving.

Note `counts["missing"]` returns `0` rather than raising, and — unlike `defaultdict` — **does not
insert the key.**

### 4. Grouping

The general shape, with a key function deciding the group:

```python
groups = defaultdict(list)
for item in items:
    groups[key_of(item)].append(item)
```

That is the whole pattern, and it is worth recognising because it is the ancestor of pandas'
`groupby` (Day 75) and SQL's `GROUP BY` (Day 78). The same idea, three sizes.

`itertools.groupby` exists and is **not** this — it only groups *consecutive* equal items, so it
requires sorted input. It surprises everybody once. Use the `defaultdict` version unless you
specifically want runs.

### 5. Inverting

```python
{v: k for k, v in d.items()}
```

**Only safe when the values are unique.** With duplicates, later keys silently overwrite earlier
ones and you lose data with no error. The safe version groups:

```python
inverted = defaultdict(list)
for k, v in d.items():
    inverted[v].append(k)
```

Which is grouping again — inverting a dict *is* grouping by value.

To find the key with the largest value:

```python
max(d, key=d.get)              # one key
max(d.items(), key=lambda kv: kv[1])    # the pair
```

`key=` is Day 27's material and it is the single most useful argument in Python.

### 6. Words are harder than they look

The build has to decide what a "word" is, and every decision is visible in the output:

- **Case** — `The` and `the`. Lowercase first, almost always.
- **Punctuation** — `dog.` and `dog`. Strip it, but `don't` and `well-known` are one word each.
- **Stop words** — the top ten words of any English text are `the, of, and, to, a...`. A frequency
  report that does not exclude them tells you nothing about the text.
- **Numbers** — usually noise, sometimes the point.

There is no universally right answer. There is only *stating what you did*, which the build does
in its output.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Counting four ways, `defaultdict` and its trap, `Counter`, grouping, safe inversion. |
| `build.py`  | The word frequency analyser: tokenising, stop words, top-N, a histogram, and a letter distribution. |

```bash
python3 lesson.py
python3 build.py                 # uses the bundled sample.txt
python3 build.py sample.txt 30
python3 build.py sample.txt 20 --keep-stopwords
```

---

## Common mistakes

**`counts[word] += 1` on a plain dict.** `KeyError`. Use `.get()` or `defaultdict`.

**Reading a missing key on a `defaultdict`.** It creates it. Use `.get()` to peek.

**`itertools.groupby` on unsorted data.** It only groups runs.

**Inverting a dict with duplicate values.** Silent data loss.

**Counting words without lowercasing.** `The` and `the` counted separately.

**Reporting the top 20 without removing stop words.** You get `the, of, and`.

**Sorting a dict and expecting the dict to be sorted.** `sorted()` returns a list of pairs.

---

## Exercises

1. Count characters in a string four ways: manual `if`, `.get()`, `defaultdict`, `Counter`.
2. Group a list of names by first letter, then by length.
3. Show that reading a missing key on a `defaultdict` inserts it.
4. Invert a dict with duplicate values, both ways. Say what the first one lost.
5. Find the most common word in a text without `Counter`, using `max(d, key=d.get)`.
6. Count word *pairs* (bigrams) rather than words. The top bigram of most English text is
   `of the`.

---

## Checklist

- [ ] I can count with a plain dict and know why `+= 1` alone fails
- [ ] I know `defaultdict` creates on read
- [ ] I use `Counter` and `.most_common()` for frequency work
- [ ] I recognise the group-by-key pattern and its relatives in SQL and pandas
- [ ] I know inverting a dict loses data when values repeat
- [ ] My analyser states its tokenising rules in its output
