# Day 059 — Type hints

**Phase 6 · Robust code** · ~85 minutes

> **Today's build:** annotate your whole package and drive mypy to zero errors without using `Any` as an escape.

**Concepts:** annotations · `Optional` & `Union` · `list[str]` generics · mypy · typing gradually

---

## The article

### Why this day exists

Day 57's suite has 146 cases and covers the lines it runs. Type checking covers **every line**, including
the eighty per cent no test reaches — shallowly, and for a completely different class of mistake.

Neither replaces the other, and today ends by measuring exactly that.

### 1. The interpreter does not care

```python
def double(n: int) -> int:
    return n * 2

double("ha")     -> 'haha'
double([1, 2])   -> [1, 2, 1, 2]
```

Both ran. Annotations are **metadata** — Python stores them in `__annotations__` and never checks
them. Nothing about hints slows your program down or changes what it does.

They exist for two readers: a human, and a checker you run separately. If you never run the checker,
hints are documentation that can quietly become wrong — which is worse than a comment, because it
looks authoritative.

Run the checker on exactly that code and you get two errors in under a second, without running
anything.

### 2. The syntax, in one screen

```python
items: list[str]                # 3.9+: lowercase builtins, no import
pairs: dict[str, int]
point: tuple[float, float]      # exactly two
row: tuple[str, ...]            # any number
maybe: str | None               # 3.10+: instead of Optional[str]
either: int | str               # instead of Union[int, str]

def f(a: int, b: str = "x") -> bool: ...
def h() -> None: ...            # returns nothing — say so
```

From `collections.abc` for parameters: `Iterable`, `Sequence`, `Mapping`, `Callable`, `Iterator`.

**The rule that matters most:**

> Accept the broadest thing that works. Return the most specific.

```python
def summarise(rows: Iterable[str]) -> list[str]:
```

That accepts a list, tuple, set, generator or file, and promises the caller a real list they can
index. `rows: list[str]` accepts one thing; `-> Iterable[str]` forces the caller to convert.

### 3. `Any` is not a type. It is an off switch.

```python
def with_any(data: Any) -> int:
    return data.anything_at_all().nonsense[42] + "not a number"    # no error

def with_object(data: object) -> int:
    return data.anything_at_all()     # error: "object" has no attribute ...
```

The first function is nonsense and mypy says nothing. `Any` means *stop checking*, and it is
contagious: everything an `Any` touches becomes unchecked, so one `Any` in a signature can switch off
a whole call chain.

`object` is the honest version of "I do not know what this is". It accepts anything and lets you do
nothing with it until you narrow with `isinstance`.

`Any` is right at a boundary where data genuinely has no static shape — `json.loads()`, `**kwargs`
forwarded to an untyped library. Even then, narrow it as soon as you can.

`# type: ignore[error-code]` with the code in brackets is a targeted, greppable exception. Bare
`# type: ignore` silences everything on that line forever, including the error you introduce next
year.

### 4. When the answer's type depends on the argument's

```python
T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]
```

A `TypeVar` promises that two places hold the **same** type. Without it, the honest return type is
`object` and every caller has to narrow.

Bounded, when the function needs the type to be able to do something:

```python
class Comparable(Protocol):
    def __lt__(self, other: object, /) -> bool: ...

C = TypeVar("C", bound=Comparable)

def clamp(value: C, low: C, high: C) -> C: ...
```

That is the real signature of the toolkit's `clamp()`, and the Protocol is **necessary**: `int`,
`float`, `str`, `date` and `Decimal` are all comparable and share no base class. Day 49 argued for
structural typing; this is where it becomes checkable.

### 5. The hard one: decorators

```python
def lazy(f: Callable[..., Any]) -> Callable[..., Any]: ...

@lazy
def add(a: int, b: int) -> int: ...

add("x", "y", "z", nonsense=True)      # NOT an error. It should be.
```

`Callable[..., Any]` on a decorator **deletes the signature** of every function it decorates. That is
why so much decorated code cannot be called wrongly enough to be told about.

