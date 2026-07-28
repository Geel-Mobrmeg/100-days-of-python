# 100 Days of Python Code

One hundred consecutive days, each one a single sitting: something to learn, something to build.
It starts at installing Python and ends with a deployed full-stack app and a package on PyPI.
No day depends on anything you haven't already written yourself.

| | |
|---|---|
| **100** | days |
| **10** | phases |
| **100** | builds |
| **~152** | hours total |
| **60–90** | min, regular day |

---

## How to run this course

**One sitting, one commit.** Finish the build before you close the editor, then commit it. The repo becomes the proof — a hundred small, dated, working programs.

**Missing a day is fine.** Skipping the build is not. The order matters far more than the calendar; pick the streak back up on the day you left it.

**Type the examples.** Reading Python is not writing Python. Every concept listed on a day should appear in something you typed yourself that day.

**Break the builds.** When a build works, change one thing until it fails, and read the traceback. Ten extra minutes here is worth an hour of tutorials.

---

## What a day looks like

Every day lives in its own folder under `days/` and contains exactly three things:

| File | What it is |
|---|---|
| `README.md` | **The article.** The day's teaching: what the concepts are, why they exist, where they bite, and the brief for the build. Read this first. |
| `lesson.py` | **The code you're taught.** Every concept from the article, runnable and annotated. Type it, run it, change it until it breaks. |
| `build.py` | **The code you build.** A complete, working reference solution for the day's project. Write yours before you read this one. |

```bash
cd days/day-001-first-contact
python lesson.py     # read and run the teaching examples
python build.py      # then the finished build
```

Days that aren't a plain script say so in their article — Day 79 is a notebook, Day 89 ships a
`Dockerfile`, Day 98 is a CI workflow. The two-part shape (article, then code) never changes.

---

## The ten phases

| # | Phase | Days | You end up able to | Milestone |
|---|---|---|---|---|
| 1 | **Foundations** | 1–10 | Get Python running and get comfortable with the four things every later day is made of: values, names, expressions and output. No libraries, no frameworks — just you and the interpreter. | A scored command-line quiz |
| 2 | **Control flow** | 11–20 | Teach your programs to decide and repeat. By the end of this phase you can express any procedure a human could follow by hand. | A playable text adventure |
| 3 | **Data structures** | 21–30 | Stop juggling loose variables. Learn the four containers Python programs are actually built out of, and which one to reach for when. | An expense tracker with monthly reports |
| 4 | **Functions & modular code** | 31–40 | Turn scripts into reusable pieces. Arguments, scope, decorators and generators — the tools that let a program grow past one file without collapsing. | Your own installable utility toolkit |
| 5 | **Object-oriented Python** | 41–50 | Model the problem instead of the procedure. Classes, dunder methods and dataclasses — plus when not to use inheritance, which matters more than the syntax. | An object-modelled inventory system |
| 6 | **Robust code** | 51–60 | The phase that separates scripts from software: errors you handle, files you read, tests that prove it works, and types that catch mistakes before you run it. | A fully tested, typed CLI tool |
| 7 | **The outside world** | 61–70 | Python's real advantage is its standard library and its ecosystem. Dates, regex, HTTP, real CLIs, logging, environments and Git — the working day-to-day kit. | A live API-powered terminal dashboard |
| 8 | **Data & analysis** | 71–80 | Handle data at a scale loops can't. NumPy for arrays, pandas for tables, matplotlib for the picture, SQL for the source — and a written conclusion at the end. | A full data analysis report |
| 9 | **Web & APIs** | 81–90 | Put your work behind a URL. Flask for pages, FastAPI for services, SQLAlchemy for storage, auth for users — and a real deployment at the end of it. | A deployed full-stack application |
| 10 | **Scale & craft** | 91–100 | The professional layer: concurrency, profiling, packaging, CI and code review. Ends with a project that is entirely yours, shipped the way real projects ship. | Capstone — ship your own project |

---

## All 100 days


### Phase 1 · Foundations · days 1–10

