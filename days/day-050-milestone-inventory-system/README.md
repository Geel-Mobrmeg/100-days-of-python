# Day 050 — Milestone: inventory system 🏁

**Phase 5 · Object-oriented Python** · ~180 minutes

> **Today's build:** model products, stock and orders as objects, with a menu-driven interface over the top.

**Concepts:** domain modelling · class collaboration · validation · a CLI front end

---

## The article

### What this milestone is testing

Not whether you can write a class. Days 41–49 settled that. Today asks the question those nine days
were preparation for:

> **Given a paragraph of English describing a business, which classes should exist?**

That question has no syntax in it. It is the whole of object-oriented design, and it is the part
that stays hard after the mechanics stop being hard.

### 1. Nouns are candidates, not answers

The standard advice is "underline the nouns, those are your classes". It is a good *start* and a
bad *rule*.

Today's brief mentions **products, stock, orders, prices, discounts, an audit log**. Six nouns.
The build has classes for four of them and deliberately not for the other two:

- **Price** is not a class. It is what a `PricingRule` returns — a `Money`. A noun with no data of
  its own and no rule of its own is a method, not a class.
- **Discount** is not a class either. It is a *parameter* of `BulkDiscountPricing`.

The cut is: **does this noun own data, or own a rule?** If it owns neither, it is a method name.

`lesson.py` runs the same exercise on a four-sentence library brief and shows a noun ("fine") that
survives step one and dies at step two.

### 2. The rule that shaped the whole system

Day 48 ended on a slogan. Today is that slogan applied to a system big enough for it to matter:

> **Values are frozen dataclasses. Things are plain classes.**

| | **VALUE** | **THING** |
|---|---|---|
| identity | its contents | itself |
| two identical ones | are the same one | are two |
| mutability | frozen | has a lifecycle |
| written as | `@dataclass(frozen=True)` | a plain class |
| in the build | `Sku`, `Money`, `Quantity`, `Product` | `Warehouse`, `Order` |

The test is one question: **if two of these have all the same fields, are they the same one?**

Two `Sku("WID-001")`s are the same sku — there is no sense in which one is a different WID-001.
Two `Order`s for the same customer with the same lines are two orders, and a system that thinks
otherwise will lose one of them. Day 48 showed the generated `__eq__` turning two people's bank
accounts into one; the same mistake on an order is a shipment that never happens.

### 3. Enforce at the value level, not the system level

This is the part of the build worth taking away, and it is three lines:

```python
@dataclass(frozen=True, order=True, slots=True)
class Quantity:
    units: int

    def __post_init__(self):
        if not isinstance(self.units, int) or isinstance(self.units, bool):
            raise TypeError(...)
        if self.units < 0:
            raise ValueError(f"quantity cannot be negative: {self.units}")
```

`Warehouse.issue()` checks stock before it mutates — that is Day 41's discipline and it is still
required. But even if that check were deleted, `stock - wanted` would raise, because a negative
`Quantity` **cannot be constructed**. The invalid state has no representation.

That is a different kind of safety from a check. A check is something you must remember to write on
every route; a type that refuses to hold nonsense is enforced on routes you have not written yet.

`bool` is excluded explicitly, because `isinstance(True, int)` is `True` in Python and
`Quantity(True)` would otherwise be one unit.

### 4. Class collaboration is mostly about who *asks* whom

The smell to learn is **ids as parameters**:

```python
system.lend(book_id, member_id, when)      # something is wrong
library.lend(book, member, today)          # something is right
```

When methods take ids and look things up, the object that *owns* the data is not the object being
asked the question, and the caller is doing the joining a model should do for you. `lesson.py`
builds both and lets you see the difference at the call site.

In the build, `Warehouse` is thin on purpose. It does not compute prices (a `PricingRule` does), it
does not know how to log (an `AuditSink` does), and it does not know what a valid quantity is (a
`Quantity` does). **A coordinator that has grown fat means the objects underneath it are too
passive.**

### 5. Derive, do not store

`Warehouse.below_reorder` and `stock_value` are properties, computed each time. `Library.is_out()`
in `lesson.py` is computed from the loans that exist.

The alternative — storing `book.on_loan` alongside the loans — gives you two places where the same
fact lives, and `lesson.py` demonstrates the resulting lie in one line. If a fact can be true in
two places, it will eventually be true in only one of them.

Store what you are told. Derive what follows.

### 6. All-or-nothing is Day 41 at transaction scale

`Order.confirm()` checks **every** line before issuing **any**:

```python
for sku, quantity, _ in self.lines:            # check first...
    if quantity.units > self.warehouse.stock_of(sku).units:
        raise InsufficientStock(sku, quantity, self.warehouse.stock_of(sku))
for sku, quantity, _ in self.lines:            # ...then mutate
    self.warehouse.issue(sku, quantity)
self.status = "confirmed"
```

Written the obvious way — one loop, check and issue together — an order that fails on its third
line has already shipped the first two, and stock is now reduced for an order that does not exist.
The build stages exactly that: an order for the last three of an item, somebody else takes them
first, and the report shows stock byte-identical before and after the failed confirm.

Two loops instead of one, and the failure mode goes from "silent corruption" to "nothing happened".

### 7. Composition is what made it testable

The test in `build.py` needs no mocking library, no monkeypatching and no subclass of the thing
under test:

```python
spy = ListAudit()
warehouse = build_warehouse(pricing=ClearancePricing(), audit=spy)
```

Two constructor arguments. Had `Warehouse` *inherited* its pricing and its logging — the shape Day
46 started from — each of those would have needed a parallel subclass, and you would be testing the
subclass rather than the warehouse.

