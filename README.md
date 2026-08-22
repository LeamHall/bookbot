# BookBot


A Python tool for assembling book manuscripts from multiple chapter files and generating readability reports.

## Features

- Collates the text files in one directory into a single manuscript, in filename order
- Generates readability reports using Flesch-Kincaid grade level
- Configurable via TOML file
- Supports special chapters (prologue, epilogue, ISBN page, etc.)
- Built with Python standard library only - no external dependencies

## Requirements

- Python 3.11 or higher
- No external dependencies required for core functionality

## What BookBot Does Not Do

- No spell checking and no grammar checking. Use your word processor for those.
- No formatting. BookBot writes plain text and leaves markers such as `__section_break__` for you to resolve in LibreOffice. See `docs/HOWTO`.
- One run produces one manuscript. It does not build several books at once.

Sentence detection assumes standard English punctuation, which is worth knowing when you read the grade level.


## Quick Start:

- Download bookbot.py to a directory in your path.

### Create a directory structure for your masterpiece

- Make a directory for your book, for example:   my_book
- Go into that directory and then make the following directories:  book, chapters, reports, research
- Add your chapter files to the chapters/ directory
- Each file should be named to sort in order (`01_chapter.txt`, `02_chapter.txt`, etc.)

### Create `book_config.toml` (see `sample_book_config.toml`)


```text
    title         = "My Great Novel"
    author        = "Your Name"
    book_dir      = "book"
    chapter_dir   = "chapters"
    reports_dir   = "reports"
    has_header    = true
    section_break = "\n__section_break__\n"
    report        = true
```

### Run BookBot

Run BookBot from inside your book's directory. It reads `book_config.toml` and `chapters/` from the directory you are standing in, not from the directory `bookbot.py` lives in. That is what lets one copy in `/usr/local/bin` serve every book you write.

```
python ../bookbot.py
```


## Usage

### Command Line Options

```
-f, --file            Config file in TOML format (default: book_config.toml)
-a, --author          Author name
-b, --book_dir        Directory for book results (default: book)
-c, --chapter_dir     Directory for chapters (default: chapters)
--has_header          Chapters have headers (default: True)
-p, --section_break   String used to identify section break locations
-r, --reports_dir     Directory for reports (default: reports)
-t, --title           Book title
```

## Writing Structure

BookBot assumes a simple order for chapter filenames and for chapter formats.

### Chapter Files

- Name files to sort in desired order: `01_chapter.txt`, `02_chapter.txt`, etc.
- Special chapter types (use exact filenames):
  - `title.txt` - Title page
  - `isbn.txt` - ISBN information
  - `prologue.txt` - Prologue
  - `epilogue.txt` - Epilogue
  - `afterward.txt` - Afterward
  - `author_bio.txt` - Author biography
  - `more.txt` - Additional content

### Chapter Format

If `has_header = true` then the first line of each chapter file is treated as a header:

```
[Location and Date]

First paragraph of the chapter.

Second paragraph.
```

## Output

BookBot generates:
- A compiled manuscript in `book/your_title.txt`
- Readability reports in `reports/report.txt`


## For New Python Developers

This project demonstrates:

- **Single-file application** - All code in one place for easy learning
- **Standard library only** - No dependency management complexity
- **Test-driven development** - 28 unit tests with unittest
- **Configuration management** - TOML-based configuration
- **File I/O operations** - Reading and writing text files
- **Object-oriented design** - Classes with clear responsibilities
- **Command-line interfaces** - Using argparse for CLI tools

### Learning Path For New Pythonistas

1. Start with `parse_args()` to understand CLI argument parsing
2. Study `Chapter` class to see OOP in action
3. Examine test files to learn unittest patterns
4. Review `Report` class for algorithm implementation
5. Explore `BookBuilder` class for the builder pattern

## Contributing

Contributions welcome! These rules are not negotiable, because they are what keeps the tool handable by writers who do not program:

- Python 3.6
- `bookbot.py` stays a single file. Do not split it into a package, and do not add modules it imports.
- Runtime code uses the Python standard library and nothing else.
- Tests use unittest. Never pytest.
- Third-party tools are for developers only. black, flake8, coverage and semgrep are listed in `requirements_dev.txt` and run in a venv. They never become runtime dependencies.
- PEP 8 style, enforced by black and flake8. See Code Quality below.
- Comprehensive documentation


### Contributing Basics

- Check out the [Issues](https://github.com/LeamHall/bookbot/issues) page
- Clone/Fork the repo to your local machine
- Use a venv or similar with black, coverage, flake8, and semgrep
- Verify your code works with Python 3.6, and any later versions you wish to test


### Code Quality

Run the test suite, all tests should pass:

```bash
make test
```

After the tests pass, ensure there's code coverage for your new code, it is formatted correctly, and there are no security issues.
This is where you need to be in a venv or similar, with black, coverage, flake8, and semgrep installed.

```bash
make all
```

### Project Structure

```
bookbot/
├── bookbot.py              # Main application
├── test/                   # Unit tests
│   ├── test_book.py
│   ├── test_chapter.py
│   ├── test_collate.py
│   ├── test_config.py
│   └── test_report.py
├── docs/
│   └── HOWTO              # LibreOffice formatting guide
├── requirements_dev.txt    # Developer tools, never runtime dependencies
├── sample_book_config.toml
└── README.md
```

## License

This software is Copyright (c) 2020-2026 by Leam Hall.

The code is free software, licensed under the MIT License. See LICENSE for the full text.

The files in `data/` are data rather than code, and they are not all MIT. Each records its own origin, terms and required attribution in `data/README`. In particular, `data/en_50k.txt` is used under CC BY-SA 4.0:

> Frequency list by Hermit Dave, from the [FrequencyWords project](https://github.com/hermitdave/FrequencyWords), used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Holding that file alongside MIT code does not make the code share-alike. A published derivative of the list would itself be CC BY-SA 4.0; `data/README` states where that line falls.

## Author

Leam Hall