> Get Python running and get comfortable with the four things every later day is made of: values, names, expressions and output. No libraries, no frameworks — just you and the interpreter.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [001](days/day-001-first-contact/) | **First contact** | installing Python, the REPL vs. a script, print(), running a .py file, your editor | A program that prints your name inside an ASCII frame it draws to fit. | 60m |
| [002](days/day-002-variables-and-types/) | **Variables and types** | assignment, int, float, str, bool, dynamic typing, type(), None | A temperature converter that handles Celsius, Fahrenheit and Kelvin in both directions. | 60m |
| [003](days/day-003-strings/) | **Strings** | indexing, slicing, concatenation, escape sequences, immutability | An initials extractor that turns any full name into a set of initials. | 70m |
| [004](days/day-004-string-methods-and-f-strings/) | **String methods and f-strings** | upper / lower / strip, split & join, replace, f-strings, format specs | A receipt printer that aligns item names, quantities and prices into clean columns. | 75m |
| [005](days/day-005-numbers-and-operators/) | **Numbers and operators** | arithmetic, // and %, **, precedence, the math module, round() | A bill splitter that handles tips, uneven shares and rounds to real currency. | 70m |
| [006](days/day-006-input-and-type-conversion/) | **Input and type conversion** | input(), casting, why input is always a string, basic validation | An interactive BMI calculator that refuses nonsense input instead of crashing. | 70m |
| [007](days/day-007-booleans-and-comparison/) | **Booleans and comparison** | truthiness, == vs. is, and / or / not, chained comparison, short-circuiting | A password strength checker that reports which rules a password fails. | 75m |
| [008](days/day-008-style-comments-and-pep-8/) | **Style, comments and PEP 8** | naming conventions, docstrings, line length, black, ruff | Take a deliberately ugly 60-line script and refactor it until ruff is silent. | 60m |
| [009](days/day-009-reading-tracebacks/) | **Reading tracebacks** | stack traces, common error types, print debugging, breakpoint(), rubber-ducking | Five broken scripts, five bugs. Fix all of them and write down what each error meant. | 75m |
| [010](days/day-010-milestone-command-line-quiz/) 🏁 | **Milestone — command-line quiz** | combining everything so far, program structure, scoring, user feedback | A ten-question quiz that asks, scores, gives feedback per answer and prints a final grade. | 150m |

### Phase 2 · Control flow · days 11–20

> Teach your programs to decide and repeat. By the end of this phase you can express any procedure a human could follow by hand.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [011](days/day-011-if-elif-else/) | **if, elif, else** | branching, nesting, guard clauses, the ternary expression | A grade calculator that turns any percentage into a letter, with boundary cases handled. | 65m |
| [012](days/day-012-while-loops/) | **while loops** | loop conditions, accumulators, sentinel values, avoiding infinite loops | A number guessing game that gives higher/lower hints and counts attempts. | 70m |
| [013](days/day-013-for-loops-and-range/) | **for loops and range** | iterating sequences, range(start, stop, step), enumerate(), zip() | A multiplication table generator that lines up perfectly for any size you ask for. | 70m |
| [014](days/day-014-break-continue-and-loop-else/) | **break, continue and loop-else** | early exit, skipping iterations, for...else, flag variables | A prime number finder that stops checking the moment it knows the answer. | 70m |
| [015](days/day-015-nested-loops/) | **Nested loops** | loops inside loops, row and column thinking, cost of nesting, 2D grids | An ASCII art generator: pyramids, diamonds and a chessboard, all from nested loops. | 80m |
| [016](days/day-016-randomness-and-simulation/) | **Randomness and simulation** | random module, randint & choice, shuffle, seeding for reproducibility | A dice simulator that rolls ten thousand times and plots the distribution as text bars. | 75m |
| [017](days/day-017-structural-pattern-matching/) | **Structural pattern matching** | match / case, literal & sequence patterns, guards, the wildcard case | A command parser that turns typed instructions like 'go north' into actions. | 75m |
| [018](days/day-018-loop-patterns-worth-knowing/) | **Loop patterns worth knowing** | accumulator, search-and-flag, running min/max, single-pass thinking | Compute mean, median, mode, min and max over a list — without importing anything. | 80m |
| [019](days/day-019-time-and-pacing/) | **Time and pacing** | time.sleep(), perf_counter(), loop timing, carriage-return output | A Pomodoro timer that counts down in place and rings when the interval ends. | 70m |
| [020](days/day-020-milestone-text-adventure/) 🏁 | **Milestone — text adventure** | game loop, state, rooms & transitions, inventory, win conditions | A multi-room adventure with an inventory, locked doors and at least two endings. | 180m |

