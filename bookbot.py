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


special_chapters = {
    "title": "",
    "isbn": "",
    "prologue": "",
    "epilogue": "",
    "afterward": "",
    "author_bio": "",
    "more": "",
}


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
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), target_dir
        )
    filenames = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".txt"):
                filenames.append(os.path.join(target_dir, file))
    if not filenames:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), target_dir
        )
    return sorted(filenames)


def lines_from_file(filename):
    """
    Returns a list of non-blank lines in the file.
    """
    file_data = []
    with open(filename, "r", encoding="utf-8-sig") as in_f:
        for line in in_f.readlines():
            line = line.strip()
            if line:
                file_data.append(line)
    return file_data


def chapter_type(filename):
    """Returns the type of the chapter, based on filename."""
    p = Path(filename)
    if p.stem in special_chapters:
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


class Report:

    def __init__(self, data, filename):
        self.punctuation = [".", "?", "!"]
        self.vowels = ["a", "e", "i", "o", "u"]
        self.doubles = ["ee", "oi", "oo", "ou"]
        self.quotes = ['"', "'"]
        self.filename = filename
        self.lines = list()
        for line in data:
            self.lines.append(line.lower())
        self._count_sentences()
        self._count_words()
        self._count_syallables()
        self._grade_report()

    def _count_sentences(self):
        """Counts the number of sentence ending marks."""
        self.sentence_count = 0
        for line in self.lines:
            for p in self.punctuation:
                self.sentence_count += line.count(p)

    def _count_words(self):
        """Counts the number of words, ignoring punctuation."""
        self.word_count = 0
        for line in self.lines:
            self.word_count += len(line.split())

    def _count_syallables(self):
        """Simplistic syllable counter. Does not handle unicode."""
        self.syllable_count = 0
        for line in self.lines:
            for v in self.vowels:
                self.syllable_count += line.count(v)
            for d in self.doubles:
                self.syllable_count -= line.count(d)
            scrubbed_line = line
            for p in self.punctuation:
                scrubbed_line = scrubbed_line.replace(p, " ")
            for q in self.quotes:
                scrubbed_line = scrubbed_line.replace(q, " ")
            words = scrubbed_line.split()
            for word in words:
                for phrase in ["e", "ey"]:
                    if word.endswith(phrase):
                        self.syllable_count -= 1
                for phrase in ["y"]:
                    if word.endswith(phrase):
                        self.syllable_count += 1
        if self.syllable_count < 1:
            self.syllable_count = 1

    def _grade_report(self):
        """Calculates grade level per:
        https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
        """
        if not self.word_count or not self.sentence_count:
            raise ValueError(
                "Insufficient words or sentences in {}.".format(self.filename)
            )

        self.sentence_average = self.word_count / self.sentence_count
        self.syllables_per_word_average = self.syllable_count / self.word_count
        self.grade_level = (
            (0.39 * self.sentence_average)
            + (11.8 * self.syllables_per_word_average)
            - 15.59
        )
        self.grade_level = float("{:.2f}".format(self.grade_level))

    def report_data(self):
        """Collates and returns report data."""
        data = dict()
        data["filename"] = self.filename
        data["sentence_average"] = self.sentence_average
        data["grade_level"] = self.grade_level
        data["syllables_per_word_average"] = self.syllables_per_word_average
        return data


