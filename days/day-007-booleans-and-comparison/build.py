"""Day 007 build — a password strength checker that says WHICH rules failed.

The design rule for this build: every check is an INDEPENDENT boolean, and
every one is reported. A checker that only says "too weak" is useless; a
checker that stops at the first failure makes the user fix one thing, resubmit,
and be told about the next one. Evaluate everything, report everything.

This is also the day's concepts doing real work: truthiness for the empty
case, chained comparison for the length band, short-circuiting to keep the
indexing safe, and bools-as-ints to score.

    python3 build.py
    printf 'correct-horse-battery-staple\\n' | python3 build.py
"""

WIDTH = 58

DIGITS = "0123456789"
SPECIALS = "!@#$%^&*()-_=+[]{};:,.<>?/|~`\"'\\"
COMMON = "password,123456,qwerty,letmein,admin,welcome,iloveyou,monkey,dragon"

MIN_LENGTH = 12
STRONG_LENGTH = 16

print("=" * WIDTH)
print(f"{'PASSWORD STRENGTH CHECKER':^{WIDTH}}")
print("=" * WIDTH)

password = input("Password: ")

# ---------------------------------------------------------------------------
# Derived facts. Compute once, name clearly, reuse below.
# ---------------------------------------------------------------------------

length = len(password)
lowered = password.lower()
stripped = password.strip()

# `any(...)` over a generator is Day 22 syntax; read it as "is there at least
# one character in the password for which this is true". You could write each
# of these with a loop on Day 13 — and it would be five lines instead of one.
has_lower = any(ch.islower() for ch in password)
has_upper = any(ch.isupper() for ch in password)
has_digit = any(ch in DIGITS for ch in password)
has_special = any(ch in SPECIALS for ch in password)
has_space = any(ch.isspace() for ch in password)

distinct = len(set(password))          # Day 26 explains set(); it drops duplicates

# ---------------------------------------------------------------------------
# The rules. Each one is one boolean expression and nothing else.
# ---------------------------------------------------------------------------

# Truthiness: a non-empty string is truthy. `if password:` is the idiom.
rule_not_empty = bool(password)

# Short-circuit: `password and ...` means the comparisons below never run on
# an empty string. The protective test goes on the LEFT.
rule_no_edge_space = bool(password) and password == stripped

# Length is worth THREE of the twelve rules, and composition only four. That
# weighting is the entire opinion of this checker, and it is the mainstream
# one: a long passphrase beats a short cryptic string, because attackers
# search the short space first whatever symbols are in it.
rule_length = MIN_LENGTH <= length
rule_length_good = STRONG_LENGTH <= length
rule_length_great = 20 <= length

rule_has_lower = has_lower
rule_has_upper = has_upper
rule_has_digit = has_digit
rule_has_special = has_special
rule_no_spaces = not has_space

# Variety catches "aaaaaaaaaaaaaaaa", which is long but has one character in
# it. A flat floor is the right shape here: a ratio would punish a long
# passphrase for reusing letters, which is not a weakness.
rule_variety = distinct >= 5

# Not a well-known password, and does not merely contain one.
rule_not_common = bool(password) and not any(
    bad in lowered for bad in COMMON.split(",")
)

# ---------------------------------------------------------------------------
# The report. One line per rule, always, whatever else failed.
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print(f"{'RULE':<44}{'RESULT':>14}")
print("-" * WIDTH)
print(f"{'is not empty':<44}{str(rule_not_empty):>14}")
print(f"{f'is at least {MIN_LENGTH} characters':<44}{str(rule_length):>14}")
print(f"{f'is at least {STRONG_LENGTH} characters':<44}{str(rule_length_good):>14}")
print(f"{'is at least 20 characters':<44}{str(rule_length_great):>14}")
print(f"{'has a lowercase letter':<44}{str(rule_has_lower):>14}")
print(f"{'has an uppercase letter':<44}{str(rule_has_upper):>14}")
print(f"{'has a digit':<44}{str(rule_has_digit):>14}")
print(f"{'has a special character':<44}{str(rule_has_special):>14}")
print(f"{'has no whitespace inside':<44}{str(rule_no_spaces):>14}")
print(f"{'has no leading or trailing space':<44}{str(rule_no_edge_space):>14}")
print(f"{'is not mostly one repeated character':<44}{str(rule_variety):>14}")
print(f"{'is not a well-known password':<44}{str(rule_not_common):>14}")
print("-" * WIDTH)

# ---------------------------------------------------------------------------
# Score. Bools are ints (Day 2), so they add.
# ---------------------------------------------------------------------------

score = (
    rule_not_empty
    + rule_length
    + rule_length_good
    + rule_length_great
    + rule_has_lower
    + rule_has_upper
    + rule_has_digit
    + rule_has_special
    + rule_no_spaces
    + rule_no_edge_space
    + rule_variety
    + rule_not_common
)
TOTAL_RULES = 12

# The two length bonuses are extra credit, not requirements — a 12-character
# password with everything else right is still ACCEPTED.
all_passed = all([
    rule_not_empty, rule_length, rule_has_lower, rule_has_upper,
    rule_has_digit, rule_has_special, rule_no_spaces, rule_no_edge_space,
    rule_variety, rule_not_common,
])

print(f"{'PASSED':<44}{f'{score} / {TOTAL_RULES}':>14}")
print(f"{'ACCEPTED':<44}{str(all_passed):>14}")
print()

# The bands, as booleans. Exactly one is True.
print(f"{'  weak      (0-5 rules)':<44}{str(score <= 5):>14}")
print(f"{'  fair      (6-8 rules)':<44}{str(6 <= score <= 8):>14}")
print(f"{'  good      (9-10 rules)':<44}{str(9 <= score <= 10):>14}")
print(f"{'  strong    (11 rules)':<44}{str(score == 11):>14}")
print(f"{'  excellent (all 12)':<44}{str(score == TOTAL_RULES):>14}")
print()

# ---------------------------------------------------------------------------
# Facts, for the curious
# ---------------------------------------------------------------------------

print("-" * WIDTH)
print(f"{'length':<44}{length:>14}")
print(f"{'distinct characters':<44}{distinct:>14}")
print(f"{'repeated characters':<44}{length - distinct:>14}")
print("=" * WIDTH)

# Note what the checker deliberately does NOT do: it never says "add a
# symbol". Telling an attacker your composition rules narrows their search.
# Length beats composition every time — which is why a long passphrase of
# ordinary words outscores "P@ss1!" here, and should.


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Try "" , "password", "Password1!", "aaaaaaaaaaaaaaaa", " hunter2 " and
#     "correct-horse-battery-staple". Every rule must report independently:
#     no failure may hide another.
#   * rule_variety was ONCE `distinct * 2 >= length`, and it was wrong: it
#     failed a 28-character passphrase for reusing letters, which is not a
#     weakness. Change it back and watch the passphrase drop below "P@ss1!".
#     A scoring rule that disagrees with your own advice is a bug.
#   * Add a rule that rejects a password containing three consecutive
#     characters from the keyboard row "qwertyuiop". You have `in`.
#   * On Day 11 turn this into a program that only ACCEPTS a good password.
#     On Day 12 make it re-ask. On Day 31 make each rule a function, so the
#     ten-term score expression becomes one line.