This is the concrete payoff of Day 46, and it only becomes visible at this size.

### 8. Where inheritance did earn its place

`BulkDiscountPricing(CostPlusPricing)` is a real `is-a`: it *is* cost-plus, with a break above a
threshold, and it is substitutable everywhere its parent is. `ClearancePricing` ignores margin
completely, so it inherits from `PricingRule` directly and does not pretend.

The interface is a two-method ABC. `AuditSink` is a `Protocol`, because the caller may pass anything
with `.record()` — including a class from a logging library you do not own. Day 49's table, used
rather than recited.

### 9. The CLI is deliberately thin

The interactive front end is about forty lines and contains **no rules**. It parses a word, calls a
method, prints a result. Every refusal it displays comes from the model.

That is the test of the model: if the front end has to re-check anything, the rules are in the wrong
place, and the next front end — a web form, a scheduled job, a test — will have to re-check them
too.

```
> issue WID-001 500
  InsufficientStock: WID-001: wanted 500, only 150 available
> price ab 3
  ValueError: sku 'ab' is too short
```

Both messages were written once, in the model, and appear anywhere anyone uses it.

### 10. What the build proves rather than claims

| Claim | How `build.py` checks it |
|---|---|
| the model refuses bad input | 11 named attacks, each expecting a specific exception type |
| refusals change nothing | stock snapshot compared before and after all eleven |
| a partial order is atomic | stages a conflicting issue, compares stock across the failure |
| composition made it testable | swaps pricing and audit through the constructor |
| the invariants hold | 4,000 random operations — 3,930 allowed, 70 refused, `stock == received - issued` for every sku |

The random attack is the one worth copying. Invariants that hold on the six operations you thought
of are not evidence; invariants that hold on four thousand you did not choose are.

---

## The code

| File | What it is |
|---|---|
| `lesson.py` | The same brief modelled three ways — dicts, one god class, collaborating objects — and the six-step method for choosing. |
| `build.py`  | The inventory system: 4 value types, 2 things, a pricing hierarchy, an audit protocol, a CLI, and the checks above. |

```bash
python3 lesson.py
python3 build.py                                          # the report
python3 build.py --interactive                            # then a prompt
printf 'list\nprice WID-001 60\nlow\nquit\n' | python3 build.py -i
```

---

## The brief

Build yours before reading `build.py`. It must have:

- [ ] **value types** for the things defined by their contents — a stock code, an amount of money,
      a count — frozen, and refusing to hold an invalid value
- [ ] **plain classes** for the things with identity and a lifecycle
- [ ] a **product catalogue** separate from **stock levels** (a product is a description; stock is a
      fact about a warehouse)
- [ ] an **order** with lines, a total, and a status that only moves forwards
- [ ] **all-or-nothing confirmation** — an order that cannot be filled changes nothing
- [ ] at least **two pricing rules** behind one interface, swapped without touching the warehouse
- [ ] validation on **every route in**, not just the obvious one
- [ ] a `check_invariants()` you can call at any moment
- [ ] a **menu-driven CLI** containing no business rules
- [ ] a demonstration that **refusals leave the state untouched**

Then attack it: a few thousand random operations, and assert the invariants after every one.

---

## Common mistakes

**Storing what you can derive.** `on_loan`, `total`, `is_overdue` — every stored duplicate is a
future contradiction.

**Ids as parameters.** `issue(sku_string, n)` where `issue(Sku, Quantity)` would do. The types are
where the validation lives.

**A god class.** Six parallel dicts keyed by id is not a model, it is a database with no integrity
checks.

**Anaemic objects.** Classes with only fields and getters, and all the rules in the coordinator.
That is a dict with extra syntax.

**Mutating before checking.** Half an order shipped is worse than none.

**Rules in the CLI.** They will not be there for the next caller.

**`@dataclass` on a thing.** The generated `__eq__` says two orders with the same lines are the same
order.

**Validation only on `__init__`.** Day 47: every route in, or the invariant is not one.

---

## Extend it

1. **Delete `Quantity`'s negative check** and re-run the invariant attack. The warehouse-level
   checks still catch it — but later, and with a worse message. That gap is the argument for
   enforcing at the value level.
2. **Make `Warehouse` a dataclass.** Two warehouses with identical stock now compare equal. Decide
   whether that is ever what you want.
3. **Add a fourth pricing rule.** Nothing outside it should change. If something does, the interface
   is wrong.
4. **Add stock movements as a value type** (`Received`, `Issued`, `Adjusted`) and rebuild the
   current level by replaying them. That is event sourcing, and it falls out of the value/thing
   split almost for free.
5. **Add a second warehouse and transfers between them.** Watch which class the new rule wants to
   live in.

---

## Phase 5 checklist

You are leaving Object-oriented Python. Before you do:

- [ ] I can write a class with an invariant and enforce it on every route in
- [ ] I know when a value belongs on the class and when it belongs on the instance
- [ ] I can implement `__repr__`, `__eq__` and `__hash__` and keep their contract
- [ ] I overload operators only where the meaning is obvious, and return `NotImplemented` otherwise
- [ ] I use inheritance only for a genuine `is-a`, and can name one I rejected
- [ ] **I reach for composition first, and can say what it bought me**
- [ ] I use properties to validate rather than to decorate
- [ ] I use `@dataclass` for values and a plain class for things
- [ ] I can choose between an `ABC` and a `Protocol` and say why
- [ ] **I can turn a paragraph of English into objects and defend every one of them**

Tomorrow: exceptions. Every `raise` in today's build has been a promise that somebody, somewhere,
catches it — Phase 6 is about being that somebody, and about the difference between code that runs
and software that survives.
