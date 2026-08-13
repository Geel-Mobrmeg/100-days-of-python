"""Day 062 build — pulling structure out of an unstructured dump.

    python3 build.py                 # the demonstration
    python3 build.py somefile.txt    # your own text

THE INPUT is what a support ticket, an incident channel or a pasted log
actually looks like: prose, half-formatted logs, an HTML fragment, three
date formats, addresses in angle brackets, and a few things that look like
data and are not.

THE DESIGN, and it is the whole day:

    MATCH LOOSELY WITH A SIMPLE PATTERN, THEN CHECK IN PYTHON.

An IP regex that enforces 0-255 is four repetitions of
(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d) and nobody can read it. A simple
pattern plus `int(part) <= 255` is obvious, testable, and catches more.

Every pattern below is re.VERBOSE, compiled once, and has a matching set
of NEGATIVE examples at the bottom — because a pattern is only as good as
the things it refuses.
"""

from __future__ import annotations

import csv
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

WIDTH = 78

# ###########################################################################
# THE DUMP
# ###########################################################################

DUMP = r"""
INCIDENT 4417 — checkout timeouts
Opened 2026-03-18 09:12 UTC by ada.lovelace@example.com

09:12  First report from a customer (grace.hopper+billing@example.co.uk).
       Order ref AB-1024. They saw a 503 at 09:07.
09:14  10.0.4.17 is refusing connections. 10.0.4.18 is fine.
09:16  Paged alan@example.com and the on-call number 07700 900123.
09:18  Load balancer 192.168.1.1 shows 4 of 6 backends down:
         10.0.4.17  DOWN   since 09:07:41
         10.0.4.19  DOWN   since 09:07:44
         10.0.4.21  DOWN   since 09:08:02
         10.0.4.23  DOWN   since 09:08:09
09:22  Rolled back the 18/03/2026 deploy (build 4417, commit 9f3a2b1).
       Release notes: https://intranet.example.com/releases/2026-03-18
09:31  Recovered. Confirmed by ada.lovelace@example.com at 09:33.

Post-incident
  - The change landed on March 18, 2026 and was not soak-tested.
  - Version 2.31.0 raised the connection pool from 8 to 64.
  - Follow-up ticket: https://tickets.example.com/T-8891?owner=hopper
  - Contact for the vendor: <support@vendor.example>, +44 20 7946 0958.
  - Their status page said 999.999.999.999 was blocked, which is not an
    address; the CIDR 10.0.4.0/24 is.
  - Costs so far: £12,400.50 (est.), 1,299 orders affected.
  - <a href="mailto:legal@example.com">legal@example.com</a>
  - not.an.email@ and @also.not and plain-old-text
  - Version 3.4 of the runbook is at /srv/docs/runbook.md
  - Retry after 2026-13-45 (a typo in the ticket) — should be 2026-03-20.
"""


# ###########################################################################
# THE PATTERNS — loose, readable, and each with a checker
# ###########################################################################

EMAIL = re.compile(r"""
    (?<![\w.+-])            # not in the middle of a longer token
    [\w.+-]+                # local part: letters, digits, . + - _
    @
    [\w-]+                  # domain label
    (?: \. [\w-]+ )+        # at least one dot and another label
    (?![\w.-])              # and stop cleanly
""", re.VERBOSE)

IPV4 = re.compile(r"""
    (?<![\d.])              # not part of a longer number or a version
    \d{1,3} (?: \. \d{1,3} ){3}
    (?![\d.])
""", re.VERBOSE)

ISO_DATE = re.compile(r"""
    (?<!\d)
    (?P<year>\d{4}) - (?P<month>\d{2}) - (?P<day>\d{2})
    (?!\d)
""", re.VERBOSE)

SLASH_DATE = re.compile(r"""
    (?<!\d)
    (?P<first>\d{1,2}) / (?P<second>\d{1,2}) / (?P<year>\d{4})
    (?!\d)
""", re.VERBOSE)

WORD_DATE = re.compile(r"""
    (?P<month>January|February|March|April|May|June|July|
              August|September|October|November|December)
    \s+ (?P<day>\d{1,2}) ,? \s+ (?P<year>\d{4})
""", re.VERBOSE)

URL = re.compile(r"""
    https? :// [\w.-]+      # scheme and host — no lazy quantifier
    (?: / [^\s<>"']* )?     # path: anything that is not whitespace or a
                            # quote. [^...]* cannot backtrack past them.
""", re.VERBOSE)

UK_PHONE = re.compile(r"""
    (?<![\d+])
    (?: \+44 \s? | 0 )      # international or national prefix
    (?: \d \s? ){9,10}      # nine or ten more digits, spaces allowed
    (?![\d])
""", re.VERBOSE)

