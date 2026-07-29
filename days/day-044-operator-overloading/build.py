"""Day 044 build — Money: arithmetic that refuses to mix currencies.

    python3 build.py

The arithmetic is easy. The design decisions are the exercise:

  Money + Money (same currency)      -> Money
  Money + Money (different)          -> raises. 10 GBP + 10 USD is not 20
                                        of anything, and silently returning
                                        20 is worse than any error.
  Money + int                        -> NotImplemented. Money is not a
                                        number; 10 + GBP 5 has no meaning.
  Money * int                        -> Money. Three times the amount.
  Money * Money                      -> undefined. What unit is GBP squared?
  Money / Money                      -> a plain float: a RATIO, not money.

Note the distinction that runs through the whole file: WRONG TYPE returns
NotImplemented, WRONG VALUE raises.
"""

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from functools import total_ordering

WIDTH = 76
PENNY = Decimal("0.01")

SYMBOLS = {"GBP": "£", "USD": "$", "EUR": "€", "JPY": "¥"}
MINOR_UNITS = {"GBP": 2, "USD": 2, "EUR": 2, "JPY": 0}    # yen has no cents


class CurrencyMismatch(ValueError):
    """Raised when an operation would combine two different currencies.

    A subclass of ValueError, so callers who only care that "the value was
    wrong" still catch it — and callers who want to say something specific
    about currencies can.
    """

    def __init__(self, left, right):
        self.left, self.right = left, right
        super().__init__(f"cannot combine {left} and {right}")


@total_ordering
class Money:
    """An exact amount in one currency. Immutable."""

    __slots__ = ("_amount", "_currency")

    def __init__(self, amount, currency="GBP"):
        currency = str(currency).upper()
        if currency not in SYMBOLS:
            raise ValueError(f"unknown currency {currency!r}")
        places = Decimal(10) ** -MINOR_UNITS[currency]
        object.__setattr__(
            self, "_amount",
            Decimal(str(amount)).quantize(places, rounding=ROUND_HALF_UP),
        )
        object.__setattr__(self, "_currency", currency)

    def __setattr__(self, name, value):
        raise AttributeError("Money is immutable")

    @property
    def amount(self):
        return self._amount

    @property
    def currency(self):
        return self._currency

    # -- display -----------------------------------------------------------

    def __repr__(self):
        return f"Money('{self._amount}', {self._currency!r})"

    def __str__(self):
        return f"{SYMBOLS[self._currency]}{self._amount:,}"

    def __format__(self, spec):
        if spec == "code":
            return f"{self._amount:,} {self._currency}"
        if not spec:
            return str(self)
        return f"{SYMBOLS[self._currency]}{self._amount:{spec}}"

    # -- the guard every binary operation uses -----------------------------

    def _same_currency(self, other):
        """Raise if `other` is Money in a different currency."""
        if other._currency != self._currency:
            raise CurrencyMismatch(self._currency, other._currency)

    # -- arithmetic --------------------------------------------------------

    def __add__(self, other):
        if not isinstance(other, Money):
            # WRONG TYPE -> NotImplemented, so Python can try the other side
            # and then produce its own, better, error message.
            return NotImplemented
        # WRONG VALUE -> raise. NotImplemented here would give the useless
        # "unsupported operand type(s) for +: 'Money' and 'Money'".
        self._same_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __radd__(self, other):
        # sum() starts from the integer 0.
        if other == 0:
            return self
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, factor):
        # Money * Money is deliberately absent: GBP squared is not a thing.
        if isinstance(factor, Money) or not isinstance(factor, (int, float, Decimal)):
            return NotImplemented
        return Money(self._amount * Decimal(str(factor)), self._currency)

    __rmul__ = __mul__                      # 3 * money, as well as money * 3

    def __truediv__(self, other):
        if isinstance(other, Money):
            # money / money is a RATIO — a plain number, not money.
            self._same_currency(other)
            if not other._amount:
                raise ZeroDivisionError("division by zero money")
            return float(self._amount / other._amount)
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        if not other:
            raise ZeroDivisionError("division by zero")
        return Money(self._amount / Decimal(str(other)), self._currency)

    def __neg__(self):
        return Money(-self._amount, self._currency)

    def __abs__(self):
        return Money(abs(self._amount), self._currency)

    def __bool__(self):
        return bool(self._amount)

    # -- comparison --------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        # Different currencies are simply NOT EQUAL — this must not raise,
        # or `money in a_list` would explode on the first foreign entry.
        return (self._amount, self._currency) == (other._amount, other._currency)

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        # ORDERING, unlike equality, is meaningless across currencies, so
        # this one raises.
        self._same_currency(other)
        return self._amount < other._amount

    def __hash__(self):
        return hash((self._amount, self._currency))

    # -- the operation operators cannot express ---------------------------

    def allocate(self, ratios):
        """Split into parts that sum EXACTLY back to this amount.

        Day 5's problem, solved properly. Divide, floor every share, then
        hand out the leftover minor units one at a time. No penny is
        created or destroyed.
        """
        if not ratios or any(r < 0 for r in ratios):
            raise ValueError("ratios must be positive")
        places = Decimal(10) ** -MINOR_UNITS[self._currency]
        total_ratio = Decimal(str(sum(ratios)))

        shares = []
        for ratio in ratios:
            share = (self._amount * Decimal(str(ratio)) / total_ratio)
            shares.append(share.quantize(places, rounding=ROUND_DOWN))

        remainder = self._amount - sum(shares)
        units = int(remainder / places)
        for index in range(units):
            shares[index % len(shares)] += places

        return [Money(s, self._currency) for s in shares]


