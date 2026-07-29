"""Day 050 MILESTONE — an inventory system, modelled as objects.

    python3 build.py                 # the scripted demonstration
    python3 build.py --interactive   # the demonstration, then a prompt
    printf 'list\\nprice WID-001 60\\nlow\\nquit\\n' | python3 build.py -i

Everything from Phase 5:

  Day 41  classes with invariants          Warehouse, Order
  Day 42  class attributes, classmethods   sequential order references
  Day 43  dunder methods                   Sku, Quantity in sets and dicts
  Day 44  operator overloading             Money and Quantity arithmetic
  Day 45  inheritance                      the pricing hierarchy
  Day 46  COMPOSITION                      Warehouse HAS a policy, HAS a log
  Day 47  properties                       validated on every route
  Day 48  dataclasses                      Sku, Money, Quantity, Product
  Day 49  ABC and Protocol                 PricingRule, AuditSink

The design rule, and the reason this file is worth reading twice:

    VALUES ARE FROZEN DATACLASSES. THINGS ARE PLAIN CLASSES.
    Sku, Money, Quantity, Product     -> values
    Warehouse, Order                  -> things

Day 48 argued that; this is it applied to a whole system.
"""

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol, runtime_checkable

WIDTH = 78
PENNY = Decimal("0.01")


# ###########################################################################
# VALUES — frozen dataclasses. Immutable, hashable, compared by content.
# ###########################################################################

@dataclass(frozen=True, order=True, slots=True)
class Sku:
    """A stock code. A VALUE: two Skus with the same code ARE the same sku."""

    code: str

    def __post_init__(self):
        code = self.code.strip().upper()
        if not code or len(code) < 3:
            raise ValueError(f"sku {self.code!r} is too short")
        object.__setattr__(self, "code", code)

    def __str__(self):
        return self.code


