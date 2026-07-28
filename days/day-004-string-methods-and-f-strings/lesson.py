"""Day 004 — String methods and f-strings.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. Methods return NEW strings. Always. Without exception.
# ---------------------------------------------------------------------------

name = "  aDa LoVeLaCe  "

name.strip()                 # computed, then thrown away
print(repr(name))            # unchanged — this is Day 3's immutability biting

cleaned = name.strip()       # keep the result
print(repr(cleaned))

# Because each method returns a string, methods CHAIN:
print(repr(name.strip().title()))         # 'Ada Lovelace'
print(repr(name.strip().lower()))         # 'ada lovelace'


# ---------------------------------------------------------------------------
# 2. Case and whitespace
# ---------------------------------------------------------------------------

print("ada".upper())              # ADA
print("ADA".lower())              # ada
print("ada lovelace".title())     # Ada Lovelace
print("ada lovelace".capitalize())  # Ada lovelace  — first word only

# .lower() is how you compare text a human typed:
answer = "YES"
print(answer == "yes")            # False — almost never what you meant
print(answer.lower() == "yes")    # True  — what you meant

# .strip() takes whitespace off BOTH ends, never the middle:
print(repr("  hello  ".strip()))  # 'hello'
print(repr(" a b ".strip()))      # 'a b'  — inner space survives
print(repr("xxhixx".strip("x")))  # 'hi'   — strip any characters you name

# One end at a time. .rstrip() is how you drop a trailing newline (Day 53):
print(repr("line\n".rstrip()))    # 'line'
print(repr("  pad  ".lstrip()))   # 'pad  '


# ---------------------------------------------------------------------------
# 3. split() and join() — the most important pair on this page
# ---------------------------------------------------------------------------

print("a,b,c".split(","))                  # ['a', 'b', 'c']
print("Ada Augusta Byron".split())         # ['Ada', 'Augusta', 'Byron']

# Bare .split() splits on RUNS of whitespace and drops the empties.
# .split(" ") splits on each single space and keeps them. Compare:
print("  Ada   Byron  ".split())           # ['Ada', 'Byron']
print("  Ada   Byron  ".split(" "))        # ['', '', 'Ada', '', '', 'Byron', '', '']

# maxsplit caps how many cuts are made — useful for "key: value" lines:
print("key: some: value".split(":", 1))    # ['key', ' some: value']

# .join() is the inverse. THE SEPARATOR IS WHAT YOU CALL IT ON.
print(", ".join(["a", "b", "c"]))          # a, b, c
print("".join(["A", "B", "C"]))            # ABC
print(" -> ".join(["start", "middle", "end"]))

# Round trip: split it, change it, put it back.
print("-".join("2024 01 15".split()))      # 2024-01-15

# Yesterday's whole build, in one line. The `part[0] for part in ...` shape is
# a comprehension — Day 22 explains it. Read it as "the first letter of each
# part"; you do not need to be able to write one yet.
full = "Ada Augusta Byron King"
print("".join(part[0] for part in full.split()))    # AABK

# .join() only joins STRINGS. This is the error you will hit:
# print(", ".join([1, 2, 3]))              # TypeError
print(", ".join([str(n) for n in [1, 2, 3]]))       # 1, 2, 3  (Day 22 again)

# For multi-line text use .splitlines(), which handles \n, \r\n and \r:
print("line1\nline2\nline3".splitlines())


# ---------------------------------------------------------------------------
# 4. replace() and the predicates
# ---------------------------------------------------------------------------

print("2024-01-15".replace("-", "/"))      # 2024/01/15
print("aaa".replace("a", "b", 1))          # baa — third arg caps the count
print("hello world".replace(" ", ""))      # helloworld

# .replace() is LITERAL. No patterns, no wildcards. That is Day 62.

# The predicates all return bool:
print("file.csv".endswith(".csv"))         # True
print("Dr. Ada".startswith("Dr."))         # True
print("42".isdigit())                      # True  — cheap input validation
print("4.2".isdigit())                     # False — the dot is not a digit!
print("abc".isalpha())                     # True
print("   ".isspace())                     # True

print("Ada" in "Ada Lovelace")             # True — membership, not a method
print("Lovelace".count("l"))               # 1 — case matters


# ---------------------------------------------------------------------------
# 5. f-strings
# ---------------------------------------------------------------------------

first = "Ada"
age = 36

print(f"{first} is {age}")                 # Ada is 36
print(f"Next year: {age + 1}")             # any expression, not just names
print(f"Shouting: {first.upper()}")        # method calls work too

# The three generations, for reading old code. Only write the third.
print("Hello, " + first + "! You are " + str(age) + ".")
print("Hello, {}! You are {}.".format(first, age))
print(f"Hello, {first}! You are {age}.")

# A literal brace is doubled:
print(f"{{not a placeholder}} but {first} is")

# `=` prints the expression AND its value. The fastest debugger in Python:
print(f"{age=}")
print(f"{age * 2 = }")

# !r shows the repr — quotes and escapes visible. Use it whenever you suspect
# whitespace, which is often:
value = " 42 "
print(f"plain: {value}")
print(f"repr:  {value!r}")


# ---------------------------------------------------------------------------
# 6. Format specs — everything after the colon
# ---------------------------------------------------------------------------

# ALIGNMENT AND WIDTH. This is how columns exist.
print(f"[{'Coffee':<15}]")     # left
print(f"[{'Coffee':>15}]")     # right
print(f"[{'Coffee':^15}]")     # centre
print(f"[{'Coffee':.<15}]")    # left, dot-filled — the receipt leader
print(f"[{'Coffee':*^15}]")    # centre, star-filled

# Text defaults to left, numbers default to right — which is what tables want:
print(f"[{'text':10}][{42:10}]")

# NUMBERS.
print(f"{3.14159:.2f}")        # 3.14       — 2 decimals, always shown
print(f"{5:.2f}")              # 5.00       — this is what money looks like
print(f"{1234567:,}")          # 1,234,567  — thousands separators
print(f"{1234.5:>12,.2f}")     # combined: width 12, commas, 2 decimals
print(f"{0.257:.1%}")          # 25.7%      — as a percentage
print(f"{255:04d}")            # 0255       — zero padded
print(f"{255:b} {255:o} {255:x} {255:X}")   # binary, octal, hex
print(f"{12345678:.2e}")       # scientific

# WIDTH FROM A VARIABLE, via nested braces. This is how a table sizes itself
# to its contents instead of to numbers you guessed.
w = 20
print(f"[{'Coffee':<{w}}]")
print(f"[{'Tea':.<{w}}]")

places = 3
print(f"{2/3:.{places}f}")     # 0.667


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Drop the f from an f-string and look at what prints.
#   * Try f"{1234:,.2f}" and f"{1234:.2f,}". One is an error — which, and why?
#   * Chain methods on "  MIXED case, TEXT  " until it is "Mixed Case, Text".
#   * Set w = 5 and print a 12-character name into it. Does it truncate or
#     overflow? Now you know what width does and does not guarantee.
