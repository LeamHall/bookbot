#!/usr/bin/env python

# name    :  vortolisto.py
# version :  0.0.1
# date    :  20260728
# author  :
# desc    :


#### Notes
# Creates lists
# - contractions
# - potential possessives
# - potential proper nouns
# - domain specific terms
# - percentage of text words known by most used to least

# What if the dicts was built first, then the lists above were
# pulled from that?

from collections import defaultdict
import string
import sys

s1 = "My, how nice those roses's are!"

# symbols = ['"', "'", '.', '?', '!', ',', '(', ')']


def get_words(line, data):
    """
    Takes a string and an existing dictionary of word:count,
    Adds to the dict.
    """
    symbols = ['"', "'", ".", "?", "!", ",", "(", ")"]
    line = line.lower()
    line_data = line.split()
    for datum in line_data:
        if datum[0] in symbols:
            datum = datum[1:]
        if datum[-1] in symbols:
            datum = datum[:-1]
        base = ""

        for d in datum:
            if d not in string.ascii_lowercase:
                break
            if d in string.ascii_lowercase:
                base += d
        if len(base) == 0:
            continue
        if base not in data.keys():
            data[base] = 1
        else:
            data[base] += 1


def get_contractions(data, contractions):
    """
    Takes a dict and copies the potential contractions to contractions dict.
    """
    for datum in data.keys():
        if "'" in datum:  # and datum[-1] != "'":
            contractions[datum] = data[datum]


def get_phrases(data, phrases):
    """
    Takes the line and removes punctuation
    """
    pass


def scrub_phrase(phrase):
    """Removes all symbols from a phrase"""
    result = ""
    for c in phrase:
        if c in string.ascii_letters:
            result += c
        elif c not in string.ascii_letters:
            break
    return result


def get_proper_nouns(data, storage):
    """
    Takes a string and returns words that start with an uppercase
    that are not the first word.
    """

    symbols = ['"', "'", ".", "?", "!", ",", "(", ")"]
    punctuation = [".", "?", "!"]
    data_list = data.split()
    for i in range(0, len(data_list)):
        if scrub_phrase(data_list[i]) in storage.keys():
            storage[scrub_phrase(data_list[i])] += 1
        elif i == 0:
            continue
        elif (
            data_list[i][0] in string.ascii_uppercase
            and data_list[i - 1][-1] not in punctuation
        ):
            storage[data_list[i]] += 1


if __name__ == "__main__":
    contractions = defaultdict(int)
    phrases = defaultdict(int)
    data = defaultdict(int)

    file = sys.argv[1]

    with open(file, "r") as in_f:
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                get_words(line, data)

    # get_contractions(data, contractions)

    reversed_data = defaultdict(str)
    for k, v in data.items():
        if v not in reversed_data.keys():
            reversed_data[v] = list()
        reversed_data[v].append(k)

    for k, v in reversed_data.items():
        print(k, ":", len(v), ":", v)

    print("Unique Words:", len(data))

    outfile = "data/words__agent.txt"
    with open(outfile, "w") as out_f:
        for k,v in data.items():
            out_f.write("{}  {}\n".format(k,v))



