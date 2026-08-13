"""Day 062 — Regular expressions, and the four traps.

    python3 lesson.py

Every match, count and timing below is computed by running the pattern.
"""

from __future__ import annotations

import re
import time

WIDTH = 76

# ---------------------------------------------------------------------------
# 1. Raw strings, and why every pattern starts with r
# ---------------------------------------------------------------------------

print("=" * WIDTH)
TITLE_1 = '1. ALWAYS r""'
print(f"{TITLE_1:^{WIDTH}}")
print("=" * WIDTH)

BACKSLASH = chr(92)
SEEN_D = repr(BACKSLASH + "d")          # what "\d" becomes
SEEN_N = repr(chr(10))                  # what "\n" becomes
SEEN_B = repr(BACKSLASH + "b")          # what "\\b" and r"\b" become

print(rf"""
  A backslash means something to Python AND something to the regex engine,
  so a pattern written without r"" is escaped twice:

      "\d"      Python keeps it as   {SEEN_D}   (no such escape, so it survives)
      "\n"      Python turns it into {SEEN_N}   a NEWLINE — the engine never sees \n
      "\\b"     Python turns it into {SEEN_B}  which the regex reads as a boundary
      r"\b"     Python keeps it as   {SEEN_B}  the same thing, written once

  r"" turns off Python's escape processing, so what you type is what the
  engine gets. Write every pattern as a raw string, without deciding each
  time whether this one needs it.""")



# ---------------------------------------------------------------------------
# 2. The pieces
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. THE WHOLE SYNTAX, ON ONE SCREEN':^{WIDTH}}")
print("=" * WIDTH)
print(r"""
  MATCH ONE CHARACTER            QUANTIFY THE THING BEFORE
  .      any except newline      *      0 or more
  \d     a digit                 +      1 or more
  \w     letter, digit or _      ?      0 or 1
  \s     whitespace              {3}    exactly 3
  \D \W \S   the opposites       {2,4}  2 to 4
  [aeiou]    one of these        {2,}   2 or more
  [^aeiou]   NOT one of these    *? +? ??   the LAZY versions

  ANCHOR                         GROUP
  ^      start of string         (...)      capture
  $      end of string           (?:...)    group without capturing
  \b     word boundary           (?P<n>...) capture, by name
  \A \Z  start/end, always       a|b        either

  THE FUNCTIONS
  re.search(p, s)      the first match anywhere, or None
  re.match(p, s)       a match at the START only  (rarely what you want)
  re.fullmatch(p, s)   the WHOLE string must match  (for validation)
  re.findall(p, s)     every match, as a list of strings or tuples
  re.finditer(p, s)    every match, as Match objects — with positions
  re.sub(p, r, s)      replace
  re.split(p, s)       split on a pattern

  re.compile(p) ONCE, at module level, when the pattern is used in a loop.""")

text = "Ada was born in 1815 and died in 1852, aged 36."

print(f"\n  text = {text!r}\n")
for label, call in [
    ("findall(r'\\d+')", lambda: re.findall(r"\d+", text)),
    ("findall(r'\\d{4}')", lambda: re.findall(r"\d{4}", text)),
    ("search(r'born in (\\d+)')",
     lambda: re.search(r"born in (\d+)", text).group(1)),
    ("match(r'Ada')", lambda: bool(re.match(r"Ada", text))),
    ("match(r'born')", lambda: bool(re.match(r"born", text))),
    ("fullmatch(r'.*')", lambda: bool(re.fullmatch(r".*", text))),
    ("sub(r'\\d{4}', 'YYYY')", lambda: re.sub(r"\d{4}", "YYYY", text)[:40]),
]:
    print(f"  {label:<30}{call()}")


# ---------------------------------------------------------------------------
# 3. Greedy and lazy
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. THE FIRST TRAP: * IS GREEDY':^{WIDTH}}")
print("=" * WIDTH)

html = '<b>Ada</b> and <i>Grace</i>'

print(f"\n  text = {html!r}\n")
print(f"  {'PATTERN':<20}{'MATCHES':<44}COUNT")
print("  " + "-" * (WIDTH - 4))
for pattern in (r"<.*>", r"<.*?>", r"<[^>]*>"):
    found = re.findall(pattern, html)
    print(f"  {pattern:<20}{str(found)[:43]:<44}{len(found)}")

print("""
  `.*` TAKES EVERYTHING IT CAN and then backs off until the rest of the
  pattern fits — so `<.*>` matched from the first `<` to the LAST `>`, one
  match covering the whole string.

  `.*?` is lazy: it takes as little as possible. `[^>]*` is better still,
  because it cannot cross a `>` at all — no backtracking, and the
  intention is written down rather than implied.

  PREFER A NEGATED CHARACTER CLASS TO A LAZY QUANTIFIER. It is faster, and
  it says what you mean.""")