MONTHS = {name: number for number, name in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


# ###########################################################################
# THE CHECKERS — the half a regex should not do
# ###########################################################################

def valid_ip(text: str) -> bool:
    """0-255 in four octets, and no leading zeros.

    Writing this in the pattern is possible and unreadable. Writing it here
    is four lines that anybody can check by reading.
    """
    parts = text.split(".")
    return len(parts) == 4 and all(
        part.isdigit() and (part == "0" or not part.startswith("0"))
        and int(part) <= 255
        for part in parts
    )


def valid_date(year: int, month: int, day: int) -> date | None:
    """The calendar decides, not the pattern. Day 61."""
    try:
        return date(year, month, day)
    except ValueError:
        return None


def valid_email(text: str) -> bool:
    """The rules a pattern cannot sensibly hold.

    NOT an RFC 5322 implementation — nothing short of a parser is, and
    even that cannot tell you the address exists. These are the checks
    that catch real typos.
    """
    local, _, domain = text.rpartition("@")
    return bool(
        local and domain
        and ".." not in text
        and not local.startswith(".") and not local.endswith(".")
        and "." in domain
        and not domain.startswith("-") and not domain.endswith("-")
        and len(text) <= 254
        and len(local) <= 64
    )


# ###########################################################################
# EXTRACTION
# ###########################################################################

@dataclass(frozen=True, slots=True, order=True)
class Finding:
    kind: str
    value: str
    line: int
    context: str

    def as_row(self) -> dict[str, str]:
        return {"kind": self.kind, "value": self.value,
                "line": str(self.line), "context": self.context}


@dataclass(frozen=True, slots=True)
class Rejected:
    kind: str
    text: str
    line: int
    why: str


def line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def context_of(text: str, start: int, end: int, width: int = 30) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    line = text[line_start:line_end if line_end != -1 else len(text)].strip()
    return line[:width]


def extract(text: str) -> tuple[list[Finding], list[Rejected]]:
    """Find everything, check everything, and record both outcomes."""
    findings: list[Finding] = []
    rejected: list[Rejected] = []

    def record(kind: str, value: str, match: re.Match[str]) -> None:
        findings.append(Finding(kind, value, line_of(text, match.start()),
                                context_of(text, match.start(), match.end())))

    def refuse(kind: str, match: re.Match[str], why: str) -> None:
        rejected.append(Rejected(kind, match.group(0),
                                 line_of(text, match.start()), why))

    for match in EMAIL.finditer(text):
        address = match.group(0).rstrip(".,;:)")
        if valid_email(address):
            record("email", address.lower(), match)
        else:
            refuse("email", match, "fails the shape checks")

    for match in IPV4.finditer(text):
        if valid_ip(match.group(0)):
            record("ipv4", match.group(0), match)
        else:
            refuse("ipv4", match, "an octet is above 255 or zero-padded")

    for match in ISO_DATE.finditer(text):
        found = valid_date(int(match["year"]), int(match["month"]),
                           int(match["day"]))
        if found:
            record("date", found.isoformat(), match)
        else:
            refuse("date", match, "no such day in the calendar")

    for match in SLASH_DATE.finditer(text):
        # AMBIGUOUS BY CONSTRUCTION. 18/03 can only be day-first, but
        # 01/02 cannot be resolved at all — so this records what it
        # assumed instead of pretending it knew (Day 60's rule).
        first, second = int(match["first"]), int(match["second"])
        found = valid_date(int(match["year"]), second, first)
        if found and first > 12:
            record("date", found.isoformat(), match)
        elif found:
            refuse("date", match, "ambiguous: could be month-first")
        else:
            refuse("date", match, "no such day in the calendar")

    for match in WORD_DATE.finditer(text):
        found = valid_date(int(match["year"]), MONTHS[match["month"]],
                           int(match["day"]))
        if found:
            record("date", found.isoformat(), match)
        else:
            refuse("date", match, "no such day in the calendar")

    for match in URL.finditer(text):
        record("url", match.group(0).rstrip(".,;:)"), match)

    for match in UK_PHONE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) in (11, 12):
            record("phone", digits, match)
        else:
            refuse("phone", match, f"{len(digits)} digits, expected 11 or 12")

    findings.sort()
    return findings, rejected


# ###########################################################################
# RUN IT
# ###########################################################################

if len(sys.argv) > 1:
    TEXT = Path(sys.argv[1]).read_text(encoding="utf-8")
    SOURCE = sys.argv[1]
else:
    TEXT = DUMP
    SOURCE = "the built-in incident report"

findings, rejected = extract(TEXT)
counts = Counter(finding.kind for finding in findings)

