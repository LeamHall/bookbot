import os
import tempfile
import unittest

import bookbot as bb


class TestSectionType(unittest.TestCase):

    def test_prologue_is_special(self):
        self.assertEqual(bb.section_type("prologue.txt"), "prologue")

    def test_epilogue_is_special(self):
        self.assertEqual(bb.section_type("epilogue.txt"), "epilogue")

    def test_isbn_is_special(self):
        self.assertEqual(bb.section_type("isbn.txt"), "isbn")

    def test_title_is_special(self):
        self.assertEqual(bb.section_type("title.txt"), "title")

    def test_afterward_is_special(self):
        self.assertEqual(bb.section_type("afterward.txt"), "afterward")

    def test_author_bio_is_special(self):
        self.assertEqual(bb.section_type("author_bio.txt"), "author_bio")

    def test_numbered_chapter_file_is_chapter(self):
        self.assertEqual(bb.section_type("01_05.txt"), "chapter")

    def test_arbitrary_name_is_chapter(self):
        self.assertEqual(bb.section_type("my_scene.txt"), "chapter")

    def test_works_with_full_path(self):
        self.assertEqual(bb.section_type("/some/dir/prologue.txt"), "prologue")

    def test_chapter_alias_works(self):
        self.assertEqual(bb.chapter_type("01_10.txt"), "chapter")


class TestSectionBasic(unittest.TestCase):

    def test_default_section_is_empty(self):
        s = bb.Section()
        self.assertEqual(s.paragraphs, [])
        self.assertIsNone(s.title)
        self.assertEqual(s.type, "chapter")

    def test_section_stores_type(self):
        s = bb.Section({"type": "prologue", "lines": []})
        self.assertEqual(s.type, "prologue")

    def test_section_stores_filename(self):
        s = bb.Section({"filename": "01_05.txt", "lines": []})
        self.assertEqual(s.filename, "01_05.txt")

    def test_section_stores_number(self):
        s = bb.Section({"number": 3, "lines": []})
        self.assertEqual(s.number, 3)

    def test_no_title_by_default(self):
        s = bb.Section({"lines": ["first", "", "second"], "has_header": False})
        self.assertIsNone(s.title)

    def test_title_extracted_when_has_header(self):
        s = bb.Section({"lines": ["My Title", "", "paragraph text."], "has_header": True})
        self.assertEqual(s.title, "My Title")

    def test_title_not_in_paragraphs(self):
        s = bb.Section({"lines": ["My Title", "", "paragraph text."], "has_header": True})
        self.assertNotIn("My Title", s.paragraphs)

    def test_no_title_extracted_without_has_header(self):
        s = bb.Section({"lines": ["My Title", "", "paragraph text."], "has_header": False})
        self.assertIn("My Title", s.paragraphs)

    def test_has_header_false_all_lines_are_paragraphs(self):
        s = bb.Section({"lines": ["one.", ""], "has_header": False})
        self.assertEqual(len(s.paragraphs), 1)

    def test_chapter_alias_is_section(self):
        c = bb.Chapter({"lines": ["para one.", ""], "has_header": False})
        self.assertIsInstance(c, bb.Section)


class TestSectionParagraphHandling(unittest.TestCase):

    def test_blank_lines_separate_paragraphs(self):
        s = bb.Section({"lines": ["first.", "", "second."], "has_header": False})
        self.assertEqual(len(s.paragraphs), 2)

    def test_scene_break_preserved_in_paragraphs(self):
        s = bb.Section({"lines": ["before.", "", "- - -", "", "after."], "has_header": False})
        self.assertIn(bb.SCENE_BREAK, s.paragraphs)

    def test_scene_break_not_counted_as_paragraph_text(self):
        s = bb.Section({"lines": ["before.", "", "- - -", "", "after."], "has_header": False})
        prose = [p for p in s.paragraphs if p != bb.SCENE_BREAK]
        self.assertEqual(len(prose), 2)

    def test_multiple_scene_breaks(self):
        lines = ["a.", "", "- - -", "", "b.", "", "***", "", "c."]
        s = bb.Section({"lines": lines, "has_header": False})
        breaks = [p for p in s.paragraphs if p == bb.SCENE_BREAK]
        self.assertEqual(len(breaks), 2)

    def test_whitespace_normalized_in_paragraphs(self):
        s = bb.Section({"lines": ["too  many   spaces."], "has_header": False})
        self.assertEqual(s.paragraphs[0], "too many spaces.")

    def test_empty_section_has_no_paragraphs(self):
        s = bb.Section({"lines": [], "has_header": False})
        self.assertEqual(s.paragraphs, [])

    def test_paragraphs_kwarg_accepted(self):
        s = bb.Section({"paragraphs": ["first.", "second."]})
        self.assertEqual(len(s.paragraphs), 2)

    def test_paragraphs_kwarg_takes_precedence_over_lines(self):
        s = bb.Section({
            "paragraphs": ["from paragraphs."],
            "lines": ["from lines.", "", "extra."],
        })
        self.assertEqual(len(s.paragraphs), 1)
        self.assertIn("from paragraphs.", s.paragraphs)


class TestSectionStats(unittest.TestCase):

    def test_section_with_prose_has_stats(self):
        s = bb.Section({"lines": ["Al sat. The view was great."], "has_header": False})
        self.assertIsNotNone(s.stats)

    def test_stats_is_dict(self):
        s = bb.Section({"lines": ["Al sat. The view was great."], "has_header": False})
        self.assertIsInstance(s.stats, dict)

    def test_section_without_prose_has_no_stats(self):
        s = bb.Section({"lines": [], "has_header": False})
        self.assertIsNone(s.stats)

    def test_stats_none_for_scene_break_only(self):
        s = bb.Section({"lines": ["- - -"], "has_header": False})
        self.assertIsNone(s.stats)

    def test_stats_contains_grade_level(self):
        s = bb.Section({"lines": ["Al sat. The view was great."], "has_header": False})
        self.assertIn("grade_level", s.stats)


class TestSectionStr(unittest.TestCase):

    def test_str_joins_paragraphs_with_double_newline(self):
        s = bb.Section({"lines": ["first.", "", "second."], "has_header": False})
        result = str(s)
        self.assertIn("first.", result)
        self.assertIn("second.", result)
        self.assertIn("\n\n", result)

    def test_scene_break_rendered_as_dashes(self):
        s = bb.Section({"lines": ["before.", "", "- - -", "", "after."], "has_header": False})
        result = str(s)
        self.assertIn("- - -", result)

    def test_empty_section_str_is_empty(self):
        s = bb.Section({"lines": []})
        self.assertEqual(str(s), "")
