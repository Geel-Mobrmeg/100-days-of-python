"""Day 009 build — the five bugs, fixed, with what each traceback actually said.

Write your own fixes before reading these. The fix is the easy part; the
skill being trained is reading the traceback well enough to know what to fix.

    python3 build.py
"""

WIDTH = 68


def rule(title):
    """Print a section heading. (Functions are Day 31 — this is just plumbing.)"""
    print()
    print("=" * WIDTH)
    print(title)
    print("=" * WIDTH)


# ===========================================================================
rule("BUG 1 — ValueError: invalid literal for int() with base 10: '3.0'")
# ===========================================================================
#
# WHAT THE TRACEBACK SAID
#   ValueError  = the TYPE was right (a string) but the VALUE was unusable.
#   It even quoted the offending value: '3.0'. Tracebacks name the bad data
#   more often than people expect — read the message to the end.
#
# WHY
#   int() on a STRING demands an integer literal. int("3.0") raises, while
#   int(3.0) truncates happily. That asymmetry is Day 6's material and it is
#   exactly what a CSV export full of floats will hand you.
#
# THE FIX
#   Go via float. int(float("3.0")) is 3, and it still rejects "three".

ORDER_A = "1043,Cairo,2,14.50"
ORDER_B = "1044,Alexandria,3.0,22.00"

FREE_SHIPPING_OVER = 50.00
SHIPPING_FLAT = 4.99

print("order          city          qty     goods  shipping")
print("-" * 56)

for order in (ORDER_A, ORDER_B):
    ref, city, qty_text, price_text = order.split(",")
    qty = int(float(qty_text))
    price = float(price_text)
    goods = qty * price
    ship = SHIPPING_FLAT * (goods < FREE_SHIPPING_OVER)
    print(f"{ref:<15}{city:<14}{qty:>3}{goods:>10.2f}{ship:>10.2f}")

# (The `for` is Day 13. The original repeated these six lines per order,
#  which is how the bug hid in the second copy and not the first.)


# ===========================================================================
rule("BUG 2 — TypeError: can only concatenate str (not 'float') to str")
# ===========================================================================
#
# WHAT THE TRACEBACK SAID
#   TypeError = the type itself was wrong, as opposed to ValueError's "right
#   type, bad value". Python refused to guess what "text plus number" means.
#
# WHY
#   `+` on a str requires a str on both sides. Day 2's strong typing.
#
# THE FIX
#   Not str() — f-strings. str() would work and would still be five noisy
#   calls. The f-string is the reason this class of bug is rare in modern
#   Python: there is nothing to convert.

SUBTOTAL = 26.30
SERVICE = 3.29
VAT = 5.92

total = SUBTOTAL + SERVICE + VAT
items = 7

print(f"Subtotal: {SUBTOTAL:>7.2f}")
print(f"Service:  {SERVICE:>7.2f}")
print(f"VAT:      {VAT:>7.2f}")
print(f"Total:    {total:>7.2f}")
print(f"Items:    {items:>7}")


# ===========================================================================
rule("BUG 3 — IndexError: list index out of range")
# ===========================================================================
#
# WHAT THE TRACEBACK SAID
#   The ^^^ marker sat under `parts_3[1]`, not under the whole line. Python
#   points at the exact subexpression. Use that.
#
# WHY
#   Not malformed data — a person with one name. The code assumed every name
#   has three parts, then two, and "Prince" has one. The assumption was
#   never written down anywhere, which is what made it a bug rather than a
#   documented limitation.
#
# THE FIX
#   Stop indexing fixed positions. first is [0], last is [-1], and the middle
#   is whatever is in between — a slice, which is never out of range.
#   `* (len(parts) > 1)` blanks the surname when first and last would be the
#   same word (Day 7: a bool is an int, so a string times False is "").

CONTACTS = (
    "Ada Augusta Lovelace|ada@example.com",
    "Charles Babbage|charles@example.com",
    "Prince|prince@example.com",
)

print(f"{'FIRST':<12}{'MIDDLE':<12}{'LAST':<12}{'EMAIL':<24}")
print("-" * 60)

for contact in CONTACTS:
    name, email = contact.split("|")
    parts = name.split()
    first = parts[0]
    middle = " ".join(parts[1:-1])
    last = parts[-1] * (len(parts) > 1)
    print(f"{first:<12}{middle:<12}{last:<12}{email:<24}")


# ===========================================================================
rule("BUG 4 — NameError: name 'celcius_reading' is not defined")
# ===========================================================================
#
# WHAT THE TRACEBACK SAID
#   Everything. It named the undefined name AND suggested the one you meant:
#     Did you mean: 'celsius_reading'?
#   Python 3.10+ does this. It is the single easiest bug of the five, and it
#   is still the one people panic at, because they read the first line of the
#   traceback instead of the last.
#
# WHY
#   A typo. celcius / celsius.
#
# THE FIX
#   Spell it correctly — and notice that this is what a linter is for. `ruff`
#   flags an undefined name (F821) without running the program at all.

CITY = "Reykjavik"
celsius_reading = -3.5

fahrenheit = celsius_reading * 9 / 5 + 32
kelvin = celsius_reading + 273.15

print(f"{CITY}")
print(f"  {celsius_reading:>8.1f} C")
print(f"  {fahrenheit:>8.1f} F")
print(f"  {kelvin:>8.1f} K")


# ===========================================================================
rule("BUG 5 — ZeroDivisionError, four lines away from the actual bug")
# ===========================================================================
#
# WHAT THE TRACEBACK SAID
#   `average = total_ms / count`, division by zero.
#
# WHY IT LIED
#   It did not lie. It told you exactly where the program DIED. It cannot
#   tell you where the program went WRONG, and those are different lines.
#
#   The real bug is the filter: it tested for " 200ms " — a duration string
#   that appears nowhere — instead of " 200 ", the status code. It matched
#   nothing, silently, and the emptiness travelled four lines downstream
#   before anything complained.
#
#   THIS IS THE LESSON OF THE DAY. A traceback is the scene of the crash,
#   not the scene of the crime. Walk backwards from it and check that every
#   value on the way is what you assumed. `print(f"{count=}")` between the
#   filter and the division would have found it in ten seconds.
#
# THE FIX
#   Two of them, and you need both:
#     1. Correct the filter. That is the actual bug.
#     2. Guard the division anyway. An empty log is a legitimate input, not
#        an error, and "no requests yet" should print a dash, not a crash.

LOG = """GET /home 200 118ms
GET /about 200 92ms
POST /login 302 240ms
GET /assets/app.css 200 12ms
GET /missing 404 8ms"""

lines = LOG.splitlines()

successful = [line for line in lines if " 200 " in line]
durations = [int(line.split()[-1].replace("ms", "")) for line in successful]

count = len(successful)
total_ms = sum(durations)

print(f"log lines:        {len(lines)}")
print(f"successful (200): {count}")
print(f"durations:        {durations}")

# `count or 1` keeps the divisor away from zero (Day 7: 0 is falsy). The
# reported figure is then guarded by count itself, so an empty log prints
# 0.0 over a count of 0 rather than pretending to an average.
average = total_ms / (count or 1)
print(f"average response: {average:.1f}ms over {count} request(s)")

print()
print("=" * WIDTH)
print("All five fixed. Now go and write down, in your own words, what each")
print("exception type MEANS — not what the fix was. The fix you will forget.")
print("=" * WIDTH)
