"""Day 021 — Lists.

    python3 lesson.py
"""

import copy

# ---------------------------------------------------------------------------
# 1. Creating, indexing, slicing — all exactly as for strings (Day 3)
# ---------------------------------------------------------------------------

tasks = ["write", "test", "ship"]

print(tasks[0], tasks[-1])          # write ship
print(tasks[0:2])                   # ['write', 'test']  — a NEW list
print(tasks[::-1])                  # reversed COPY
print(len(tasks), "test" in tasks)

# A list can hold anything, including other lists. In practice keep ONE KIND
# of thing in a list, or every reader has to check types before using it.
mixed = [1, "two", 3.0, True, None]
print(mixed)


# ---------------------------------------------------------------------------
# 2. The methods — and which return None
# ---------------------------------------------------------------------------

tasks = ["write", "test", "ship"]

print("\nappend returns:", tasks.append("deploy"))   # None!
print("insert returns:", tasks.insert(0, "plan"))    # None
print("after both:    ", tasks)

# THE RULE, first met with shuffle on Day 16:
# METHODS THAT CHANGE A LIST IN PLACE RETURN None.
# So `tasks = tasks.append("x")` sets tasks to None, and the mistake shows
# up somewhere else entirely.

broken = ["a", "b"]
broken = broken.append("c")
print("tasks = tasks.append(...) gives:", broken)

# pop DOES return something — the item it removed:
tasks = ["plan", "write", "test", "ship"]
print("\npop()   ->", tasks.pop(), " leaving", tasks)
print("pop(0)  ->", tasks.pop(0), "leaving", tasks)

# append adds ONE item. extend adds MANY. This catches everybody once:
a = ["x"]
a.append(["y", "z"])
print("\nappend a list:", a)          # ['x', ['y', 'z']]  — a list inside
b = ["x"]
b.extend(["y", "z"])
print("extend a list:", b)            # ['x', 'y', 'z']
b += ["w"]                            # += is extend
print("+= a list:    ", b)

# remove deletes by VALUE, first match only, and raises if absent:
c = ["a", "b", "a"]
c.remove("a")
print("\nremove('a'):", c)            # only the first one went
# c.remove("z")                       # ValueError

# Delete by POSITION with del or pop:
del c[0]
print("del c[0]:  ", c)

# Where you want a RESULT rather than a mutation, use the function form:
nums = [3, 1, 2]
print("\nsorted(nums):", sorted(nums), " nums unchanged:", nums)
nums.sort()
print("nums.sort(): ", nums, "        nums changed")


# ---------------------------------------------------------------------------
# 3. ALIASING — today's real subject
# ---------------------------------------------------------------------------

a = [1, 2, 3]
b = a                      # NOT a copy. A second label on the SAME list.
b.append(4)

print(f"\na = {a}")        # [1, 2, 3, 4]  <- a changed too
print(f"b = {b}")
print(f"b is a: {b is a}") # True — Day 7's `is` tells you the truth

# Nothing is wrong with that code. It does exactly what it says. The problem
# is that `b = a` READS like a copy and is not one. Strings never behaved
# this way because they are immutable — there was no change to share.

# FOUR ways to actually copy:
a = [1, 2, 3]
c1 = a.copy()              # clearest
c2 = a[:]                  # idiomatic, older
c3 = list(a)               # also converts other iterables
c4 = copy.deepcopy(a)      # for NESTED data — see below

c1.append(99)
print(f"\nafter c1.append(99): a = {a}")
print(f"c1 is a: {c1 is a}   c1 == a: {c1 == a}")


# ---------------------------------------------------------------------------
# 4. Shallow vs deep — where .copy() is not enough
# ---------------------------------------------------------------------------

grid = [[0, 0], [0, 0]]
shallow = grid.copy()
shallow[0][0] = 9

print(f"\ngrid after changing the SHALLOW copy: {grid}")
print("The outer list was copied. The inner lists were SHARED.")

grid = [[0, 0], [0, 0]]
deep = copy.deepcopy(grid)
deep[0][0] = 9
print(f"grid after changing a DEEP copy:     {grid}")

# For a flat list of numbers or strings, shallow is completely fine.
# For a list of lists it is a trap. Day 28 goes further into nested data.


# ---------------------------------------------------------------------------
# 5. THE [[0] * 3] * 3 TRAP — commit this one to memory
# ---------------------------------------------------------------------------

bad = [[0] * 3] * 3        # THREE REFERENCES TO ONE ROW
bad[0][0] = 9
print(f"\n[[0]*3]*3  after bad[0][0] = 9: {bad}")

good = [[0] * 3 for _ in range(3)]     # a NEW row each time (Day 22)
good[0][0] = 9
print(f"comprehension after good[0][0] = 9: {good}")

print(f"bad[0] is bad[1]:   {bad[0] is bad[1]}")
print(f"good[0] is good[1]: {good[0] is good[1]}")

# The * operator copies REFERENCES, not objects. It is only safe when the
# thing being repeated is immutable: [0] * 3 is fine, [[0]] * 3 is not.


# ---------------------------------------------------------------------------
# 6. Never mutate what you are iterating
# ---------------------------------------------------------------------------

numbers = [1, 2, 2, 3, 2, 4]

broken = numbers.copy()
for n in broken:
    if n == 2:
        broken.remove(n)
print(f"\nremoving 2s while iterating: {broken}   <- a 2 survives")

# Iterate over a COPY:
ok = numbers.copy()
for n in ok[:]:
    if n == 2:
        ok.remove(n)
print(f"iterating over a copy:       {ok}")

# Or build a new list — tomorrow's comprehension, and the best answer:
best = [n for n in numbers if n != 2]
print(f"building a new list:         {best}")


# ---------------------------------------------------------------------------
# 7. What lists are fast and slow at
# ---------------------------------------------------------------------------
#
#   FAST   indexing, append to the END, iterating, len()
#   SLOW   `in` and .index() on a big list  — they SCAN, one item at a time
#          insert(0, x) and pop(0)          — everything after shifts along
#
# `if x in big_list` inside a loop is a nested loop in disguise. Day 26's
# set makes it a single step; Day 29 measures the difference.

stack = []
stack.append("a")          # a stack: append / pop      — both fast
stack.append("b")
print(f"\nstack pop: {stack.pop()}")

queue = ["a", "b", "c"]
print(f"queue pop(0): {queue.pop(0)}  <- O(n): everything shifts left")
print("For a real queue use collections.deque, which is O(1) at both ends.")


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Write `x = my_list.sort()` and then try to use x.
#   * Alias a list, pass it around, and change it in one place. Then add
#     .copy() and confirm the bug goes.
#   * Build a 3x3 grid the wrong way and set one cell. Then the right way.
#   * Time queue.pop(0) on a 200,000-item list against deque.popleft().
