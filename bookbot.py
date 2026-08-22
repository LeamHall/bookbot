#!/usr/bin/env python

# name    :  bookbot.py
# version :  0.1.0
# date    :  20260525
# author  :  Leam Hall
# desc    :  Assembles and reports on text file based documents.
#            Supports novels, reports, SOPs, and other plain-text document types.
# license :  MIT
# copyright: Copyright (c) 2020-2026 Leam Hall
#
# This file is distributed as a single self-contained script and may be copied
# on its own, apart from the repository that holds the full LICENSE text.

import argparse
import errno
import os
from pathlib import Path
import re
import sys
import tomllib


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "author": "",
    "book_dir": "book",
    "chapter_dir": "chapters",
    "has_header": False,
    "section_break": "\n__section_break__\n",
    "scene_break_pattern": r"^[-*~\s]{3,}$",
    "reports_dir": "reports",
    "title": "",
    "report": False,
    "doc_type": "novel",
}

SPECIAL_SECTION_NAMES = frozenset(
    [
        "title",
        "isbn",
        "prologue",
        "epilogue",
        "afterward",
        "author_bio",
        "more",
    ]
)

SCENE_BREAK = "__scene_break__"

DOC_TYPE_SECTION_LABEL = {
    "novel": "Chapter",
    "report": "Section",
    "sop": "Step",
    "generic": "",
}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def parse_args(args=None):
    """Returns parsed CLI arguments as a dict. Pass args=[] for defaults."""
    parser = argparse.ArgumentParser(
        description="Assemble text files into a formatted document."
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Config file in TOML format.",
        default="book_config.toml",
    )
    parser.add_argument("-a", "--author", help="Author name", default=None)
    parser.add_argument(
        "-b",
        "--book_dir",
        help="Directory for assembled output.",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--chapter_dir",
        help="Directory containing section files.",
        default=None,
    )
    parser.add_argument(
        "--has_header",
        help="Section files begin with a title line.",
        action="store_true",
        default=None,
    )
    parser.add_argument(
        "-p",
        "--section_break",
        help="String inserted between sections in output.",
        default=None,
    )
    parser.add_argument(
        "-r",
        "--reports_dir",
        help="Directory for report output.",
        default=None,
    )
    parser.add_argument("-t", "--title", help="Document title", default=None)
    parser.add_argument(
        "--doc_type",
        help="Document type: novel, report, sop, generic.",
        default=None,
    )
    return vars(parser.parse_args(args if args is not None else []))


def read_config(_args=None, base_config=None):
    """
    Returns a config dict by layering: defaults, then TOML file, then CLI args.
    Never mutates DEFAULT_CONFIG.
    """
    config = dict(DEFAULT_CONFIG if base_config is None else base_config)

    if _args is None:
        return config

    toml_path = _args.get("file", "book_config.toml")
    try:
        with open(toml_path, "rb") as f:
            config.update(tomllib.load(f))
    except (KeyError, FileNotFoundError):
        pass

    for key in (
        "author",
        "book_dir",
        "chapter_dir",
        "section_break",
        "reports_dir",
        "title",
        "doc_type",
    ):
        if _args.get(key) is not None:
            config[key] = _args[key]

    if _args.get("has_header") is not None:
        config["has_header"] = _args["has_header"]

    return config


def setup_dirs(conf=None, root_dir=None):
    """Creates output directories if they do not exist."""
    if not conf:
        raise TypeError("program config required")
    root = root_dir or os.getcwd()
    for key in ("book_dir", "reports_dir", "chapter_dir"):
        new_dir = os.path.join(root, conf[key])
        if not os.path.exists(new_dir):
            os.mkdir(new_dir, mode=0o0750)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def load_lines(filename):
    """
    Returns all lines from a file with trailing whitespace stripped.
    Blank lines are preserved — they carry paragraph structure.
    """
    with open(filename, "r", encoding="utf-8-sig") as f:
        return [line.rstrip() for line in f]


