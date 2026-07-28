"""Day 004 build — a receipt printer with columns that actually line up.

Every width in this file comes from a named constant, and every column is
produced by a format spec rather than by typed-in spaces. That is the whole
discipline: if you are pressing the space bar to align something, you are
doing it wrong and it will drift the moment the data changes.

No loops yet (Day 13), so the line items are written out one per statement.
That repetition is uncomfortable on purpose — notice it.

    python3 build.py
"""

# ---------------------------------------------------------------------------
# Layout constants. Change WIDTH and the entire receipt re-flows.
# ---------------------------------------------------------------------------

WIDTH = 44            # total characters per line
QTY_W = 5             # quantity column
PRICE_W = 10          # line-total column
NAME_W = WIDTH - QTY_W - PRICE_W

SHOP = "The Difference Engine Cafe"
ADDRESS = "12 Analytical Row, London"
VAT_RATE = 0.20
SERVICE_RATE = 0.125

# ---------------------------------------------------------------------------
# The order. Name, quantity, unit price.
# ---------------------------------------------------------------------------

item_1 = "Flat white"
qty_1 = 2
unit_1 = 3.40

item_2 = "Almond croissant"
qty_2 = 1
unit_2 = 3.95

item_3 = "Sourdough toast & jam"
qty_3 = 3
unit_3 = 4.25

item_4 = "Tea"
qty_4 = 1
unit_4 = 2.80

line_1 = qty_1 * unit_1
line_2 = qty_2 * unit_2
line_3 = qty_3 * unit_3
line_4 = qty_4 * unit_4

subtotal = line_1 + line_2 + line_3 + line_4
service = subtotal * SERVICE_RATE
vat = (subtotal + service) * VAT_RATE
total = subtotal + service + vat

# ---------------------------------------------------------------------------
# Header — centring done by ^, not by counting spaces
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{SHOP.upper():^{WIDTH}}")
print(f"{ADDRESS:^{WIDTH}}")
print("=" * WIDTH)
print()

# Column headings, using exactly the same widths as the rows below them.
print(f"{'ITEM':<{NAME_W}}{'QTY':>{QTY_W}}{'TOTAL':>{PRICE_W}}")
print("-" * WIDTH)

# ---------------------------------------------------------------------------
# Line items
#
#   :<NAME_W   left-align the name into its column
#   :>QTY_W    right-align the quantity
#   :>PRICE_W.2f  right-align the money to exactly two decimal places
#
# Long names overflow rather than truncate, which would break the alignment.
# The slice keeps every row honest.
# ---------------------------------------------------------------------------

print(f"{item_1[:NAME_W - 1]:<{NAME_W}}{qty_1:>{QTY_W}}{line_1:>{PRICE_W}.2f}")
print(f"{item_2[:NAME_W - 1]:<{NAME_W}}{qty_2:>{QTY_W}}{line_2:>{PRICE_W}.2f}")
print(f"{item_3[:NAME_W - 1]:<{NAME_W}}{qty_3:>{QTY_W}}{line_3:>{PRICE_W}.2f}")
print(f"{item_4[:NAME_W - 1]:<{NAME_W}}{qty_4:>{QTY_W}}{line_4:>{PRICE_W}.2f}")

print("-" * WIDTH)

# ---------------------------------------------------------------------------
# Totals — label right-aligned against the money column, so the numbers stack
# ---------------------------------------------------------------------------

LABEL_W = WIDTH - PRICE_W

print(f"{'Subtotal':>{LABEL_W}}{subtotal:>{PRICE_W}.2f}")
print(f"{f'Service ({SERVICE_RATE:.1%})':>{LABEL_W}}{service:>{PRICE_W}.2f}")
print(f"{f'VAT ({VAT_RATE:.0%})':>{LABEL_W}}{vat:>{PRICE_W}.2f}")
print("=" * WIDTH)
print(f"{'TOTAL':>{LABEL_W}}{total:>{PRICE_W}.2f}")
print("=" * WIDTH)
print()

# ---------------------------------------------------------------------------
# A dot-leader summary — the other classic receipt shape, and a good use of
# a fill character. Note that nothing here counts spaces either.
# ---------------------------------------------------------------------------

print(f"{'Items on this bill':.<{WIDTH - 6}}{qty_1 + qty_2 + qty_3 + qty_4:>6}")
print(f"{'Distinct products':.<{WIDTH - 6}}{4:>6}")
print(f"{'Average line value':.<{WIDTH - 6}}{subtotal / 4:>6.2f}")
print()

print(f"{'Thank you':^{WIDTH}}")
print(f"{'served by Ada':^{WIDTH}}")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Set WIDTH = 60 and run it. Every rule, every column and every centred
#     line should move together. If one does not, it has a hard-coded number.
#   * Set item_3 to a 40-character name. The slice keeps the row aligned —
#     decide whether truncating or wrapping is the better answer, and say why.
#   * Add a "unit price" column between name and quantity without touching any
#     of the printing code except the widths.
#   * Print the totals block with the money right-aligned but the labels
#     LEFT-aligned, using a dot leader between them. One format spec each.
