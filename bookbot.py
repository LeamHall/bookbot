#!/usr/bin/env python

# name    :  bookbot.py
# version :  0.0.1
# date    :  20230923
# author  :  Leam Hall
# desc    :  Assembles and reports on a text file based book.


## Notes

## TODO
# Figure out word list locations.
# Spell checker?

from configparser import ConfigParser
import os


DEFAULT_CONFIG = {
    "author": "",
    "book_dir": "book",
    "chapter_dir": "chapters",
    "chapter_header": False,
    "reports_dir": "reports",
    "title": "",
}

CONFIG_FILE = "book_config.ini"


def list_of_files(target_dir):
    """
    Takes a target directory and returns the list of filenames.
    """
    filenames = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            filenames.append(file)
    return filenames


def lines_from_file(filename):
    """
    Returns a list of non-blank lines in the file.
    """
    file_data = []
    with open(filename, "r") as in_f:
        for line in in_f.readlines():
            line = line.strip()
            if line:
                file_data.append(line)
    return file_data


def read_config(defaults=DEFAULT_CONFIG, config_file=CONFIG_FILE):
    """
    Takes the default configuration dict and a config file,
    and returns a dict of configuration.
    """
    # Need to test for missing config file.
    # Set the blanks to something odd?
    config = defaults
    parser = ConfigParser()
    try:
        parser.read(config_file)
        config.update(dict(parser["Book"]))
    except KeyError:
        pass

    return config


def setup_dirs(conf=None, root_dir=None):
    """
    Creates the required directories if they are not available.
    """
    if not conf:
        raise TypeError("program config required")
    if not root_dir:
        root_dir = os.getcwd()
    for d in [conf["book_dir"], conf["reports_dir"], conf["chapter_dir"]]:
        new_dir = os.path.join(root_dir, d)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir, mode=0o0750)


def scrub_line(line):
    """
    Removes multiple whitespaces in the middle of a line.
    """
    return " ".join(line.split())


class Chapter:
    def __init__(self, data={}):
        self._lines = data.get("lines", [])
        self._get_counts()

    def __str__(self):
        lines = "\n\n".join(self._lines)
        return lines

    def _get_counts(self):
        """Sets the word and sentence counts."""
        self.sentence_count = 0
        self.word_count = 0
        for line in self._lines:
            self.word_count += len(line.split())
            self.sentence_count += line.count(".")
            self.sentence_count += line.count("!")
            self.sentence_count += line.count("?")
            self.average_sentence_length = round(
                self.word_count / self.sentence_count
            )


## Working with individual Chapters
# pull each chapter into its own object
# - [Done] strip beginning and ending whitespace.
# - [Done] break sentences into list items.
# -- [Done] include closing quotes
# - [Done] remove two or more spaces next to each other.
# - [Done] get word and sentence counts.
# - [Done] get average sentence lengths.
# - deal with chapter headers, like [this]
# - format so it is easier to bold the chapter number and datetime stamp.
# - format extended spacers
# - do grade analysis.
# - count words used for each grade's word lists.
# - no indent for epub, has para spacing.
# - indent for print, no para spacing.
def parse_chapters():
    pass


# order chapters so that prologues, epiloges, etc, are in place.
# - needs a book object
def order_chapters():
    pass


# create header pages
# - title
# - copyright, etc
def create_header_pages():
    pass


# write each chapter into the book.
def collate_book(chapters=[], chapter_divider=""):
    """Collate a list of chapters, separated by a divider, into a string."""
    book_data = ""
    for chapter in chapters:
        if book_data:
            book_data += "\n{}\n".format(chapter_divider)
        book_data += str(chapter.__str__())
    return book_data


# Write book files; print, text, pdf(?)
def write_book():
    pass


# collate all reports.
def collate_reports():
    pass


# write all reports.
def write_reports():
    pass


if __name__ == "__main__":
    config = read_config()
    setup_dirs(config)
    parse_chapters()
    collate_book()
    write_book()
    collate_reports()
    write_reports()
