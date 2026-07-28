"""BUG 2 — a receipt footer.

The numbers are all correct. The program still will not print them.
"""

SUBTOTAL = 26.30
SERVICE = 3.29
VAT = 5.92

total = SUBTOTAL + SERVICE + VAT
items = 7

print("Subtotal: " + SUBTOTAL)
print("Service:  " + SERVICE)
print("VAT:      " + VAT)
print("Total:    " + total)
print("Items:    " + items)