# ---------------------------------------------------------------------------
# 4. Groups
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. GROUPS, AND WHAT findall DOES WITH THEM':^{WIDTH}}")
print("=" * WIDTH)

log = "2026-03-18 ERROR api 503\n2026-03-19 WARN worker 200"

print(f"\n  {'PATTERN':<34}findall RETURNS")
print("  " + "-" * (WIDTH - 4))
for pattern in [r"\d{4}-\d{2}-\d{2}",
                r"(\d{4})-(\d{2})-(\d{2})",
                r"(\d{4})-(?:\d{2})-(\d{2})"]:
    print(f"  {pattern:<34}{str(re.findall(pattern, log))[:38]}")

print("""
  NO GROUPS -> a list of whole matches.
  ONE GROUP -> a list of that group.
  TWO OR MORE -> a list of TUPLES, and the whole match is gone.

  That last one surprises people every time. If you want the whole match
  AND the parts, use finditer:""")

pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) +(?P<level>\w+) +(?P<service>\w+) +"
    r"(?P<status>\d{3})")

print()
for match in pattern.finditer(log):
    print(f"  {match.group('date')}  {match['level']:<6}"
          f"{match['service']:<8}{match['status']}   "
          f"at chars {match.start()}-{match.end()}")

print(f"\n  .groupdict()  {pattern.search(log).groupdict()}")
print("""
  NAME YOUR GROUPS as soon as there are more than two. `match["level"]`
  survives somebody inserting a group in the middle; `match.group(2)` does
  not.""")


# ---------------------------------------------------------------------------
# 5. Flags and VERBOSE
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'5. A PATTERN YOU CAN READ IN SIX MONTHS':^{WIDTH}}")
print("=" * WIDTH)

compact = re.compile(r"^(?:\+44|0)\s?7\d{3}\s?\d{6}$")

readable = re.compile(r"""
    ^                  # the whole string, nothing else
    (?: \+44 | 0 )     # international or national prefix
    \s?
    7 \d{3}            # a UK mobile always starts 07
    \s?
    \d{6}
    $
""", re.VERBOSE)

numbers = ["07700900123", "+447700900123", "07700 900123",
           "0770090012", "01234567890", "7700900123"]

print(f"\n  {'NUMBER':<20}{'compact':<12}{'VERBOSE':<12}same?")
print("  " + "-" * (WIDTH - 4))
for number in numbers:
    a, b = bool(compact.fullmatch(number)), bool(readable.fullmatch(number))
    print(f"  {number:<20}{str(a):<12}{str(b):<12}{a == b}")

print("""
  IDENTICAL BEHAVIOUR, and one of them has comments. re.VERBOSE ignores
  whitespace and everything after a # — so a pattern longer than about
  thirty characters should be written this way, always.

  (Inside VERBOSE, a literal space must be written \\  or [ ].)

  THE FLAGS WORTH KNOWING:
      re.IGNORECASE   case-insensitive
      re.MULTILINE    ^ and $ match at every LINE, not just the string
      re.DOTALL       . also matches a newline
      re.VERBOSE      whitespace and comments allowed""")

paragraph = "first line\nsecond line\nthird line"
LABEL = 'findall(r"^' + BACKSLASH + 'w+", text)'
plain = re.findall(r"^\w+", paragraph)
multiline = re.findall(r"^\w+", paragraph, re.MULTILINE)
print(f"\n  {LABEL:<34}{plain}")
print(f"  {'...with re.MULTILINE':<34}{multiline}")


# ---------------------------------------------------------------------------
# 6. Catastrophic backtracking
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. THE PATTERN THAT NEVER FINISHES':^{WIDTH}}")
print("=" * WIDTH)

bad = re.compile(r"^(a+)+$")
good = re.compile(r"^a+$")

print("\n  ^(a+)+$  against 'aaaa...!' — a string that CANNOT match\n")
print(f"  {'LENGTH':>8}{'(a+)+':>14}{'a+':>14}")
print("  " + "-" * (WIDTH - 4))
timings = {}
for length in (14, 18, 22, 24):
    attack = "a" * length + "!"

    started = time.perf_counter()
    bad.fullmatch(attack)
    slow = time.perf_counter() - started

    started = time.perf_counter()
    good.fullmatch(attack)
    fast = time.perf_counter() - started

    timings[length] = slow
    print(f"  {length:>8}{slow:>13.4f}s{fast:>13.6f}s")

# Extrapolate from what was just measured rather than quoting a number.
per_character = (timings[24] / timings[14]) ** (1 / 10)
seconds_at_40 = timings[24] * per_character ** 16

