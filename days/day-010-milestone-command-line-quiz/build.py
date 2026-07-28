"""Day 010 MILESTONE — a scored ten-question quiz.

Everything from days 1-9 and nothing from day 11 onwards: no if, no loops,
no functions, no data structures beyond what .split() hands back.

    python3 build.py

Answer without typing (these answers score 6/10 on purpose):

    printf 'cairo\\nParis\\n7\\ntrue\\nzero\\nfalse\\n1969\\nlist\\n42\\npython\\n' \\
      | python3 build.py
"""

WIDTH = 66
PASS_MARK = 6

# Selection tables — the whole of today's technique. See lesson.py sections
# 2 and 3.
VERDICT = ("WRONG", "RIGHT")
MARK = ("x", "v")
GRADES = "FFFFFDDCBAA"
#         0    5 7 9 10

# ---------------------------------------------------------------------------
# THE QUIZ. Question, accepted answers (| separated, lowercase), and the
# explanation shown when you get it wrong.
# ---------------------------------------------------------------------------

Q1 = "1.  What is the capital of Egypt?"
A1 = "cairo|al-qahirah|el cairo"
E1 = "Cairo. Alexandria is the one people guess."

Q2 = "2.  Which city hosted the 1900 Olympics?"
A2 = "paris"
E2 = "Paris, alongside that year's World's Fair."

Q3 = "3.  What is 3 + 4?"
A3 = "7|seven"
E3 = "7. If you typed 'seven' that was accepted too."

Q4 = "4.  True or false: in Python, 0 is falsy."
A4 = "true|t|yes|y|1"
E4 = "True. 0, 0.0, '', None and every empty container are falsy (Day 7)."

Q5 = "5.  What does len('') return?"
A5 = "0|zero"
E5 = "0. The empty string has no characters, and is therefore falsy."

Q6 = "6.  True or false: strings in Python can be modified in place."
A6 = "false|f|no|n|0"
E6 = "False. Strings are immutable; every 'change' builds a new one (Day 3)."

Q7 = "7.  Which operator gives the remainder after division?"
A7 = "%|modulo|mod|percent"
E7 = "%  — Day 5. // gives the whole part, % gives what is left."

Q8 = "8.  What type does input() always return?"
A8 = "str|string|a string|text"
E8 = "str. Always, even when the user typed digits (Day 6)."

Q9 = "9.  What is 2 ** 3 ** 2?"
A9 = "512"
E9 = "512. ** is right-associative, so it is 2 ** (3 ** 2), not (2 ** 3) ** 2."

Q10 = "10. Which exception does int('abc') raise?"
A10 = "valueerror|value error"
E10 = "ValueError — right type, wrong value. int([]) would be a TypeError."

# ===========================================================================
# ASK
# ===========================================================================

print("=" * WIDTH)
print(f"{'PYTHON QUIZ — DAYS 1 TO 9':^{WIDTH}}")
print("=" * WIDTH)
print("Ten questions. Case and surrounding spaces do not matter.")
print()

print(Q1)
given_1 = input("    > ")
print(Q2)
given_2 = input("    > ")
print(Q3)
given_3 = input("    > ")
print(Q4)
given_4 = input("    > ")
print(Q5)
given_5 = input("    > ")
print(Q6)
given_6 = input("    > ")
print(Q7)
given_7 = input("    > ")
print(Q8)
given_8 = input("    > ")
print(Q9)
given_9 = input("    > ")
print(Q10)
given_10 = input("    > ")

# ===========================================================================
# SCORE — normalise both sides the same way, then test membership against
# the whole options, never against the raw string (lesson.py section 6).
# ===========================================================================

ok_1 = given_1.strip().lower() in A1.split("|")
ok_2 = given_2.strip().lower() in A2.split("|")
ok_3 = given_3.strip().lower() in A3.split("|")
ok_4 = given_4.strip().lower() in A4.split("|")
ok_5 = given_5.strip().lower() in A5.split("|")
ok_6 = given_6.strip().lower() in A6.split("|")
ok_7 = given_7.strip().lower() in A7.split("|")
ok_8 = given_8.strip().lower() in A8.split("|")
ok_9 = given_9.strip().lower() in A9.split("|")
ok_10 = given_10.strip().lower() in A10.split("|")

score = ok_1 + ok_2 + ok_3 + ok_4 + ok_5 + ok_6 + ok_7 + ok_8 + ok_9 + ok_10
total = 10

