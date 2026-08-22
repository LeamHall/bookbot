"""Vocabulary-band analysis for estimating the reading demand of a text.

The input is a simple "word<whitespace>count" file, one unique word per line,
such as the output of a word-frequency pass over a manuscript.  Each word is
looked up in an external frequency-ranked word list, sorted into rank bands,
and the running-text coverage of each band is reported.

The number that matters for reading difficulty is coverage: what percentage of
the running words in the text a reader already knows.  Reading research puts
the threshold for comprehension-with-effort at about 95 percent and the
threshold for comfortable independent reading at about 98 percent.  So the
question "how big a vocabulary does this text demand" becomes "how far down the
frequency list do you have to go before cumulative coverage crosses 95 or 98
percent", which is what vocabulary_demand() answers.

Frequency list: this module expects a plain list, most frequent word first, one
word per line, optionally followed by a count.  The list used for the original
analysis was the OpenSubtitles-derived English 50k list from
https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt
which suits narrative fiction far better than a web-crawl list does.  See the
notes file for why that choice mattered.

No third-party packages are required.
"""

import argparse
import re
import sys


DEFAULT_BANDS = [
    (1, 1000),
    (1001, 2000),
    (2001, 3000),
    (3001, 5000),
    (5001, 10000),
    (10001, 50000),
]

# Suffix rules used to fold an inflected form back onto its dictionary form.
# Each pair is (suffix to strip, string to append).  Order does not matter
# because every candidate is tried against the frequency list.
_SUFFIX_RULES = [
    ("s", ""),
    ("es", ""),
    ("ed", ""),
    ("ed", "e"),
    ("ing", ""),
    ("ing", "e"),
    ("ies", "y"),
    ("ied", "y"),
    ("er", ""),
    ("er", "e"),
    ("est", ""),
    ("est", "e"),
    ("ly", ""),
    ("n", ""),
    ("d", ""),
]

# A stem shorter than this is almost certainly a mangling, not a real word.
_MIN_STEM_LENGTH = 3


def load_word_counts(source):
    """Read a 'word<whitespace>count' file into a dict of word -> total count.

    'source' is any iterable of lines, so a file object or a list of strings
    both work.  Words are lowercased and duplicate entries are summed.
    """
    counts = {}
    for line in source:
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit(None, 1)
        if len(parts) != 2:
            raise ValueError("expected 'word count', got: %r" % line)
        word, raw_count = parts
        word = word.strip().lower()
        counts[word] = counts.get(word, 0) + int(raw_count)
    return counts


def load_frequency_ranks(source):
    """Read a frequency-ordered word list into a dict of word -> rank.

    Rank is 1-based line order.  Lines may be a bare word or 'word count';
    anything after the first whitespace is ignored.  If a word appears more
    than once, the first (most frequent) position wins.
    """
    ranks = {}
    position = 0
    for line in source:
        line = line.strip()
        if not line:
            continue
        position += 1
        word = line.split()[0].lower()
        if word not in ranks:
            ranks[word] = position
    return ranks


def load_exclusions(source):
    """Read a list of words to drop before banding, one per line.

    Blank lines are ignored.  Everything from a '#' onwards is a comment,
    whether it starts the line or trails a word, so a list can be annotated
    with what each entry is and why it was excluded.
    """
    words = set()
    for line in source:
        word = line.split("#", 1)[0].strip().lower()
        if word:
            words.add(word)
    return words


def candidate_stems(word):
    """Yield the word itself followed by plausible dictionary forms of it.

    This is deliberately a crude stemmer rather than a real lemmatiser.  It
    over-generates on purpose: every candidate is checked against the frequency
    list, and a candidate that is not a real word simply never matches.  The
    word itself is always yielded first so a direct hit wins over a stem hit.
    """
    yield word
    for suffix, replacement in _SUFFIX_RULES:
        if word.endswith(suffix) and len(word) - len(suffix) >= _MIN_STEM_LENGTH:
            stem = word[: len(word) - len(suffix)] + replacement
            yield stem
            # A doubled consonant left behind by stripping, e.g.
            # stopped -> stopp -> stop, grinned -> grinn -> grin.
            if _has_doubled_final_consonant(stem):
                yield stem[:-1]
    if _has_doubled_final_consonant(word):
        yield word[:-1]


def _has_doubled_final_consonant(word):
    return (
        len(word) > _MIN_STEM_LENGTH
        and word[-1] == word[-2]
        and word[-1] not in "aeiou"
    )


def rank_of(word, ranks):
    """Return the lowest frequency rank among the word and its candidate stems.

    Lowest, not first.  The question this answers is how much of a burden the
    word places on a reader, and an inflected form is no harder than the
    commonest member of its family: someone who knows 'step' and '-ed' can read
    'stepped'.  Taking the form's own rank instead penalises every regular
    inflection in the text, which in practice is most of the verbs.

    Returns None if neither the word nor any stem appears in the list.
    """
    found = [ranks[candidate] for candidate in candidate_stems(word) if candidate in ranks]
    return min(found) if found else None