@dataclass(frozen=True, order=True, slots=True)
class Money:
    """Day 44's Money, as a dataclass. Note what could NOT be generated."""

    amount: Decimal
    currency: str = "GBP"

    def __post_init__(self):
        object.__setattr__(
            self, "amount",
            Decimal(str(self.amount)).quantize(PENNY, rounding=ROUND_HALF_UP),
        )

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:          # NOT generatable
            raise ValueError(f"cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        return self if other == 0 else NotImplemented

    def __sub__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError(f"cannot subtract {other.currency} from {self.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        if isinstance(factor, Money) or not isinstance(factor, (int, Decimal)):
            return NotImplemented
        return Money(self.amount * Decimal(factor), self.currency)

    __rmul__ = __mul__

    def __str__(self):
        return f"£{self.amount:,}" if self.currency == "GBP" else \
            f"{self.amount:,} {self.currency}"


@dataclass(frozen=True, order=True, slots=True)
class Quantity:
    """A count of units. Cannot be negative, ever."""

    units: int

    def __post_init__(self):
        if not isinstance(self.units, int) or isinstance(self.units, bool):
            raise TypeError(f"quantity must be a whole number, got {self.units!r}")
        if self.units < 0:
            raise ValueError(f"quantity cannot be negative: {self.units}")

    def __add__(self, other):
        return Quantity(self.units + other.units) if isinstance(other, Quantity) \
            else NotImplemented

    def __sub__(self, other):
        # Quantity's __post_init__ refuses the negative, so an over-issue
        # cannot silently produce nonsense — it raises at the VALUE level,
        # before any Warehouse logic gets involved.
        return Quantity(self.units - other.units) if isinstance(other, Quantity) \
            else NotImplemented

    def __bool__(self):
        return bool(self.units)

    def __str__(self):
        return f"{self.units:,}"


@dataclass(frozen=True, slots=True)
class Product:
    """A catalogue entry. A VALUE — it describes, it does not do."""

    sku: Sku
    name: str
    cost: Money
    category: str = "general"
    reorder_level: Quantity = field(default_factory=lambda: Quantity(10))
    perishable: bool = False

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("a product needs a name")


# ###########################################################################
# INTERFACES — Day 49
# ###########################################################################

class PricingRule(ABC):
    """An ABC: we own every implementation, and describe() is shared."""

    @abstractmethod
    def price_for(self, product: Product, quantity: Quantity) -> Money:
        """Return the unit price for buying this many."""

    @property
    def name(self):
        return type(self).__name__.replace("Pricing", "")

    def describe(self):
        return f"{self.name}"


@runtime_checkable
class AuditSink(Protocol):
    """A Protocol: the caller may supply anything with .record()."""

    def record(self, event: str, detail: dict) -> None: ...


# ###########################################################################
# PRICING — Day 45's inheritance, used where it genuinely fits
# ###########################################################################

class CostPlusPricing(PricingRule):
    def __init__(self, margin=Decimal("0.40")):
        self.margin = Decimal(str(margin))

    def price_for(self, product, quantity):
        return product.cost * (1 + self.margin)

    def describe(self):
        return f"{self.name} (+{self.margin:.0%})"


class BulkDiscountPricing(CostPlusPricing):
    """A genuine is-a: it IS cost-plus, with a break. Substitutable."""

    def __init__(self, margin=Decimal("0.40"), threshold=50,
                 discount=Decimal("0.15")):
        super().__init__(margin)
        self.threshold = threshold
        self.discount = Decimal(str(discount))

    def price_for(self, product, quantity):
        base = super().price_for(product, quantity)
        if quantity.units >= self.threshold:
            return base * (1 - self.discount)
        return base

    def describe(self):
        return (f"{self.name} (+{self.margin:.0%}, "
                f"-{self.discount:.0%} over {self.threshold})")


class ClearancePricing(PricingRule):
    """NOT a subclass of CostPlusPricing — it ignores margin entirely."""

    def __init__(self, of_cost=Decimal("0.60")):
        self.of_cost = Decimal(str(of_cost))

    def price_for(self, product, quantity):
        return product.cost * self.of_cost

    def describe(self):
        return f"{self.name} ({self.of_cost:.0%} of cost)"


# ###########################################################################
# AUDIT SINKS — composition, so the warehouse can be tested
# ###########################################################################

class ListAudit:
    def __init__(self):
        self.events = []

    def record(self, event, detail):
        self.events.append((event, detail))


class NullAudit:
    def record(self, event, detail):
        pass


# ###########################################################################
# THINGS — plain classes with identity, invariants and behaviour
# ###########################################################################

class InsufficientStock(Exception):
    def __init__(self, sku, wanted, available):
        self.sku, self.wanted, self.available = sku, wanted, available
        super().__init__(f"{sku}: wanted {wanted}, only {available} available")


class Warehouse:
    """Holds stock. A THING: two warehouses with identical stock are not
    the same warehouse, so the DEFAULT identity-based __eq__ is correct and
    a dataclass would have been wrong (Day 48).

    COMPOSITION (Day 46): the pricing rule and the audit sink are
    CONSTRUCTOR ARGUMENTS, not base classes. That is what makes the tests
    at the bottom possible without any mocking library.

    INVARIANTS, true after every public method:
      1. no quantity is ever negative
      2. on_hand == received - issued, for every sku
    """

    def __init__(self, name, pricing=None, audit=None):
        self.name = name
        self.pricing = pricing or CostPlusPricing()
        self.audit = audit or NullAudit()
        self._products = {}                       # Sku -> Product
        self._stock = {}                          # Sku -> Quantity
        self._received = {}
        self._issued = {}

    # -- catalogue --------------------------------------------------------

    def add_product(self, product):
        if product.sku in self._products:
            raise ValueError(f"{product.sku} is already in the catalogue")
        self._products[product.sku] = product
        self._stock[product.sku] = Quantity(0)
        self._received[product.sku] = Quantity(0)
        self._issued[product.sku] = Quantity(0)
        self.audit.record("product_added", {"sku": str(product.sku)})

    def product(self, sku):
        if sku not in self._products:
            raise KeyError(f"{sku} is not in the catalogue")
        return self._products[sku]

    # -- stock ------------------------------------------------------------

    def stock_of(self, sku):
        return self._stock.get(sku, Quantity(0))

    def receive(self, sku, quantity):
        """Check first, mutate second (Day 41)."""
        self.product(sku)                          # raises if unknown
        if not quantity:
            raise ValueError("cannot receive zero units")
        self._stock[sku] = self._stock[sku] + quantity
        self._received[sku] = self._received[sku] + quantity
        self.audit.record("received", {"sku": str(sku), "qty": quantity.units})

    def issue(self, sku, quantity):
        self.product(sku)
        available = self.stock_of(sku)
        if quantity.units > available.units:
            raise InsufficientStock(sku, quantity, available)
        self._stock[sku] = self._stock[sku] - quantity
        self._issued[sku] = self._issued[sku] + quantity
        self.audit.record("issued", {"sku": str(sku), "qty": quantity.units})

    # -- derived (Day 47: computed, never stored) -------------------------

    @property
    def skus(self):
        return sorted(self._products)

    @property
    def total_units(self):
        return sum((q.units for q in self._stock.values()), 0)

    @property
    def stock_value(self):
        total = Money(0)
        for sku, quantity in self._stock.items():
            total = total + self._products[sku].cost * quantity.units
        return total

    @property
    def below_reorder(self):
        return [s for s in self.skus
                if self._stock[s] < self._products[s].reorder_level]

    def price_of(self, sku, quantity):
        return self.pricing.price_for(self.product(sku), quantity)

    def check_invariants(self):
        problems = []
        for sku in self._products:
            if self._stock[sku].units < 0:
                problems.append(f"{sku}: negative stock")
            expected = self._received[sku].units - self._issued[sku].units
            if self._stock[sku].units != expected:
                problems.append(
                    f"{sku}: {self._stock[sku]} != received-issued ({expected})"
                )
        return problems

    def __repr__(self):
        return (f"Warehouse({self.name!r}, {len(self._products)} products, "
                f"{self.total_units:,} units)")


class Order:
    """A customer order. A THING with a lifecycle and a sequential id."""

    _next_reference = 1000                         # Day 42's class counter

    def __init__(self, customer, warehouse):
        self.reference = f"ORD-{Order._next_reference}"
        Order._next_reference += 1                 # THROUGH THE CLASS
        self.customer = customer
        self.warehouse = warehouse
        self.placed = date.today()
        self.lines = []
        self.status = "draft"

    @classmethod
    def reset_references(cls):
        cls._next_reference = 1000

    def add(self, sku, quantity):
        if self.status != "draft":
            raise ValueError(f"cannot add to a {self.status} order")
        available = self.warehouse.stock_of(sku)
        if quantity.units > available.units:
            raise InsufficientStock(sku, quantity, available)
        unit_price = self.warehouse.price_of(sku, quantity)
        self.lines.append((sku, quantity, unit_price))

    @property
    def total(self):
        return sum((price * qty.units for _, qty, price in self.lines),
                   Money(0))

    @property
    def unit_count(self):
        return sum(q.units for _, q, _ in self.lines)

    def confirm(self):
        """All-or-nothing: check EVERY line before issuing ANY of them."""
        if self.status != "draft":
            raise ValueError(f"already {self.status}")
        if not self.lines:
            raise ValueError("cannot confirm an empty order")

        for sku, quantity, _ in self.lines:        # check first...
            if quantity.units > self.warehouse.stock_of(sku).units:
                raise InsufficientStock(
                    sku, quantity, self.warehouse.stock_of(sku)
                )
        for sku, quantity, _ in self.lines:        # ...then mutate
            self.warehouse.issue(sku, quantity)
        self.status = "confirmed"

    def __repr__(self):
        return (f"Order({self.reference}, {self.customer!r}, "
                f"{len(self.lines)} lines, {self.total}, {self.status})")


# ###########################################################################
# THE DEMONSTRATION
# ###########################################################################

def build_warehouse(pricing=None, audit=None):
    warehouse = Warehouse("Leeds", pricing=pricing, audit=audit)
    catalogue = [
        Product(Sku("wid-001"), "Widget", Money("4.50"), "hardware",
                Quantity(20)),
        Product(Sku("gzm-002"), "Gizmo", Money("12.00"), "hardware",
                Quantity(10)),
        Product(Sku("dhk-003"), "Doohickey", Money("2.25"), "consumable",
                Quantity(100)),
        Product(Sku("thg-004"), "Thingummy", Money("48.00"), "premium",
                Quantity(5)),
    ]
    for product in catalogue:
        warehouse.add_product(product)
    for sku, units in [("WID-001", 150), ("GZM-002", 40),
                       ("DHK-003", 80), ("THG-004", 3)]:
        warehouse.receive(Sku(sku), Quantity(units))
    return warehouse


audit = ListAudit()
warehouse = build_warehouse(
    pricing=BulkDiscountPricing(margin=Decimal("0.40"), threshold=50),
    audit=audit,
)

print("=" * WIDTH)
print(f"{'INVENTORY':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'warehouse':<24}{warehouse.name:>{WIDTH - 24}}")
print(f"{'pricing rule':<24}{warehouse.pricing.describe():>{WIDTH - 24}}")
print(f"{'products':<24}{len(warehouse.skus):>{WIDTH - 24}}")
print(f"{'units on hand':<24}{warehouse.total_units:>{WIDTH - 24},}")
print(f"{'stock at cost':<24}{str(warehouse.stock_value):>{WIDTH - 24}}")

print()
print(f"{'SKU':<10}{'PRODUCT':<14}{'CATEGORY':<12}{'COST':>9}"
      f"{'STOCK':>8}{'REORDER':>9}  {'':<8}")
print("-" * WIDTH)
for sku in warehouse.skus:
    product = warehouse.product(sku)
    stock = warehouse.stock_of(sku)
    flag = "LOW" if sku in warehouse.below_reorder else ""
    print(f"{str(sku):<10}{product.name:<14}{product.category:<12}"
          f"{str(product.cost):>9}{str(stock):>8}"
          f"{str(product.reorder_level):>9}  {flag:<8}")

print("-" * WIDTH)
print(f"{'below reorder level':<40}"
      f"{', '.join(str(s) for s in warehouse.below_reorder) or 'none':>{WIDTH - 40}}")

# ---------------------------------------------------------------------------
# Pricing rules are interchangeable — Day 45 and 49 together
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("THE SAME PRODUCT, THREE PRICING RULES, ONE CALL SITE")
print("-" * WIDTH)

rules = [CostPlusPricing(), BulkDiscountPricing(threshold=50),
         ClearancePricing()]
widget = Sku("WID-001")

print(f"  {'RULE':<40}{'qty 1':>12}{'qty 100':>12}")
for rule in rules:
    shop = build_warehouse(pricing=rule)
    one = shop.price_of(widget, Quantity(1))
    hundred = shop.price_of(widget, Quantity(100))
    print(f"  {rule.describe():<40}{str(one):>12}{str(hundred):>12}")

print("""
  price_of() is one line and never asks which rule it has. BulkDiscount IS
  a CostPlus (a genuine is-a, substitutable), Clearance is not and does not
  pretend to be — both satisfy PricingRule and that is all the warehouse
  needs.""")

# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("ORDERS")
print("-" * WIDTH)

order = Order("Babbage & Co", warehouse)
order.add(Sku("WID-001"), Quantity(60))
order.add(Sku("GZM-002"), Quantity(5))
order.add(Sku("DHK-003"), Quantity(20))

print(f"  {order!r}")
print(f"  {'SKU':<10}{'QTY':>6}{'UNIT':>12}{'LINE':>14}")
for sku, quantity, price in order.lines:
    print(f"  {str(sku):<10}{str(quantity):>6}{str(price):>12}"
          f"{str(price * quantity.units):>14}")
print(f"  {'':<10}{'':>6}{'TOTAL':>12}{str(order.total):>14}")

before = warehouse.stock_of(Sku("WID-001"))
order.confirm()
after = warehouse.stock_of(Sku("WID-001"))
print(f"\n  confirmed. WID-001 stock {before} -> {after}")
print(f"  audit events recorded: {len(audit.events)}")

# ---------------------------------------------------------------------------
# What it refuses
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'WHAT THE MODEL REFUSES':^{WIDTH}}")
print("=" * WIDTH)

stock_before = dict(warehouse._stock)
refusals = [
    ("Quantity(-5)", lambda: Quantity(-5)),
    ("Quantity(1.5)", lambda: Quantity(1.5)),
    ("Sku('ab')", lambda: Sku("ab")),
    ("Money('5','GBP') + Money('5','USD')",
     lambda: Money("5", "GBP") + Money("5", "USD")),
    ("issue more than held",
     lambda: warehouse.issue(Sku("THG-004"), Quantity(999))),
    ("issue an unknown sku",
     lambda: warehouse.issue(Sku("NOPE-999"), Quantity(1))),
    ("duplicate product",
     lambda: warehouse.add_product(
         Product(Sku("WID-001"), "Widget", Money("1")))),
    ("order more than available",
     lambda: Order("X", warehouse).add(Sku("THG-004"), Quantity(999))),
    ("add to a confirmed order",
     lambda: order.add(Sku("WID-001"), Quantity(1))),
    ("confirm an empty order",
     lambda: Order("X", warehouse).confirm()),
    ("mutate a frozen value",
     lambda: setattr(warehouse.product(Sku("WID-001")), "name", "x")),
]

for label, attempt in refusals:
    try:
        attempt()
        print(f"  {label:<42}ALLOWED — should it be?")
    except Exception as exc:                       # noqa: BLE001
        print(f"  {label:<42}{type(exc).__name__}")

print()
print(f"  {'stock unchanged by all eleven refusals':<42}"
      f"{str(dict(warehouse._stock) == stock_before):>10}")
print(f"  {'invariants still hold':<42}"
      f"{str(not warehouse.check_invariants()):>10}")

# ---------------------------------------------------------------------------
# All-or-nothing confirmation
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("ALL-OR-NOTHING: a partly-fillable order changes NOTHING")
print("-" * WIDTH)

fresh = build_warehouse()
partial = Order("Optimist Ltd", fresh)
partial.add(Sku("WID-001"), Quantity(10))          # fine
partial.add(Sku("THG-004"), Quantity(3))           # exactly all of it
fresh.issue(Sku("THG-004"), Quantity(3))           # somebody else took them

print("  order: 10x WID-001 (plenty in stock) + 3x THG-004 (all there was)")
print("  ...then somebody else issued the last 3 THG-004 before we confirmed")

stock_before = {s: fresh.stock_of(s).units for s in fresh.skus}
try:
    partial.confirm()
except InsufficientStock as exc:
    print(f"  confirm() raised: {exc}")
stock_after = {s: fresh.stock_of(s).units for s in fresh.skus}

print(f"  {'the WID-001 line was NOT issued':<42}"
      f"{str(stock_before == stock_after):>10}")
print(f"  {'order status':<42}{partial.status:>10}")
print("""
  confirm() checks EVERY line before issuing ANY. Without that loop, the
  widgets would have shipped and the order would have failed halfway —
  leaving stock reduced for an order that does not exist. Day 41's
  check-first-mutate-second, at transaction scale.""")

# ---------------------------------------------------------------------------
# Testing, without any mocking
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'WHY COMPOSITION MADE THIS TESTABLE':^{WIDTH}}")
print("=" * WIDTH)

