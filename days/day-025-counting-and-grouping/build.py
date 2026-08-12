"""Day 025 build — a word frequency analyser.

    python3 build.py                              # sample.txt, top 20
    python3 build.py sample.txt 30
    python3 build.py sample.txt 20 --keep-stopwords

The counting is four lines. The other eighty are about DECIDING WHAT A WORD
IS, which is the actual work — and the program prints every decision it made
so the numbers can be argued with.
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

WIDTH = 74
BAR = 30

# The commonest words in English. Any frequency report that leaves these in
# says "the, of, and, to, a" and tells you nothing about the text.
STOP_WORDS = set("""
a about above after again against all am an and any are as at be because been
before being below between both but by cannot could did do does doing down
during each few for from further had has have having he her here hers herself
him himself his how i if in into is it its itself me more most my myself no
nor not of off on once only or other ought our ours ourselves out over own
same she should so some such than that the their theirs them themselves then
there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your yours
""".split())

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

args = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = [a for a in sys.argv[1:] if a.startswith("--")]

path = Path(args[0]) if args else Path(__file__).parent / "sample.txt"
top_n = int(args[1]) if len(args) > 1 and args[1].isdigit() else 20
drop_stopwords = "--keep-stopwords" not in flags

if not path.exists():
    sys.exit(f"No such file: {path}")

text = path.read_text(encoding="utf-8")

# ===========================================================================
# TOKENISING — every line here is a judgement call, and each one changes
# the answer. They are listed in the output for exactly that reason.
# ===========================================================================

# 1. Case: "The" and "the" are the same word.
lowered = text.lower()

# 2. Punctuation: "dog." is "dog". But an apostrophe inside a word is part
#    of it ("don't"), and so is an internal hyphen ("well-known"). So strip
#    from the EDGES rather than deleting everywhere.
EDGE = ".,!?;:\"'()[]{}<>*_=/\\|`~“”‘’—–"

raw_tokens = lowered.split()
tokens = []
for token in raw_tokens:
    token = token.strip(EDGE)
    if not token:
        continue
    # 3. Numbers and pure punctuation runs: dropped. "1970" is usually noise
    #    in a word-frequency report. Sometimes it is the point — state it.
    if not any(ch.isalpha() for ch in token):
        continue
    tokens.append(token)

words = [w for w in tokens if not (drop_stopwords and w in STOP_WORDS)]

# ===========================================================================
# COUNTING — this is the four lines the other eighty exist to serve
# ===========================================================================

counts = Counter(words)
all_counts = Counter(tokens)          # including stop words, for comparison
letters = Counter(ch for ch in lowered if ch.isalpha())
by_length = defaultdict(list)
for word in counts:
    by_length[len(word)].append(word)

# ===========================================================================
# REPORT
# ===========================================================================

print("=" * WIDTH)
print(f"{'WORD FREQUENCY':^{WIDTH}}")
print("=" * WIDTH)
print(f"{'file':<28}{str(path.name):>{WIDTH - 28}}")
print(f"{'characters':<28}{len(text):>{WIDTH - 28},}")
print(f"{'lines':<28}{len(text.splitlines()):>{WIDTH - 28},}")
print(f"{'tokens after cleaning':<28}{len(tokens):>{WIDTH - 28},}")
print(f"{'words counted':<28}{len(words):>{WIDTH - 28},}")
print(f"{'distinct words':<28}{len(counts):>{WIDTH - 28},}")
print(f"{'stop words removed':<28}{len(tokens) - len(words):>{WIDTH - 28},}")

# Lexical density: distinct words over total. Higher means less repetition.
density = len(counts) / len(words) if words else 0
print(f"{'distinct / total':<28}{density:>{WIDTH - 28}.1%}")

print()
print("-" * WIDTH)
print("TOKENISING RULES APPLIED  (change these and the numbers change)")
print("-" * WIDTH)
print("  lowercased                                     yes")
print(f"  stripped from word edges                       {EDGE[:14]}...")
print("  apostrophes and hyphens INSIDE words kept      yes (don't, well-known)")
print("  tokens with no letters dropped                 yes (1970, ---)")
print(f"  stop words removed                             "
      f"{'yes' if drop_stopwords else 'NO (--keep-stopwords)'}")

# ---------------------------------------------------------------------------
# The top N
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{f'TOP {top_n} WORDS':^{WIDTH}}")
print("=" * WIDTH)

if not counts:
    print("  nothing to count.")
    sys.exit(0)

peak = counts.most_common(1)[0][1]
print(f"{'#':>4}  {'WORD':<20}{'COUNT':>7}{'SHARE':>8}  {'':<{BAR}}")
print("-" * WIDTH)
for rank, (word, n) in enumerate(counts.most_common(top_n), start=1):
    bar = "#" * int(n / peak * BAR)
    print(f"{rank:>4}. {word:<20}{n:>7}{n / len(words):>8.2%}  {bar:<{BAR}}")

# ---------------------------------------------------------------------------
# What the stop words were hiding
# ---------------------------------------------------------------------------

if drop_stopwords:
    print()
    print("-" * WIDTH)
    print("WITHOUT STOP-WORD REMOVAL, the top 8 would have been:")
    print("-" * WIDTH)
    line = "  " + "   ".join(
        f"{w}({n})" for w, n in all_counts.most_common(8)
    )
    print(line)
    print("  ...which is a fact about English, not about this document.")

# ---------------------------------------------------------------------------
# Words that appear exactly once
# ---------------------------------------------------------------------------

singletons = [w for w, n in counts.items() if n == 1]
print()
print("-" * WIDTH)
print(f"{'words appearing exactly once':<40}"
      f"{f'{len(singletons)}  ({len(singletons) / len(counts):.0%} of vocabulary)':>{WIDTH - 40}}")
print("-" * WIDTH)
print("  " + ", ".join(sorted(singletons)[:14]) + " ...")
print()
print("  A large fraction of any text appears exactly once. That is Zipf's")
print("  law showing up: rank 2 appears about half as often as rank 1,")
print("  rank 3 about a third, and the tail is enormous.")

# Check Zipf: count of rank N times N should be roughly constant.
print()
print(f"  {'RANK':>5}{'WORD':>16}{'COUNT':>8}{'COUNT x RANK':>16}")
for rank, (word, n) in enumerate(counts.most_common(6), start=1):
    print(f"  {rank:>5}{word:>16}{n:>8}{n * rank:>16}")

# ---------------------------------------------------------------------------
# Grouping by length — the defaultdict pattern
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'VOCABULARY BY WORD LENGTH':^{WIDTH}}")
print("=" * WIDTH)
longest_group = max(len(v) for v in by_length.values())
for length in sorted(by_length):
    group = by_length[length]
    bar = "#" * int(len(group) / longest_group * BAR)
    sample = ", ".join(sorted(group)[:3])
    print(f"{length:>3} chars {len(group):>5}  {bar:<{BAR}} {sample[:22]}")

# ---------------------------------------------------------------------------
# Letters
# ---------------------------------------------------------------------------

print()
print("=" * WIDTH)
print(f"{'LETTER FREQUENCY':^{WIDTH}}")
print("=" * WIDTH)
letter_peak = letters.most_common(1)[0][1]
for letter, n in letters.most_common(12):
    bar = "#" * int(n / letter_peak * BAR)
    print(f"  {letter}  {n:>6}  {n / letters.total():>7.2%}  {bar}")
print()
print("  English letter order is normally ETAOIN SHRDLU. If this text")
print("  disagrees near the top, it is short enough for that to be noise.")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Run with --keep-stopwords and compare. The report becomes useless, and
#     that is the most convincing possible argument for the STOP_WORDS set.
#
#   * The Counter work is four lines. Rewrite it with a plain dict and
#     .get(w, 0) + 1, then with defaultdict(int). All three agree; keep the
#     one you would rather read.
#
#   * Count BIGRAMS: Counter(zip(words, words[1:])). Do it before removing
#     stop words, or "of the" — the commonest bigram in English — vanishes.
#
#   * Compare two files: which words are common in one and rare in the other?
#     That ratio is the beginning of TF-IDF, which is how search engines
#     decided what a document was about for about thirty years.
#
#   * `singletons` scans counts.items() — fine here. On a 500 MB file you
#     cannot hold the text at all. Day 38's generators handle that, and the
#     Counter part does not change at all.