# ===========================================================================
# 1. What it does
# ===========================================================================

rent = Money("875.00")
bills = Money("134.45")
dollars = Money("500", "USD")
yen = Money("12345", "JPY")

print("=" * WIDTH)
print(f"{'MONEY':^{WIDTH}}")
print("=" * WIDTH)

for label, value in [
    ("Money('875.00')", rent),
    ("repr", repr(rent)),
    ("f'{m:code}'", f"{rent:code}"),
    ("JPY has no minor unit", yen),
    ("rounding: '2.675'", Money("2.675")),
    ("rent + bills", rent + bills),
    ("rent - bills", rent - bills),
    ("rent * 12", rent * 12),
    ("3 * bills   (__rmul__)", 3 * bills),
    ("rent / 4", rent / 4),
    ("rent / bills  (a ratio)", f"{rent / bills:.3f}"),
    ("-bills", -bills),
    ("abs(-bills)", abs(-bills)),
    ("bool(Money('0'))", bool(Money("0"))),
    ("sum([...])", sum([rent, bills, Money("10")])),
    ("max([...])", max([rent, bills])),
    ("sorted", sorted([bills, rent, Money("1")])),
    ("rent == Money('875.00')", rent == Money("875.00")),
    ("rent == dollars", rent == dollars),
    ("in a set", len({rent, Money("875.00"), bills})),
]:
    print(f"  {label:<28}{str(value):>{WIDTH - 30}}")

# ===========================================================================
# 2. What it refuses, and with which error
# ===========================================================================

print()
print("-" * WIDTH)
print("WRONG TYPE -> NotImplemented (Python writes the error)")
print("-" * WIDTH)

for label, attempt in [
    ("rent + 100", lambda: rent + 100),
    ("rent + 'a string'", lambda: rent + "a string"),
    ("rent * dollars", lambda: rent * dollars),
    ("rent < 100", lambda: rent < 100),
]:
    try:
        attempt()
        print(f"  {label:<28}ALLOWED — should it be?")
    except TypeError as exc:
        print(f"  {label:<28}TypeError: {exc}")

print()
print("-" * WIDTH)
print("WRONG VALUE -> raise (we write the error)")
print("-" * WIDTH)

for label, attempt in [
    ("rent + dollars", lambda: rent + dollars),
    ("rent < dollars", lambda: rent < dollars),
    ("rent / 0", lambda: rent / 0),
    ("Money('1', 'XYZ')", lambda: Money("1", "XYZ")),
    ("rent.amount = 0", lambda: setattr(rent, "amount", 0)),
]:
    try:
        attempt()
        print(f"  {label:<28}ALLOWED — should it be?")
    except (ValueError, ZeroDivisionError, AttributeError) as exc:
        print(f"  {label:<28}{type(exc).__name__}: {str(exc)[:34]}")

print(f"""
  Note `rent == dollars` did NOT raise — it returned False. Equality across
  currencies is a meaningful question with a clear answer, and raising
  would make `rent in some_list` explode on the first foreign entry.

  But `rent < dollars` DOES raise, because ordering across currencies is
  meaningless without an exchange rate. Same class, two different answers,
  each argued for separately. That is the work.""")

# ===========================================================================
# 3. ALLOCATION — what operators cannot express
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'SPLITTING WITHOUT LOSING A PENNY':^{WIDTH}}")
print("=" * WIDTH)

cases = [
    (Money("100.00"), [1, 1, 1], "three equal ways"),
    (Money("0.05"), [1, 1, 1], "5p three ways"),
    (Money("187.45"), [1, 1, 1, 1, 1, 1, 1], "seven ways"),
    (Money("1000.00"), [70, 20, 10], "70/20/10 split"),
    (Money("12345", "JPY"), [1, 1, 1], "a currency with no minor unit"),
]

all_exact = True
for total, ratios, label in cases:
    parts = total.allocate(ratios)
    rebuilt = sum(parts)
    exact = rebuilt == total
    all_exact = all_exact and exact
    shown = ", ".join(str(p) for p in parts)
    print(f"  {label:<30}{shown[:30]:<32}{'exact' if exact else 'LOST':>8}")

print("-" * WIDTH)
print(f"  {'every split sums back exactly':<44}{str(all_exact):>{WIDTH - 48}}")

naive = Money("100.00") / 3
print(f"""
  The naive version — Money('100.00') / 3 = {naive} — gives three shares
  of {naive} that total {naive * 3}, which is not 100.00.

  allocate() rounds every share DOWN and then distributes the leftover
  minor units one at a time. Nobody differs from anybody by more than a
  penny, and the parts sum back exactly. Day 5 posed this problem and could
  not solve it; a type with its own arithmetic can.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Change __add__ to raise TypeError instead of returning NotImplemented
#     for `rent + 100`, and compare the messages. Yours will be worse.
#
#   * Delete __radd__ and run sum([rent, bills]). Then read the traceback
#     and work out where the 0 came from.
#
#   * `rent == dollars` returns False but `rent < dollars` raises. Argue the
#     opposite position for both, then decide what YOUR API should do and
#     write it in the docstring. Either is defensible; silence is not.
#
#   * Add exchange(rate, to_currency). Now ask whether `rent + dollars`
#     should start working automatically. (It should not — implicit
#     conversion at an unstated rate is how real money goes missing.)
#
#   * On Day 48, rewrite this as @dataclass(frozen=True, order=True) and
#     see which parts it can generate and which it cannot. The currency
#     check is the part it cannot.
