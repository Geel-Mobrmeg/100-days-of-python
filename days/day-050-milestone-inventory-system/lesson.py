"""Day 050 — Domain modelling: turning a description into objects.

    python3 lesson.py

No new syntax today. Everything here is Days 41–49. What is new is the
QUESTION: given a paragraph of English describing a business, which classes
should exist?

The same tiny problem is modelled three times — as loose dicts, as one big
class, and as collaborating objects — and each version is asked the same
four awkward questions. The differences are the lesson.
"""

from dataclasses import dataclass
from datetime import date, timedelta

WIDTH = 74

# ---------------------------------------------------------------------------
# THE BRIEF
# ---------------------------------------------------------------------------

BRIEF = """
  A library lends books. A member may hold at most three loans at once.
  A loan runs for fourteen days; after that it is overdue and accrues a
  fine of 20p per day, capped at the price of the book. A book that is on
  loan cannot be lent again.
"""

print("=" * WIDTH)
print(f"{'THE BRIEF':^{WIDTH}}")
print("=" * WIDTH)
print(BRIEF)

print("""  STEP 1 — UNDERLINE THE NOUNS.   library, book, member, loan, fine
  STEP 2 — UNDERLINE THE VERBS.   lend, hold, run, accrue, cap
  STEP 3 — UNDERLINE THE RULES.   at most three · fourteen days · 20p/day
                                  · capped at price · not twice at once

  The nouns are candidate classes. The verbs are candidate methods. The
  RULES are the actual work — they are what a dict cannot hold on to.""")


# ###########################################################################
# VERSION 1 — dicts and loose functions (Phase 3's toolkit)
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'VERSION 1 — DICTS':^{WIDTH}}")
print("=" * WIDTH)

books_v1 = {
    "b1": {"title": "Dune", "price": 9.99, "on_loan": False},
    "b2": {"title": "Solaris", "price": 7.50, "on_loan": False},
}
members_v1 = {"m1": {"name": "Ada", "loans": []}}


def lend_v1(book_id, member_id, when):
    book = books_v1[book_id]
    member = members_v1[member_id]
    if book["on_loan"]:
        return "already out"
    if len(member["loans"]) >= 3:
        return "too many loans"
    book["on_loan"] = True
    member["loans"].append({"book": book_id, "due": when + timedelta(days=14)})
    return "ok"


print(f"  lend b1 -> {lend_v1('b1', 'm1', date(2026, 1, 1))}")
print(f"  lend b1 -> {lend_v1('b1', 'm1', date(2026, 1, 1))}")

# ...and here is what nothing prevents:
books_v1["b1"]["on_loan"] = False               # the book "returns" itself
print("\n  books_v1['b1']['on_loan'] = False    <- nothing stopped this")
print(f"  the loan still exists:   "
      f"{len(members_v1['m1']['loans'])} loan(s)")
print(f"  the book says it is free: "
      f"{not books_v1['b1']['on_loan']}")
print("""
  THE STATE IS NOW A LIE, and no single line is wrong. The rule "a book on
  loan cannot be lent again" lives inside lend_v1() and nowhere else, so
  every other line of the program is free to contradict it.

  A dict has no opinions. That is exactly what makes it a bad home for a
  rule.""")


# ###########################################################################
# VERSION 2 — one class that knows everything
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'VERSION 2 — ONE GOD CLASS':^{WIDTH}}")
print("=" * WIDTH)


class LibrarySystem:
    """Everything in one place. Watch the parameter lists grow."""

    def __init__(self):
        self.book_titles = {}
        self.book_prices = {}
        self.book_on_loan = {}
        self.member_names = {}
        self.member_loans = {}
        self.loan_due = {}

    def add_book(self, book_id, title, price):
        self.book_titles[book_id] = title
        self.book_prices[book_id] = price
        self.book_on_loan[book_id] = False

    def add_member(self, member_id, name):
        self.member_names[member_id] = name
        self.member_loans[member_id] = []

    def lend(self, book_id, member_id, when):
        if self.book_on_loan[book_id]:
            raise ValueError("already out")
        if len(self.member_loans[member_id]) >= 3:
            raise ValueError("too many loans")
        self.book_on_loan[book_id] = True
        self.member_loans[member_id].append(book_id)
        self.loan_due[book_id] = when + timedelta(days=14)

    def fine(self, book_id, today):
        days = (today - self.loan_due[book_id]).days
        if days <= 0:
            return 0.0
        return min(days * 0.20, self.book_prices[book_id])


system = LibrarySystem()
system.add_book("b1", "Dune", 9.99)
system.add_member("m1", "Ada")
system.lend("b1", "m1", date(2026, 1, 1))
print(f"  fine after 10 days late   £{system.fine('b1', date(2026, 1, 25)):.2f}")
print(f"  fine after 90 days late   £{system.fine('b1', date(2026, 4, 15)):.2f}"
      f"   <- capped at the price")