### Phase 3 · Data structures · days 21–30

> Stop juggling loose variables. Learn the four containers Python programs are actually built out of, and which one to reach for when.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [021](days/day-021-lists/) | **Lists** | creation & indexing, slicing, append / insert / pop, mutability, aliasing vs. copying | A to-do list you can add to, complete, reorder and delete from, all in memory. | 75m |
| [022](days/day-022-list-comprehensions/) | **List comprehensions** | map form, filter form, nested comprehensions, when a loop reads better | Rewrite ten explicit loops as comprehensions, then rewrite two of them back and say why. | 70m |
| [023](days/day-023-tuples-and-unpacking/) | **Tuples and unpacking** | immutability, tuple unpacking, swapping, star unpacking, namedtuple | A geometry helper: distance, midpoint and area, all passing points around as tuples. | 70m |
| [024](days/day-024-dictionaries/) | **Dictionaries** | keys & values, get() with defaults, iteration order, nesting, in | A contact book with lookup by name, partial search and safe handling of missing entries. | 80m |
| [025](days/day-025-counting-and-grouping/) | **Counting and grouping** | dict comprehensions, collections.Counter, defaultdict, inverting a dict | A word frequency analyser that reports the top twenty words in any text file. | 80m |
| [026](days/day-026-sets/) | **Sets** | uniqueness, union & intersection, difference, membership speed, frozenset | A duplicate finder that also reports what two tag lists share and where they differ. | 70m |
| [027](days/day-027-sorting/) | **Sorting** | sorted() vs. .sort(), key functions, reverse, stability, multi-key sorts | A leaderboard sorted by score descending, then by time ascending, then alphabetically. | 75m |
| [028](days/day-028-nested-data/) | **Nested data** | dicts of lists of dicts, safe traversal, flattening, shape-first thinking | Read a deeply nested config structure and answer five questions about it without crashing. | 80m |
| [029](days/day-029-choosing-the-right-structure/) | **Choosing the right structure** | list vs. set vs. dict, lookup cost, when order matters, measuring it | Benchmark membership tests across a list, a set and a dict at three sizes; explain the curve. | 75m |
| [030](days/day-030-milestone-expense-tracker/) 🏁 | **Milestone — expense tracker** | modelling with nested dicts, aggregation, reporting, input validation | Track expenses by category and month, then print a report with totals and the biggest spend. | 165m |

### Phase 4 · Functions & modular code · days 31–40

> Turn scripts into reusable pieces. Arguments, scope, decorators and generators — the tools that let a program grow past one file without collapsing.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [031](days/day-031-writing-functions/) | **Writing functions** | def & return, parameters vs. arguments, local scope, implicit None, docstrings | A personal library of ten small utilities you will actually reuse later in the course. | 75m |
| [032](days/day-032-default-and-keyword-arguments/) | **Default and keyword arguments** | default values, keyword-only args, argument order rules, the mutable default trap | A report generator whose defaults make the common call one argument long. | 75m |
| [033](days/day-033-args-and-kwargs/) | ***args and **kwargs** | packing, unpacking at the call site, forwarding arguments, signature design | A wrapper that logs every call — its name, its arguments and what it returned. | 75m |
| [034](days/day-034-scope-and-closures/) | **Scope and closures** | LEGB rule, global & nonlocal, functions returning functions, captured state | A counter factory and a memo cache, both built from closures instead of classes. | 80m |
| [035](days/day-035-lambdas-and-functional-tools/) | **Lambdas and functional tools** | lambda, map & filter, functools.reduce, readability limits | The same data pipeline written three ways — loop, comprehension, functional — then judged. | 75m |
| [036](days/day-036-recursion/) | **Recursion** | base case, the call stack, recursion limits, memoisation, when to use iteration | A directory tree walker that prints an indented listing of any folder you point it at. | 85m |
| [037](days/day-037-decorators/) | **Decorators** | functions as objects, wrapper functions, @syntax, functools.wraps, arguments | Write @timer, @retry and @cache, then apply them to your Day 31 utilities. | 90m |
| [038](days/day-038-generators-and-yield/) | **Generators and yield** | yield, lazy evaluation, generator expressions, memory footprint, itertools | Stream a 500 MB log file and count error lines without ever loading it into memory. | 85m |
| [039](days/day-039-modules-and-packages/) | **Modules and packages** | import mechanics, __name__ == '__main__', __init__.py, project layout, relative imports | Split your utilities into a proper package with submodules and a clean public surface. | 80m |
| [040](days/day-040-milestone-your-own-toolkit/) 🏁 | **Milestone — your own toolkit** | API design, docstrings, package structure, a demo script | Package your best helpers into one importable library with documentation and examples. | 150m |