spy = ListAudit()
test_warehouse = build_warehouse(pricing=ClearancePricing(), audit=spy)
test_warehouse.issue(Sku("WID-001"), Quantity(5))

last_event, last_detail = spy.events[-1]
detail = " ".join(f"{k}={v}" for k, v in last_detail.items())
print(f"  {'audit events captured':<44}{len(spy.events):>{WIDTH - 48}}")
print(f"  {'the last one':<28}{last_event + ': ' + detail:>{WIDTH - 32}}")
print(f"  {'pricing swapped for the test':<44}"
      f"{test_warehouse.pricing.name:>{WIDTH - 48}}")
print("""
  Two constructor arguments. No mocking library, no monkeypatching, no
  subclass of the thing being tested.

  If Warehouse had INHERITED its pricing and its logging (the shape Day 46
  started with), every one of those would have needed a parallel subclass —
  and you would be testing the subclass, not the warehouse.""")

# ---------------------------------------------------------------------------
# The invariants, attacked
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("INVARIANTS UNDER RANDOM OPERATIONS")
print("-" * WIDTH)

import random                                      # noqa: E402

random.seed(50)
victim = build_warehouse()
allowed = refused = 0
for _ in range(4000):
    sku = random.choice(victim.skus)
    quantity = Quantity(random.randint(1, 60))
    try:
        if random.random() < 0.5:
            victim.receive(sku, quantity)
        else:
            victim.issue(sku, quantity)
        allowed += 1
    except (InsufficientStock, ValueError):
        refused += 1
    if victim.check_invariants():
        break

