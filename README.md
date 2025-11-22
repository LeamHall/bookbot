# BookBot


A Python tool for assembling book manuscripts from multiple chapter files and generating readability reports.

## Features

- Collates text files into a single manuscript
- Generates readability reports using Flesch-Kincaid grade level
- Configurable via TOML file
- Supports special chapters (prologue, epilogue, ISBN page, etc.)
- Built with Python standard library only - no external dependencies

## Requirements

- Python 3.11 or higher
- No external dependencies required for core functionality


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

### Code Requirements

-  Will take text files in a single directory, sort them by filename, modify them as chapters or specific sections, and collate them.
-  Will be a single file application.
-  May take word lists for grade level reading reports. 
-  The output will be a single text file.
-  The program will not to spell or grammar checking.
-  The program will use specific directories for output and input.
-  The program will use a config file for book specific data.
-  The program will be runnable from a shared location, such as /usr/local/bin, when the user is in the directory for the book.
-  The program uses standard English punctuation for determining sentences. 

### Code Process Requirements

-  Will use Python and its standard lib for all code. Nothing else.
-  Third-party code may be used by the developers. For example, black, flake8, coverage, etc.
-  The testing framework will be unittest. 
-  Where practical, the code will conform to good Python style.

### Learning Path For New Pythonistas

1. Start with `parse_args()` to understand CLI argument parsing
2. Study `Chapter` class to see OOP in action
3. Examine test files to learn unittest patterns
4. Review `Report` class for algorithm implementation
5. Explore `BookBuilder` class for the builder pattern

## Contributing

Contributions welcome! This project follows:

- Python 3.6
- PEP 8 style guidelines
- Python standard library only (no external dependencies)
- unittest for testing
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
│   ├── HOWTO              # LibreOffice formatting guide
│   └── requirements.txt   # Project requirements documentation
├── sample_book_config.toml
└── README.md
```

## License

This software is Copyright (c) 2025 by Leam Hall.

This is free software, licensed under: The Artistic License 2.0 (GPL Compatible)

## Author

Leam Hall


