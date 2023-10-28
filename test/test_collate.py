# name    :  test/test_collate.py
# version :  0.0.1
# date    :  20231004
# author  :  Leam Hall
# desc    :  Test the collation method

import os.path
import tempfile
import unittest

import bookbot as bb


class TestCollate(unittest.TestCase):
    def setUp(self):
        self.chapters = [
            bb.Chapter(data={"lines": ["header", "Line one.", "Line two."]}),
            bb.Chapter(data={"lines": ["header", "Lino unu.", "Lino du."]}),
        ]
        self.test_dir = tempfile.TemporaryDirectory()
        filenames = ["01_10.txt", "01_20.txt", "02_10.txt"]
        for f in filenames:
            in_file = os.path.join(self.test_dir.name, f)
            with open(in_file, "w") as in_f:
                in_f.write("{}\n\n".format(f))
                in_f.write("Something in {}.\n\n".format(f))

    def tearDown(self):
        self.test_dir.cleanup()

    def test_collate_empty(self):
        result = bb.collate_book()
        self.assertEqual(result, "")

    def test_collate_with_data(self):
        expected = "Line one.\n\nLine two.\n\nLino unu.\n\nLino du."
        result = bb.collate_book(self.chapters)
        self.assertEqual(result, expected)

    def test_collate_with_data_and_sep(self):
        expected = "Line one.\n\nLine two.\n##\nLino unu.\n\nLino du."
        result = bb.collate_book(self.chapters, chapter_divider = "##")
        self.assertEqual(result, expected)

    def test_collate_file_list(self):
        result = bb.list_of_files(self.test_dir.name)
        expected = ["01_10.txt", "01_20.txt", "02_10.txt"]
        self.assertEqual(result, expected)
