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
    "reports_dir": "reports",
    "scene_dir": "scenes",
    "title": "",
}

CONFIG_FILE = "book_config.ini"


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
    except KeyError as e:
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
    for d in [conf["book_dir"], conf["reports_dir"], conf["scene_dir"]]:
        new_dir = os.path.join(root_dir, d)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir, mode=0o0750)


# pull each section into its own object
# - strip beginning and ending whitespace.
# - remove two or more spaces next to each other.
# - break sentences into list items.
# -- include closing quotes
# - get word and sentence counts.
# - get sentence lengths.
# - format so it is easier to bold the chapter number and datetime stamp.
# - format extended spacers
# - do grade analysis.
# - count words used for each grade's word lists.
# - no indent for epub, has para spacing.
# - indent for print, no para spacing.
def parse_sections():
    pass


# order sections so that prologues, epiloges, etc, are in place.
def order_sections():
    pass


# create header pages
# - title
# - copyright, etc
def create_header_pages():
    pass


# write each section into the book.
def collate_book():
    pass


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
    parse_sections()
    collate_book()
    write_book()
    collate_reports()
    write_reports()
