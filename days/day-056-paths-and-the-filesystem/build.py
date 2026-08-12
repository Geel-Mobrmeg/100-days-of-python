"""Day 056 build — a bulk renamer that shows you everything first.

    python3 build.py                     # the demonstration, on a sample tree
    python3 build.py ~/Downloads         # DRY RUN on a folder of your own
    python3 build.py ~/Downloads --apply # ...and actually do it

THE DESIGN DECISION, AND IT IS THE WHOLE DAY:

    DRY RUN IS THE DEFAULT. Doing the work needs --apply.

A tool that renames files is a tool that can lose them, and the difference
between "shows you the plan" and "shows you the plan unless you forget a
flag" is the difference between a tool people trust and one they run once.

THE FOUR PROBLEMS A NAIVE RENAMER GETS WRONG:

    collisions    two files that normalise to the same name
    cycles        a -> b while b -> a. Rename in order and one is gone.
    overwrites    Path.rename() replaces silently on POSIX
    case          'A.txt' -> 'a.txt' is a no-op on Linux and a conflict on
                  a case-insensitive disk

All four are handled below, and all four are checked at the bottom.
"""

import hashlib
import re
import shutil
import sys
import tempfile
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

WIDTH = 78

# Windows forbids these, and any name that ends in a dot or a space.
ILLEGAL = r'<>:"|?*\\/' + "".join(chr(c) for c in range(32))
RESERVED = {"con", "prn", "aux", "nul",
            *(f"com{n}" for n in range(1, 10)),
            *(f"lpt{n}" for n in range(1, 10))}
EXTENSION_ALIASES = {".jpeg": ".jpg", ".JPG": ".jpg", ".htm": ".html",
                     ".tif": ".tiff", ".mpeg": ".mpg", ".TXT": ".txt"}


# ###########################################################################
# THE NAMING RULE
# ###########################################################################

def tidy_name(path, when=None):
    """Return the name this file should have. Pure: it touches nothing.

    A pure function of (name, mtime) is what makes the dry run HONEST —
    the preview and the rename cannot disagree, because they call this.
    """
    stem, suffix = path.stem, path.suffix

    # 1. Normalise the extension: .JPEG, .jpeg and .JPG are all .jpg
    suffix = EXTENSION_ALIASES.get(suffix, EXTENSION_ALIASES.get(
        suffix.lower(), suffix.lower()))

    # 2. Fold accents off LATIN letters: 'café' -> 'cafe'
    #
    #    THE NAIVE VERSION OF THIS STEP IS WRONG, and this file had the
    #    bug before it had the check. "decompose, then drop every
    #    combining mark" also turns Russian 'й' into 'и' — a different
    #    letter, in a different word — because й decomposes to и plus a
    #    combining breve. Folding is a Latin convenience, so it is applied
    #    only where the base character is ASCII.
    folded = []
    for character in unicodedata.normalize("NFKD", stem):
        if unicodedata.combining(character):
            if folded and folded[-1].isascii():
                continue                      # an accent on a Latin letter
        folded.append(character)
    stem = unicodedata.normalize("NFC", "".join(folded))

    # 3. Lower case; illegal characters and whitespace become '-'
    #
    #    KEEPING \w RATHER THAN [a-z0-9] IS A DELIBERATE CHOICE. An
    #    ASCII-only slug turns 'Другой файл.md' into 'unnamed.md' and
    #    every Greek, Arabic, Hebrew, Hindi, Chinese or Japanese filename
    #    into the same thing — silently, and identically, so they then
    #    collide with each other. Modern filesystems store Unicode names
    #    perfectly well; the only characters that MUST go are the ones
    #    Windows forbids.
    stem = stem.lower()
    stem = re.sub(rf"[{re.escape(ILLEGAL)}\s_]+", "-", stem)
    stem = re.sub(r"[^\w.-]+", "-", stem, flags=re.UNICODE)
    stem = re.sub(r"-{2,}", "-", stem).strip("-.")

    # 4. A date prefix from the file's own modification time
    if when is not None:
        stem = f"{when:%Y-%m-%d}-{stem}"

    # 5. Windows reserved names, with or without an extension
    if stem.lower() in RESERVED:
        stem = f"{stem}-file"

    # 6. Never empty, never absurdly long (leave room for a -2 suffix)
    stem = stem or "unnamed"
    stem = stem[:100]

    return stem + suffix


def modified_at(path):
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


# ###########################################################################
# THE PLAN
# ###########################################################################

class Change:
    """One proposed rename, and what is known about it."""

    __slots__ = ("source", "target", "status", "note")

    def __init__(self, source, target, status, note=""):
        self.source = source
        self.target = target
        self.status = status          # rename | unchanged | conflict | skipped
        self.note = note

    @property
    def acts(self):
        return self.status == "rename"


