# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

    make test        # python -m unittest  (from the repo root)
    make coverage    # coverage run -m unittest, then coverage report -m
    make all         # clean, coverage, black -l 79, flake8, semgrep
    make clean       # remove .pyc and .swp files

Single test module or case:

    python -m unittest test.test_document
    python -m unittest test.test_document.TestDocumentBuilder
    python -m unittest test.test_document.TestDocumentBuilder.test_empty_build_returns_document

Developer tools (black, flake8, coverage, semgrep) are listed in `requirements_dev.txt` at the repository root and are expected to run inside a venv. They are never runtime dependencies.

All tests live in `test/` and all of them run under a plain `python -m unittest` from the repo root. `bin/` carries an empty `__init__.py` so that its scripts can be imported as `from bin import cefr_bands`; they are still runnable directly as `python bin/cefr_bands.py`.

## Hard constraints

These are not negotiable without asking:

1. `bookbot.py` is a single file. The tool is handed to non-technical writers who do not do Python packaging. Do not split it into a package or add modules it imports.
2. Runtime code uses only the Python standard library.
3. Tests use `unittest`, never pytest.
4. `tomllib` sets the real floor at Python 3.11, even though the Contributing section of README.md still says 3.6. Trust 3.11.
5. Output is plain text destined for LibreOffice. `docs/HOWTO` documents the manual formatting steps a writer performs after bookbot runs, which is why markers like `__section_break__` and `- - -` survive into the output rather than being resolved by the program.
6. One run produces one output document. The program collates a directory into a single text file; it does not emit several manuscripts from one invocation.
7. The program runs from inside the book's directory, and must stay runnable from a shared location such as `/usr/local/bin`. Nothing may depend on `bookbot.py` sitting next to the book.

## Scope boundaries

Deliberately outside the program's job. These are decided, not open questions:

- No spell checking and no grammar checking. Those belong to the writer's word processor.
- Sentence detection assumes standard English punctuation. The readability code splits on ordinary sentence-ending marks and has no model of any other writing system. This is a stated limit, not a defect, though `count_sentences` counting punctuation characters rather than sentences is a defect and is tracked separately.
- The program does not render italics, page breaks or any other formatting. It emits markers that a person resolves in LibreOffice.

## Architecture of bookbot.py

The program is run from inside a book's own directory, not from this repo. It reads a `book_config.toml` there, collates `chapters/*.txt` into one manuscript in `book/`, and optionally writes a readability report to `reports/`.

The `__main__` block at the bottom is the whole pipeline and is the fastest way to see how the pieces connect:

    parse_args -> read_config -> setup_dirs
      -> list_of_files -> parse_sections -> [Section, ...]
      -> DocumentBuilder(config, sections).build() -> Document
      -> write_document
      -> collate_reports -> write_report_string -> write_reports

Config layers in a fixed order: `DEFAULT_CONFIG`, then the TOML file, then CLI arguments. `read_config` copies rather than mutating `DEFAULT_CONFIG`, and `parse_sections` returns a new specials dict rather than mutating the one passed in. Both were past bugs; keep them that way.

The file is organized as pure functions first, state-holding classes after. Readability (`count_sentences`, `count_words`, `count_syllables`, `readability_stats`) is deliberately pure: data in, dict out, no side effects. Prefer adding analysis as another pure function over adding a method to a class.

Two sentinels drive the text model. `parse_paragraphs` turns raw lines into a flat list where each element is either a paragraph string or the `SCENE_BREAK` constant; blank lines separate paragraphs and lines matching `scene_break_pattern` (`- - -`, `***`, `---`) become `SCENE_BREAK`. Scene breaks are excluded from readability counts and rendered as `- - -` on output. Separately, `section_break` from config is inserted between sections and is what the writer converts to page breaks in LibreOffice.

A file's *stem* decides its role. Stems in `SPECIAL_SECTION_NAMES` (title, isbn, prologue, epilogue, afterward, author_bio, more) become special sections; everything else is a numbered chapter. `doc_type` then controls the label: novel gives "Chapter N", report gives "Section N", sop gives "Step N", generic gives none. This is the hook for using bookbot on non-novel documents.

`load_lines` preserves blank lines because paragraph structure depends on them. `lines_from_file` strips them and exists only for backwards compatibility.

## The backwards-compatibility block

Near the bottom of `bookbot.py` is a deliberate alias section: `Chapter = Section`, `Book = Document`, `BookBuilder = DocumentBuilder`, `chapter_type`, `book_filename`, `write_book`, `parse_chapters`, `lines_from_file`, the `Report` class, and the `special_chapters` dict. Some classes also carry compatibility properties (`Section.header`, `Section.lines`, `Section.report`, `Document.chapters`).

These exist because writers have their own scripts against the old names. Write new code against the new names; do not remove the old ones without being asked.

## bin/ is not part of bookbot

`bin/` holds standalone analysis scripts. They are separate programs, and `bookbot.py` does not import them. The single-file rule applies to `bookbot.py`, not to these.

`bin/` is a Python package, but only so the test suite can import it. That does not make it part of bookbot.

- `cefr_bands.py` — vocabulary-band coverage analysis. Takes a "word count" file plus a frequency-ranked list (`data/en_50k.txt`) and an optional exclusions file (`data/exclude_proper_nouns.txt`), and reports what percentage of running text falls in each frequency band. Its docstrings explain the reasoning; `docs/cefr_analysis_notes.txt` records what the numbers meant for an actual book.
- `vortolisto.py` — word-frequency extraction, produces the "word count" input `cefr_bands.py` consumes. Still rough: it has an unimplemented `get_phrases`.
- `pov_copy.py` — copies chapters matching a point-of-view character. Its tests are in `test/test_pov_copy.py`.
- `make_thumbnail.pl` — a leftover Perl script that makes thumbnail images. Not part of bookbot and scheduled for conversion or removal.
- `analysis_commands.txt` — the shell commands used in an actual read-through pass over a book, kept so the same analysis can be repeated.

## Working notes

`docs/` holds everything a reader may need:

- `HOWTO` — the LibreOffice formatting steps a writer performs after bookbot runs.
- `cefr_analysis_notes.txt` — what the band numbers meant for an actual book.
- `session_1_summary.txt` — why the current structure looks the way it does.
- `code_review_20260525.txt` — an earlier review; several open items still cite it.

`research/` holds working notes and is git-ignored, so nothing there can be relied on. Anything a reader needs is moved to `docs/` instead.

`data/` holds the frequency and exclusion word lists. `data/README` records where each came from and what may be published from it.
