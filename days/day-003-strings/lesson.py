"""Day 003 — Strings.

    python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. A string is a sequence, indexed from zero
# ---------------------------------------------------------------------------

name = "Python"
#       012345      <- forward indices
#      -654321      <- backward indices

print(name[0])       # P  — first character
print(name[5])       # n  — last character, the hard way
print(name[-1])      # n  — last character, the way you will actually write it
print(name[-2])      # o

print("length:", len(name))          # 6
# The last valid index is len(s) - 1. This is where off-by-one errors live.
# print(name[6])                     # IndexError: string index out of range


# ---------------------------------------------------------------------------
# 2. Slicing: [start:stop], start INCLUDED, stop EXCLUDED
# ---------------------------------------------------------------------------

print(name[0:2])     # "Py"    — 2 - 0 = 2 characters
print(name[2:6])     # "thon"  — 6 - 2 = 4 characters

# The length of a slice is always stop - start. Say it out loud.

# Omit an end to mean "as far as you can go":
print(name[:3])      # "Pyt"    — from the beginning
print(name[3:])      # "hon"    — to the end
print(name[:])       # "Python" — a full copy
print(name[-3:])     # "hon"    — "the last three", the idiom worth memorising

# Slices never raise. Out-of-range is silently clamped:
print(repr(name[0:999]))   # 'Python'
print(repr(name[99:]))     # ''  — empty, no error. Convenient and dangerous.

# The third slot is the step:
print(name[::2])     # "Pto"     — every second character
print(name[1::2])    # "yhn"     — every second, starting at 1
print(name[::-1])    # "nohtyP"  — the standard string reversal


# ---------------------------------------------------------------------------
# 3. Concatenation and repetition
# ---------------------------------------------------------------------------

first = "Ada"
last = "Lovelace"

# + joins and inserts NOTHING. Every space is yours to supply.
print(first + last)          # AdaLovelace   <- the classic bug
print(first + " " + last)    # Ada Lovelace

# * repeats. Combine with len() and you get rules that always fit (Day 1).
print("=" * len(first + " " + last))

# + still refuses to mix types:
# print("Total: " + 5)       # TypeError
print("Total: " + str(5))    # fine, and obsolete tomorrow

# Do NOT build long strings by += in a loop. Each + copies the whole string,
# so the cost grows quadratically. Day 4's "".join() is the right answer.


# ---------------------------------------------------------------------------
# 4. Escape sequences
# ---------------------------------------------------------------------------

print("Line one\nLine two")       # \n is a newline
print("Name:\tAda")               # \t is a tab
print("She said \"hi\"")          # escaped double quotes
print('She said "hi"')            # or just use the other quote character
print("A backslash: \\")          # \\ is one literal backslash

# Raw strings: the r prefix turns escapes off. Essential for Windows paths
# and for the regexes on Day 62.
print(r"C:\temp\new")             # C:\temp\new
print("C:\temp\new")              # note what \t and \n did to that. Now you know.

# Worse: "C:\Users\name" is not even a runnable line. \U begins an 8-digit
# unicode escape, so Python rejects the FILE, not just the string. A raw
# string or forward slashes avoids the whole category.

# Triple quotes span lines and keep their own formatting:
banner = """
  +-------------------+
  |  Day 3: Strings   |
  +-------------------+
"""
print(banner)


# ---------------------------------------------------------------------------
# 5. Immutability: strings can never be changed in place
# ---------------------------------------------------------------------------

word = "Python"

# word[0] = "J"          # TypeError: 'str' object does not support item assignment

# Every "modifying" operation returns a NEW string and leaves the old one alone:
word.upper()
print(word)              # still "Python" — the result was thrown away

# Keep it by assigning it. This is the fix for the single most common
# beginner mistake in Python:
word = word.upper()
print(word)              # PYTHON

# To "edit" a string, slice around the part you are replacing:
word = "Python"
word = "J" + word[1:]    # replace character 0
print(word)              # Jython

word = "Python"
word = word[:3] + "ON" + word[5:]
print(word)              # PytONn  — count carefully, this is deliberate


# ---------------------------------------------------------------------------
# 6. Searching: the inverse of indexing
# ---------------------------------------------------------------------------

full = "Ada Lovelace"

print(full.index(" "))       # 3  — position of the first space
print(full.find(" "))        # 3  — same, but returns -1 instead of raising
print(full.find("z"))        # -1 — not found, no exception
# print(full.index("z"))     # ValueError: substring not found

print("Love" in full)        # True — membership, the check you want most often

# Put searching and slicing together and you can split a two-part name:
space = full.index(" ")
print(full[:space])          # Ada
print(full[space + 1:])      # Lovelace

# Three parts needs two searches. N parts needs a loop you do not have yet.
# That limit is exactly why .split() exists — see it tomorrow.


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Predict then check: "abcdef"[1:4], [-3:], [::-2], [4:1], [1:100].
#     One of those returns "" — work out why before you run it.
#   * Take s = "hello" and try to change it to "jello" three different ways.
#   * Write "C:\temp\new\file.txt" so it prints exactly as written. Two ways.
#   * Reverse a string without [::-1]. It is more annoying than you expect.
