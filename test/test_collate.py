# name    :  test/test_collate.py
# version :  0.0.1
# date    :  20231004
# author  :  Leam Hall 
# desc    :  Test the collation method

import unittest

import bookbot as bb

class TestCollate(unittest.TestCase):

    def setUp(self):
        self.chapters = [
            bb.Chapter(data = {"lines": ["Line one.", "Line two."]}),
            bb.Chapter(data = {"lines": ["Lino unu.", "Lino du."]}),
        ]

    def tearDown(self):
        pass 

    def test_collate_empty(self):
        result = bb.collate_book() 
        self.assertEqual(result, "")

    def test_collate_with_data(self):
        expected = "Line one.\n\nLine two.\n\nLino unu.\n\nLino du."
        result =  bb.collate_book(self.chapters)
        self.assertEqual(result, expected)

    def test_collate_with_data_and_sep(self):
        expected = "Line one.\n\nLine two.\n##\nLino unu.\n\nLino du."
        result =  bb.collate_book(self.chapters, "##")
        self.assertEqual(result, expected)