### Phase 5 · Object-oriented Python · days 41–50

> Model the problem instead of the procedure. Classes, dunder methods and dataclasses — plus when not to use inheritance, which matters more than the syntax.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [041](days/day-041-classes-and-objects/) | **Classes and objects** | class statement, __init__, self, instance attributes, methods | A BankAccount class that deposits, withdraws, refuses overdrafts and keeps a history. | 80m |
| [042](days/day-042-class-vs-instance-attributes/) | **Class vs. instance attributes** | shared state, @classmethod, @staticmethod, alternative constructors | An Employee class that issues sequential IDs and can be built from a CSV row. | 80m |
| [043](days/day-043-dunder-methods/) | **Dunder methods** | __str__ vs. __repr__, __len__, __eq__, __hash__, __contains__ | A Vector class that prints usefully, compares correctly and works inside a set. | 85m |
| [044](days/day-044-operator-overloading/) | **Operator overloading** | __add__ & __sub__, __lt__, __getitem__, total_ordering, NotImplemented | A Money type that adds, compares and sorts — and refuses to mix currencies silently. | 85m |
| [045](days/day-045-inheritance/) | **Inheritance** | subclassing, super(), overriding, isinstance, the MRO | A shape hierarchy where every subclass computes its own area behind one shared interface. | 80m |
| [046](days/day-046-composition-over-inheritance/) | **Composition over inheritance** | is-a vs. has-a, delegation, fragile base classes, mixins | Take a four-level inheritance chain and rebuild it from small collaborating objects. | 85m |
| [047](days/day-047-properties-and-encapsulation/) | **Properties and encapsulation** | @property, setters, validation on assign, the underscore convention | A Temperature class where setting an impossible value raises instead of quietly storing it. | 80m |
| [048](days/day-048-dataclasses/) | **Dataclasses** | @dataclass, field defaults, frozen=True, order=True, __post_init__ | Rewrite three of your earlier classes as dataclasses and count the lines you deleted. | 75m |
| [049](days/day-049-abstract-bases-and-protocols/) | **Abstract bases and protocols** | ABC, @abstractmethod, duck typing, typing.Protocol, interface design | A plugin interface with two working implementations that the caller can't tell apart. | 85m |
| [050](days/day-050-milestone-inventory-system/) 🏁 | **Milestone — inventory system** | domain modelling, class collaboration, validation, a CLI front end | Model products, stock and orders as objects, with a menu-driven interface over the top. | 180m |

### Phase 6 · Robust code · days 51–60

