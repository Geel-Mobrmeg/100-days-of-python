"""Day 036 build — a directory tree walker.

    python3 build.py                  # walks this course repository
    python3 build.py .. 3             # a different root, max depth 3
    python3 build.py . 4 --iterative  # explicit stack instead of recursion

A folder contains folders. That single sentence is why this is the right
problem for recursion, and why the recursive version below is fifteen lines
while the iterative one is twenty-five and harder to get right.

Three hazards a textbook tree does not have, all handled:

    SYMLINKS      can point at a parent, giving an infinite tree
    PERMISSIONS   a directory you cannot read raises mid-walk
    DEPTH         a deep tree exhausts the stack

os.walk() and Path.rglob() already exist and are iterative. Writing this
once is how you understand what they do.
"""

import sys
from pathlib import Path

WIDTH = 78
DEFAULT_DEPTH = 3

SKIP = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

flags = [a for a in sys.argv[1:] if a.startswith("--")]
plain = [a for a in sys.argv[1:] if not a.startswith("--")]

root = Path(plain[0]) if plain else Path(__file__).resolve().parents[2]
max_depth = int(plain[1]) if len(plain) > 1 and plain[1].isdigit() else DEFAULT_DEPTH
use_iterative = "--iterative" in flags

if not root.exists():
    sys.exit(f"No such path: {root}")

stats = {"dirs": 0, "files": 0, "bytes": 0, "skipped": 0, "denied": 0,
         "links": 0, "truncated": 0, "deepest": 0}


