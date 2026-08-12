"""Day 046 — Composition over inheritance.

    python3 lesson.py
"""

import json

WIDTH = 74

# ---------------------------------------------------------------------------
# 1. THE CLASSIC MISTAKE — inheriting to reuse code
# ---------------------------------------------------------------------------


class InheritedStack(list):
    """A stack that IS a list. It should HAVE one."""

    def push(self, item):
        self.append(item)


class ComposedStack:
    """A stack that HAS a list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1] if self._items else None

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"ComposedStack({self._items})"


bad = InheritedStack()
bad.push(1)
bad.push(2)

print("InheritedStack, doing things a stack cannot do:")
bad.insert(0, "jumped the queue")
bad.sort(key=str)
bad.reverse()
print(f"  after insert/sort/reverse: {bad}")
print(f"  bad[0] = {bad[0]}, and slicing works: {bad[:2]}")

leaked = [m for m in dir(bad) if not m.startswith("_") and m != "push"]
print(f"\n  methods inherited and now PUBLIC forever: {leaked}")

good = ComposedStack()
good.push(1)
good.push(2)
print(f"\nComposedStack exposes exactly: "
      f"{[m for m in dir(good) if not m.startswith('_')]}")
print(f"  {good}, pop -> {good.pop()}, len -> {len(good)}")
print(f"  good.insert exists: {hasattr(good, 'insert')}")

print("""
  You wanted a list INSIDE, not to BE one. Inheriting exposed the entire
  list API — every one of those methods is now part of Stack's public
  interface and somebody will use one.

  The composed version exposes three operations. Adding a fourth is a
  DECISION. That is the whole technique: delegation, deliberately.""")


# ---------------------------------------------------------------------------
# 2. is-a versus has-a
# ---------------------------------------------------------------------------

print("""
  INHERITANCE IS is-a       A Circle IS A Shape. Anywhere a Shape is
                            expected, a Circle works.
  COMPOSITION IS has-a      A Car HAS AN Engine. It holds one and asks it
                            to do things.

  THE FOUR COSTS OF INHERITANCE

  1. YOU INHERIT EVERYTHING — including methods that make no sense, and
     ones added to the base next year.
  2. THE BASE BECOMES FRAGILE — change one method and every subclass
     changes, including ones in code you have never read.
  3. IT IS FIXED AT DEFINITION TIME — a Circle cannot stop being a Shape.
     A car can be given a different engine.
  4. DEEP CHAINS ARE UNREADABLE — four levels means four files to
     understand one call.""")


# ---------------------------------------------------------------------------
# 3. THE FRAGILE BASE CLASS, demonstrated
# ---------------------------------------------------------------------------


class Base:
    def __init__(self):
        self.calls = 0

    def add(self, item):
        self.calls += 1

    def add_many(self, items):
        for item in items:
            self.add(item)               # the base calls its OWN method


class Counter(Base):
    """Counts adds. Looks correct in isolation."""

    def add_many(self, items):
        self.calls += len(items)         # "optimised": skip the loop
        super().add_many(items)


counter = Counter()
counter.add_many([1, 2, 3])
print(f"\nCounter.calls after adding 3 items: {counter.calls}   <- expected 3")
print("""
  Double-counted, because add_many() calls add() internally and the
  subclass did not know. Nothing in Base's PUBLIC contract said so.

  That is the FRAGILE BASE CLASS PROBLEM: correctness of the subclass
  depends on the base's INTERNAL call pattern, which is not documented and
  can change in a patch release. It is why library authors are so reluctant
  to touch base classes.""")


# ---------------------------------------------------------------------------
# 4. COMPOSITION MAKES THINGS TESTABLE — the biggest practical win
# ---------------------------------------------------------------------------


class MemoryStorage:
    def __init__(self):
        self.saved = []

    def save(self, record):
        self.saved.append(record)
        return len(self.saved)


class LoudStorage:
    def save(self, record):
        print(f"      (pretending to write {record!r} to a database)")
        return 1


class NullNotifier:
    def notify(self, message):
        return False


class RecordingNotifier:
    def __init__(self):
        self.messages = []

    def notify(self, message):
        self.messages.append(message)
        return True


class Service:
    """Holds its collaborators. Does not inherit from any of them."""

    def __init__(self, storage, notifier):
        self.storage = storage
        self.notifier = notifier

    def handle(self, record):
        row = self.storage.save(record)
        self.notifier.notify(f"saved {record!r} as row {row}")
        return row


print("\nthe same Service, two configurations:")
print("  production-ish:")
Service(LoudStorage(), NullNotifier()).handle("order-1")

print("  in a test:")
storage, notifier = MemoryStorage(), RecordingNotifier()
Service(storage, notifier).handle("order-2")
print(f"      storage received:  {storage.saved}")
print(f"      notifier received: {notifier.messages}")

print("""
  THE COMPONENTS ARE ARGUMENTS, so a test substitutes fakes and then
  INSPECTS them. With inheritance you would need a parallel subclass
  hierarchy — TestService(Service) overriding two methods — and Day 58's
  monkeypatch exists largely to work around designs that did not do this.

  It also avoids a combinatorial explosion: 3 storages x 3 notifiers x 2
  formatters is 8 objects composed, or 18 subclasses.""")


# ---------------------------------------------------------------------------
# 5. MIXINS — the reasonable middle
# ---------------------------------------------------------------------------


class JsonMixin:
    """ONE capability. No state. No __init__."""

    def to_json(self):
        return json.dumps(
            {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        )


class ComparableMixin:
    def __eq__(self, other):
        return type(self) is type(other) and self.__dict__ == other.__dict__


class User(JsonMixin, ComparableMixin):
    def __init__(self, name, email):
        self.name, self.email = name, email


user = User("Ada", "ada@example.com")
print(f"\nto_json():  {user.to_json()}")
print(f"equality:   {user == User('Ada', 'ada@example.com')}")
print(f"MRO:        {' -> '.join(c.__name__ for c in User.__mro__)}")

print("""
  A mixin is inheritance used for can-do rather than is-a, and it is
  genuinely useful — Django and DRF are built on them.

  RULES THAT KEEP THEM SANE
    * no __init__, no state of their own
    * ONE capability each
    * named ...Mixin
    * listed BEFORE the real base class (MRO order, Day 45)

  And the failure mode: five mixins on one class and nobody can find where
  a method comes from.""")


# ---------------------------------------------------------------------------
# 6. __getattr__ forwarding — powerful, and usually a bad idea
# ---------------------------------------------------------------------------


class Wrapper:
    """Forwards ANYTHING it does not define to the wrapped object."""

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getattr__(self, name):
        # Only called when normal lookup FAILS.
        return getattr(self._wrapped, name)

    def extra(self):
        return "something of my own"


wrapper = Wrapper([3, 1, 2])
print(f"\nwrapper.extra()   {wrapper.extra()}")
print(f"wrapper.append(9) forwarded, giving {wrapper._wrapped}"
      if wrapper.append(9) is None else "")
print("wrapper.sort()    forwarded: ", end="")
wrapper.sort()
print(wrapper._wrapped)

print("""
  This gets you delegation with no boilerplate — and it is USUALLY WRONG,
  for the same reason Stack(list) was: you have promised the entire wrapped
  API without choosing any of it, and now it is implicit rather than
  visible. Dunder methods are not forwarded either, so len(wrapper) fails
  while wrapper.sort() works, which is a confusing halfway house.

  Forward explicitly, one method at a time, and let the list of forwards BE
  the interface.""")


# ---------------------------------------------------------------------------
# 7. When inheritance IS right
# ---------------------------------------------------------------------------

print("""
USE INHERITANCE WHEN ALL FOUR HOLD

  1. a genuine is-a, SUBSTITUTABLY (Day 45's Liskov test)
  2. the subclasses are interchangeable to the caller
  3. the base is stable, and ideally you control it
  4. the hierarchy is one or two levels deep

Yesterday's shapes qualify on all four. A framework asking you to subclass
Model or TestCase qualifies — that is its chosen extension point.

THE THREE QUESTIONS BEFORE SUBCLASSING

  1. Is every child usable everywhere the parent is expected?  no -> compose
  2. Am I doing this to REUSE CODE or to be SUBSTITUTABLE?    reuse -> compose
  3. Would I be happy inheriting every future base method?     no -> compose

And the one that catches most of it:
  WOULD THIS READ BETTER AS A CONSTRUCTOR ARGUMENT?""")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Subclass dict "to add a feature" and count how many methods you have
#     now promised to keep correct.
#   * Reproduce the fragile base class by changing Base.add_many to not
#     call add(). The subclass silently starts under-counting.
#   * Write a Service that INHERITS its storage, then try to test it.
#   * Add a third mixin and find a method without using an editor.
#   * Call len(wrapper) in section 6 and read the error.
