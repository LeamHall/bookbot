#!/usr/bin/env python

# name    :  bookbot.py
# version :  0.0.1
# date    :  20230923
# author  :  Leam Hall
# desc    :  Assembles and reports on a text file based book.


## Notes

import argparse
import errno
import os
from pathlib import Path
import re
import sys
import tomllib

DEFAULT_CONFIG = {
    "author": "",
    "book_dir": "book",
    "chapter_dir": "chapters",
    "has_header": True,
    "section_break": "\n__section_break__\n",
    "reports_dir": "reports",
    "title": "",
}

SPECIAL_LIST = [
    "title",
    "isbn",
    "prologue",
    "epilogue",
    "afterward",
    "author",
    "more",
]


def parse_args(args=[]):
    """Returns the parsed arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Config file in TOML format.",
        default="book_config.toml",
    )
    parser.add_argument("-a", "--author", help="Author name")
    parser.add_argument(
        "-b", "--book_dir", help="Directory for book results.", default="book"
    )
    parser.add_argument(
        "-c",
        "--chapter_dir",
        help="Directory for chapters.",
        default="chapters",
    )
    parser.add_argument(
        "--has_header", help="Chapters have headers?", default=True
    )
    parser.add_argument(
        "-p",
        "--section_break",
        help="String used to identify section_break locations",
        default="\n__section_break__\n",
    )
    parser.add_argument(
        "-r", "--reports_dir", help="Directory for reports.", default="reports"
    )
    parser.add_argument("-t", "--title", help="Book title")
    return vars(parser.parse_args(args))


def list_of_files(target_dir):
    """
    Takes a target directory and returns the list of filenames.
    """
    filenames = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            filenames.append(file)

    return sorted(filenames)


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


def chapter_type(filename):
    """Returns the type of the chapter, based on filename."""
    p = Path(filename)
    if p.stem in SPECIAL_LIST:
        return p.stem
    return "chapter"


def read_config(_args={}, config=DEFAULT_CONFIG):
    """
    Takes the default configuration dict and parsed arguments,
    and returns a dict of configuration.
    """
    try:
        with open(_args["file"], "rb") as f:
            data = tomllib.load(f)
        config.update(data)
    except (KeyError, FileNotFoundError):
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


class Chapter:
    def __init__(self, data={}):
        self.lines = data.get("lines", [])
        self._has_header = data.get("has_header", True)
        self._set_header()
        self._scrub_lines()
        self._set_type()

    def __str__(self):
        lines = "\n\n".join(self.lines)
        return lines

    def _set_header(self):
        """Sets the header if present, otherwise to an empty string."""
        if self._has_header:
            self.header = self.lines[0]
            self.lines = self.lines[1:]
        else:
            self.header = ""

    def _scrub_lines(self):
        """Removes multiple whitespaces and empty lines."""
        clean_lines = []
        for line in self.lines:
            line = line.strip()
            if line:
                clean_lines.append(" ".join(line.split()))
        self.lines = clean_lines

    def _set_type(self):
        """Sets the chapter type, based on SPECIAL_LIST."""
        if self.lines[0] in SPECIAL_LIST:
            self.type = self.lines.pop(0)
            self.number = False
        else:
            self.type = "chapter"
            self.number = True

    # This should be in the Report
    # def _get_counts(self):
    #    """Sets the word and sentence counts."""
    #    self.sentence_count = 0
    #    self.word_count = 0
    #    for line in self._lines:
    #        self.word_count += len(line.split())
    #        self.sentence_count += line.count(".")
    #        self.sentence_count += line.count("!")
    #        self.sentence_count += line.count("?")
    #        self.average_sentence_length = round(
    #            self.word_count / self.sentence_count
    #        )


## Working with individual Chapters
# pull each chapter into its own object
# - [Done] strip beginning and ending whitespace.
# - [Done] break sentences into list items.
# -- [Done] include closing quotes
# - [Done] remove two or more spaces next to each other.
# - [Done] get word and sentence counts.
# - [Done] get average sentence lengths.
# - [done] deal with chapter headers, like [this]
# - [done] format to be easier to bold the chapter number and datetime stamp.
# - format extended spacers
# - do grade analysis.
# - count words used for each grade's word lists.
# - no indent for epub, has para spacing.
# - indent for print, no para spacing.


# order chapters so that prologues, epiloges, etc, are in place.
# - needs a book object
def order_chapters(chapters, special_list):
    """
    Removes special chapters from chapter list, and returns the reduced
    list of chapters, and the specificaly sorted order of specials.
    """
    new_chapters = list()
    temp_specials = list()
    specials = list()
    for chapter in chapters:
        if chapter in special_list:
            temp_specials.append(chapter)
        else:
            new_chapters.append(chapter)
    for special in special_list:
        if special in temp_specials:
            specials.append(special)

    return new_chapters, specials


class BookBuilder:
    def __init__(self, config={}, chapters=[], specials={}):
        self.config = DEFAULT_CONFIG | config
        self.chapters = chapters
        self.specials = specials
        self.text = ""

    def write_chapter(self, chapter):
        """Returns a string of the chapter, with additions."""
        section_break = self.config["section_break"]
        text = section_break
        if chapter.number:
            text += "Chapter {}\n\n".format(chapter.number)
        if chapter.header:
            text += "{}\n\n".format(chapter.header)
        for line in chapter.lines:
            text += "\n\n" + line
        return text.strip()

    def build(self):
        """Returns the Book object."""
        book = Book()
        book.author = self.config["author"]
        chapter_number = 0
        for chapter in self.chapters:
            if chapter.type == "chapter":
                chapter_number += 1
                chapter.number = chapter_number
            book.text += self.write_chapter(chapter)
        book.text += "\n\n"
        return book


class Book:
    def __init__(self, text=""):
        self.text = text


def book_filename(config, file_type="txt"):
    """Munges the title into something that is easy to deal with."""
    title = config["title"].lower()
    title = re.sub(r"[\W]", " ", title)
    title_words = title.split()
    title = "_".join(title_words)
    title += "." + file_type
    return title


# Write book files; print, text, pdf(?)
def write_book(book, config):
    book_dir = config["book_dir"]
    book_file = book_filename(config, "txt")
    book_name = os.path.join(book_dir, book_file)
    with open(book_name, "w") as b:
        b.write(book.text)


# collate all reports.
def collate_reports():
    pass


# write all reports.
def write_reports():
    pass


def parse_chapters(_dir, has_header=False):
    """Takes a directory of chapter files, and returns a list of
    Chapter objects."""
    chapters = []
    data = {}
    if not os.path.isdir(_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), _dir)
    files = list_of_files(_dir)
    if not files:
        print("No chapter files found in {}.".format(_dir))
        sys.exit(1)
    for file in files:
        filepath = os.path.join(_dir, file)
        data["lines"] = lines_from_file(filepath)
        data["has_header"] = has_header
        chapters.append(Chapter(data))
    return chapters


if __name__ == "__main__":
    _args = parse_args(args=sys.argv[1:])
    config = read_config(_args)
    setup_dirs(config)
    chapters = parse_chapters(config["chapter_dir"], config["has_header"])
    book = BookBuilder(config, chapters).build()
    write_book(book, config)
    collate_reports()
    write_reports()