def human(count):
    """Bytes as something a person can read (Day 31's toolkit)."""
    size = float(count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def entries_of(path):
    """Return (dirs, files) for a path, surviving every filesystem hazard.

    This is the only function that touches the filesystem, so it is the
    only place that has to know about permissions and symlinks. The walkers
    below stay clean because of that.
    """
    try:
        children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        stats["denied"] += 1
        return [], []
    except OSError:
        stats["denied"] += 1
        return [], []

    dirs, files = [], []
    for child in children:
        if child.name in SKIP:
            stats["skipped"] += 1
            continue
        if child.is_symlink():
            # A symlink to a parent gives an INFINITE tree. Never follow one.
            stats["links"] += 1
            files.append(child)
            continue
        if child.is_dir():
            dirs.append(child)
        else:
            files.append(child)
    return dirs, files


# ===========================================================================
# THE RECURSIVE WALKER
# ===========================================================================

def walk_recursive(path, depth=0, prefix="", lines=None):
    """Print an indented listing. Returns (lines, total_bytes).

    THE THREE QUESTIONS:
      1. Smallest input?   A directory with no subdirectories — the loop
                           over `dirs` simply does not run, so it returns.
      2. Strictly smaller? Each call is one level deeper, and depth is
                           capped, so it terminates even on a pathological
                           tree.
      3. Trust the call?   Yes: assume walk_recursive returns the correct
                           byte total for a subtree, and add it up.

    `lines=None` rather than `lines=[]` — Day 32's B006. A mutable default
    here would accumulate across every separate call to the function.
    """
    if lines is None:
        lines = []

    stats["deepest"] = max(stats["deepest"], depth)

    if depth >= max_depth:
        # BASE CASE 2: too deep. Report rather than silently stopping.
        dirs, files = entries_of(path)
        if dirs or files:
            stats["truncated"] += 1
            lines.append(f"{prefix}    ... {len(dirs)} dir(s), "
                         f"{len(files)} file(s) not shown")
        return lines, 0

    dirs, files = entries_of(path)
    subtotal = 0

    items = dirs + files
    for index, child in enumerate(items):
        last = index == len(items) - 1
        branch = "`-- " if last else "|-- "
        onward = "    " if last else "|   "

        if child in dirs:
            stats["dirs"] += 1
            lines.append(f"{prefix}{branch}{child.name}/")
            # BASE CASE 1 is implicit: a directory with no children means
            # the loop inside the recursive call never runs.
            _, size = walk_recursive(child, depth + 1, prefix + onward, lines)
            subtotal += size
        else:
            try:
                size = 0 if child.is_symlink() else child.stat().st_size
            except OSError:
                size = 0
            stats["files"] += 1
            stats["bytes"] += size
            subtotal += size
            marker = " -> (symlink)" if child.is_symlink() else ""
            lines.append(f"{prefix}{branch}{child.name}{marker}"
                         f"{'' if child.is_symlink() else f'  [{human(size)}]'}")

    return lines, subtotal


# ===========================================================================
# THE ITERATIVE WALKER — the same traversal, with an explicit stack
# ===========================================================================

def _frames_for(path, depth, prefix):
    """Return one work item per entry of `path`, in the order to emit them."""
    stats["deepest"] = max(stats["deepest"], depth)

    if depth >= max_depth:
        dirs, files = entries_of(path)
        if dirs or files:
            stats["truncated"] += 1
            return [("truncated", prefix, len(dirs), len(files))]
        return []

    dirs, files = entries_of(path)
    items = dirs + files
    frames = []
    for index, child in enumerate(items):
        last = index == len(items) - 1
        frames.append(("entry", child, depth, prefix, last, child in dirs))
    return frames


def walk_iterative(root_path):
    """The same listing with no recursion, and therefore no depth limit.

    THE SUBTLE PART. The first version of this pushed all of a directory's
    children and moved on, which emitted every sibling BEFORE descending —
    a different order from the recursive version, and the comparison at the
    bottom of this file caught it.

    To match pre-order depth-first exactly, a directory's children must be
    pushed so they are emitted IMMEDIATELY after it, not after its siblings.
    That means one work item per ENTRY rather than per DIRECTORY, and
    reversed() so they pop in name order.

    You are doing by hand exactly what the call stack did for you. The cost
    is visible: the per-subtree byte roll-up is gone, because there is no
    return value per level. Only the whole-tree total survives.
    """
    lines = []
    total = 0
    stack = list(reversed(_frames_for(root_path, 0, "")))

    while stack:
        frame = stack.pop()

        if frame[0] == "truncated":
            _, prefix, n_dirs, n_files = frame
            lines.append(f"{prefix}    ... {n_dirs} dir(s), "
                         f"{n_files} file(s) not shown")
            continue

        _, child, depth, prefix, last, is_dir = frame
        branch = "`-- " if last else "|-- "
        onward = "    " if last else "|   "

        if is_dir:
            stats["dirs"] += 1
            lines.append(f"{prefix}{branch}{child.name}/")
            # Push this directory's children so they come next, not last.
            stack.extend(
                reversed(_frames_for(child, depth + 1, prefix + onward))
            )
        else:
            try:
                size = 0 if child.is_symlink() else child.stat().st_size
            except OSError:
                size = 0
            stats["files"] += 1
            stats["bytes"] += size
            total += size
            marker = " -> (symlink)" if child.is_symlink() else ""
            lines.append(f"{prefix}{branch}{child.name}{marker}"
                         f"{'' if child.is_symlink() else f'  [{human(size)}]'}")

    return lines, total


# ===========================================================================
# RUN
# ===========================================================================

print("=" * WIDTH)
print(f"{'DIRECTORY TREE':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'root':<16}{str(root.resolve())[-58:]:>{WIDTH - 16}}")
print(f"{'max depth':<16}{max_depth:>{WIDTH - 16}}")
print(f"{'walker':<16}"
      f"{('explicit stack' if use_iterative else 'recursive'):>{WIDTH - 16}}")
print("-" * WIDTH)
print(f"{root.name or root}/")

if use_iterative:
    lines, size = walk_iterative(root)
else:
    lines, size = walk_recursive(root)

for line in lines:
    print(line[:WIDTH])

print("-" * WIDTH)
print(f"{'directories':<24}{stats['dirs']:>{WIDTH - 24},}")
print(f"{'files':<24}{stats['files']:>{WIDTH - 24},}")
print(f"{'total size':<24}{human(stats['bytes']):>{WIDTH - 24}}")
print(f"{'deepest level reached':<24}{stats['deepest']:>{WIDTH - 24}}")
print(f"{'skipped (.git etc)':<24}{stats['skipped']:>{WIDTH - 24},}")
print(f"{'symlinks not followed':<24}{stats['links']:>{WIDTH - 24},}")
print(f"{'permission denied':<24}{stats['denied']:>{WIDTH - 24},}")
print(f"{'truncated at max depth':<24}{stats['truncated']:>{WIDTH - 24},}")
print("=" * WIDTH)

# ===========================================================================
# BOTH WALKERS, SAME ANSWER
# ===========================================================================

before = dict(stats)
recursive_lines, _ = walk_recursive(root)
stats.update(before)
iterative_lines, _ = walk_iterative(root)
stats.update(before)

print()
print(f"{'recursive produced':<34}{len(recursive_lines):>8} lines")
print(f"{'iterative produced':<34}{len(iterative_lines):>8} lines")
print(f"{'identical listings':<34}"
      f"{str(recursive_lines == iterative_lines):>8}")

print(f"""
WHY RECURSION IS THE RIGHT TOOL HERE

  A folder contains folders. The recursive walker says exactly that and
  nothing else: for each subdirectory, do the same thing one level deeper.
  Fifteen lines, and the byte roll-up is free because each call RETURNS its
  subtree's total.

  The iterative version has to carry (path, depth, prefix) on the stack by
  hand, reverse the pending list to preserve order, and — the real tell —
  cannot roll up per-subtree sizes without a second structure, because
  there is no return value per level. It only totals the whole tree.

WHY YOU MIGHT STILL WANT IT

  No depth limit. A tree 5,000 levels deep kills the recursive version with
  RecursionError and the iterative one does not notice. Raising
  sys.setrecursionlimit() is not the fix; the explicit stack is.

  In practice: use recursion for trees, and reach for the stack only when
  the depth is genuinely unbounded — or just use os.walk(), which is
  iterative and written by people who have thought about all of this.""")


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run with max_depth 1, then 6. The "truncated" count should change and
#     the listing should never lie about what it did not show.
#
#   * Make a symlink pointing at a parent directory:
#         ln -s .. days/loop
#     Run it. The walker reports the link and does not follow it. Now delete
#     the is_symlink() check and watch it recurse until RecursionError —
#     that is the hazard, and it is one line of defence.
#
#   * Add per-directory subtotals to the RECURSIVE version. It is two lines,
#     because each call already returns its subtree total. Then try adding
#     them to the iterative version and see how much harder it is.
#
#   * Sort directories by total size rather than by name. You need the sizes
#     before you can print the tree, so it becomes two passes — a real
#     consequence of the recursion returning as it unwinds.
#
#   * Replace the whole thing with os.walk() and compare. Then look at the
#     CPython source for os.walk and note that it is iterative, for exactly
#     the depth reason above.