> The phase that separates scripts from software: errors you handle, files you read, tests that prove it works, and types that catch mistakes before you run it.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [051](days/day-051-exceptions/) | **Exceptions** | try / except, else & finally, exception types, catching too much | A safe input reader that survives bad types, empty input and Ctrl-C without a traceback. | 80m |
| [052](days/day-052-raising-and-custom-exceptions/) | **Raising and custom exceptions** | raise, exception hierarchies, raise ... from, error messages people can act on | A validation layer for your inventory system with domain-specific error types. | 80m |
| [053](days/day-053-files-and-context-managers/) | **Files and context managers** | open() modes, with statements, encodings, reading line by line, writing safely | A log splitter that breaks one large file into daily files without loading it all at once. | 80m |
| [054](days/day-054-csv/) | **CSV** | csv.reader, DictReader & DictWriter, headers, delimiters, messy real data | Clean a CSV with missing fields and inconsistent casing, then write a summary CSV back out. | 85m |
| [055](days/day-055-json/) | **JSON** | dumps & loads, dump & load, nested structures, custom encoders, config files | A settings store that loads defaults, merges user overrides and saves changes to disk. | 80m |
| [056](days/day-056-paths-and-the-filesystem/) | **Paths and the filesystem** | pathlib.Path, globbing, exists & mkdir, shutil, cross-platform paths | A bulk renamer with a dry-run mode that shows every change before it touches anything. | 80m |
| [057](days/day-057-testing-with-pytest/) | **Testing with pytest** | assert, test discovery, arrange-act-assert, pytest.raises, test naming | Write a real test suite for the toolkit you built on Day 40 and find at least one bug. | 90m |
| [058](days/day-058-fixtures-parametrize-and-mocks/) | **Fixtures, parametrize and mocks** | @pytest.fixture, @parametrize, monkeypatch, tmp_path, isolating side effects | Table-driven tests for your validators, plus a mocked clock so time-based code is testable. | 90m |
| [059](days/day-059-type-hints/) | **Type hints** | annotations, Optional & Union, list[str] generics, mypy, typing gradually | Annotate your whole package and drive mypy to zero errors without using Any as an escape. | 85m |
| [060](days/day-060-milestone-tested-cli-tool/) 🏁 | **Milestone — tested CLI tool** | a real utility, test coverage, type checking, documentation | A file-processing tool with a test suite above 90% coverage, full type hints and a README. | 180m |

### Phase 7 · The outside world · days 61–70

> Python's real advantage is its standard library and its ecosystem. Dates, regex, HTTP, real CLIs, logging, environments and Git — the working day-to-day kit.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [061](days/day-061-dates-and-times/) | **Dates and times** | datetime & date, timedelta, strftime & strptime, zoneinfo, UTC discipline | An age and countdown calculator that gets leap years and time zones right. | 80m |
| [062](days/day-062-regular-expressions/) | **Regular expressions** | character classes, quantifiers, groups, findall & sub, greedy vs. lazy | Pull every email address, date and IP out of a messy raw text dump into a clean report. | 90m |
| [063](days/day-063-command-line-interfaces/) | **Command-line interfaces** | argparse, positional vs. optional args, subcommands, help text, exit codes | Give your Day 60 tool a real CLI with subcommands, --help and correct exit statuses. | 85m |
| [064](days/day-064-logging/) | **Logging** | levels, loggers & handlers, formatters, logging config, why not print | Replace every print in one of your projects with structured logging to console and file. | 80m |
| [065](days/day-065-http-with-requests/) | **HTTP with requests** | GET & POST, query params, headers, status codes, timeouts, raise_for_status | A weather CLI that takes a city and prints a formatted forecast from a public API. | 85m |
| [066](days/day-066-working-with-real-apis/) | **Working with real APIs** | pagination, rate limits, retry with backoff, API keys in env vars, caching | Fetch a fully paginated dataset, cache it locally and never re-request what you already have. | 90m |
| [067](days/day-067-web-scraping/) | **Web scraping** | BeautifulSoup, CSS selectors, HTML structure, robots.txt, scraping politely | Scrape a book catalogue into a CSV — title, price, rating — across multiple pages. | 90m |
| [068](days/day-068-environments-and-dependencies/) | **Environments and dependencies** | venv, pip, requirements.txt, pyproject.toml, uv, pinning versions | Give every project you have built so far a reproducible environment someone else can install. | 75m |
| [069](days/day-069-git-for-python-projects/) | **Git for Python projects** | init & commit, branches, .gitignore for Python, pre-commit hooks, readable history | Put the whole hundred-day repo under version control with a commit for each day so far. | 85m |
| [070](days/day-070-milestone-terminal-dashboard/) 🏁 | **Milestone — terminal dashboard** | live data, caching, formatting, error handling, scheduling | Pull live data from two APIs, cache it, and render a formatted dashboard in the terminal. | 165m |