problems = victim.check_invariants()
print(f"  {'operations attempted':<44}{4000:>{WIDTH - 48},}")
print(f"  {'allowed / refused':<44}"
      f"{f'{allowed:,} / {refused:,}':>{WIDTH - 48}}")
print(f"  {'no negative stock':<44}"
      f"{str(all(victim.stock_of(s).units >= 0 for s in victim.skus)):>{WIDTH - 48}}")
print(f"  {'stock == received - issued, every sku':<44}"
      f"{str(not problems):>{WIDTH - 48}}")
for problem in problems:
    print(f"    {problem}")

print()
print("=" * WIDTH)
print("""VALUES ARE FROZEN DATACLASSES. THINGS ARE PLAIN CLASSES.

  Sku, Money, Quantity, Product     immutable, hashable, compared by
                                    content, safe to share, and impossible
                                    to put into an invalid state

  Warehouse, Order                  identity, invariants, behaviour, and a
                                    lifecycle — where a generated __eq__
                                    would have been a bug

  Quantity refusing to be negative is the neatest part of the whole model:
  an over-issue cannot produce nonsense at the WAREHOUSE level, because the
  VALUE level will not construct it. The invariant is enforced by the type,
  not by remembering to check.""")
print("=" * WIDTH)


# ###########################################################################
# INTERACTIVE
# ###########################################################################

