"""Day 041 build — a BankAccount that cannot be made to go negative.

    python3 build.py

The deposits and withdrawals are the easy part. The interesting part is the
INVARIANT: `balance` must never be negative, and `balance` must always equal
the sum of the history. A class is where a rule like that can live, because
every route to changing the balance goes through a method that enforces it.

The last section attacks the account with every sequence it can think of and
checks the invariants survive.
"""

from decimal import Decimal, ROUND_HALF_UP

WIDTH = 76
PENNY = Decimal("0.01")


class InsufficientFunds(Exception):
    """Raised when a withdrawal would take the balance below zero.

    A custom exception (Day 52) so callers can catch THIS specifically
    rather than a bare ValueError that could mean anything.
    """

    def __init__(self, requested, available):
        self.requested = requested
        self.available = available
        super().__init__(
            f"cannot withdraw {requested}: only {available} available"
        )


class BankAccount:
    """A current account with a non-negative balance and a full history.

    INVARIANTS — true after every public method returns:
      1. balance >= 0
      2. balance == opening balance + sum of every history entry
      3. len(history) only ever grows
    """

    def __init__(self, owner, opening_balance="0.00"):
        if not owner or not owner.strip():
            raise ValueError("an account needs an owner")

        opening = Decimal(str(opening_balance)).quantize(
            PENNY, rounding=ROUND_HALF_UP
        )
        if opening < 0:
            raise ValueError(f"cannot open an account at {opening}")

        self.owner = owner.strip()
        self.opening_balance = opening
        self.balance = opening
        # NOT history=[] as a default (Day 32) — a new list per account.
        self.history = []

    # -- queries: return a value, change nothing --------------------------

    def can_withdraw(self, amount):
        """Return True if `amount` could be withdrawn right now."""
        return Decimal(str(amount)) <= self.balance

    def statement(self):
        """Return the full history as lines of text."""
        lines = [f"{'DATE':<6}{'TYPE':<12}{'AMOUNT':>12}{'BALANCE':>12}"]
        running = self.opening_balance
        lines.append(f"{'':<6}{'opening':<12}{'':>12}{running:>12}")
        for index, (kind, amount, note) in enumerate(self.history, start=1):
            running += amount
            lines.append(f"{index:<6}{kind:<12}{amount:>12}{running:>12}")
        return lines

    def total_deposited(self):
        return sum((a for _, a, _ in self.history if a > 0), Decimal("0.00"))

    def total_withdrawn(self):
        return -sum((a for _, a, _ in self.history if a < 0), Decimal("0.00"))

    # -- commands: change the object, return None -------------------------

    def deposit(self, amount, note=""):
        """Add to the balance. Returns None, like list.append (Day 21)."""
        value = Decimal(str(amount)).quantize(PENNY, rounding=ROUND_HALF_UP)
        if value <= 0:
            raise ValueError(f"a deposit must be positive, got {value}")
        self.balance += value
        self.history.append(("deposit", value, note))

    def withdraw(self, amount, note=""):
        """Take from the balance, or raise InsufficientFunds.

        THE INVARIANT IS ENFORCED HERE, before anything changes. Check
        first, mutate second — so a refused withdrawal leaves the object
        exactly as it was, with nothing half-applied.
        """
        value = Decimal(str(amount)).quantize(PENNY, rounding=ROUND_HALF_UP)
        if value <= 0:
            raise ValueError(f"a withdrawal must be positive, got {value}")
        if value > self.balance:
            raise InsufficientFunds(value, self.balance)
        self.balance -= value
        self.history.append(("withdrawal", -value, note))

    def transfer_to(self, other, amount, note=""):
        """Move money to another account.

        Withdraw FIRST, deposit second. If the withdrawal raises, nothing
        has happened to either account — money cannot be created by a
        failed transfer. Doing it the other way round can.
        """
        if other is self:
            raise ValueError("cannot transfer to the same account")
        self.withdraw(amount, note or f"to {other.owner}")
        other.deposit(amount, note or f"from {self.owner}")

    # -- the invariants, as code ------------------------------------------

    def check_invariants(self):
        """Return a list of any invariant currently violated."""
        problems = []
        if self.balance < 0:
            problems.append(f"balance is negative: {self.balance}")
        expected = self.opening_balance + sum(
            (a for _, a, _ in self.history), Decimal("0.00")
        )
        if self.balance != expected:
            problems.append(
                f"balance {self.balance} != history total {expected}"
            )
        return problems

    def __repr__(self):
        return (f"BankAccount(owner={self.owner!r}, "
                f"balance={self.balance}, entries={len(self.history)})")

    def __str__(self):
        return f"{self.owner}: {self.balance}"


# ===========================================================================
# A normal session
# ===========================================================================

print("=" * WIDTH)
print(f"{'BANK ACCOUNT':^{WIDTH}}")
print("=" * WIDTH)

ada = BankAccount("Ada Lovelace", "250.00")
alan = BankAccount("Alan Turing", "80.00")

