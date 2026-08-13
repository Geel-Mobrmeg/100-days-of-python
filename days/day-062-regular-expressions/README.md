# Day 062 — Regular expressions

**Phase 7 · The outside world** · ~90 minutes

> **Today's build:** pull every email address, date and IP out of a messy raw text dump into a clean report.

**Concepts:** character classes · quantifiers · groups · `findall` & `sub` · greedy vs. lazy

---

## The article

### Why this day exists

A regex is the shortest path from *unstructured text* to *data you can use*, and it is also the
easiest tool in this course to get subtly, expensively wrong. Today is about both halves.

### 1. Always `r""`

A backslash means something to Python **and** something to the regex engine:

```
"\d"      Python keeps it as   '\\d'   (no such escape, so it survives)
"\n"      Python turns it into '\n'    a NEWLINE — the engine never sees \n
"\\b"     Python turns it into '\\b'   which the regex reads as a boundary
r"\b"     Python keeps it as   '\\b'   the same thing, written once
```

Write every pattern as a raw string without deciding each time whether this one needs it.

### 2. The whole syntax on one screen

```
MATCH ONE CHARACTER            QUANTIFY THE THING BEFORE
.      any except newline      *      0 or more
\d     a digit                 +      1 or more
\w     letter, digit or _      ?      0 or 1
\s     whitespace              {3}    exactly 3
[aeiou]    one of these        {2,4}  2 to 4
[^aeiou]   NOT one of these    *? +?  the LAZY versions

ANCHOR                         GROUP
^  $   start / end             (...)      capture
\b     word boundary           (?:...)    group without capturing
                               (?P<n>...) capture, by name
```

| function | returns |
|---|---|
| `re.search` | the first match anywhere, or `None` |
| `re.match` | a match at the **start** only — rarely what you want |
| `re.fullmatch` | the **whole** string must match — for validation |
| `re.findall` | every match, as strings **or tuples** |
| `re.finditer` | every match, as `Match` objects — with positions |

### 3. `*` is greedy

```
text = '<b>Ada</b> and <i>Grace</i>'

PATTERN             MATCHES                          COUNT
<.*>                ['<b>Ada</b> and <i>Grace</i>']      1
<.*?>               ['<b>', '</b>', '<i>', '</i>']       4
<[^>]*>             ['<b>', '</b>', '<i>', '</i>']       4
```

`.*` takes everything it can and backs off until the rest fits. `.*?` is lazy. `[^>]*` is better than
either: it **cannot cross a `>` at all**, so there is no backtracking, and the intention is written
down rather than implied.

**Prefer a negated character class to a lazy quantifier.**

### 4. `findall` changes its return type under you

| pattern | `findall` returns |
|---|---|
| no groups | a list of whole matches |
| one group | a list of **that group** |
| two or more | a list of **tuples**, and the whole match is gone |

When you want the match *and* the parts, use `finditer` and name your groups:

```python
match["level"]        # survives somebody inserting a group
match.group(2)        # does not
```

### 5. `re.VERBOSE`, for a pattern you can read in six months

```python
readable = re.compile(r"""
    ^                  # the whole string, nothing else
    (?: \+44 | 0 )     # international or national prefix
    \s?
    7 \d{3}            # a UK mobile always starts 07
    \s?
    \d{6}
    $
""", re.VERBOSE)
```

Identical behaviour to the one-line version, and one of them has comments. Anything longer than
about thirty characters should be written this way.

### 6. The pattern that never finishes

```
^(a+)+$  against 'aaaa...!' — a string that CANNOT match

  LENGTH         (a+)+            a+
      14       0.0007s     0.000001s
      18       0.0116s     0.000002s
      22       0.1840s     0.000004s
      24       0.7580s     0.000005s
```

Each extra character **multiplies the time by 2**, measured from those four rows. Extrapolating to a
40-character input gives about **15 hours for one call** — on a string a user could paste into a
form.

The cause is a quantifier inside a quantifier, which gives the engine exponentially many ways to
divide the same string. Python's `re` is a backtracking engine and has no protection against it.
This has a name — **ReDoS** — and it is a denial-of-service bug whenever the text comes from a user.

How to avoid it:

- no quantifier directly inside a quantifier
- prefer `[^x]*` to `.*?`
- make alternatives mutually exclusive: `(?:cat|car)`, not `(?:ca[tr]|c.*)`
- **test against a long non-matching string before you ship**

### 7. The things a regex must not parse

**If it can nest inside itself, a regex cannot parse it.** Not "should not" — cannot, as a matter of
formal language theory. HTML, JSON, and the RFC 5322 email grammar are all in that category. (The
"official" email regex is over 6,000 characters and still cannot tell you the address exists.)

