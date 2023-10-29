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
from pathlib import Path

CONFIG_FILE = "book_config.ini"

DEFAULT_CONFIG = {
    "author": "",
    "book_dir": "book",
    "chapter_dir": "chapters",
    "page_break": "__page_break__",
    "reports_dir": "reports",
    "title": "",
}

SPECIAL_LIST = [
    'title', 'isbn', 'prologue', 'epilogue', 'afterward', 'author', 'more']


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


def chapter_type(filename):
    """ Returns the type of the chapter, based on filename. """
    p = Path(filename)
    if p.stem in SPECIAL_LIST:
        return p.stem 
    return "chapter"


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


class Chapter:
    def __init__(self, data={}):
        self.lines = data.get("lines", [])
        self._has_header = data.get("has_header", True)
        self._set_header()
        self._scrub_lines()

    def __str__(self):
        lines = "\n\n".join(self.lines)
        return lines

    def _set_header(self):
        """ Sets the header if present, otherwise to an empty string. """
        if self._has_header:
            self.header = self.lines[0]
            self.lines = self.lines[1:]
        else:
            self.header = ""
   
    def _scrub_lines(self):
        """ Removes multiple whitespaces in the middle of a line.  """
        clean_lines = []
        for line in self.lines:
            clean_lines.append(" ".join(line.split()))
        self.lines = clean_lines
             
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
def parse_chapters():
    pass


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



# write each chapter into the book.
# def collate_book(chapters=[], specials = [], page_break = ""):
#    """Collate a list of chapters, separated by a divider, into a string."""
#    book_data = ""
#     for chapter in chapters:
#        if book_data:
#            book_data += "\n{}\n".format(page_break)
#        # This no longer works, due to the header and specials.
#        book_data += str(chapter.__str__())
#    return book_data


class BookBuilder:
    def __init__(self, config=DEFAULT_CONFIG, chapters=[], specials = {}):
        self.config = config
        self.chapters = chapters
        self.specials = specials
        self.text = ""

    def write_chapter(
        self, chapter, chapter_number = 0, is_numbered = True, has_header = True):
        """ Returns a string of the chapter, with additions. """
        text = ""
        page_break = self.config["page_break"]
     
        for line in chapter.lines:
            text += line + "\n\n"
 
        return text 

    def build(self):
        """ Returns the Book object. """
        book = Book()
        book.author = self.config["author"]
        text = ""
        for chapter in self.chapters:
            text += self.write_chapter(chapter, chapter_number = 0,
                is_numbered = False,
                has_header = False,
            )
            book.text += text
        return book


class Book:
    def __init__(self, text = ""):
        self.text = text


# Write book files; print, text, pdf(?)
def write_book(book):
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