def list_of_files(target_dir):
    """
    Returns a sorted list of .txt file paths in target_dir.
    Non-recursive: subdirectories (e.g. archive/) are ignored.
    """
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), target_dir
        )
    filenames = sorted(
        os.path.join(target_dir, f)
        for f in os.listdir(target_dir)
        if f.endswith(".txt") and os.path.isfile(os.path.join(target_dir, f))
    )
    if not filenames:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), target_dir
        )
    return filenames


# ---------------------------------------------------------------------------
# Text parsing
# ---------------------------------------------------------------------------


def parse_paragraphs(lines, scene_break_pattern=None):
    """
    Converts raw lines into a flat list of paragraphs and scene break markers.

    Rules:
      - Blank lines are paragraph separators.
      - Lines matching scene_break_pattern become SCENE_BREAK sentinels.
      - Consecutive non-blank, non-break lines are joined into one paragraph.

    Inline italic markup (_text_) passes through unchanged for downstream
    processing by the user's word processor.
    """
    pattern = re.compile(
        scene_break_pattern or DEFAULT_CONFIG["scene_break_pattern"]
    )
    result = []
    current = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                result.append(" ".join(current))
                current = []
        elif pattern.match(stripped):
            if current:
                result.append(" ".join(current))
                current = []
            result.append(SCENE_BREAK)
        else:
            current.append(" ".join(stripped.split()))

    if current:
        result.append(" ".join(current))

    return result


def section_type(filename):
    """Returns the section type: a special name if the stem is recognized, else 'chapter'."""
    stem = Path(filename).stem
    return stem if stem in SPECIAL_SECTION_NAMES else "chapter"


# ---------------------------------------------------------------------------
# Readability analysis  (pure functions — no side effects, no state)
# ---------------------------------------------------------------------------


def count_sentences(text):
    """Counts sentence-ending punctuation (. ? !) in text."""
    return sum(text.count(p) for p in ".?!")


def count_words(text):
    """Counts whitespace-delimited tokens in text."""
    return len(text.split())


def count_syllables(text):
    """
    Simple English syllable estimator.
    Counts vowels, subtracts common double-vowel sequences, and adjusts
    for silent-e and consonantal-y word endings.
    Returns at least 1 to avoid division-by-zero in grade computation.
    """
    VOWELS = "aeiou"
    DOUBLES = ("ee", "oi", "oo", "ou")

    lowered = text.lower()
    total = sum(lowered.count(v) for v in VOWELS)
    total -= sum(lowered.count(d) for d in DOUBLES)

    scrubbed = re.sub(r'[.?!"\']', " ", lowered)
    for word in scrubbed.split():
        if word.endswith("ey") or word.endswith("e"):
            total -= 1
        if word.endswith("y"):
            total += 1

    return max(total, 1)


def readability_stats(paragraphs, filename=""):
    """
    Computes Flesch-Kincaid grade level for a list of paragraphs.
    SCENE_BREAK sentinels are excluded from analysis.
    Raises ValueError if there is insufficient text.
    Returns a dict with sentence_count, word_count, syllable_count,
    sentence_average, syllables_per_word_average, grade_level, filename.
    """
    prose = " ".join(p for p in paragraphs if p != SCENE_BREAK)

    sentences = count_sentences(prose)
    words = count_words(prose)
    syllables = count_syllables(prose)

    if not words or not sentences:
        raise ValueError(
            "Insufficient text to compute readability in {!r}.".format(
                filename
            )
        )

    sentence_avg = words / sentences
    syllables_per_word = syllables / words
    grade = round(
        (0.39 * sentence_avg) + (11.8 * syllables_per_word) - 15.59, 2
    )

    return {
        "filename": filename,
        "sentence_count": sentences,
        "word_count": words,
        "syllable_count": syllables,
        "sentence_average": sentence_avg,
        "syllables_per_word_average": syllables_per_word,
        "grade_level": grade,
    }


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------