def plan(folder, dated=False, recursive=False):
    """Work out every rename WITHOUT touching anything.

    Returns a list of Change. Nothing here opens, moves or creates a file;
    the only filesystem calls are the listing and stat().
    """
    folder = Path(folder).resolve()
    files = sorted(p for p in (folder.rglob("*") if recursive
                               else folder.iterdir()) if p.is_file())

    proposed = []
    for source in files:
        when = modified_at(source) if dated else None
        target = source.with_name(tidy_name(source, when))
        proposed.append((source, target))

    # WHO IS ALREADY THERE, and who wants to be there.
    existing = {p.name.lower() for p in files}
    wanted = Counter(target.name.lower() for _, target in proposed)

    changes = []
    for source, target in proposed:
        key = target.name.lower()

        if source.name == target.name:
            changes.append(Change(source, target, "unchanged"))
            continue

        # TWO FILES WANT THE SAME NAME. Refuse both, loudly. Auto-numbering
        # them would be a defensible other choice — and it would make the
        # result depend on directory order, which is not stable.
        if wanted[key] > 1:
            changes.append(Change(source, target, "conflict",
                                  f"{wanted[key]} files want {target.name!r}"))
            continue

        # THE TARGET EXISTS AND IS NOT PART OF THE PLAN — so nothing will
        # move it out of the way, and renaming onto it would destroy it.
        renamed_away = {s.name.lower() for s, t in proposed
                        if s.name != t.name}
        if key in existing and key not in renamed_away:
            changes.append(Change(source, target, "conflict",
                                  f"{target.name!r} already exists"))
            continue

        changes.append(Change(source, target, "rename"))

    return changes


# ###########################################################################
# APPLYING IT — in two phases, which is the only correct way
# ###########################################################################

def apply(changes):
    """Rename in two passes so cycles and swaps cannot lose a file.

    THE PROBLEM: given a -> b and b -> a, renaming in any order destroys
    one of them, because rename() overwrites.

    THE FIX: move every source to a unique temporary name first, then move
    each temporary to its target. No target is ever occupied when it is
    written to, so no order is wrong.
    """
    acting = [c for c in changes if c.acts]
    staged = []
    done = 0

    try:
        for change in acting:
            temporary = change.source.with_name(
                f".renaming-{change.source.name}-"
                f"{hashlib.sha1(str(change.source).encode()).hexdigest()[:8]}"
            )
            change.source.rename(temporary)
            staged.append((temporary, change.target))

        for temporary, target in staged:
            temporary.rename(target)
            done += 1
    except OSError:
        # Put back anything still parked under a temporary name.
        for temporary, target in staged[done:]:
            if temporary.exists():
                temporary.rename(target.with_name(
                    temporary.name.split("-", 2)[2].rsplit("-", 1)[0]))
        raise
    return done


def report(changes, folder, applied=False):
    counts = Counter(c.status for c in changes)
    print(f"\n  {'BEFORE':<34}{'AFTER':<34}{'':<8}")
    print("  " + "-" * (WIDTH - 4))
    for change in changes:
        before = change.source.name
        after = (change.target.name if change.status != "unchanged"
                 else "(no change)")
        mark = {"rename": "->", "unchanged": "  ",
                "conflict": "!!", "skipped": ".."}[change.status]
        print(f"  {before[:33]:<34}{after[:33]:<34}{mark:<8}")
        if change.note:
            print(f"  {'':<34}{change.note[:40]}")
    print("  " + "-" * (WIDTH - 4))
    verb = "renamed" if applied else "would rename"
    print(f"  {folder}")
    print(f"  {verb} {counts['rename']}, "
          f"unchanged {counts['unchanged']}, "
          f"refused {counts['conflict']}")
    return counts


# ###########################################################################
# A SAMPLE TREE, WITH EVERY AWKWARD CASE IN IT
# ###########################################################################

SAMPLE = [
    "Holiday Photo 01.JPEG",
    "  leading and trailing  .txt",
    "café menu (final).PDF",
    "report:draft.txt",                     # ':' is illegal on Windows
    "Report Draft.txt",                     # ...and collides with the above
    "CON.txt",                              # reserved on Windows
    "already-tidy.txt",
    "UPPER.TXT",
    "spaces   and___underscores.md",
    "a.txt",                                # a -> b and b -> a, below
    "B.TXT",
    "naïve-résumé.docx",
    "....dots....txt",
    "2019 Invoice #7 (paid).csv",
]