### Phase 8 · Data & analysis · days 71–80

> Handle data at a scale loops can't. NumPy for arrays, pandas for tables, matplotlib for the picture, SQL for the source — and a written conclusion at the end.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [071](days/day-071-numpy-arrays/) | **NumPy arrays** | ndarray, dtypes, shape & reshape, vectorised vs. looped, array creation | Load an image as an array and produce greyscale, inverted and cropped versions of it. | 85m |
| [072](days/day-072-numpy-operations/) | **NumPy operations** | broadcasting, boolean masks, fancy indexing, axis-wise aggregation, np.where | A full grade analytics report — per student, per subject, per cohort — with no Python loops. | 90m |
| [073](days/day-073-pandas-series-and-dataframes/) | **pandas Series and DataFrames** | constructing frames, read_csv, loc vs. iloc, dtypes, head / info / describe | Load a real public dataset and produce a one-page profile of what is actually in it. | 90m |
| [074](days/day-074-cleaning-data/) | **Cleaning data** | missing values, dropna & fillna, type coercion, duplicates, string accessors | Take a deliberately messy sales export and get it to the point where every column is trustworthy. | 90m |
| [075](days/day-075-groupby-and-aggregation/) | **groupby and aggregation** | split-apply-combine, agg with multiple functions, pivot_table, multi-index | Revenue by region by quarter, with growth rates, from a single grouped expression. | 90m |
| [076](days/day-076-joining-and-reshaping/) | **Joining and reshaping** | merge & join types, concat, melt & pivot, long vs. wide, index alignment | Combine three separate exports into one analysis-ready table and prove no rows were lost. | 90m |
| [077](days/day-077-visualisation/) | **Visualisation** | figure & axes, chart type selection, labels & scales, seaborn, colour with intent | A four-panel figure where every panel supports the same single conclusion. | 90m |
| [078](days/day-078-sql-from-python/) | **SQL from Python** | sqlite3, SELECT / WHERE / JOIN / GROUP BY, parameterised queries, read_sql | Load your dataset into SQLite and answer the same five questions in SQL and in pandas. | 90m |
| [079](days/day-079-notebooks-and-exploratory-work/) | **Notebooks and exploratory work** | Jupyter, cell discipline, narrative analysis, reproducibility, when to leave the notebook | Redo one earlier analysis as a notebook that reads as an argument, not a pile of cells. | 80m |
| [080](days/day-080-milestone-data-analysis-report/) 🏁 | **Milestone — data analysis report** | framing a question, cleaning, analysis, charts, written findings | Pick a dataset, ask one real question, and answer it with charts and a written conclusion. | 180m |

### Phase 9 · Web & APIs · days 81–90

> Put your work behind a URL. Flask for pages, FastAPI for services, SQLAlchemy for storage, auth for users — and a real deployment at the end of it.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [081](days/day-081-how-the-web-actually-works/) | **How the web actually works** | request & response, methods, status codes, headers, REST, JSON payloads | Map an API you already use into a table of endpoints, methods, inputs and responses. | 70m |
| [082](days/day-082-flask-basics/) | **Flask basics** | routes, the dev server, Jinja templates, template inheritance, static files | A personal portfolio site with a shared layout and a page for each project you have built. | 90m |
| [083](days/day-083-forms-and-state/) | **Forms and state** | POST handling, server-side validation, sessions, flash messages, redirect-after-post | A guestbook that accepts entries, rejects bad ones with useful messages and remembers you. | 90m |
| [084](days/day-084-databases-with-sqlalchemy/) | **Databases with SQLAlchemy** | models, sessions, queries, relationships, migrations with Alembic | Move the guestbook off memory and onto a real database, with a migration to prove it. | 95m |
| [085](days/day-085-building-an-api-with-fastapi/) | **Building an API with FastAPI** | path & query params, Pydantic models, response models, status codes, auto docs | A complete CRUD API for your Day 50 inventory model, with generated interactive docs. | 95m |
| [086](days/day-086-authentication/) | **Authentication** | password hashing, sessions vs. tokens, JWT, protected routes, what never to store | Add signup, login and per-user data to your API — with passwords you could safely leak. | 95m |
| [087](days/day-087-testing-and-documenting-an-api/) | **Testing and documenting an API** | TestClient, fixtures for a test DB, OpenAPI, error contracts, status code discipline | A test suite that covers every endpoint including the failure paths, not just the happy ones. | 90m |
| [088](days/day-088-talking-to-a-front-end/) | **Talking to a front end** | fetch(), CORS, JSON contracts, templates vs. SPA, loading & error states | A small JavaScript front end that reads and writes through your API in the browser. | 90m |
| [089](days/day-089-deployment/) | **Deployment** | Dockerfile, environment config, gunicorn / uvicorn, secrets, logs in production | Containerise the API and ship it to a public URL that someone else can hit. | 100m |
| [090](days/day-090-milestone-full-stack-app/) 🏁 | **Milestone — full-stack app** | auth, database, API, interface, deployment | One deployed application with accounts, persistent data and a UI — live, on the internet. | 180m |