What regex is excellent at is finding **shaped text** in unstructured noise — which is today's build.

### 8. Match loosely, then check

```
CANDIDATE             regex says    valid?    WHY
999.999.999.999       True          False     the regex is WRONG here
```

You *can* express 0–255 in a pattern:

```
(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)
```

…four times, unreadable, and easy to get subtly wrong. The better shape:

> **Match loosely with a simple pattern, then check in Python.**

`int(part) <= 255` is obvious, testable and impossible to misread.

### 9. The build: three outcomes, not two

The dump is what a real incident ticket looks like: prose, half-formatted logs, an HTML fragment,
three date formats, addresses in angle brackets, and things that look like data and are not.

```
KIND      VALUE                                     LINE   CONTEXT
email     grace.hopper+billing@example.co.uk           5   09:12  First report from
email     legal@example.com                           26   - <a href="mailto:legal@
ipv4      10.0.4.17                                    7   09:14  10.0.4.17 is refu
date      2026-03-20                                  29   - Retry after 2026-13-45
url       https://tickets.example.com/T-8891?owne     21   - Follow-up ticket: http
phone     442079460958                                22   - Contact for the vendor
```

And, separately:

```
WHAT THE PATTERN FOUND AND THE CHECK REJECTED
date      2026-13-45                    29   no such day in the calendar
ipv4      999.999.999.999               23   an octet is above 255 or zero-padded
```

Both were **matched by the pattern**. A regex that enforced the rules itself would have skipped them
silently, and nobody would know `999.999.999.999` was in the ticket at all — which is exactly what an
incident report should tell you.

Matching loosely and checking separately gives a **third outcome**: found-and-rejected, with a
reason. A stricter pattern has only two.

### 10. Lookarounds, and why `2.31.0` is not an address

```
INPUT                         EXPECTED    GOT
1.2.3                         False       False
2.31.0                        False       False
010.1.1.1                     False       False
```

A version number is three dot-separated numbers and an IP address is four, so the `{3}` and the
`(?<![\d.])` are doing real work. Without the lookbehind, the finder would pull `2.31.0` out of
"Version 2.31.0" as if the leading digits of something else were an octet.

**Lookarounds are how you say "not in the middle of something else"** — the difference between a
pattern that works on your three examples and one that works on a page of prose.

### 11. And the check people forget

All five patterns are run against 8,000 hostile characters that cannot match. They finish in **0.7 ms**.
Yesterday's `^(a+)+$` takes fifteen hours on forty characters.

If a pattern will ever see text from a user, run it against a long non-matching string before you
ship it. It takes ten seconds.

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Raw strings, the syntax, greedy vs lazy measured, what `findall` does with groups, `re.VERBOSE`, the ReDoS timing table, and the loose-then-check argument. |
| `build.py` | Seven `VERBOSE` patterns, three checkers, 20 negative examples, a CSV report, and 21 checks including a hostile-input timing. |

```bash
python3 lesson.py
python3 build.py                  # the built-in incident report
python3 build.py somefile.txt     # your own text
```

---

## Common mistakes

**A pattern without `r""`.** Escaped twice, and `\b` becomes a backspace.

**`re.match` when you meant `re.search`.** It only looks at the start.

**Adding a second group and wondering why `findall` returns tuples.**

**`.*` where `[^x]*` was meant.** Greedy, and slow.

**A quantifier inside a quantifier.** A denial-of-service bug.

**Parsing HTML, CSV or JSON with a regex.** They nest; it cannot.

**Enforcing value rules in the pattern.** Unreadable, and it hides bad data instead of reporting it.

**No lookarounds.** Your address finder eats version numbers.

**Never testing what the pattern should *refuse*.**

---

## Exercises

1. Run `^(a+)+$` against 30 `a`s and a `!`. Then make it 35.
2. Add a second group to a `findall` and watch the return type change.
3. Write a date pattern, feed it `2026-13-45`, then add the calendar check.
4. Rewrite your longest pattern with `re.VERBOSE` and comments.
5. Write ten **negative** examples for a pattern of yours before writing the pattern.
6. Remove a lookaround from today's IP pattern and see what starts matching.
7. Extract something from a real file of yours — a log, an export, an email — and find the case that
   breaks it.

---

## Checklist

- [ ] Every pattern I write is a raw string
- [ ] I use `finditer` and named groups when I need the parts
- [ ] I prefer `[^x]*` to `.*?`
- [ ] I use `re.VERBOSE` for anything longer than a line
- [ ] I never put a quantifier inside a quantifier
- [ ] I know what a regex cannot parse, and why
- [ ] I match loosely and check in Python
- [ ] I test what my patterns refuse, not only what they accept
- [ ] I time my patterns against long non-matching input
