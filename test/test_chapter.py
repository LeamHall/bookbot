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
            s1.write(
                "Al sat with her dad on the rusty hood of the family car. The view from Solomon Mountain seemed to go on forever. Twenty kilometers away and two kilometers down she could see her hometown. A light morning fog, and the quiet, raised up and comforted her.\n"
            )
            s1.write("\n")
            s1.write(
                "A staggered line of four large planes approached from the east.\n"
            )
            s1.write("\n\n\n")
            s1.write("\n\n\n")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_read_chapter(self):
        chapter_lines = bb.lines_from_file(self.chapter_one_file)
        self.assertTrue(type(chapter_lines), list)
        self.assertEqual(len(chapter_lines), 3)
        self.assertTrue(chapter_lines[0].startswith("["))

    def test_scrub_line(self):
        sample = "This sort        of thing shouldn't     pass!"
        expected = "This sort of thing shouldn't pass!"
        result = bb.scrub_line(sample)
        self.assertEqual(result, expected)

    def test_chapter_lines(self):
        lines = bb.lines_from_file(self.chapter_one_file)
        chapter_data = {
            "lines": lines,
        }
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(len(chapter_1._lines), 2)

    # def test_chapter_counts(self):
    #    lines = bb.lines_from_file(self.chapter_one_file)
    #    chapter_data = {
    #        "lines": lines,
    #    }
    #    chapter_1 = bb.Chapter(chapter_data)
    #    self.assertEqual(chapter_1.sentence_count, 5)
    #    self.assertEqual(chapter_1.word_count, 58)
    #    self.assertEqual(chapter_1.average_sentence_length, 12)

    def test_order_chapters(self):
        orig_chapters = [
            "author", "this", "that", "epilogue", "title", "isbn", "prologue"]
        chapters, specials = bb.order_chapters(
            orig_chapters, bb.SPECIAL_LIST)
        self.assertEqual(chapters, ["this", "that"])
        self.assertEqual(specials, [
            "title", "isbn", "prologue", "epilogue", "author"])

    def test_chapter_header(self):
        lines = bb.lines_from_file(self.chapter_one_file)
        chapter_data = {
            "lines": lines,
        }
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(
            chapter_1.header,
            "[1429.180.0745] Casimir District, Saorsa"
        )