ada.deposit("1200.00", "salary")
ada.withdraw("45.50", "groceries")
ada.withdraw("875.00", "rent")
ada.deposit("12.34", "refund")
ada.transfer_to(alan, "100.00", "birthday")

print(f"{ada!r}")
print(f"{alan!r}")
print()
for line in ada.statement():
    print("  " + line)
print()
print(f"  {'total deposited':<30}{ada.total_deposited():>14}")
print(f"  {'total withdrawn':<30}{ada.total_withdrawn():>14}")
print(f"  {'closing balance':<30}{ada.balance:>14}")

# ===========================================================================
# What it refuses to do
# ===========================================================================

print()
print("-" * WIDTH)
print("WHAT IT REFUSES")
print("-" * WIDTH)

attempts = [
    ("withdraw more than the balance",
     lambda: ada.withdraw("999999.00")),
    ("withdraw a negative amount",
     lambda: ada.withdraw("-50.00")),
    ("deposit zero",
     lambda: ada.deposit("0")),
    ("open an account with a negative balance",
     lambda: BankAccount("Nobody", "-10.00")),
    ("open an account with no owner",
     lambda: BankAccount("   ")),
    ("transfer to itself",
     lambda: ada.transfer_to(ada, "1.00")),
]

balance_before = ada.balance
entries_before = len(ada.history)

for label, attempt in attempts:
    try:
        attempt()
        print(f"  {label:<44}ALLOWED — should it be?")
    except (InsufficientFunds, ValueError) as exc:
        print(f"  {label:<44}{type(exc).__name__}")

print()
print(f"  {'balance unchanged by all six refusals':<44}"
      f"{str(ada.balance == balance_before):>10}")
print(f"  {'no history entries added':<44}"
      f"{str(len(ada.history) == entries_before):>10}")
print("""
  That is the important line. Each method CHECKS FIRST AND MUTATES SECOND,
  so a refused operation leaves the object exactly as it was. A method that
  half-applies a change before discovering it cannot finish is how objects
  end up in states no sequence of legal calls could have produced.""")

# ===========================================================================
# Attack the invariants
# ===========================================================================

print()
print("=" * WIDTH)
print(f"{'CAN THE INVARIANTS BE BROKEN?':^{WIDTH}}")
print("=" * WIDTH)

import random                                   # noqa: E402

random.seed(7)
victim = BankAccount("Test", "100.00")
allowed = refused = 0

for _ in range(5000):
    action = random.choice(["deposit", "withdraw", "withdraw"])
    amount = Decimal(random.randrange(1, 20000)) / 100
    try:
        if action == "deposit":
            victim.deposit(amount)
        else:
            victim.withdraw(amount)
        allowed += 1
    except (InsufficientFunds, ValueError):
        refused += 1
    if victim.check_invariants():
        break

problems = victim.check_invariants()

print(f"{'random operations attempted':<44}{5000:>{WIDTH - 44},}")
print(f"{'allowed':<44}{allowed:>{WIDTH - 44},}")
print(f"{'refused':<44}{refused:>{WIDTH - 44},}")
print(f"{'final balance':<44}{str(victim.balance):>{WIDTH - 44}}")
print(f"{'balance never went negative':<44}"
      f"{str(victim.balance >= 0):>{WIDTH - 44}}")
print(f"{'balance still matches the history':<44}"
      f"{str(not problems):>{WIDTH - 44}}")
if problems:
    for problem in problems:
        print(f"    {problem}")

# And now break it from outside, to show what the class does NOT protect.
victim.balance = Decimal("-1000.00")
print()
print("-" * WIDTH)
print("BUT: `victim.balance = Decimal('-1000.00')` from outside")
print("-" * WIDTH)
for problem in victim.check_invariants():
    print(f"  {problem}")
print("""
  Python has no private attributes. A class protects its invariants against
  MISUSE OF ITS METHODS, not against somebody reaching in and assigning.

  The conventions and tools that address this:
    _balance      a leading underscore means "internal, do not touch"
    @property     Day 47 — makes assignment run validation
    __slots__     Day 43 — stops NEW attributes, not assignment to real ones
    frozen=True   Day 48 — genuinely refuses assignment

  Day 47 rebuilds this account so that even the line above raises.""")

print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * transfer_to withdraws before depositing. Swap the two lines, then make
#     the withdrawal fail, and check both balances. Money appears from
#     nowhere. Order is not a style choice here.
#
#   * Add an overdraft LIMIT: the balance may go to -limit but no further.
#     Notice the invariant changes from `balance >= 0` to
#     `balance >= -self.overdraft`, and that check_invariants() is the only
#     place that has to know.
#
#   * Add interest(rate) that compounds monthly. Should it appear in the
#     history? Decide, and make check_invariants() agree with your answer.
#
#   * On Day 43 give this class __eq__ and __len__. On Day 47 make balance
#     a read-only property so the attack above raises. On Day 48 see how
#     much of __init__ a @dataclass deletes — and why this class is one of
#     the ones it should NOT replace.