class Section:
    """
    A single section of a document: a chapter, a report section, a SOP step,
    or a special page (prologue, epilogue, etc.).

    Accepts a data dict with these keys:
      lines       - raw file lines (blank lines preserved); parsed internally
      paragraphs  - pre-parsed paragraph list (takes precedence over lines)
      has_header  - bool; if True, first paragraph becomes the section title
      filename    - source filename (used in readability reports)
      type        - "chapter" or a special section name
      number      - int; set externally by DocumentBuilder
      scene_break_pattern - optional regex override for scene break detection
    """

    def __init__(self, data=None):
        if data is None:
            data = {}
        self._has_header = data.get("has_header", False)
        self.filename = data.get("filename", "")
        self.type = data.get("type", "chapter")
        self.number = data.get("number", 0)
        self.title = None

        if "paragraphs" in data:
            self.paragraphs = list(data["paragraphs"])
        else:
            self.paragraphs = parse_paragraphs(
                data.get("lines", []),
                data.get("scene_break_pattern"),
            )

        self._extract_title()
        self.stats = None
        self._compute_stats()

    def _extract_title(self):
        """Pops the first non-break paragraph as the section title when has_header is set."""
        if self._has_header and self.paragraphs:
            candidate = self.paragraphs[0]
            if candidate != SCENE_BREAK:
                self.title = candidate
                self.paragraphs = self.paragraphs[1:]

    def _compute_stats(self):
        try:
            self.stats = readability_stats(self.paragraphs, self.filename)
        except ValueError:
            self.stats = None

    def __str__(self):
        parts = []
        for p in self.paragraphs:
            parts.append("- - -" if p == SCENE_BREAK else p)
        return "\n\n".join(parts)

    # --- Backwards-compatibility properties ---

    @property
    def header(self):
        return self.title

    @property
    def lines(self):
        return [p for p in self.paragraphs if p != SCENE_BREAK]

    @property
    def report(self):
        return self.stats

    @property
    def report_data(self):
        return self.stats


# ---------------------------------------------------------------------------
# Document building
# ---------------------------------------------------------------------------


class DocumentBuilder:
    """
    Assembles a list of Section objects into a Document.
    doc_type controls how sections are labeled in the output:
      "novel"   -> Chapter N
      "report"  -> Section N
      "sop"     -> Step N
      "generic" -> (no label)
    """

    def __init__(
        self, config=None, sections=None, special_sections=None, chapters=None
    ):
        self.config = dict(DEFAULT_CONFIG)
        if config:
            self.config.update(config)
        self.sections = list(sections or chapters or [])
        self.special_sections = dict(special_sections or {})

    @property
    def chapters(self):
        return self.sections

    def _section_label(self, section):
        doc_type = self.config.get("doc_type", "novel")
        label = DOC_TYPE_SECTION_LABEL.get(doc_type, "")
        if label and section.number:
            return "{} {}".format(label, section.number)
        return ""

    def _render_section(self, section):
        """Returns the formatted text for one section."""
        section_break = self.config["section_break"]
        parts = [section_break.rstrip("\n")]

        label = self._section_label(section)
        if label:
            parts.append(label)
        if section.title:
            parts.append(section.title)

        for p in section.paragraphs:
            parts.append("- - -" if p == SCENE_BREAK else p)

        return "\n\n".join(parts)

    def write_chapter(self, section):
        """Backwards-compatible alias for _render_section."""
        return self._render_section(section)

    def build(self):
        """Assembles and returns a Document."""
        doc = Document()
        doc.author = self.config.get("author", "")
        doc.title = self.config.get("title", "")

        section_number = 0
        for section in self.sections:
            if section.type == "chapter":
                section_number += 1
                section.number = section_number
            doc.text += self._render_section(section)
            doc.sections.append(section)

        doc.text += "\n\n"
        return doc


class Document:
    """The assembled document."""

    def __init__(self, text=""):
        self.text = text
        self.sections = []
        self.author = ""
        self.title = ""

    # Backwards compat: old Book stored chapters, not sections
    @property
    def chapters(self):
        return self.sections


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def document_filename(config, file_type="txt"):
    """Converts the document title into a safe filename."""
    title = config.get("title", "") or "untitled"
    title = title.lower()
    title = re.sub(r"[^\w\s]", " ", title)
    title = "_".join(title.split())
    return title + "." + file_type