class Chapter:
    def __init__(self, data={}):
        self.lines = data.get("lines", [])
        self._has_header = data.get("has_header", True)
        self.filename = data.get("filename", "")
        self.type = data.get("type", "chapter")
        self.number = data.get("number", 0)
        self._set_header()
        self._scrub_lines()
        try:
            self.report = Report(data=self.lines, filename=self.filename)
            self.report_data = self.report.report_data()
        except ValueError:
            pass

    def __str__(self):
        lines = "\n\n".join(self.lines)
        return lines

    def _set_header(self):
        """Sets the header if present, otherwise to an empty string."""
        self.header = False
        try:
            if self._has_header:
                self.header = self.lines[0]
                self.lines = self.lines[1:]
        except IndexError:
            pass

    def _scrub_lines(self):
        """Removes multiple whitespaces and empty lines."""
        clean_lines = []
        for line in self.lines:
            line = line.strip()
            if line:
                clean_lines.append(" ".join(line.split()))
        self.lines = clean_lines

    # def _set_type(self):
    #    """Sets the chapter type, based on SPECIAL_LIST."""
    #    if self.lines[0] in SPECIAL_LIST:
    #        self.type = self.lines.pop(0)
    #        self.number = False
    #    else:
    #        self.type = "chapter"
    #        self.number = True

    ## Working with individual Chapters
    # pull each chapter into its own object
    # - [Done] strip beginning and ending whitespace.
    # - [Done] break sentences into list items.
    # -- [Done] include closing quotes
    # - [Done] remove two or more spaces next to each other.
    # - [Done] get word and sentence counts.
    # - [Done] get average sentence lengths.
    # - [done] deal with chapter headers, like [this]
    # - [done] format to be easier to bold chapter number and datetimes.
    # - format extended spacers
    # - do grade analysis.
    # - count words used for each grade's word lists.
    # - no indent for epub, has para spacing.
    # - indent for print, no para spacing.


# def order_chapters(chapters, special_list):
#    """
#    Removes special chapters from chapter list, and returns the reduced
#    list of chapters, and the specificaly sorted order of specials.
#    """
#    new_chapters = list()
#    temp_specials = list()
#    specials = list()
#    for chapter in chapters:
#        if chapter in special_list:
#            temp_specials.append(chapter)
#        else:
#            new_chapters.append(chapter)
#    for special in special_list:
#        if special in temp_specials:
#            specials.append(special)
#
#    return new_chapters, specials


class BookBuilder:
    def __init__(
        self, config={}, chapters=[], special_chapters=special_chapters
    ):
        self.config = DEFAULT_CONFIG | config
        self.chapters = chapters
        self.special_chapters = special_chapters
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
        return text.rstrip()

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
            book.chapters.append(chapter)
        book.text += "\n\n"
        return book


class Book:
    def __init__(self, text=""):
        self.text = text
        self.chapters = list()


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
    with open(book_name, "w", encoding="utf-8") as b:
        b.write(book.text)


def collate_reports(book):
    """Builds a list of reports from each chapter. Does this go in book?"""
    chapter_reports = []
    for chapter in book.chapters:
        chapter_reports.append(chapter.report_data)
    return chapter_reports


def write_report_string(reports):
    """Takes the reports and builds a string.
    Need to figure out if this goes into the Book, or someplace else.
    """
    grade_levels = list()
    report_string = ""
    for report in reports:
        report_string += "Filename: {}\n".format(report["filename"])
        report_string += "Grade Level: {:.1f}\n".format(report["grade_level"])
        grade_levels.append(report["grade_level"])
        report_string += "\n"

    report_string += "Average Grade Level: {:.1f}".format(
        sum(grade_levels) / len(grade_levels)
    )
    return report_string


def write_reports(reports_dir, report_string):
    """Writes the report file(s)."""
    # Needs to check for/create report directory.
    report_filename = os.path.join(reports_dir, "report.txt")
    with open(report_filename, "w") as f:
        f.write(report_string)


def parse_chapters(files, specials, has_header=False):
    """Takes a list of files and returns list of
    Chapter objects and a dict of Special Chapter objects."""
    chapters = []
    chapter_count = 0
    special_chapters = specials
    for file in files:
        data = {}
        data["lines"] = lines_from_file(file)
        data["has_header"] = has_header
        data["filename"] = os.path.basename(file)
        data["type"] = chapter_type(file)
        if data["type"] in special_chapters:
            special_name = data["type"]
            special_chapters[special_name] = Chapter(data)
        else:
            chapter_count += 1
            data["number"] = chapter_count
            chapters.append(Chapter(data))
    return chapters, special_chapters


if __name__ == "__main__":
    _args = parse_args(args=sys.argv[1:])
    config = read_config(_args)
    setup_dirs(config)
    chapters, specials = parse_chapters(
        list_of_files(config["chapter_dir"]),
        special_chapters,
        config["has_header"],
    )
    book = BookBuilder(config, chapters).build()
    write_book(book, config)
    if config["report"]:
        collated_reports = collate_reports(book)
        report = write_report_string(collated_reports)
        write_reports(_args["reports_dir"], report)
