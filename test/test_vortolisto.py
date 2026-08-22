#!/usr/bin/env python

# name    :  test/test_vortolisto.py
# version :  0.0.1
# date    :  20260728
# author  :
# desc    :

from collections import defaultdict
import unittest


from bin import vortolisto as vl


class TestVortolistoGetWords(unittest.TestCase):
    def setUp(self):
        self.data = defaultdict(int)

    def tearDown(self):
        pass

    def test_vortolisto_word(self):
        test_string = "Fred"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_start_quote(self):
        test_string = '"Fred'
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_end_quote(self):
        test_string = '"Fred"'
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_apos_s(self):
        test_string = "Fred's"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_apos_end(self):
        test_string = "Fred's"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_question(self):
        test_string = "Fred?"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_exclaim(self):
        test_string = "Fred!"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_comma(self):
        test_string = "Fred,"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_colon(self):
        test_string = "Fred:"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_semicolon(self):
        test_string = "Fred;"
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 1)
        self.assertEqual(self.data["fred"], 1)

    def test_vortolisto_words(self):
        test_string = (
            "Al and Wilbur are happily married! And Amanda plays happily."
        )
        vl.get_words(test_string, self.data)
        self.assertEqual(len(self.data), 8)
        self.assertIn("married", self.data.keys())
        self.assertEqual(self.data["and"], 2)


class TestContractions(unittest.TestCase):
    def setUp(self):
        self.data = defaultdict(int)
        test_string = "Ain't that I cain't but I don't wanna."
        vl.get_words(test_string, self.data)
        self.contractions = defaultdict(int)

    def tearDown(self):
        pass

    def test_contraction_works(self):
        vl.get_contractions(self.data, self.contractions)
        self.assertEqual(len(self.data), 7)
        # self.assertEqual(len(self.contractions), 3)


class TestProperNouns(unittest.TestCase):
    def test_not_first_word(self):
        test_string = "Al and Wilbur are happily married! Wilbur, Al and Amanda play happily."
        proper_nouns = defaultdict(int)
        vl.get_proper_nouns(test_string, proper_nouns)
        self.assertEqual(len(proper_nouns), 3)


class TestScrubPhrase(unittest.TestCase):
    def test_scrub_poss_s(self):
        test_phrase = "Al's"
        result = vl.scrub_phrase(test_phrase)
        expected = "Al"
        self.assertEqual(result, expected)