# ===========================================================================
# FEEDBACK — one block per question, always printed, with the explanation
# appearing only where the answer was wrong (string * bool).
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'ANSWERS':^{WIDTH}}")
print("=" * WIDTH)

print(f"[{MARK[ok_1]}] {VERDICT[ok_1]:<6} you said {given_1.strip()!r}")
print(("    " + E1 + "\n") * (not ok_1), end="")
print(f"[{MARK[ok_2]}] {VERDICT[ok_2]:<6} you said {given_2.strip()!r}")
print(("    " + E2 + "\n") * (not ok_2), end="")
print(f"[{MARK[ok_3]}] {VERDICT[ok_3]:<6} you said {given_3.strip()!r}")
print(("    " + E3 + "\n") * (not ok_3), end="")
print(f"[{MARK[ok_4]}] {VERDICT[ok_4]:<6} you said {given_4.strip()!r}")
print(("    " + E4 + "\n") * (not ok_4), end="")
print(f"[{MARK[ok_5]}] {VERDICT[ok_5]:<6} you said {given_5.strip()!r}")
print(("    " + E5 + "\n") * (not ok_5), end="")
print(f"[{MARK[ok_6]}] {VERDICT[ok_6]:<6} you said {given_6.strip()!r}")
print(("    " + E6 + "\n") * (not ok_6), end="")
print(f"[{MARK[ok_7]}] {VERDICT[ok_7]:<6} you said {given_7.strip()!r}")
print(("    " + E7 + "\n") * (not ok_7), end="")
print(f"[{MARK[ok_8]}] {VERDICT[ok_8]:<6} you said {given_8.strip()!r}")
print(("    " + E8 + "\n") * (not ok_8), end="")
print(f"[{MARK[ok_9]}] {VERDICT[ok_9]:<6} you said {given_9.strip()!r}")
print(("    " + E9 + "\n") * (not ok_9), end="")
print(f"[{MARK[ok_10]}] {VERDICT[ok_10]:<6} you said {given_10.strip()!r}")
print(("    " + E10 + "\n") * (not ok_10), end="")

# ===========================================================================
# GRADE
# ===========================================================================

percent = score / total
grade = GRADES[score]
passed = score >= PASS_MARK

# A bar drawn from the score. "#" * score is the whole implementation.
bar = "#" * score + "." * (total - score)

print()
print("=" * WIDTH)
print(f"{'RESULT':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'Score':<24}{f'{score} / {total}':>18}")
print(f"{'Percent':<24}{percent:>18.0%}")
print(f"{'Grade':<24}{grade:>18}")
print(f"{'Passed':<24}{str(passed):>18}")
print(f"{'':<24}{bar:>18}")
print("-" * WIDTH)
print(f"{'Right':<24}{score:>18}")
print(f"{'Wrong':<24}{total - score:>18}")
print(f"{'Perfect paper':<24}{str(score == total):>18}")
print("=" * WIDTH)

# The closing line, chosen by score without a single conditional: the score
# indexes an eleven-element tuple, exactly like the grade indexes a string.
CLOSING = (
    "Start again from Day 1. Genuinely — it is nine hours, not nine weeks.",
    "Re-read Days 2 and 3. The types are the foundation of everything after.",
    "Re-read Days 2 and 3. The types are the foundation of everything after.",
    "Go back over the days you missed. You are close.",
    "Go back over the days you missed. You are close.",
    "A pass is a pass. Skim the explanations above before Day 11.",
    "Solid. Read the two explanations above and move on.",
    "Good. You have the foundations.",
    "Very good. On to control flow.",
    "Excellent. Day 11 will feel like being handed a power tool.",
    "Perfect paper. Ten from ten, with no `if` in the whole program.",
)
print(CLOSING[score])
print()

# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Count the repetition in this file. Ten near-identical ask blocks, ten
#     near-identical scoring lines, twenty near-identical feedback lines.
#     That is roughly 60 lines expressing 3 ideas. It is not bad code for
#     today — it is the honest cost of having no loop.
#
#   * On Day 13, put the questions in a list and collapse all of it to about
#     twelve lines. Diff the two versions and keep both; that diff is the
#     single clearest argument for loops you will ever see.
#
#   * On Day 11, add per-question `if` feedback that can differ in STRUCTURE
#     ("so close — you had the right idea but..."), not just in content.
#     Then notice that the GRADES lookup is still better as a table, and
#     leave it alone. Knowing which to convert is the skill.
#
#   * On Day 24, move the questions into a dict of question -> answers.
#     On Day 55, move them into a JSON file so the quiz has no content in it
#     at all — at which point you have written a quiz ENGINE.
