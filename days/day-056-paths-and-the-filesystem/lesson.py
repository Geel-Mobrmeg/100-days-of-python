"""Day 056 — Paths, and the filesystem underneath them.

    python3 lesson.py

Everything destructive happens in a scratch directory that is created and
removed by this file.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

WIDTH = 76

WORK = Path(tempfile.mkdtemp(prefix="day056-"))

# ---------------------------------------------------------------------------
# 1. A path is an object, not a string
# ---------------------------------------------------------------------------

print("=" * WIDTH)
print(f"{'1. A PATH IS AN OBJECT':^{WIDTH}}")
print("=" * WIDTH)
print("""
  THE OLD WAY                             THE PATHLIB WAY
  os.path.join(a, b, c)                   Path(a) / b / c
  os.path.basename(p)                     p.name
  os.path.splitext(p)[0]                  p.stem
  os.path.splitext(p)[1]                  p.suffix
  os.path.dirname(p)                      p.parent
  os.path.exists(p)                       p.exists()
  os.makedirs(p, exist_ok=True)           p.mkdir(parents=True, exist_ok=True)
  open(p).read()                          p.read_text(encoding="utf-8")

  The `/` operator is not cuteness. It uses the right separator on every
  platform, so "c:\\\\users\\\\" + name never appears in your code again.""")

sample = Path("/home/ada/docs/report.final.tar.gz")

print(f"\n  {sample}\n")
for attribute in ("name", "stem", "suffix", "suffixes", "parent", "parts"):
    print(f"    .{attribute:<12}{getattr(sample, attribute)}")

print(f"""
  READ .stem AND .suffix AGAIN. `.suffix` is the LAST one and `.stem` is
  everything before it, so this file's stem is 'report.final.tar'. If you
  want the real base name, strip suffixes in a loop or use .suffixes.

  .with_suffix('.zip')  ->  {sample.with_suffix('.zip').name}
  .with_stem('final')   ->  {sample.with_stem('final').name}
  .with_name('x.txt')   ->  {sample.with_name('x.txt').name}""")


# ---------------------------------------------------------------------------
# 2. Relative, absolute, and where you actually are
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'2. WHERE ARE YOU?':^{WIDTH}}")
print("=" * WIDTH)

print(f"""
  Path.cwd()          {Path.cwd()}
  Path.home()         {Path.home()}
  __file__'s folder   {Path(__file__).parent.name}/

  A RELATIVE PATH IS RESOLVED AGAINST THE WORKING DIRECTORY, which is
  where the user ran the command — NOT where your script lives. This is
  the single commonest "it works on my machine":

      Path("data.csv")                       depends on the caller's shell
      Path(__file__).parent / "data.csv"     always next to the script

  Use the second for files that ship WITH your code, and the first for
  files the user is pointing you at.""")

messy = Path(WORK) / "sub" / ".." / "sub" / "./file.txt"
(WORK / "sub").mkdir()
(WORK / "sub" / "file.txt").write_text("hello", encoding="utf-8")

print(f"  as written    ...{str(messy)[-38:]}")
print(f"  .resolve()    ...{str(messy.resolve())[-38:]}")
print("""
  .resolve() removes '..' and '.', follows symlinks, and makes the path
  absolute. Do it BEFORE you compare two paths or check whether one is
  inside another — string comparison on unresolved paths is how directory
  traversal bugs happen.""")

root = WORK.resolve()
for candidate in ("sub/file.txt", "../../etc/passwd", "sub/../../elsewhere"):
    target = (root / candidate).resolve()
    inside = target.is_relative_to(root)
    print(f"  {candidate:<24}inside the root? {inside}")

print("""
  is_relative_to() on RESOLVED paths is the check. If you ever accept a
  filename from a user — an upload, a URL, a config — this is the line
  that stops '../../etc/passwd'.""")


# ---------------------------------------------------------------------------
# 3. Finding files
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'3. FINDING THINGS':^{WIDTH}}")
print("=" * WIDTH)

tree = {
    "notes.txt": "a",
    "photo.JPG": "b",
    "archive/old.txt": "c",
    "archive/2025/summary.csv": "d",
    "archive/2025/photo.jpg": "e",
    ".hidden": "f",
}
for relative, content in tree.items():
    path = WORK / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

queries = [
    ("iterdir()", lambda: WORK.iterdir()),
    ("glob('*.txt')", lambda: WORK.glob("*.txt")),
    ("glob('*')", lambda: WORK.glob("*")),
    ("rglob('*.txt')", lambda: WORK.rglob("*.txt")),
    ("glob('**/*.csv')", lambda: WORK.glob("**/*.csv")),
    ("rglob('*.[jJ][pP]*[gG]')", lambda: WORK.rglob("*.[jJ][pP]*[gG]")),
]

print()
for label, query in queries:
    found = sorted(p.relative_to(WORK).as_posix() for p in query())
    print(f"  {label:<26}{', '.join(found)[:WIDTH - 30]}")

import glob as glob_module                                # noqa: E402

others = sorted(Path(found).name
                for found in glob_module.glob(str(WORK / "*")))
print("\n  ...and the same pattern, through the stdlib `glob` module:\n")
print(f"  {'glob.glob(work + /*)':<26}{', '.join(others)[:WIDTH - 30]}")

print("""
  THREE THINGS TO NOTICE:

    * pathlib's glob('*') DOES return '.hidden'. The stdlib `glob` module's
      glob('*') does NOT — the two have opposite defaults, and code
      converted from one to the other silently changes which files it
      touches. (`iterdir()` returns everything, always.)
    * rglob(p) is glob('**/' + p) — the same thing, spelled shorter.
    * GLOB IS CASE-SENSITIVE ON LINUX AND NOT ON macOS/WINDOWS. '*.jpg'
      finds one file here and two on a Mac. Match case yourself if it
      matters — with a character class, or by filtering on
      p.suffix.lower().

  AND GLOB RETURNS AN ITERATOR IN ARBITRARY ORDER. sorted() it, or your
  output changes between runs and between machines.""")


# ---------------------------------------------------------------------------
# 4. Making, moving, copying, removing
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'4. THE OPERATIONS, AND WHICH ONE BITES':^{WIDTH}}")
print("=" * WIDTH)
print("""
  p.mkdir()                       FileExistsError if it exists
  p.mkdir(parents=True,           the one you almost always want
          exist_ok=True)
  p.touch()                       create, or update the timestamp
  p.unlink()                      delete a FILE (missing_ok=True to ignore)
  p.rmdir()                       delete an EMPTY directory
  shutil.rmtree(p)                delete a directory AND EVERYTHING IN IT
  p.rename(q)                     move/rename — see below
  p.replace(q)                    move/rename, always overwriting
  shutil.copy2(p, q)              copy, keeping the timestamps
  shutil.copytree(p, q)           copy a whole tree
  shutil.move(p, q)               move, and works ACROSS filesystems
  shutil.disk_usage(p)            total, used, free
  shutil.which("git")             where a command lives, or None""")

(WORK / "a.txt").write_text("AAA", encoding="utf-8")
(WORK / "b.txt").write_text("BBB", encoding="utf-8")
(WORK / "a.txt").rename(WORK / "b.txt")

print(f"""
  THE ONE THAT BITES:

      a.txt contains 'AAA', b.txt contains 'BBB'
      a.txt.rename(b.txt)
      b.txt now contains {(WORK / 'b.txt').read_text(encoding='utf-8')!r} and BBB IS GONE

  rename() overwrites an existing file on POSIX, silently, with no
  confirmation and no way back. (On Windows it raises instead, so the same
  code behaves differently — which is worse.) If the destination might
  exist, CHECK FIRST, and know that the check is not atomic:

      if not destination.exists():
          source.rename(destination)

  Between those two lines another process can create the file. For a
  rename there is no atomic "only if absent" in the standard library;
  os.link() plus unlink is the POSIX trick, and for most tools the honest
  answer is to check, and to say so in the documentation.""")

print(f"\n  shutil.disk_usage('/').free = "
      f"{shutil.disk_usage('/').free / 1e9:.1f} GB")
print(f"  shutil.which('python3')     = {shutil.which('python3')}")


# ---------------------------------------------------------------------------
# 5. Metadata
# ---------------------------------------------------------------------------

print()
print("-" * WIDTH)
print("  WHAT stat() KNOWS")
print("-" * WIDTH)

target = WORK / "notes.txt"
info = target.stat()
print(f"""
  st_size      {info.st_size} bytes
  st_mtime     {info.st_mtime:.0f}   (seconds since 1970 — Day 61 formats it)
  st_mode      {info.st_mode:o}   (octal: type and permissions)

  p.exists()      {target.exists()}
  p.is_file()     {target.is_file()}
  p.is_dir()      {target.is_dir()}
  p.is_symlink()  {target.is_symlink()}

  EXISTS() ANSWERS A QUESTION ABOUT THE PAST. By the time you act on it,
  the answer may have changed — Day 51's LBYL gap. For opening a file,
  try/except FileNotFoundError has no gap. For a bulk tool that must
  report before it acts, you check anyway, and you re-check as you go.""")


# ---------------------------------------------------------------------------
# 6. Cross-platform
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
TITLE_5 = "5. THE SAME CODE ON SOMEBODY ELSE'S MACHINE"
print(f"{TITLE_5:^{WIDTH}}")
print("=" * WIDTH)

print(f"""
  PurePosixPath('a/b') / 'c'        {PurePosixPath('a/b') / 'c'}
  PureWindowsPath('a/b') / 'c'      {PureWindowsPath('a/b') / 'c'}

  The Pure* classes manipulate paths for a platform you are NOT on — for
  writing a Windows path from Linux, or for tests.

  WHAT ACTUALLY DIFFERS:

    CASE          Linux: 'File.txt' and 'file.txt' are two files.
                  macOS/Windows: usually the same file. A renamer that
                  lowercases names is a no-op on one and a rename on the
                  other — and 'a.txt' -> 'A.txt' can fail as "already
                  exists" on a case-insensitive disk.

    SEPARATORS    Path handles it. Never build a path with + or f-strings.

    ILLEGAL       Windows forbids  < > : " | ? *  and trailing dots or
    CHARACTERS    spaces. Linux forbids only '/' and NUL. A tool that
                  writes 'report: final.txt' works here and cannot even
                  create the file there.

    RESERVED      CON, PRN, AUX, NUL, COM1-9, LPT1-9 — with ANY extension.
    NAMES         'nul.txt' is not a legal Windows filename.

    LENGTH        260 characters, historically, on Windows.

  IF YOUR TOOL NAMES FILES, sanitise for the strictest platform even if
  you are not on it. Today's build does, and it is eight lines.""")


