"""Day 001 — First contact.

Every concept from today's article, in the order the article introduces them.

    python3 lesson.py

Then open the REPL (`python3` with no filename) and try the same lines there.
Spotting the difference between the two is most of today's point.
"""

# ---------------------------------------------------------------------------
# 1. print() — the one function you need on day one
# ---------------------------------------------------------------------------

print("Hello, world!")

# The quotes are not decoration. "Hello" is a piece of text; Hello without
# quotes is a NAME, and Python would go looking for something called Hello.
# Uncomment the next line to watch that fail, then comment it back:
# print(Hello)

# Single and double quotes are identical. Pick one and be consistent.
print('Single quotes work exactly the same way.')


# ---------------------------------------------------------------------------
# 2. print() takes as many arguments as you like
# ---------------------------------------------------------------------------

# Multiple arguments are joined with a space:
print("Ada", "Lovelace")

# Arguments are evaluated BEFORE they are printed, so this prints 4, not "2 + 2":
print("2 + 2 =", 2 + 2)

# print() with nothing in it prints a blank line. This is how you space output.
print()


# ---------------------------------------------------------------------------
# 3. sep and end — the two keyword arguments worth knowing early
# ---------------------------------------------------------------------------

# sep controls what goes BETWEEN the arguments. Default is one space.
print("a", "b", "c")             # a b c
print("a", "b", "c", sep="-")    # a-b-c
print("a", "b", "c", sep="")     # abc

# end controls what goes AFTER the last argument. Default is "\n", a newline.
# Setting it to "" keeps the next print on the same line:
print("no newline here", end="")
print(" <- same line")

# Day 19 uses end="\r" to build a timer that overwrites itself in place.

print()


# ---------------------------------------------------------------------------
# 4. Scripts print only what you ask them to
# ---------------------------------------------------------------------------

# In the REPL, typing this shows 4 immediately. Here it shows nothing at all:
2 + 2

# Python computed 4, found that nobody wanted the answer, and discarded it.
# That is the single biggest difference between the REPL and a script.
# To see it from a script you must say so:
print(2 + 2)


# ---------------------------------------------------------------------------
# 5. Borrowed from tomorrow — the three pieces today's build needs
# ---------------------------------------------------------------------------

# A name pointing at a value. Properly covered on Day 2.
name = "Ada Lovelace"
print(name)

# len() reports how many characters a string has. Properly covered on Day 3.
print("characters in name:", len(name))

# A string multiplied by a number repeats it. Also Day 3.
print("-" * 12)
print("=" * len(name))

# Put those two together and you have a rule that always matches the text
# above it, no matter what the text is. Change `name` and run the file again:
# the underline follows. That is the whole idea of today's build.


# ---------------------------------------------------------------------------
# 6. Strings can be added together
# ---------------------------------------------------------------------------

# Joining strings with + is called concatenation. Note that + inserts nothing,
# so you have to supply your own spaces.
print("Hello, " + name + "!")

# Day 4 replaces this with f-strings, which are much nicer. For today, + is
# enough to build the sides of a frame:
print("| " + name + " |")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Delete a closing parenthesis and run the file. Read the error.
#   * Delete a closing quote and run it. Read that error too — it is different.
#   * Change `name` to your own name and confirm the "=" underline still fits.
#   * Try `print("-" * len(name) * 2)` and work out why it does what it does.