### Phase 10 · Scale & craft · days 91–100

> The professional layer: concurrency, profiling, packaging, CI and code review. Ends with a project that is entirely yours, shipped the way real projects ship.

| Day | Topic | Concepts | Build | Time |
|---|---|---|---|---|
| [091](days/day-091-concurrency-conceptually/) | **Concurrency, conceptually** | concurrency vs. parallelism, processes vs. threads, the GIL, I/O-bound vs. CPU-bound | Run one I/O workload and one CPU workload three ways each and chart which approach wins. | 85m |
| [092](days/day-092-threads-and-thread-pools/) | **Threads and thread pools** | ThreadPoolExecutor, futures, locks, race conditions, thread safety | A parallel downloader that fetches fifty files at once and reports live progress. | 90m |
| [093](days/day-093-multiprocessing/) | **Multiprocessing** | Process & Pool, map vs. imap, pickling limits, shared state, chunk sizing | Process a folder of images across every core and measure the real speed-up you got. | 90m |
| [094](days/day-094-async-and-await/) | **async and await** | the event loop, coroutines, asyncio.gather, async context managers, httpx | Fetch a hundred URLs concurrently and compare the wall-clock time against the threaded version. | 95m |
| [095](days/day-095-performance-and-profiling/) | **Performance and profiling** | timeit, cProfile, reading a profile, algorithmic vs. micro-optimisation, measuring first | Profile your slowest script, make it ten times faster, and show the before-and-after numbers. | 90m |
| [096](days/day-096-design-patterns-the-pythonic-way/) | **Design patterns, the Pythonic way** | strategy, factory, adapter, when a function beats a class, the standard library's answers | Refactor the inventory system with one pattern that removes real duplication, not just structure. | 90m |
| [097](days/day-097-packaging-and-publishing/) | **Packaging and publishing** | pyproject.toml, build backends, semantic versioning, TestPyPI, entry points | Publish your toolkit so that pip install works from a clean machine. | 95m |
| [098](days/day-098-automation-and-ci/) | **Automation and CI** | GitHub Actions, workflow files, matrix builds, scheduled jobs, badges that mean something | A pipeline that runs your tests, linter and type checker on every push and blocks on failure. | 90m |
| [099](days/day-099-reading-code-and-contributing/) | **Reading code and contributing** | navigating an unfamiliar repo, issue etiquette, small first patches, review feedback, the PR loop | Open one real pull request against an open-source Python project — docs count. | 120m |
| [100](days/day-100-capstone-ship-something-of-your-own/) 🏁 | **Capstone — ship something of your own** | scoping, building, testing, documenting, deploying, writing it up | Your idea, built and shipped: tested, documented, deployed, and written up so others can use it. | 240m |

🏁 = phase milestone: a longer sitting that assembles everything from the ten days before it.

---

## Prerequisites

Python 3.11 or newer (Day 17 needs `match`, and the type-hint syntax from Day 59 assumes 3.10+),
a text editor, and a terminal. Everything else gets installed on the day it's needed —
the first third-party package doesn't appear until Day 65.

```bash
python3 --version    # expect 3.11 or higher
```

_100 Days of Python Code — curriculum & learning path_