def make_sample(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for name in SAMPLE:
        path = folder / name
        path.write_text(f"contents of {name}\n", encoding="utf-8")
    return folder


def fingerprint(folder):
    """The multiset of file CONTENTS. Renaming must not change it."""
    return Counter(hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(folder.iterdir()) if p.is_file())


# ###########################################################################
# RUN IT
# ###########################################################################

arguments = [a for a in sys.argv[1:] if not a.startswith("-")]
flags = {a for a in sys.argv[1:] if a.startswith("-")}

if arguments:
    FOLDER = Path(arguments[0]).expanduser().resolve()
    TEMPORARY = False
    if not FOLDER.is_dir():
        sys.exit(f"{FOLDER} is not a directory")
else:
    ROOT = Path(tempfile.mkdtemp(prefix="day056-build-"))
    FOLDER = make_sample(ROOT / "downloads")
    TEMPORARY = True

print("=" * WIDTH)
print(f"{'BULK RENAMER — DRY RUN':^{WIDTH}}")
print("=" * WIDTH)

before = fingerprint(FOLDER)
before_names = sorted(p.name for p in FOLDER.iterdir() if p.is_file())
before_mtimes = {p.name: p.stat().st_mtime
                 for p in FOLDER.iterdir() if p.is_file()}

changes = plan(FOLDER)
counts = report(changes, FOLDER, applied=False)

print("""
  NOTHING HAS HAPPENED YET. That is the point of the tool: you read the
  right-hand column, and only then decide.

  Read the refusals, though — a `!!` is not a failure of the renamer, it
  is a question only you can answer.""")

# Prove the dry run really did nothing.
untouched = (sorted(p.name for p in FOLDER.iterdir() if p.is_file())
             == before_names)
mtimes_unchanged = all(
    p.stat().st_mtime == before_mtimes[p.name]
    for p in FOLDER.iterdir() if p.is_file()
)
print(f"  {'file names unchanged by the dry run':<52}{untouched}")
print(f"  {'modification times unchanged':<52}{mtimes_unchanged}")


# ###########################################################################
# APPLYING
# ###########################################################################

if TEMPORARY or "--apply" in flags:
    print()
    print("=" * WIDTH)
    print(f"{'--apply':^{WIDTH}}")
    print("=" * WIDTH)

    renamed = apply(changes)
    after = fingerprint(FOLDER)

    print(f"\n  renamed {renamed} files")
    print(f"  {'no file contents were lost or duplicated':<52}"
          f"{after == before}")
    print(f"  {'file count is the same':<52}"
          f"{sum(after.values()) == sum(before.values())}")

    print("\n  the folder now:")
    for path in sorted(FOLDER.iterdir()):
        print(f"    {path.name}")

    # Running it again must propose nothing: the rule is idempotent.
    second = plan(FOLDER)
    second_counts = Counter(c.status for c in second)
    print(f"\n  {'running it again proposes 0 renames':<52}"
          f"{second_counts['rename'] == 0}")
else:
    print("\n  (dry run only — add --apply to perform these renames)")
    renamed, after, second_counts = 0, before, Counter()


# ###########################################################################
# THE CYCLE, ON ITS OWN
# ###########################################################################

if TEMPORARY:
    print()
    print("=" * WIDTH)
    print(f"{'THE CASE A ONE-PASS RENAMER LOSES A FILE ON':^{WIDTH}}")
    print("=" * WIDTH)

    def build_swap(folder):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "a.txt").write_text("I am A\n", encoding="utf-8")
        (folder / "b.txt").write_text("I am B\n", encoding="utf-8")
        return folder

    def swap_plan(folder):
        return [Change(folder / "a.txt", folder / "b.txt", "rename"),
                Change(folder / "b.txt", folder / "a.txt", "rename")]

    naive_folder = build_swap(ROOT / "naive")
    for change in swap_plan(naive_folder):
        change.source.rename(change.target)       # ONE pass. Watch.

    two_phase_folder = build_swap(ROOT / "two-phase")
    apply(swap_plan(two_phase_folder))

    print("\n  a.txt says 'I am A', b.txt says 'I am B', and the plan is to"
          "\n  swap their names.\n")
    print(f"  {'':<16}{'a.txt':<20}{'b.txt':<20}{'FILES':>8}")
    print("  " + "-" * (WIDTH - 4))
    for label, folder in [("one pass", naive_folder),
                          ("two phases", two_phase_folder)]:
        contents = {p.name: p.read_text(encoding="utf-8").strip()
                    for p in folder.iterdir()}
        print(f"  {label:<16}{contents.get('a.txt', '-- GONE --'):<20}"
              f"{contents.get('b.txt', '-- GONE --'):<20}"
              f"{len(contents):>8}")

    print("""
  The one-pass version renamed a.txt onto b.txt — destroying 'I am B' —
  and then renamed the result back. Two files went in, one came out, and
  Python raised nothing at all.

  The two-phase version parks both under temporary names first, so neither
  target is occupied when it is written to. It is six extra lines and it
  is not optional.""")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