print("=" * WIDTH)
print(f"{'WHAT WAS IN THE TEXT':^{WIDTH}}")
print("=" * WIDTH)
print(f"  {'source':<20}{SOURCE}")
print(f"  {'characters':<20}{len(TEXT):,}")
print(f"  {'lines':<20}{TEXT.count(chr(10)) + 1}")
print(f"  {'found':<20}{len(findings)}")
print(f"  {'refused':<20}{len(rejected)}")

print(f"\n  {'KIND':<10}{'VALUE':<40}{'LINE':>6}   CONTEXT")
print("  " + "-" * (WIDTH - 4))
seen: set[tuple[str, str]] = set()
for finding in findings:
    if (finding.kind, finding.value) in seen:
        continue
    seen.add((finding.kind, finding.value))
    print(f"  {finding.kind:<10}{finding.value[:39]:<40}{finding.line:>6}   "
          f"{finding.context[:24]}")

print("  " + "-" * (WIDTH - 4))
print(f"  {len(seen)} distinct values, {len(findings)} occurrences: "
      + ", ".join(f"{count} {kind}" for kind, count in counts.most_common()))


# ###########################################################################
# WHAT IT REFUSED — the more interesting half
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'WHAT THE PATTERN FOUND AND THE CHECK REJECTED':^{WIDTH}}")
print("=" * WIDTH)

print(f"\n  {'KIND':<10}{'TEXT':<26}{'LINE':>6}   WHY")
print("  " + "-" * (WIDTH - 4))
for item in sorted(rejected, key=lambda r: (r.kind, r.line)):
    print(f"  {item.kind:<10}{item.text[:25]:<26}{item.line:>6}   {item.why}")

print("""
  EVERY ONE OF THOSE WAS MATCHED BY THE PATTERN. A regex that enforced the
  rules itself would have SKIPPED them silently, and nobody would know
  that 999.999.999.999 was in the ticket at all — which is exactly the
  thing an incident report should tell you.

  MATCHING LOOSELY AND CHECKING SEPARATELY GIVES YOU A THIRD OUTCOME:
  found-and-rejected, with a reason. A stricter pattern has only two.""")


# ###########################################################################
# THE NEGATIVE TESTS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'A PATTERN IS ONLY AS GOOD AS WHAT IT REFUSES':^{WIDTH}}")
print("=" * WIDTH)

email_cases = [
    ("ada@example.com", True), ("a.b+c@sub.example.co.uk", True),
    ("x@y.zz", True),
    ("not.an.email@", False), ("@also.not", False), ("plain-old-text", False),
    ("two@@ats.com", False), ("no.tld@example", False),
    ("trailing.dot.@example.com", False), ("a..b@example.com", False),
]

ip_cases = [
    ("10.0.4.17", True), ("192.168.1.1", True), ("0.0.0.0", True),
    ("255.255.255.255", True),
    ("999.999.999.999", False), ("256.1.1.1", False), ("1.2.3", False),
    ("1.2.3.4.5", False), ("010.1.1.1", False), ("2.31.0", False),
]

print(f"\n  {'INPUT':<30}{'EXPECTED':<12}{'GOT':<12}")
print("  " + "-" * (WIDTH - 4))
failures = 0
for text, expected in email_cases:
    match = EMAIL.fullmatch(text)
    got = bool(match) and valid_email(text)
    failures += got != expected
    flag = "" if got == expected else "   <- WRONG"
    print(f"  {text:<30}{str(expected):<12}{str(got):<12}{flag}")
print("  " + "-" * (WIDTH - 4))
for text, expected in ip_cases:
    match = IPV4.fullmatch(text)
    got = bool(match) and valid_ip(text)
    failures += got != expected
    flag = "" if got == expected else "   <- WRONG"
    print(f"  {text:<30}{str(expected):<12}{str(got):<12}{flag}")

print(f"""
  {len(email_cases) + len(ip_cases)} cases, {failures} disagreements.

  NOTE `2.31.0` AND `1.2.3`. A version number is three dot-separated
  numbers and an IP address is four, so the pattern's `{{3}}` and its
  lookarounds are doing real work — without the (?<![\\d.]) the address
  finder would happily pull `2.31.0` out of "Version 2.31.0" as if the
  leading digits of something else were an octet.

  LOOKAROUNDS ARE HOW YOU SAY "NOT IN THE MIDDLE OF SOMETHING ELSE", and
  they are the difference between a pattern that works on your three
  examples and one that works on a page of prose.""")


# ###########################################################################
# THE REPORT
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE REPORT':^{WIDTH}}")
print("=" * WIDTH)

output = Path("findings.csv")
with open(output, "w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["kind", "value", "line",
                                                "context"])
    writer.writeheader()
    writer.writerows(finding.as_row() for finding in findings)

print(f"\n  wrote {output} — {output.stat().st_size:,} bytes, "
      f"{len(findings)} rows")
