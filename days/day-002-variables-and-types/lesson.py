"""Day 002 — Variables and types.

    python3 lesson.py

Read top to bottom. Every section ends with something to try in the REPL.
"""

# ---------------------------------------------------------------------------
# 1. Assignment: the name goes on the left, always
# ---------------------------------------------------------------------------

temperature = 21.5
city = "Cairo"

print(city, "is at", temperature, "degrees")

# Read `=` as "gets", never as "equals". Python evaluates the RIGHT side first,
# then attaches the name to the result. That is why this is not circular:
count = 0
count = count + 1      # right side is 0 + 1 -> 1, then count gets 1
count = count + 1      # right side is 1 + 1 -> 2, then count gets 2
print("count is", count)

# A variable is a LABEL STUCK ON A VALUE, not a box holding one.
a = 5
b = a                  # both labels are now on the same 5
a = 6                  # only the `a` label moved
print("a =", a, "  b =", b)     # a = 6   b = 5


# ---------------------------------------------------------------------------
# 2. The four types you meet today
# ---------------------------------------------------------------------------

whole = 42                # int   — whole number, unlimited size
fraction = 3.14           # float — has a fractional part
text = "forty-two"        # str   — text
flag = True               # bool  — True or False, capitalised

print(whole, fraction, text, flag)

# Underscores in numbers are legal and purely for readability:
population = 1_000_000
print("population:", population)

# int and float are different types even when they look equal:
print(2 == 2.0)           # True  — same value
print(type(2) == type(2.0))   # False — different type

# Any arithmetic touching a float produces a float:
print(10 / 2)             # 5.0  — true division ALWAYS gives a float
print(10 // 2)            # 5    — floor division keeps ints int

# The famous one. This is not a bug; it is binary fractions.
print(0.1 + 0.2)          # 0.30000000000000004
print(round(0.1 + 0.2, 2))  # 0.3 — round for DISPLAY, don't pretend it changed


# ---------------------------------------------------------------------------
# 3. Dynamic typing, strong typing
# ---------------------------------------------------------------------------

# Dynamic: a name can point at anything, and can be repointed.
x = 42
x = "now I am a string"
print(x)

# Strong: Python will NOT silently mix types. Uncomment to see the TypeError:
# print("3" + 4)

# You have to say which one you meant:
print(int("3") + 4)       # 7    — text converted to number
print("3" + str(4))       # "34" — number converted to text

# Conversions are conversions, not casts — they build a new value:
print(int(3.7))           # 3 — truncates toward zero, does NOT round
print(int(-3.7))          # -3
print(float(3))           # 3.0
print(str(3))             # "3"

# int() on a float-looking STRING raises. This one bites everybody on Day 6:
# print(int("3.7"))       # ValueError
print(int(float("3.7")))  # 3 — go via float when the text might have a point


# ---------------------------------------------------------------------------
# 4. type() — a debugging tool, not production code
# ---------------------------------------------------------------------------

print(type(42))
print(type(3.0))
print(type("42"))
print(type(True))
print(type(None))

# A historical curiosity that confuses everyone exactly once:
print(True == 1)          # True — bool is a subclass of int
print(True + True)        # 2    — occasionally useful for counting


# ---------------------------------------------------------------------------
# 5. Truthiness: every value answers yes or no
# ---------------------------------------------------------------------------

# Falsy: 0, 0.0, "", None, and every empty container.
print(bool(0), bool(0.0), bool(""), bool(None))       # all False

# Truthy: everything else — INCLUDING these two, which trip people up:
print(bool("0"), bool("False"))                       # both True, non-empty strings
print(bool(-1), bool(0.1), bool(" "))                 # all True


# ---------------------------------------------------------------------------
# 6. None — the "nothing here" value
# ---------------------------------------------------------------------------

result = None
print("result is", result)
print("is it None?", result is None)     # use `is`, never `==`, for None

# You get None whether or not you write it. print() itself returns it:
returned = print("this line prints, and returns None")
print("print() returned:", returned)


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Set `str = "oops"` and then try `str(5)`. Read the error. Now you know
#     why shadowing builtins is a rule, not a style preference.
#   * Predict, then check: type(7/2), type(7//2), type(2**10), type(2.0**10).
#   * Assign a value to `Temperature` and print `temperature`. Read the error
#     and note that Python considers those two entirely unrelated names.