print(f"""
  EACH EXTRA CHARACTER MULTIPLIES THE TIME BY {per_character:.1f}, measured from the
  four rows above. Extrapolating the same curve to a 40-character input
  gives about {seconds_at_40 / 3600:,.0f} hours for ONE call, on a string a user could
  paste into a form.

  THE CAUSE is a quantifier inside a quantifier — (a+)+ — which gives the
  engine exponentially many ways to divide the same string, and it tries
  all of them before admitting defeat. Python's re is a BACKTRACKING
  engine, so it has no protection against this.

  THIS IS A DENIAL-OF-SERVICE BUG (it has a name: ReDoS) whenever the text
  comes from a user. The usual culprits are (\\s*)+ , (\\w+\\s?)+ and
  (.*),* in a validator somebody wrote for an email address.

  HOW TO AVOID IT:
    * no quantifier directly inside a quantifier
    * prefer [^x]* to .*?  — it cannot backtrack past x
    * make alternatives mutually exclusive: (?:cat|car) not (?:ca[tr]|c.*)
    * test your pattern against a long non-matching string before shipping""")


# ---------------------------------------------------------------------------
# 7. When not to
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'7. THE THINGS A REGEX MUST NOT PARSE':^{WIDTH}}")
print("=" * WIDTH)

nested = '<div class="a"><p>text</p></div>'
print(f"\n  HTML:  {nested}")
print(f"  r'<div>(.*)</div>' finds "
      f"{re.findall(r'<div[^>]*>(.*)</div>', nested)}")
print("""    ...which works until an element nests inside itself, at which
    point it cannot, because HTML is not a regular language. Day 67 uses
    BeautifulSoup, which is a parser.

  CSV        a quoted field can contain a comma AND a newline. Day 54.
  JSON       nested to arbitrary depth. Day 55.
  EMAIL      the RFC 5322 grammar allows comments, quoted strings and
             nested parentheses. The "official" regex is 6,000+ characters
             and still does not tell you whether the address exists.

  THE TEST: if the thing can nest inside itself, a regex cannot parse it.
  Not "should not" — cannot, as a matter of formal language theory.

  WHAT REGEX IS EXCELLENT AT: finding and extracting SHAPED TEXT out of
  unstructured noise, which is exactly today's build.""")


# ---------------------------------------------------------------------------
# 8. Validate loosely, then check
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'8. THE PATTERN IS THE FIRST HALF OF THE JOB':^{WIDTH}}")
print("=" * WIDTH)

loose_ip = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
candidates = ["10.0.0.1", "192.168.1.255", "999.999.999.999",
              "256.1.1.1", "1.2.3.4.5", "0.0.0.0"]

print(f"\n  {'CANDIDATE':<22}{'regex says':<14}{'valid?':<10}WHY")
print("  " + "-" * (WIDTH - 4))
for candidate in candidates:
    matched = bool(loose_ip.fullmatch(candidate))
    octets = candidate.split(".")
    valid = len(octets) == 4 and all(
        part.isdigit() and int(part) <= 255 for part in octets)
    why = "" if matched == valid else "the regex is WRONG here"
    print(f"  {candidate:<22}{str(matched):<14}{str(valid):<10}{why}")

print("""
  A REGEX THAT MATCHES 999.999.999.999 IS NOT AN IP ADDRESS PATTERN. You
  can express the 0-255 rule in a regex —

      (?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)

  — four times, and the result is unreadable and easy to get subtly wrong.

  THE BETTER SHAPE, and it is today's build's whole design:

      MATCH LOOSELY with a simple pattern, then CHECK in Python.

  int(part) <= 255 is obvious, testable and impossible to misread. Use the
  regex to FIND candidates; use code to decide whether they are valid.""")

print()
print("=" * WIDTH)
print(r"""  1. Every pattern is a raw string.
  2. findall with 2+ groups returns tuples. Use finditer when you need
     both the match and its parts.
  3. Name your groups.
  4. * is greedy; prefer [^x]* to .*? .
  5. re.VERBOSE for anything longer than a line.
  6. A quantifier inside a quantifier is a denial-of-service bug.
  7. If it nests, a regex cannot parse it.
  8. Match loosely, then check in Python.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Run ^(a+)+$ against 30 a's and a '!'. Then make it 35 and wait.
#   * findall with one group, then add a second, and watch the return type
#     change under you.
#   * Write a pattern for a date, then feed it 2026-13-45. Add the check.
#   * Rewrite your longest pattern with re.VERBOSE and comments.
#   * Try to match balanced parentheses with a regex. Then read about the
#     pumping lemma and stop.
