import os.path
import tempfile
import unittest

import bookbot as bb


class TestChapter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.chapter_one_file = os.path.join(self.test_dir.name, "chapter_one.txt")
        with open(self.chapter_one_file, "w") as s1:
            s1.write("[1429.180.0745] Casimir District, Saorsa\n\n")
            s1.write("Al sat with her dad on the rusty hood of the car. ")
            s1.write("The view from Solomon Mountain seemed to go on and on. ")
            s1.write("Twenty kilometers away and two klicks down she could ")
            s1.write("see her hometown. A light morning fog, and the quiet, ")
            s1.write("raised up and comforted her.\n")
            s1.write("\n")
            s1.write("A line of four large planes approached from the east.\n")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_lines_preserves_blanks(self):
        lines = bb.load_lines(self.chapter_one_file)
        self.assertIn("", lines)

    def test_load_lines_returns_list(self):
        lines = bb.load_lines(self.chapter_one_file)
        self.assertIsInstance(lines, list)

    def test_chapter_parsed_paragraphs(self):
        lines = bb.load_lines(self.chapter_one_file)
        chapter_data = {"lines": lines, "has_header": True}
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(len(chapter_1.paragraphs), 2)

    def test_chapter_header(self):
        lines = bb.load_lines(self.chapter_one_file)
        chapter_data = {"lines": lines, "has_header": True}
        chapter_1 = bb.Chapter(chapter_data)
        self.assertEqual(chapter_1.title, "[1429.180.0745] Casimir District, Saorsa")

    def test_chapter_header_via_compat_property(self):
        lines = bb.load_lines(self.chapter_one_file)
        chapter_1 = bb.Chapter({"lines": lines, "has_header": True})
        self.assertEqual(chapter_1.header, "[1429.180.0745] Casimir District, Saorsa")

    def test_chapter_no_header(self):
        chapter_data = {"paragraphs": ["one.", "two.", "three."], "has_header": False}
        chapter_1 = bb.Chapter(chapter_data)
        self.assertIsNone(chapter_1.title)
        self.assertIn("one.", str(chapter_1))
        self.assertIn("two.", str(chapter_1))
        self.assertIn("three.", str(chapter_1))

    def test_scrub_line(self):
        chapter_data = {
            "lines": ["This sort        of thing shouldn't     pass!"],
            "has_header": False,
        }
        chapter_1 = bb.Chapter(chapter_data)
        expected = "This sort of thing shouldn't pass!"
        self.assertEqual(chapter_1.paragraphs[0], expected)

    def test_set_type_no_header(self):
        chapter_data = {
            "paragraphs": ["one.", "two.", "three."],
            "has_header": False,
            "type": "prologue",
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "prologue")

    def test_set_type_with_header(self):
        chapter_data = {
            "type": "prologue",
            "paragraphs": ["some date", "one.", "two.", "three."],
            "has_header": True,
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "prologue")

    def test_set_type_chapter_with_header(self):
        chapter_data = {
            "paragraphs": ["some date", "one.", "two.", "three."],
            "has_header": True,
        }
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "chapter")

    def test_set_type_chapter_no_header(self):
        chapter_data = {"paragraphs": ["one.", "two.", "three."], "has_header": False}
        c = bb.Chapter(chapter_data)
        self.assertEqual(c.type, "chapter")

    def test_chapter_has_stats(self):
        chapter_data = {
            "paragraphs": ["one.", "two?", "three!"],
            "has_header": False,
        }
        c = bb.Chapter(chapter_data)
        self.assertIsNotNone(c.stats)
        self.assertIsInstance(c.stats, dict)

    def test_chapter_report_compat_property(self):
        chapter_data = {
            "paragraphs": ["one.", "two?", "three!"],
            "has_header": False,
        }
        c = bb.Chapter(chapter_data)
        self.assertIsNotNone(c.report)
        self.assertIsInstance(c.report_data, dict)
