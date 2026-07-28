"""BUG 3 — a contact formatter.

Three contacts. Two of them format perfectly. The third one is not malformed
— it is simply a person whose name has a different number of parts than the
programmer assumed. That distinction matters when you decide how to fix it.
"""

CONTACT_1 = "Ada Augusta Lovelace|ada@example.com"
CONTACT_2 = "Charles Babbage|charles@example.com"
CONTACT_3 = "Prince|prince@example.com"

print(f"{'FIRST':<12}{'MIDDLE':<12}{'LAST':<12}{'EMAIL':<24}")
print("-" * 60)

name_1 = CONTACT_1.split("|")[0]
email_1 = CONTACT_1.split("|")[1]
parts_1 = name_1.split()
print(f"{parts_1[0]:<12}{parts_1[1]:<12}{parts_1[2]:<12}{email_1:<24}")

name_2 = CONTACT_2.split("|")[0]
email_2 = CONTACT_2.split("|")[1]
parts_2 = name_2.split()
print(f"{parts_2[0]:<12}{'':<12}{parts_2[1]:<12}{email_2:<24}")

name_3 = CONTACT_3.split("|")[0]
email_3 = CONTACT_3.split("|")[1]
parts_3 = name_3.split()
print(f"{parts_3[0]:<12}{'':<12}{parts_3[1]:<12}{email_3:<24}")
