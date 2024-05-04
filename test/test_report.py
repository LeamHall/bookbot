#!/usr/bin/env python

# name    :  test/test_report.py
# version :  0.0.1
# date    :  20240504
# author  :  Leam Hall
# desc    :  Test the report class.


import unittest

import bookbot as bb


class TestReport(unittest.TestCase):

    def setUp(self):
        data = ["One sentence.", "Another!", "Is this anoother?"]
        self.report = bb.Report(data, "fred")

    def tearDown(self):
        pass

    def test_basic_report(self):
        self.assertIn("one sentence.", self.report.lines)
        self.assertEqual(self.report.sentence_count, 3)
        self.assertEqual(self.report.word_count, 6)
        self.assertEqual(self.report.syllable_count, 11)
        self.assertEqual(self.report.grade_level, 6.82)
