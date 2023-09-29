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

DEFAULT_CONFIG = {
    "author": "",
    "book_dir": "book",
    "reports_dir": "reports",
    "scene_dir": "scenes",
    "title": "",
}

CONFIG_FILE = "book_config.ini"

def read_config(defaults = DEFAULT_CONFIG, config_file = CONFIG_FILE):
    """ 
        read_config takes the default configuration dict and a config file,
        and returns a dict of configuration.
    """
    config = defaults
    parser = ConfigParser()
    try:
        parser.read(config_file)
        config.update(dict(parser['Book'])) 
    except KeyError as e:
        pass

    return config 


# check for/make directories
def setup_dirs():
    pass


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
    read_config()
    setup_dirs()
    parse_sections()
    collate_book()
    write_book()
    collate_reports()
    write_reports()