```python
P = ParamSpec("P")
R = TypeVar("R")

def careful(f: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return f(*args, **kwargs)
    return wrapper
```

`ParamSpec` (3.10) captures the whole parameter list, so the wrapper is checked as if it were the
original. Two lines, and `@timer` stops being a hole in your types.

### 6. Four more that earn their keep

| | |
|---|---|
| `TypedDict` | a dict with a known set of keys — `info["hitrate"]` becomes an error |
| `Literal["left", "right"]` | one of a fixed set of **values** |
| `Final` | a name that must not be reassigned |
| `NewType("UserId", int)` | a distinct type with no runtime cost |

### 7. Today's build: 32 errors → 0, with no `Any`

The before and after are two real directories, not a remembered number: Day 39 holds the same
functions unannotated, Day 40 holds them annotated.

```
                                       ERRORS   SECONDS
day 39 — the same functions                32      1.0s
day 40 — annotated                          0      0.2s

what --strict was complaining about before:
  no-untyped-def                25
  no-untyped-call                3
  var-annotated                  2
  attr-defined                   2
```

Most of that is "this function has no annotation" — the sound a checker makes when there is nothing
to check. The **two `attr-defined`** at the bottom are the interesting ones.

Six signatures needed a decision, and none of them is decoration:

| | |
|---|---|
| `clamp(value: C, low: C, high: C) -> C` | `C` bound to a `Comparable` Protocol |
| `chunked(items: Iterable[T], size: int) -> list[list[T]]` | broad in, specific out |
| `unique(items: Iterable[H]) -> list[H]` | `H` bound to `Hashable` — the precondition, written down |
| `dig(data: object, *keys: object) -> object` | `object`, not `Any`; the caller must narrow |
| `timer(f: Callable[P, R]) -> Callable[P, R]` | `ParamSpec`, plus two `@overload`s |
| `cache(f: Callable[P, R]) -> Cached[P, R]` | a Protocol — see below |

### 8. The thing 146 tests could not see

The package README has documented `square.cache_info()` since Day 40, and it works. But until today
no **type** said so, and mypy reported this at every call site:

```
"function" has no attribute "cache_info"  [attr-defined]
```

That is not a complaint about syntax. It is a real gap in the API: the documentation promised an
attribute the returned object's type did not have, so no caller could rely on it without a
`# type: ignore`.

```python
class Cached(Protocol[P, R_co]):
    def __call__(self, *a: P.args, **k: P.kwargs) -> R_co: ...
    def cache_info(self) -> CacheInfo: ...
    def cache_clear(self) -> None: ...
```

And `CacheInfo` is a `TypedDict`, so the **keys** are checked too:

```
_gap.py:9: error: TypedDict "CacheInfo" has no key "hitrate"  [typeddict-item]
_gap.py:9: note: Did you mean "hit_rate"?
```

No test in Day 57's suite could have found that typo. It would have been a `KeyError` at runtime, in
whatever code path first asked for a hit rate.

### 9. Without `Any`

```
MODULE                     LINES   Any   type: ignore   cast
__init__.py                   60     0              0      0
__main__.py                   59     0              0      0
containers.py                 68     0              0      0
decorators.py                253     0              0      1
numbers.py                   102     0              0      0
text.py                       62     0              0      0
                                     0              0      1
```

The one `cast()` is honest and worth looking at: `@cache` attaches two functions with `setattr`,
which mypy cannot follow, and the cast says *"I have added them, and the Protocol above is the
promise."* One cast next to the three lines that justify it is a different thing from a file
sprinkled with `# type: ignore`.

### 10. Turning it on in a codebase that has none

1. `mypy` with no flags — it checks only what is already annotated, so the number it prints is your
   real starting point.
2. Annotate the **public surface** first. That is where a wrong assumption costs most.
3. `--disallow-untyped-defs`, one package at a time.
4. `--strict`, with a per-module override for anything not there yet.

In `pyproject.toml`, so nobody has to remember flags:

```toml
[tool.mypy]
python_version = "3.11"
strict = true

[[tool.mypy.overrides]]
module = ["tests.*", "examples.*"]
disallow_untyped_defs = false
```

