"""Day 005 build — a bill splitter that tells the truth about the odd penny.

The requirement that makes this interesting is not the tip arithmetic. It is
this: THE SHARES MUST SUM TO THE TOTAL. Seven people splitting 215.57 each owe
30.795..., and no amount of rounding each share independently will make seven
rounded shares add back to the total. A penny goes missing, or appears.

Today's job is to DETECT and QUANTIFY that drift exactly — which is the part
almost every homemade bill splitter gets wrong. Actually distributing the
remainder needs a conditional (Day 11) and a loop (Day 13), so it is left as
the extension at the bottom, on purpose.

    python3 build.py
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

# ---------------------------------------------------------------------------
# INPUT — all money as STRINGS, so Decimal receives exact digits.
# Decimal("0.1") is exactly one tenth. Decimal(0.1) is not.
# ---------------------------------------------------------------------------

BILL = Decimal("187.45")
TIP_PERCENT = Decimal("15")
PEOPLE = 7

# Uneven shares: two of those seven are covering extra portions.
SHARES_A = 2
SHARES_B = 3

PENNY = Decimal("0.01")
WIDTH = 46

# ---------------------------------------------------------------------------
# 1. The bill plus tip
# ---------------------------------------------------------------------------

tip = (BILL * TIP_PERCENT / 100).quantize(PENNY, rounding=ROUND_HALF_UP)
total = BILL + tip

print("=" * WIDTH)
print(f"{'BILL SPLITTER':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'Bill':<30}{BILL:>16}")
print(f"{f'Tip ({TIP_PERCENT}%)':<30}{tip:>16}")
print("-" * WIDTH)
print(f"{'Total to collect':<30}{total:>16}")
print()

# ---------------------------------------------------------------------------
# 2. The even split, and the penny that goes missing
# ---------------------------------------------------------------------------

print("-" * WIDTH)
print(f"EVEN SPLIT, {PEOPLE} WAYS")
print("-" * WIDTH)

exact_share = total / PEOPLE
rounded_share = exact_share.quantize(PENNY, rounding=ROUND_HALF_UP)
collected = rounded_share * PEOPLE
drift = total - collected

print(f"{'Exact share (unrounded)':<30}{exact_share:>16.6f}")
print(f"{'Rounded share':<30}{rounded_share:>16}")
print(f"{'Which collects':<30}{collected:>16}")
print(f"{'Drift vs. total':<30}{drift:>16}")
print(f"{'Shares sum exactly?':<30}{str(collected == total):>16}")
print()

# The honest fix starts here: round every share DOWN, then count how many
# whole pennies are left over. That count is how many people have to pay one
# penny more. Nobody is ever more than a penny out.
base = exact_share.quantize(PENNY, rounding=ROUND_DOWN)
left_over = total - base * PEOPLE
pennies_to_hand_out = int(left_over / PENNY)

print(f"{'Base share (rounded down)':<30}{base:>16}")
print(f"{'Left over':<30}{left_over:>16}")
print(f"{'People paying 1p extra':<30}{pennies_to_hand_out:>16}")
print(f"{'People paying the base':<30}{PEOPLE - pennies_to_hand_out:>16}")

check = base * PEOPLE + pennies_to_hand_out * PENNY
print(f"{'Reconstructed total':<30}{check:>16}")
print(f"{'Exact?':<30}{str(check == total):>16}")
print()

# ---------------------------------------------------------------------------
# 3. Uneven shares — the denominator is portions, not heads
# ---------------------------------------------------------------------------

print("-" * WIDTH)
print("UNEVEN SPLIT, BY SHARES")
print("-" * WIDTH)

plain_people = PEOPLE - 2
total_shares = plain_people + SHARES_A + SHARES_B

per_share = (total / total_shares).quantize(PENNY, rounding=ROUND_HALF_UP)
plain_total = per_share * plain_people
owed_a = (per_share * SHARES_A).quantize(PENNY, rounding=ROUND_HALF_UP)
owed_b = (per_share * SHARES_B).quantize(PENNY, rounding=ROUND_HALF_UP)
uneven_collected = plain_total + owed_a + owed_b

print(f"{'Portions on the table':<30}{total_shares:>16}")
print(f"{'Price per portion':<30}{per_share:>16}")
print(f"{f'{plain_people} people x 1 portion':<30}{plain_total:>16}")
print(f"{f'Person A x {SHARES_A} portions':<30}{owed_a:>16}")
print(f"{f'Person B x {SHARES_B} portions':<30}{owed_b:>16}")
print("-" * WIDTH)
print(f"{'Collected':<30}{uneven_collected:>16}")
print(f"{'Drift vs. total':<30}{total - uneven_collected:>16}")
print()

# ---------------------------------------------------------------------------
# 4. The same even split in floats, for comparison
# ---------------------------------------------------------------------------
#
# This is not a strawman. It is what the obvious version of this program does,
# and it is why today spent twenty minutes on Decimal.

print("-" * WIDTH)
print("THE SAME EVEN SPLIT, IN FLOATS")
print("-" * WIDTH)

float_total = float(total)
float_share = round(float_total / PEOPLE, 2)
float_collected = round(float_share * PEOPLE, 2)

print(f"{'Each pays':<30}{float_share:>16.2f}")
print(f"{'Collected':<30}{float_collected:>16.2f}")
print(f"{'Equal to total?':<30}{str(float_collected == float_total):>16}")
print(f"{'Raw float product':<30}{float_share * PEOPLE:>16.10f}")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Set BILL = "100.00", TIP_PERCENT = "0", PEOPLE = 3. You should see a
#     base of 33.33 with one penny to hand out. Somebody pays 33.34.
#   * Try PEOPLE = 1, then PEOPLE = 100. The drift should never exceed
#     (PEOPLE - 1) pennies. Convince yourself of that from the arithmetic.
#   * Come back on Day 13 and actually print a per-person list, handing the
#     leftover pennies to the first `pennies_to_hand_out` people.
#   * Come back on Day 31 and turn the round-to-money expression into a
#     function, so `money(x)` replaces every .quantize(...) call in this file.