def band_of(rank, bands):
    """Return the (low, high) band containing rank, or None."""
    if rank is None:
        return None
    for low, high in bands:
        if low <= rank <= high:
            return (low, high)
    return None


def count_syllables(word):
    """Approximate syllable count by counting vowel groups.

    Good enough for a polysyllabic-word ratio, which is what the classic
    readability formulas lean on.  Not good enough for anything else.
    """
    groups = re.findall(r"[aeiouy]+", word)
    total = len(groups)
    if word.endswith("e") and total > 1:
        total -= 1
    return max(total, 1)


def basic_stats(counts):
    """Return size, variety and word-shape statistics for a word-count dict."""
    tokens = sum(counts.values())
    types = len(counts)
    if tokens == 0:
        return {
            "tokens": 0,
            "types": types,
            "type_token_ratio": 0.0,
            "hapax_types": 0,
            "hapax_percent": 0.0,
            "avg_word_length": 0.0,
            "polysyllabic_percent": 0.0,
        }
    hapax = sum(1 for count in counts.values() if count == 1)
    length_sum = sum(len(word) * count for word, count in counts.items())
    polysyllabic = sum(
        count for word, count in counts.items() if count_syllables(word) >= 3
    )
    return {
        "tokens": tokens,
        "types": types,
        "type_token_ratio": types / tokens,
        "hapax_types": hapax,
        "hapax_percent": hapax / types * 100 if types else 0.0,
        "avg_word_length": length_sum / tokens,
        "polysyllabic_percent": polysyllabic / tokens * 100,
    }


def coverage_report(counts, ranks, bands=None, exclude=None):
    """Sort every word into a frequency band and report running-text coverage.

    'exclude' is a set of words to drop before any percentage is computed.
    Use it for proper nouns and invented vocabulary, which distort coverage
    badly: a reader does not need to "know" a character's name to read past it,
    but an unfiltered run counts every occurrence as an unknown word.

    Returns a dict with per-band token counts, type counts, percentage of core
    running text, and running cumulative percentage.
    """
    if bands is None:
        bands = DEFAULT_BANDS
    exclude = exclude or set()

    excluded_tokens = sum(count for word, count in counts.items() if word in exclude)
    core = {word: count for word, count in counts.items() if word not in exclude}
    core_tokens = sum(core.values())

    tally = {band: {"tokens": 0, "types": 0} for band in bands}
    off_tokens = 0
    off_words = []

    for word, count in core.items():
        band = band_of(rank_of(word, ranks), bands)
        if band is None:
            off_tokens += count
            off_words.append((word, count))
            continue
        tally[band]["tokens"] += count
        tally[band]["types"] += 1

    cumulative = 0.0
    for band in bands:
        entry = tally[band]
        entry["percent"] = entry["tokens"] / core_tokens * 100 if core_tokens else 0.0
        cumulative += entry["percent"]
        entry["cum_percent"] = cumulative

    off_words.sort(key=lambda pair: -pair[1])
    return {
        "bands": tally,
        "band_order": list(bands),
        "core_tokens": core_tokens,
        "core_types": len(core),
        "excluded_tokens": excluded_tokens,
        "excluded_types": sum(1 for word in counts if word in exclude),
        "off_list": {
            "tokens": off_tokens,
            "types": len(off_words),
            "percent": off_tokens / core_tokens * 100 if core_tokens else 0.0,
            "words": off_words,
        },
    }


def decision_list(counts, ranks, min_rank=3001, min_count=5, exclude=None):
    """List the words that actually drive the difficulty, worth deciding one by one.

    Returns rows of (word, count, rank) for every word ranked at or beyond
    min_rank and occurring at least min_count times, sorted by count descending
    then alphabetically.  Words absent from the frequency list are included with
    a rank of None, since being off a 50000-word list means rarer, not easier.

    The count floor is what makes the output usable.  A book of this size has a
    long tail of words that appear once and can simply be skipped by a reader,
    so listing every rare word buries the few hundred that matter.
    """
    exclude = exclude or set()
    rows = []
    for word, count in counts.items():
        if word in exclude or count < min_count:
            continue
        rank = rank_of(word, ranks)
        if rank is None or rank >= min_rank:
            rows.append((word, count, rank))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return rows


