# name    :  test/test_collate_chapters.py
# version :  0.0.2
# date    :  20231123
# author  :  Leam Hall
# desc    :  Test the collation of files into chapters

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
        filenames = ["prologue.txt", "01_10.txt", "01_20.txt", "02_10.txt"]
        for f in filenames:
            in_file = os.path.join(self.test_dir.name, f)
            with open(in_file, "w") as in_f:
                if "prologue" in f:
                    in_f.write("{}\n".format(f))
                in_f.write("{}\n\n".format(f))
                in_f.write("Something in {}.\n\n".format(f))

        self.test_dir_no_txt_files = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()
        self.test_dir_no_txt_files.cleanup()

    # def test_collate_empty(self):
    #    result = bb.collate_book()
    #    self.assertEqual(result, "")

    # def test_collate_with_data(self):
    #    expected = "Line one.\n\nLine two.\n\nLino unu.\n\nLino du."
    #    result = bb.collate_book(self.chapters)
    #    self.assertEqual(result, expected)

    # def test_collate_with_data_and_sep(self):
    #    expected = "Line one.\n\nLine two.\n##\nLino unu.\n\nLino du."
    #    result = bb.collate_book(self.chapters, section_break = "##")
    #    self.assertEqual(result, expected)

    def test_collate_file_list(self):
        results = bb.list_of_files(self.test_dir.name)
        filenames = ["01_10.txt", "01_20.txt", "02_10.txt", "prologue.txt"]
        for name in filenames:
            self.assertTrue(any(name in result for result in results))

    def test_parse_chapters(self):
        filenames = bb.list_of_files(self.test_dir.name)
        chapters, specials = bb.parse_chapters(filenames, bb.special_chapters)
        self.assertEqual(type(chapters[0]), bb.Chapter)
        self.assertEqual(type(specials["prologue"]), bb.Chapter)
        self.assertEqual(specials["prologue"].type, "prologue")

    def test_list_of_files_no_dir(self):
        with self.assertRaises(FileNotFoundError):
            bb.list_of_files("fred")

    def test_list_of_files_no_files(self):
        with self.assertRaises(FileNotFoundError):
            bb.list_of_files(self.test_dir_no_txt_files.name)
