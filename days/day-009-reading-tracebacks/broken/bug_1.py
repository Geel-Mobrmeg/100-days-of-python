"""BUG 1 — a shipping cost calculator.

It works on the first order and dies on the second. Run it, read the
traceback, and fix it. Do not change the DATA; the data is what real data
looks like.
"""

ORDER_A = "1043,Cairo,2,14.50"
ORDER_B = "1044,Alexandria,3.0,22.00"

FREE_SHIPPING_OVER = 50.00
SHIPPING_FLAT = 4.99

print("order          city          qty     goods  shipping")
print("-" * 56)

ref_a = ORDER_A.split(",")[0]
city_a = ORDER_A.split(",")[1]
qty_a = int(ORDER_A.split(",")[2])
price_a = float(ORDER_A.split(",")[3])
goods_a = qty_a * price_a
ship_a = SHIPPING_FLAT * (goods_a < FREE_SHIPPING_OVER)
print(f"{ref_a:<15}{city_a:<14}{qty_a:>3}{goods_a:>10.2f}{ship_a:>10.2f}")

ref_b = ORDER_B.split(",")[0]
city_b = ORDER_B.split(",")[1]
qty_b = int(ORDER_B.split(",")[2])
price_b = float(ORDER_B.split(",")[3])
goods_b = qty_b * price_b
ship_b = SHIPPING_FLAT * (goods_b < FREE_SHIPPING_OVER)
print(f"{ref_b:<15}{city_b:<14}{qty_b:>3}{goods_b:>10.2f}{ship_b:>10.2f}")
