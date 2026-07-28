"""BUG 4 — a temperature report.

One character is wrong. The traceback names it exactly, which makes this the
easiest bug of the five — provided you actually read the last line instead of
panicking at the first.
"""

CITY = "Reykjavik"
celsius_reading = -3.5

fahrenheit = celsius_reading * 9 / 5 + 32
kelvin = celcius_reading + 273.15

print(f"{CITY}")
print(f"  {celsius_reading:>8.1f} C")
print(f"  {fahrenheit:>8.1f} F")
print(f"  {kelvin:>8.1f} K")