with open(output, encoding="utf-8", newline="") as handle:
    for index, line in enumerate(handle):
        if index > 4:
            print("    ...")
            break
        print(f"    {line.rstrip()[:WIDTH - 6]}")
output.unlink()


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

emails = {f.value for f in findings if f.kind == "email"}
ips = {f.value for f in findings if f.kind == "ipv4"}
dates = {f.value for f in findings if f.kind == "date"}
urls = {f.value for f in findings if f.kind == "url"}
phones = {f.value for f in findings if f.kind == "phone"}

started = time.perf_counter()
for pattern in (EMAIL, IPV4, URL, UK_PHONE, ISO_DATE):
    pattern.findall("x" * 4000 + " " + "a" * 4000 + "!")
hostile_time = time.perf_counter() - started

claims = [
    ("every negative example is refused", failures == 0),
    ("the ordinary addresses are found",
     {"ada.lovelace@example.com", "alan@example.com",
      "support@vendor.example"} <= emails),
    ("...including one with a + tag",
     "grace.hopper+billing@example.co.uk" in emails),
    ("...and one inside an HTML attribute", "legal@example.com" in emails),
    ("the three broken addresses are NOT found",
     not any(bad in emails for bad in ("not.an.email@", "@also.not",
                                       "plain-old-text"))),
    ("the five distinct real addresses are found, and only those",
     emails == {"ada.lovelace@example.com", "alan@example.com",
                "grace.hopper+billing@example.co.uk",
                "legal@example.com", "support@vendor.example"}),
    ("the private addresses are found",
     {"10.0.4.17", "10.0.4.19", "192.168.1.1"} <= ips),
    ("999.999.999.999 is refused, not silently skipped",
     "999.999.999.999" not in ips
     and any("999" in r.text for r in rejected)),
    ("a version number is not read as an address",
     not any(candidate in ips for candidate in ("2.31.0", "3.4", "1.2.3"))),
    ("the CIDR's network address is still found", "10.0.4.0" in ips),
    ("all three date formats are recognised",
     {"2026-03-18", "2026-03-20"} <= dates),
    ("...including 'March 18, 2026'",
     any(f.value == "2026-03-18" and "March" in f.context
         for f in findings)),
    ("2026-13-45 is refused by the calendar, not the pattern",
     "2026-13-45" not in dates
     and any("13-45" in r.text for r in rejected)),
    ("18/03/2026 resolves, because 18 cannot be a month",
     "2026-03-18" in dates),
    ("both URLs are found, without the trailing full stop",
     len(urls) == 2 and not any(u.endswith(".") for u in urls)),
    ("...and a query string survives",
     any("?owner=hopper" in u for u in urls)),
    ("both phone numbers are found", len(phones) == 2),
    ("every finding carries a line number",
     all(f.line > 0 for f in findings)),
    ("every pattern is compiled once, at module level",
     all(isinstance(p, re.Pattern)
         for p in (EMAIL, IPV4, ISO_DATE, SLASH_DATE, WORD_DATE, URL,
                   UK_PHONE))),
    ("every pattern is VERBOSE and therefore commentable",
     all(p.flags & re.VERBOSE
         for p in (EMAIL, IPV4, ISO_DATE, SLASH_DATE, WORD_DATE, URL,
                   UK_PHONE))),
    ("no pattern backtracks catastrophically on 8,000 hostile characters",
     hostile_time < 1.0),
]

print()
for label, ok in claims:
    print(f"  {'PASS' if ok else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(ok for _, ok in claims)} of {len(claims)} checks pass")

print(f"""
  THE LAST ONE IS THE ONE PEOPLE FORGET. All five patterns were run
  against 8,000 characters that cannot match, and finished in
  {hostile_time * 1000:.1f} ms. Yesterday's ^(a+)+$ takes fifteen hours on forty
  characters.

  If a pattern of yours will ever see text from a user, run it against a
  long non-matching string before you ship it. It takes ten seconds and it
  is the difference between a regex and an outage.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Remove the (?<![\d.]) from IPV4 and re-run. "Version 2.31.0" starts
#     producing addresses, and one check goes red.
#
#   * Add a pattern for the order references (AB-1024) and the commit
#     hashes. The commit one is interesting: how do you tell a 7-character
#     hex string from an ordinary word?
#
#   * Make SLASH_DATE accept a `day_first=True` argument instead of
#     refusing the ambiguous ones. Then decide which behaviour you would
#     want in a tool your finance team uses.
#
#   * Replace valid_email() with the 6,000-character RFC 5322 regex you can
#     find online. Time it on the dump, then decide.
#
#   * Feed it a file of your own. Every real dump has something in it that
#     one of these patterns gets wrong — find it, and add the negative
#     example.
