#!/usr/bin/env python

# name    :  test/test_report.py
# version :  0.0.1
# date    :  20240504
# author  :  Leam Hall
# desc    :  Test the report class.


# Notes:
#   - If there are files with no punctuation it can show up as a
#     ZeroDivisionError, but it is just the lack of punctuation.

import unittest

import bookbot as bb


class TestReport(unittest.TestCase):

    def setUp(self):
        data = ["Yo", "One sentence.", "Another!", "Is this anoother?"]
        self.report = bb.Report(data, "fred")

    def tearDown(self):
        pass

    def test_basic_report(self):
        self.assertIn("one sentence.", self.report.lines)
        self.assertEqual(self.report.sentence_count, 4)
        self.assertEqual(self.report.word_count, 7)
        self.assertEqual(self.report.syllable_count, 12)
        self.assertEqual(self.report.grade_level, 5.32)