if {"--interactive", "-i"} & set(sys.argv):
    shop = build_warehouse(pricing=BulkDiscountPricing())
    Order.reset_references()
    print("\ncommands: list | stock SKU | price SKU QTY | receive SKU N |")
    print("          issue SKU N | low | value | quit")
    while True:
        try:
            raw = input("\n> ").strip().split()
        except EOFError:
            break
        if not raw:
            continue
        verb, args = raw[0].lower(), raw[1:]
        try:
            if verb in ("quit", "q"):
                break
            elif verb == "list":
                for s in shop.skus:
                    print(f"  {s}  {shop.product(s).name:<14}"
                          f"{str(shop.stock_of(s)):>8}")
            elif verb == "stock" and args:
                s = Sku(args[0])
                print(f"  {shop.product(s).name}: {shop.stock_of(s)} units")
            elif verb == "price" and len(args) >= 2:
                s, q = Sku(args[0]), Quantity(int(args[1]))
                print(f"  {shop.price_of(s, q)} each, "
                      f"{shop.price_of(s, q) * q.units} total")
            elif verb == "receive" and len(args) >= 2:
                shop.receive(Sku(args[0]), Quantity(int(args[1])))
                print(f"  now {shop.stock_of(Sku(args[0]))}")
            elif verb == "issue" and len(args) >= 2:
                shop.issue(Sku(args[0]), Quantity(int(args[1])))
                print(f"  now {shop.stock_of(Sku(args[0]))}")
            elif verb == "low":
                print(f"  {[str(s) for s in shop.below_reorder] or 'none'}")
            elif verb == "value":
                print(f"  {shop.stock_value}")
            else:
                print("  unknown command")
        except Exception as exc:                   # noqa: BLE001
            print(f"  {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Make Warehouse a @dataclass. The generated __eq__ says two warehouses
#     with identical stock are the same warehouse. Decide whether that is
#     ever what you want.
#
#   * Delete Quantity's negative check and re-run the invariant attack. The
#     warehouse-level checks catch it — but LATER, and with a worse message.
#     Enforcing at the value level means the bad state never exists.
#
#   * Add a fourth pricing rule. Nothing outside it changes.
#
#   * confirm() checks every line then issues every line. Between those two
#     loops another thread could take the stock (Day 92). Work out what a
#     real system does about that — the answer is a lock, or a database
#     transaction (Day 84).
#
#   * On Day 57 write the pytest suite. Note that ListAudit and the
#     pluggable pricing mean you need almost no fixtures.