def write_document(doc, config):
    """Writes the assembled document text to the book directory."""
    book_dir = config["book_dir"]
    filename = document_filename(config, "txt")
    path = os.path.join(book_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc.text)


def collate_reports(doc):
    """Returns a list of readability stat dicts for sections that have stats."""
    return [s.stats for s in doc.sections if s.stats is not None]


def write_report_string(reports):
    """Formats readability report dicts into a human-readable string."""
    if not reports:
        return "No report data available."
    grade_levels = []
    lines = []
    for r in reports:
        lines.append("Filename: {}".format(r["filename"]))
        lines.append("Grade Level: {:.1f}".format(r["grade_level"]))
        lines.append("")
        grade_levels.append(r["grade_level"])
    avg = sum(grade_levels) / len(grade_levels)
    lines.append("Average Grade Level: {:.1f}".format(avg))
    return "\n".join(lines)


def write_reports(reports_dir, report_string):
    """Writes the report string to reports_dir/report.txt."""
    path = os.path.join(reports_dir, "report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_string)


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------


def parse_sections(
    files, specials=None, has_header=False, scene_break_pattern=None
):
    """
    Reads a list of file paths and returns (sections, special_sections).

    sections        - list of Section objects for regular chapters
    special_sections - dict mapping name to Section for special pages
                       Keys for unfound specials are set to None.

    Does not mutate the passed specials dict.
    """
    base_specials = (
        dict(specials)
        if specials is not None
        else {name: None for name in SPECIAL_SECTION_NAMES}
    )

    sections = []
    found_specials = {}

    for filepath in files:
        lines = load_lines(filepath)
        stype = section_type(filepath)
        data = {
            "lines": lines,
            "has_header": has_header,
            "filename": os.path.basename(filepath),
            "type": stype,
            "scene_break_pattern": scene_break_pattern,
        }
        sec = Section(data)
        if stype in base_specials:
            found_specials[stype] = sec
        else:
            sections.append(sec)

    result_specials = dict(base_specials)
    result_specials.update(found_specials)
    return sections, result_specials


# ---------------------------------------------------------------------------
# Backwards-compatibility aliases
# Existing user scripts and tests that import these names continue to work.
# ---------------------------------------------------------------------------


def lines_from_file(filename):
    """Returns non-blank lines from a file. Use load_lines() for raw access."""
    return [l.strip() for l in load_lines(filename) if l.strip()]


chapter_type = section_type
Chapter = Section
BookBuilder = DocumentBuilder
Book = Document
book_filename = document_filename
write_book = write_document
parse_chapters = parse_sections


class Report:
    """
    Backwards-compatible wrapper around the pure readability functions.
    New code should call readability_stats() directly.
    """

    def __init__(self, data, filename):
        paragraphs = [line.lower() for line in data if line.strip()]
        self.lines = paragraphs
        self.filename = filename
        stats = readability_stats(paragraphs, filename)
        self.sentence_count = stats["sentence_count"]
        self.word_count = stats["word_count"]
        self.syllable_count = stats["syllable_count"]
        self.sentence_average = stats["sentence_average"]
        self.syllables_per_word_average = stats["syllables_per_word_average"]
        self.grade_level = stats["grade_level"]

    def report_data(self):
        return {
            "filename": self.filename,
            "sentence_average": self.sentence_average,
            "grade_level": self.grade_level,
            "syllables_per_word_average": self.syllables_per_word_average,
        }


# Module-level dict kept for scripts that access bb.special_chapters directly
special_chapters = {name: "" for name in SPECIAL_SECTION_NAMES}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _args = parse_args(sys.argv[1:])
    config = read_config(_args)
    setup_dirs(config)

    scene_pat = config.get("scene_break_pattern")
    sections, specials = parse_sections(
        list_of_files(config["chapter_dir"]),
        has_header=config["has_header"],
        scene_break_pattern=scene_pat,
    )

    doc = DocumentBuilder(config=config, sections=sections).build()
    write_document(doc, config)

    if config.get("report"):
        reports = collate_reports(doc)
        if reports:
            report_str = write_report_string(reports)
            write_reports(config["reports_dir"], report_str)