print(f"""
  Better: the rules are in ONE object and the fine cap works. But look at
  what it is made of — {len(vars(system))} parallel dictionaries, all keyed by id, all
  required to stay in step. Deleting a book means remembering every one.

  And every method takes ids and passes them around:

      system.lend(book_id, member_id, when)
      system.fine(book_id, today)

  Ids as parameters is the smell. It means the object that OWNS the data is
  not the object being asked the question — so the caller has to do the
  joining that a real model would do for you.""")


# ###########################################################################
# VERSION 3 — collaborating objects
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'VERSION 3 — COLLABORATING OBJECTS':^{WIDTH}}")
print("=" * WIDTH)

DAILY_FINE = 0.20
LOAN_DAYS = 14
MAX_LOANS = 3


@dataclass(frozen=True, slots=True)
class Book:
    """A VALUE. Two copies of Dune with the same id ARE the same book.

    Note what is NOT here: `on_loan`. Whether a book is out is a fact about
    LOANS, not about the book, and putting it here is what made version 1
    able to lie. If a thing can be true in two places it will eventually be
    true in only one of them.
    """

    book_id: str
    title: str
    price: float

    def __str__(self):
        return self.title


class Loan:
    """A THING. It has a lifecycle, so it is a plain class.

    Everything the brief says about lateness lives here and only here.
    """

    def __init__(self, book, member, taken_on):
        self.book = book
        self.member = member
        self.taken_on = taken_on
        self.returned_on = None

    @property
    def due_on(self):
        return self.taken_on + timedelta(days=LOAN_DAYS)

    @property
    def is_open(self):
        return self.returned_on is None

    def days_late(self, today):
        end = self.returned_on or today
        return max(0, (end - self.due_on).days)

    def fine(self, today):
        """The rule and its cap, in one place, expressed once."""
        return min(self.days_late(today) * DAILY_FINE, self.book.price)

    def __repr__(self):
        state = "open" if self.is_open else f"returned {self.returned_on}"
        return f"Loan({self.book}, {self.member.name}, {state})"


class Member:
    """A THING. Owns the "at most three" rule, because it is ABOUT a member."""

    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self._loans = []

    @property
    def open_loans(self):
        return [loan for loan in self._loans if loan.is_open]

    @property
    def can_borrow(self):
        return len(self.open_loans) < MAX_LOANS

    def fines_owed(self, today):
        return sum(loan.fine(today) for loan in self._loans)

    def take(self, loan):
        self._loans.append(loan)


class Library:
    """A THING, and deliberately THIN.

    Compare it with LibrarySystem. It holds no fine arithmetic, no due
    dates and no loan counting, because each of those belongs to something
    that already exists. A coordinator that has grown fat is a sign that
    the objects underneath it are too passive.
    """

    def __init__(self):
        self._books = {}
        self._members = {}
        self._loans = []

    def add(self, book):
        self._books[book.book_id] = book

    def enrol(self, member):
        self._members[member.member_id] = member

    def is_out(self, book):
        """DERIVED, never stored. This is why version 1's lie is impossible."""
        return any(loan.book == book and loan.is_open for loan in self._loans)

    def lend(self, book, member, today):
        if self.is_out(book):
            raise ValueError(f"{book} is already on loan")
        if not member.can_borrow:
            raise ValueError(f"{member.name} already holds {MAX_LOANS} books")
        loan = Loan(book, member, today)
        self._loans.append(loan)
        member.take(loan)
        return loan

    def give_back(self, loan, today):
        loan.returned_on = today
        return loan.fine(today)


dune = Book("b1", "Dune", 9.99)
solaris = Book("b2", "Solaris", 7.50)
ada = Member("m1", "Ada")

library = Library()
for book in (dune, solaris):
    library.add(book)
library.enrol(ada)

day_one = date(2026, 1, 1)
loan = library.lend(dune, ada, day_one)

print(f"  {'lend Dune to Ada':<34}{repr(loan):>{WIDTH - 36}}")
print(f"  {'due':<34}{str(loan.due_on):>{WIDTH - 36}}")
print(f"  {'is Dune out?':<34}{str(library.is_out(dune)):>{WIDTH - 36}}")

for label, today in [("on time (day 10)", date(2026, 1, 11)),
                     ("10 days late", date(2026, 1, 25)),
                     ("90 days late", date(2026, 4, 15))]:
    print(f"  {'fine, ' + label:<34}"
          f"{'£' + format(loan.fine(today), '.2f'):>{WIDTH - 36}}")

print()
for label, attempt in [
    ("lend Dune twice", lambda: library.lend(dune, ada, day_one)),
    ("read on_loan off the book", lambda: dune.on_loan),
    ("set a book's price", lambda: setattr(dune, "price", 0.01)),
]:
    try:
        attempt()
        print(f"  {label:<34}{'ALLOWED':>{WIDTH - 36}}")
    except Exception as exc:                             # noqa: BLE001
        print(f"  {label:<34}{type(exc).__name__:>{WIDTH - 36}}")

