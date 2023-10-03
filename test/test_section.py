# name    :  test/test_bookbot.py
# version :  0.0.1
# date    :  20230928
# author  :  Leam Hall
# desc    :  Unittests for bookbot


import os.path
import tempfile
import unittest

import bookbot as bb


class TestSection(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.section_one_file = os.path.join(self.test_dir.name, "section_one")
        with open(self.section_one_file, "w") as s1:
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

    def test_read_section(self):
        section_lines = bb.lines_from_file(self.section_one_file)
        self.assertTrue(type(section_lines), list)
        self.assertEqual(len(section_lines), 3)
        self.assertTrue(section_lines[0].startswith("["))

    def test_scrub_line(self):
        sample = "This sort        of thing shouldn't     pass!"
        expected = "This sort of thing shouldn't pass!"
        result = bb.scrub_line(sample)
        self.assertEqual(result, expected)

    def test_section_lines(self):
        lines = bb.lines_from_file(self.section_one_file)
        section_data = {
            "lines": lines,
        }
        section_1 = bb.Section(section_data)
        self.assertEqual(len(section_1._lines), 3)

    def test_section_counts(self):
        lines = bb.lines_from_file(self.section_one_file)
        section_data = {
            "lines": lines,
        }
        section_1 = bb.Section(section_data)
        # This is currently +2 because of the header line.
        self.assertEqual(section_1.sentence_count, 7)
        self.assertEqual(section_1.word_count, 62)
        self.assertEqual(section_1.average_sentence_length, 9)