# ---------------------------------------------------------------------------
# 7. The dangerous one
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'6. THE LINE TO BE FRIGHTENED OF':^{WIDTH}}")
print("=" * WIDTH)
print("""
      shutil.rmtree(path)

  No confirmation, no recycle bin, no undo. If `path` came from a variable
  that turned out to be '/' or '' or the user's home directory, that is
  the end of the conversation.

  FOUR HABITS:

    1. RESOLVE FIRST, then assert the target is where you think:
           target = base.joinpath(name).resolve()
           if not target.is_relative_to(base.resolve()):
               raise ValueError(...)
    2. NEVER build a destructive path by concatenation.
    3. DRY RUN BY DEFAULT. Print what you would do; require a flag to do
       it. Today's build is built that way round on purpose.
    4. In a script that deletes, check for the empty string explicitly.
       `Path("")` is `Path('.')`, and rmtree('.') is your project.""")

print()
print("=" * WIDTH)
print("""  1. Path over os.path; `/` over string joining.
  2. .stem/.suffix take only the LAST extension.
  3. Path(__file__).parent for files that ship with your code.
  4. .resolve() before comparing, and .is_relative_to() to stay inside.
  5. glob skips dotfiles, returns an iterator, and is case-sensitive here
     and not elsewhere. sorted() it.
  6. rename() silently overwrites on POSIX and raises on Windows.
  7. Sanitise names for the strictest platform.
  8. Dry run by default.""")
print("=" * WIDTH)

shutil.rmtree(WORK, ignore_errors=True)
print(f"\n(scratch directory {WORK} removed)", file=sys.stderr)
assert not WORK.exists()                                    # noqa: S101
assert os.getcwd()                                          # noqa: S101


# ---------------------------------------------------------------------------
# Now break it
# ---------------------------------------------------------------------------
#
#   * Print .stem and .suffix for 'archive.tar.gz'. Then write the loop
#     that strips every suffix.
#
#   * Run a script that opens Path('data.csv') from a different working
#     directory. Then fix it with Path(__file__).parent.
#
#   * glob('*.jpg') a folder containing 'a.JPG'. Compare what you get on
#     Linux with what a colleague gets on a Mac.
#
#   * rename() a file onto an existing one and read the other file
#     afterwards.
#
#   * Write `(base / user_input).resolve().is_relative_to(base)` and then
#     try user_input = '../../etc/passwd'.