names_now = {p.name for p in FOLDER.iterdir() if p.is_file()}


def tidy(name):
    return tidy_name(Path(name))


claims = [
    ("the dry run changed no names", untouched),
    ("the dry run changed no timestamps", mtimes_unchanged),
    ("spaces become dashes", tidy("a b c.txt") == "a-b-c.txt"),
    ("case is normalised", tidy("UPPER.TXT") == "upper.txt"),
    ("accents are folded", tidy("café.txt") == "cafe.txt"),
    ("...including decomposed ones",
     tidy("café.txt") == tidy("café.txt")),
    ("extensions are unified", tidy("x.JPEG") == "x.jpg"
     and tidy("x.jpeg") == "x.jpg"),
    ("characters Windows forbids are removed",
     all(c not in tidy('a:b"c|d?e*f.txt') for c in ':"|?*')),
    ("Windows reserved names are escaped",
     tidy("CON.txt") == "con-file.txt"),
    ("a name that is all punctuation still gets a name",
     tidy("...___...txt") not in ("", ".txt")),
    ("a non-Latin name is kept, not flattened to 'unnamed'",
     tidy("Другой файл.md") == "другой-файл.md"),
    ("...and so is a Japanese one", tidy("日本語 ファイル.txt")
     == "日本語-ファイル.txt"),
    ("names are capped in length", len(tidy("x" * 400 + ".txt")) <= 105),
    ("the rule is idempotent", tidy(tidy("Holiday Photo 01.JPEG"))
     == tidy("Holiday Photo 01.JPEG")),
    ("two files wanting one name are BOTH refused",
     sum(1 for c in changes if c.status == "conflict") >= 2),
    ("...so no rename destroys another file",
     len({c.target.name for c in changes if c.acts})
     == len([c for c in changes if c.acts])),
]

if TEMPORARY:
    claims += [
        ("no contents were lost by --apply", after == before),
        ("the file count is unchanged",
         sum(after.values()) == sum(before.values())),
        ("running it twice proposes nothing", second_counts["rename"] == 0),
        ("a swap keeps both files under two phases",
         len(list((ROOT / 'two-phase').iterdir())) == 2),
        ("...where one pass loses one",
         len(list((ROOT / 'naive').iterdir())) == 1),
    ]

print()
for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(p for _, p in claims)} of {len(claims)} checks pass")

print("""
  THE TWO THAT MATTER MOST ARE THE FIRST AND THE LAST.

  A dry run that quietly touched a timestamp would be a dry run nobody
  could trust, so it is checked rather than asserted — and it is only
  trustworthy because plan() and apply() share one pure naming function.
  A preview computed by different code from the action is a lie waiting
  to happen.

  And a swap is not an exotic case. Any renamer whose rule can map two
  existing names onto each other will meet one, and will lose a file with
  no exception, no warning and no way back.

  THE UNICODE CHECKS ARE HERE BECAUSE THIS FILE FAILED THEM. The first
  version of tidy_name() used the textbook accent-folding recipe —
  decompose, drop every combining mark — which turns 'café' into 'cafe'
  and Russian 'Другой файл' into 'другои-фаил', because 'й' decomposes to
  'и' plus a breve. Two different letters, silently merged, in every file
  a Russian speaker owns. Folding is a Latin convenience and is now
  applied only where the base character is ASCII.""")
print("=" * WIDTH)

if TEMPORARY:
    shutil.rmtree(ROOT, ignore_errors=True)
    print(f"\n(temporary directory {ROOT} removed)", file=sys.stderr)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run it with dated=True in plan() and watch every name gain its own
#     modification date. Then run it TWICE and find out whether the rule
#     is still idempotent. (It is not. Fix it.)
#
#   * Replace the conflict refusal with automatic numbering — name-2.txt,
#     name-3.txt — and work out what makes the result depend on the order
#     the operating system happened to list the directory in.
#
#   * Add --undo: write the plan to a JSON file (Day 55) before applying,
#     and reverse it. That file is the only thing standing between a user
#     and a folder they cannot restore.
#
#   * Make it recursive with `recursive=True`, then break it by renaming a
#     DIRECTORY that later files live inside. Decide what order fixes it.
#
#   * Delete the two-phase logic and re-run the swap check. One check
#     fails, and it is the one that costs somebody a file.
#
#   * On Day 64, put a real argparse interface on it — with --apply,
#     --recursive, --dated and --pattern — and it becomes a tool you keep.
