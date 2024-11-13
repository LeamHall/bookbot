# name    :  test/test_chapter.py
# version :  0.0.1
# date    :  20230928
# author  :  Leam Hall
# desc    :  Unittests for bookbot


import os.path
import tempfile
import unittest

import bookbot as bb


class TestChapter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.chapter_one_file = os.path.join(self.test_dir.name, "chapter_one")
        with open(self.chapter_one_file, "w") as s1:
            s1.write("\n\n\n")
            s1.write("\n\n\n")
            s1.write("[1429.180.0745] Casimir District, Saorsa\n\n")
            s1.write("\n\n\n")
            s1.write("\n\n\n")
            s1.write("Al sat with her dad on the rusty hood of the car. ")
            s1.write("The view from Solomon Mountain seemed to go on and on. ")
            s1.write("Twenty kilometers away and two klicks down she could ")
            s1.write("see her hometown. A light morning fog, and the quiet, ")
            s1.write("raised up and comforted her.\n")
            s1.write("\n")
            s1.write("A line of four large planes approached from the east.\n")
            s1.write("\n\n\n")
            s1.write("\n\n\n")

    def tearDown(self):
        self.test_dir.cleanup()

    # def test_chapter_type_isbn(self):
    #    isbn_file = os.path.join(self.test_dir.name, "isbn.txt")
    #    with open(isbn_file, "w") as s1:
    #        s1.write("\nisbn\n")
    #    expected = "isbn"
    #    result = bb.chapter_type(isbn_file)
    #    self.assertEqual(result, expected)

    # def test_chapter_type_chapter(self):
    #    expected = "chapter"
    #    result = bb.chapter_type(self.chapter_one_file)
    #    self.assertEqual(result, expected)

    def test_read_chapter(self):
        chapter_lines = bb.lines_from_file(self.chapter_one_file)
        self.assertTrue(type(chapter_lines), list)
        self.assertEqual(len(chapter_lines), 3)
        self.assertTrue(chapter_lines[0].startswith("["))

    def test_chapter_lines(self):
        lines = bb.lines_from_file(self.chapter_one_file)
        chapter_data = {
            "lines": lines,
        }
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(len(chapter_1.lines), 2)

    # def test_chapter_counts(self):
    #    lines = bb.lines_from_file(self.chapter_one_file)
    #    chapter_data = {
    #        "lines": lines,
    #    }
    #    chapter_1 = bb.Chapter(chapter_data)
    #    self.assertEqual(chapter_1.sentence_count, 5)
    #    self.assertEqual(chapter_1.word_count, 58)
    #    self.assertEqual(chapter_1.average_sentence_length, 12)

    # def test_order_chapters(self):
    #    orig_chapters = [
    #        "author",
    #        "this",
    #        "that",
    #        "epilogue",
    #        "title",
    #        "isbn",
    #        "prologue",
    #    ]
    #    chapters, specials = bb.order_chapters(orig_chapters, bb.SPECIAL_LIST)
    #    self.assertEqual(chapters, ["this", "that"])
    #    self.assertEqual(
    #        specials, ["title", "isbn", "prologue", "epilogue", "author"]
    #    )

    def test_chapter_header(self):
        lines = bb.lines_from_file(self.chapter_one_file)
        chapter_data = {
            "lines": lines,
        }
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(
            chapter_1.header, "[1429.180.0745] Casimir District, Saorsa"
        )

    def test_chapter_no_header(self):
        chapter_data = {"lines": ["one", "two", "three."], "has_header": False}
        chapter_1 = bb.Chapter(chapter_data)
        self.assertFalse(chapter_1.header)
        self.assertEqual(chapter_1.__str__(), "one\n\ntwo\n\nthree.")

    def test_scrub_line(self):
        chapter_data = {
            "lines": ["This sort        of thing shouldn't     pass!"],
            "has_header": False,
        }
        chapter_1 = bb.Chapter(chapter_data)
        expected = "This sort of thing shouldn't pass!"
        self.assertEqual(chapter_1.lines[0], expected)

    def test_set_type_no_header(self):
        chapter_data = {
            "lines": ["prologue", "one", "two", "three."],
            "has_header": False,
            "type": "prologue",
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "prologue")

    def test_set_type_with_header(self):
        chapter_data = {
            "type": "prologue",
            "lines": ["prologue", "some date", "one", "two", "three."],
            "has_header": True,
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "prologue")

    def test_set_type_chapter_with_header(self):
        chapter_data = {
            "lines": ["some date", "one", "two", "three."],
            "has_header": True,
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "chapter")

    def test_set_type_chapter_no_header(self):
        chapter_data = {"lines": ["one", "two", "three."], "has_header": False}
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "chapter")

    def test_chapter_has_report(self):
        chapter_data = {
            "lines": ["one.", "two?", "three!"],
            "has_header": False,
        }
        c = bb.Chapter(chapter_data)
        self.assertTrue(c.report)
        self.assertEqual(type(c.report_data), dict)
