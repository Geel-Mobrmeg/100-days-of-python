"""Example: a file report, using six of the toolkit's functions together.

    python3 examples/report.py

This is the example the README promises. It exists because "here are the
functions" is documentation and "here is them doing a real job" is what
persuades somebody to install it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mytoolkit import chunked, human_bytes, percent, slugify, truncate, unique

FILES = [
    ("Quarterly Report: Final Version (2024).pdf", 4_812_004),
    ("notes.txt", 812),
    ("Very Long Presentation About Nothing.pptx", 91_000_000),
    ("notes.txt", 812),
    ("budget-2024.xlsx", 240_118),
]

names = unique(name for name, _ in FILES)
sizes = dict(FILES)
total = sum(sizes[name] for name in names)

print(f"{'FILE':<38}{'SIZE':>10}{'SHARE':>9}")
print("-" * 57)
for name in names:
    print(f"{truncate(name, 36):<38}"
          f"{human_bytes(sizes[name]):>10}"
          f"{percent(sizes[name], total):>9}")
print("-" * 57)
print(f"{'TOTAL':<38}{human_bytes(total):>10}")

print("\nslugs:")
for batch in chunked([slugify(n) for n in names], 2):
    print("   " + "   ".join(f"{s[:24]:<24}" for s in batch))

print(f"\n{len(FILES)} entries, {len(names)} distinct "
      f"({percent(len(names), len(FILES))} unique)")