print("""
  Version 1's exact sabotage — reaching in and flipping the flag — has no
  spelling here. There is no flag. "On loan" is DERIVED from the loans that
  exist, so the two facts cannot disagree.""")


# ###########################################################################
# THE FOUR QUESTIONS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE SAME FOUR QUESTIONS, ASKED OF ALL THREE':^{WIDTH}}")
print("=" * WIDTH)

questions = [
    ("Where does 'fine is capped' live?",
     "wherever somebody remembered to write it",
     "LibrarySystem.fine(), among everything else",
     "Loan.fine() — with the data it needs"),
    ("Can the state contradict itself?",
     "yes, and it did, forty lines ago",
     "yes — six dicts that must stay in step",
     "no: 'on loan' is derived, never stored"),
    ("Cost of 'over-65s pay no fine'",
     "find and edit every caller of the fine",
     "edit the god class and hope",
     "one method, one place"),
    ("Test the fine cap on its own",
     "hand-build two dicts in the right shape",
     "build the whole system first",
     "Loan(book, member, day).fine(later)"),
]

for question, a, b, c in questions:
    print(f"\n  {question}")
    for name, answer in (("dicts", a), ("god class", b), ("objects", c)):
        print(f"      {name:<12}{answer}")

print("""
  The `objects` line wins the last two questions, and those two are what
  a program costs AFTER it is written — which is most of what it costs.""")


# ###########################################################################
# HOW TO DECIDE — the questions to ask of every candidate class
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE METHOD':^{WIDTH}}")
print("=" * WIDTH)
print("""
  1. NOUNS ARE CANDIDATES, NOT ANSWERS. "Fine" is a noun in the brief and
     is not a class — it is a method on Loan. Cut any noun that has no data
     of its own and no rule of its own.

  2. IS IT A VALUE OR A THING?  (Day 48's rule, and the whole of today.)

         VALUE                          THING
         defined by its contents        has an identity
         two equal ones are the same    two identical ones are different
         immutable, hashable            has a lifecycle
         @dataclass(frozen=True)        plain class
         Book, Money, Sku, Date         Library, Loan, Member, Session

     Ask: "if two of these have all the same fields, are they the same
     one?" Two £5 notes: yes. Two members called Ada: no.

  3. PUT EACH RULE WHERE ITS DATA IS. The fine needs a due date and a
     price, so it belongs to the Loan. The three-loan limit needs a
     member's loans, so it belongs to the Member. A rule living away from
     its data is what forces ids into every parameter list.

  4. DERIVE, DO NOT STORE. Anything computable from something else should
     be a @property. Stored duplicates are how state starts lying.

  5. DRAW THE ARROWS BEFORE YOU TYPE.

         Library ---> Book        knows about
         Library ---> Member      knows about
         Library ---> Loan        creates and holds
         Loan    ---> Book        holds one
         Loan    ---> Member      holds one
         Member  ---> Loan        holds many

     ARROWS BOTH WAYS between Loan and Member is the one to look at hard.
     Here it earns its keep — a loan must be able to say whose it is, and
     a member must be able to count theirs. But every cycle is a chance
     for the two sides to disagree, so exactly one of them owns the write
     (Library.lend, which does both in one place).

  6. NOW WRITE THE HARDEST RULE FIRST. If the model cannot express "fine
     capped at the price of the book" cleanly, you have the wrong objects,
     and you would rather find that out on line 20 than line 400.""")

print()
print("=" * WIDTH)
print(f"{'AND THE COUNTER-WARNING':^{WIDTH}}")
print("=" * WIDTH)
print("""
  Version 3 is ~90 lines to version 1's ~20. For a script that runs once
  and is deleted, version 1 is the right answer and version 3 is a costume.

  Modelling pays for itself when:
      * the rules outlive the script
      * more than one person edits it
      * the state must never be wrong
      * the requirements will change (they will)

  and not before. Knowing when NOT to build this is the same skill as
  knowing how to.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Now do it yourself
# ---------------------------------------------------------------------------
#
#   * Add "members over 65 pay no fine". Do it in all three versions and
#     time yourself. That number is what modelling buys.
#
#   * Add reservations: a member may reserve a book that is out, and the
#     next return goes to them. Notice that Reservation is a THING and that
#     Library.lend() has to consult it — a new noun with a real rule.
#
#   * Break rule 4 on purpose: store `Book.on_loan` alongside the derived
#     Library.is_out(). Then write the line that makes them disagree. It
#     takes about ten seconds.
#
#   * Model something you actually know — a gym membership, a car park, a
#     recipe book. Do steps 1–5 on paper before typing anything.
#
#   * Then read build.py, which is this method applied to a system with
#     four value types, two things, a pricing hierarchy and an audit log.
