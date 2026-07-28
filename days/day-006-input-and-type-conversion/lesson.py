"""Day 006 — Input and type conversion.

This one talks back. Run it in a terminal:

    python3 lesson.py

Or feed it answers without typing:

    printf 'Ada\\n36\\n1.75\\n' | python3 lesson.py
"""

# ---------------------------------------------------------------------------
# 1. input() returns a STRING. Always. Without exception.
# ---------------------------------------------------------------------------

name = input("What is your name? ")     # note the trailing space in the prompt
print(f"Hello, {name}")
print(f"You typed {name!r}, which is a {type(name).__name__}")

# The newline is already removed for you. Other whitespace is not:
print(f"repr, exactly as received: {name!r}")

print()

# ---------------------------------------------------------------------------
# 2. The trap: one of these fails loudly, the other fails silently
# ---------------------------------------------------------------------------

age_text = input("How old are you? ")

# age_text + 1        # TypeError — loud, and therefore harmless

print(f"age_text * 2 = {age_text * 2!r}")
#      ^ NO ERROR. "36" * 2 is "3636". A wrong answer with no complaint is
#        far more dangerous than a crash. This is why you convert.

age = int(age_text)
print(f"int(age_text) * 2 = {age * 2}")

print()

# ---------------------------------------------------------------------------
# 3. The standard idiom: convert at the boundary
# ---------------------------------------------------------------------------

height = float(input("Height in metres? "))
print(f"Twice your height is {height * 2:.2f} m")

# One line, read and convert together. You will type this hundreds of times.
# It also crashes on anything unconvertible, which is the rest of today.

print()

# ---------------------------------------------------------------------------
# 4. How the conversions succeed and fail
# ---------------------------------------------------------------------------

print(int("30"))          # 30
print(int("  30  "))      # 30    — surrounding whitespace is tolerated
print(int("-30"))         # -30   — a sign is fine
print(int("1_000"))       # 1000  — underscores are fine too

# print(int("30.5"))      # ValueError — int() on a STRING wants an integer literal
print(int(30.5))          # 30    — int() on a FLOAT truncates. Note the asymmetry.
print(int(float("30.5"))) # 30    — the fix when input may have a decimal point

print(float("30.5"))      # 30.5
print(float("3e2"))       # 300.0 — scientific notation is accepted
print(float("  .5 "))     # 0.5   — a leading dot is fine

# print(int(""))          # ValueError — the user just pressed Enter
# print(float("abc"))     # ValueError

# ValueError means "right type, wrong value".
# TypeError means "wrong type entirely". Day 9 leans on this distinction.

print()

# ---------------------------------------------------------------------------
# 5. Predicates: cheap validation, and their limits
# ---------------------------------------------------------------------------

print("30".isdigit())        # True
print("30.5".isdigit())      # False  <- the dot is not a digit
print("-30".isdigit())       # False  <- nor is the minus sign
print("".isdigit())          # False  <- convenient: empty is never valid
print(" 30".isdigit())       # False  <- strip FIRST, then test

# So .isdigit() alone silently rejects -5 and 1.5. It is a gate for whole
# non-negative numbers and nothing else. Know what your gate lets through.

# A decimal-tolerant gate, built from Day 4 string methods only:
candidate = "70.5"
print(candidate.replace(".", "", 1).isdigit())     # True — allow ONE dot

print()

# ---------------------------------------------------------------------------
# 6. Cleaning: the shape of nearly all real input handling
# ---------------------------------------------------------------------------

raw = "  70,5 KG \n"
print(f"raw:     {raw!r}")

cleaned = raw.strip()            # ends first
cleaned = cleaned.lower()        # normalise case before comparing or replacing
cleaned = cleaned.replace("kg", "")
cleaned = cleaned.replace(",", ".")   # European decimal comma
cleaned = cleaned.strip()        # strip AGAIN — the replace left a space
print(f"cleaned: {cleaned!r}")
print(f"as float: {float(cleaned)}")

# Strip, normalise, replace, strip again. The second strip is the step people
# forget, and it is the one that makes the difference.

print()

# ---------------------------------------------------------------------------
# 7. A fallback that cannot crash
# ---------------------------------------------------------------------------

# `or` returns the first truthy operand. An empty string is falsy (Day 2), so
# this substitutes a default whenever the user typed nothing. Day 7 covers the
# mechanism; today just note that it removes one whole class of ValueError.

maybe_empty = ""
print(float(maybe_empty or "0"))     # 0.0, no exception

print()

# ---------------------------------------------------------------------------
# 8. Several values from one line
# ---------------------------------------------------------------------------

pair = input("Enter width and height, space separated: ")
parts = pair.split()
print(f"got {len(parts)} value(s): {parts}")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Answer the height question with "tall". Read the traceback. Which line?
#     Which exception? What did it actually say the bad value was?
#   * Answer it with an empty line. Same three questions.
#   * Answer the age question with "36 " (trailing space) and confirm int()
#     copes, then with "3 6" and confirm it does not.
#   * Run the whole file with `printf '\\n\\n\\n' | python3 lesson.py` and
#     watch where it dies. That is what an unvalidated boundary looks like.