def format_decision_list(rows, title):
    """Render a decision list as a plain-text worksheet with a column to fill in."""
    lines = [title, "", "%-6s %-18s %-8s %s" % ("count", "word", "rank", "decision")]
    lines.append("%-6s %-18s %-8s %s" % ("-" * 5, "-" * 18, "-" * 8, "-" * 24))
    for word, count, rank in rows:
        lines.append(
            "%-6d %-18s %-8s" % (count, word, "off-list" if rank is None else rank)
        )
    lines.append("")
    lines.append("%d words, %d running occurrences." % (rows and len(rows) or 0,
                                                        sum(r[1] for r in rows)))
    return "\n".join(lines)


def vocabulary_demand(report, threshold):
    """Return the band ceiling at which cumulative coverage first reaches threshold.

    'threshold' is a fraction, e.g. 0.95.  Returns the upper rank of that band,
    e.g. 5000, meaning "a reader needs roughly the 5000 most frequent words to
    reach this coverage".  Returns None if the text never reaches the threshold
    within the supplied bands.
    """
    target = threshold * 100
    for band in report["band_order"]:
        if report["bands"][band]["cum_percent"] >= target:
            return band[1]
    return None


def format_report(stats, report):
    """Render the analysis as plain text suitable for pasting into notes."""
    lines = []
    lines.append("SIZE AND VARIETY")
    lines.append("")
    lines.append("  running words (tokens)      %d" % stats["tokens"])
    lines.append("  unique words (types)        %d" % stats["types"])
    lines.append("  type/token ratio            %.4f" % stats["type_token_ratio"])
    lines.append(
        "  words used exactly once     %d  (%.1f%% of unique words)"
        % (stats["hapax_types"], stats["hapax_percent"])
    )
    lines.append("  average word length         %.2f characters" % stats["avg_word_length"])
    lines.append(
        "  three-or-more syllables     %.1f%% of running words"
        % stats["polysyllabic_percent"]
    )
    lines.append("")
    lines.append("EXCLUDED BEFORE BANDING")
    lines.append("")
    lines.append(
        "  proper nouns and invented words   %d running words (%d unique)"
        % (report["excluded_tokens"], report["excluded_types"])
    )
    lines.append("  core running words analysed      %d" % report["core_tokens"])
    lines.append("")
    lines.append("COVERAGE BY FREQUENCY BAND")
    lines.append("")
    lines.append("  %-14s %8s %8s %8s" % ("band", "% text", "cum %", "unique"))
    for band in report["band_order"]:
        entry = report["bands"][band]
        label = "%d-%d" % band
        lines.append(
            "  %-14s %7.2f%% %7.2f%% %8d"
            % (label, entry["percent"], entry["cum_percent"], entry["types"])
        )
    off = report["off_list"]
    lines.append(
        "  %-14s %7.2f%% %7.2f%% %8d" % ("off-list", off["percent"], 100.0, off["types"])
    )
    lines.append("")
    lines.append("VOCABULARY DEMAND")
    lines.append("")
    for threshold, meaning in ((0.95, "comprehension with effort"),
                               (0.98, "comfortable independent reading")):
        ceiling = vocabulary_demand(report, threshold)
        if ceiling is None:
            lines.append(
                "  %d%% coverage (%s): not reached within the bands supplied"
                % (threshold * 100, meaning)
            )
        else:
            lines.append(
                "  %d%% coverage (%s): about the %d most frequent words"
                % (threshold * 100, meaning, ceiling)
            )
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(
        description="Estimate the vocabulary demand of a text from a word-count list."
    )
    parser.add_argument("wordcounts", help="'word count' per line, the text being measured")
    parser.add_argument("frequencylist", help="frequency-ordered list, most frequent first")
    parser.add_argument("excludefile", nargs="?",
                        help="optional; one word per line, names and coinages to drop")
    parser.add_argument("--decisions", action="store_true",
                        help="print the decision list instead of the coverage report")
    parser.add_argument("--min-rank", type=int, default=3001,
                        help="decision list: lowest frequency rank to include (default 3001)")
    parser.add_argument("--min-count", type=int, default=5,
                        help="decision list: fewest occurrences to include (default 5)")
    args = parser.parse_args(argv[1:])

    with open(args.wordcounts) as handle:
        counts = load_word_counts(handle)
    with open(args.frequencylist) as handle:
        ranks = load_frequency_ranks(handle)

    exclude = set()
    if args.excludefile:
        with open(args.excludefile) as handle:
            exclude = load_exclusions(handle)

    if args.decisions:
        rows = decision_list(counts, ranks, args.min_rank, args.min_count, exclude)
        title = ("Words ranked %d or rarer, appearing %d or more times."
                 % (args.min_rank, args.min_count))
        print(format_decision_list(rows, title))
        return 0

    stats = basic_stats(counts)
    report = coverage_report(counts, ranks, DEFAULT_BANDS, exclude)
    print(format_report(stats, report))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        # Normal when the output is piped into head or less.
        sys.stderr.close()
        sys.exit(0)