Exempting tests is a **decision**, not laziness: `def test_clamp_pulls_a_value_down() -> None:` adds
a return type and no information. Writing it in the config is what makes it a decision.

**And ship `py.typed`.** An empty file in your package (PEP 561) is the only thing that tells other
people's checkers your annotations exist. Without it every one of them treats your library as
untyped and all this work is invisible downstream.

### 11. What each tool catches, measured

`build.py` sabotages the package twice and runs both checkers:

| sabotage | mypy | pytest |
|---|---|---|
| none | 0 err | green |
| a wrong **answer** (the rounding bug) | **0 err** | **RED** |
| a wrong **type** (returns float, not str) | **1 err** | RED |

The rounding bug is invisible to mypy — `'1024.0 KB'` and `'1.0 MB'` are both perfectly good strings.
The wrong return type is caught by both here only because the tests compare against a string; in a
function whose result is merely passed along, mypy alone would catch it.

```
mypy    every line, shallow        "this cannot be right"
pytest  the lines it runs, deep    "this answer is wrong"
```

Which is why the answer is never "types instead of tests":

```bash
pytest -q && ruff check && mypy
```

*(Fixing the version bump for 1.2.0 also exposed a defect in Day 40's own acceptance checks: the
"version matches the package" check compared **major** versions, so it passed while `pyproject` said
1.2.0 and `__init__` said 1.1.0 — the exact drift it exists to catch. It now compares exactly, and
that was verified by making them disagree.)*

---

## The code

| File | What it does |
|---|---|
| `lesson.py` | Runs mypy on nine small modules and shows the real errors: `Any` staying silent on nonsense, a `TypeVar` keeping its promise, and a `Callable[..., Any]` decorator erasing a signature. |
| `build.py` | 32 → 0 across two real directories, the six signatures that needed a decision, the `cache_info` gap, an `Any`/`ignore`/`cast` audit, and two sabotages showing what each tool catches. |
| *(the package itself)* | `days/day-040-milestone-your-own-toolkit/mytoolkit/` — now annotated, `py.typed`, version 1.2.0. |

```bash
python3 lesson.py
python3 build.py
cd ../day-040-milestone-your-own-toolkit && python3 -m mypy mytoolkit/
```

---

## Common mistakes

**Writing hints and never running a checker.** Documentation that rots and looks authoritative.

**`Any` to make an error go away.** You switched off checking for everything it touches.

**Bare `# type: ignore`.** Silences next year's error too.

**`list[str]` on a parameter.** Accept `Iterable`; return `list`.

**`Callable[..., Any]` on a decorator.** Erases every signature it touches.

**Annotating everything at once in a large codebase.** Start with the public surface.

**Forgetting `py.typed`.** Invisible to every downstream checker.

**`-> None` omitted.** Under `--strict` that is an unannotated function.

**Believing types replace tests.** They catch different things, measurably.

---

## Exercises

1. Annotate one module and run mypy with no flags, then `--strict`. The gap is the work.
2. Put `Any` on a parameter, write nonsense with it, then change it to `object` and read the error.
3. Type a decorator as `Callable[..., Any]`, call the decorated function wrongly, then use
   `ParamSpec`.
4. Use `reveal_type(x)` to ask the checker what it thinks something is.
5. Write a `Protocol` for something structural and check a class that never mentions it.
6. Add a `TypedDict` for a config dict and misspell a key.
7. Add `-> None` to a function that returns a value and watch mypy find every caller.
8. Add `py.typed`, then delete it, and check from a directory that imports the package.

---

## Checklist

- [ ] I know annotations do nothing at runtime
- [ ] I use `list[str]`, `dict[str, int]`, `str | None`
- [ ] I accept `Iterable` and return `list`
- [ ] I use `object` rather than `Any` when I do not know
- [ ] I use a `TypeVar` when the return type follows the argument's
- [ ] I use `ParamSpec` for decorators
- [ ] I configure mypy in `pyproject.toml` and ship `py.typed`
- [ ] I run mypy and pytest, and know which catches what
