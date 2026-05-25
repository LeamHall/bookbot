import os
import tempfile
import unittest

import bookbot as bb


class TestLoadLines(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name, content):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_returns_list(self):
        path = self._write("a.txt", "hello\n")
        self.assertIsInstance(bb.load_lines(path), list)

    def test_preserves_blank_lines(self):
        path = self._write("a.txt", "para one\n\npara two\n")
        lines = bb.load_lines(path)
        self.assertIn("", lines)

    def test_strips_trailing_whitespace(self):
        path = self._write("a.txt", "hello   \n")
        lines = bb.load_lines(path)
        self.assertEqual(lines[0], "hello")

    def test_does_not_strip_leading_whitespace(self):
        path = self._write("a.txt", "  indented\n")
        lines = bb.load_lines(path)
        self.assertEqual(lines[0], "  indented")

    def test_handles_utf8_bom(self):
        path = os.path.join(self.tmp.name, "bom.txt")
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("first line\n")
        lines = bb.load_lines(path)
        self.assertEqual(lines[0], "first line")

    def test_empty_file_returns_empty_list(self):
        path = self._write("empty.txt", "")
        self.assertEqual(bb.load_lines(path), [])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            bb.load_lines(os.path.join(self.tmp.name, "no_such_file.txt"))

    def test_multiple_paragraphs_preserved(self):
        path = self._write("a.txt", "first\n\nsecond\n\nthird\n")
        lines = bb.load_lines(path)
        self.assertEqual(len(lines), 5)


class TestListOfFiles(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _touch(self, name):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w") as f:
            f.write("content\n")
        return path

    def test_returns_sorted_txt_files(self):
        self._touch("02.txt")
        self._touch("01.txt")
        result = bb.list_of_files(self.tmp.name)
        basenames = [os.path.basename(r) for r in result]
        self.assertEqual(basenames, ["01.txt", "02.txt"])

    def test_ignores_non_txt_files(self):
        self._touch("chapter.txt")
        self._touch("notes.md")
        self._touch("image.png")
        result = bb.list_of_files(self.tmp.name)
        self.assertEqual(len(result), 1)

    def test_does_not_recurse_into_subdirectories(self):
        self._touch("01.txt")
        subdir = os.path.join(self.tmp.name, "archive")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "old.txt"), "w") as f:
            f.write("old content\n")
        result = bb.list_of_files(self.tmp.name)
        self.assertEqual(len(result), 1)
        self.assertNotIn("archive", result[0])

    def test_raises_for_missing_directory(self):
        with self.assertRaises(FileNotFoundError):
            bb.list_of_files("/no/such/dir")

    def test_raises_for_empty_directory(self):
        with self.assertRaises(FileNotFoundError):
            bb.list_of_files(self.tmp.name)

    def test_returns_full_paths(self):
        self._touch("ch.txt")
        result = bb.list_of_files(self.tmp.name)
        self.assertTrue(os.path.isabs(result[0]))


class TestParseParagraphs(unittest.TestCase):

    def test_empty_input_returns_empty(self):
        self.assertEqual(bb.parse_paragraphs([]), [])

    def test_single_paragraph(self):
        result = bb.parse_paragraphs(["hello world"])
        self.assertEqual(result, ["hello world"])

    def test_two_paragraphs_separated_by_blank(self):
        result = bb.parse_paragraphs(["first", "", "second"])
        self.assertEqual(result, ["first", "second"])

    def test_leading_blank_lines_ignored(self):
        result = bb.parse_paragraphs(["", "", "text"])
        self.assertEqual(result, ["text"])

    def test_trailing_blank_lines_ignored(self):
        result = bb.parse_paragraphs(["text", "", ""])
        self.assertEqual(result, ["text"])

    def test_dash_scene_break_recognized(self):
        result = bb.parse_paragraphs(["para one", "", "- - -", "", "para two"])
        self.assertIn(bb.SCENE_BREAK, result)

    def test_star_scene_break_recognized(self):
        result = bb.parse_paragraphs(["para", "", "***", "", "para"])
        self.assertIn(bb.SCENE_BREAK, result)

    def test_spaced_star_break_recognized(self):
        result = bb.parse_paragraphs(["para", "", "* * *", "", "para"])
        self.assertIn(bb.SCENE_BREAK, result)

    def test_triple_dash_break_recognized(self):
        result = bb.parse_paragraphs(["para", "", "---", "", "para"])
        self.assertIn(bb.SCENE_BREAK, result)

    def test_scene_break_position_preserved(self):
        result = bb.parse_paragraphs(["first", "", "- - -", "", "second"])
        self.assertEqual(result[0], "first")
        self.assertEqual(result[1], bb.SCENE_BREAK)
        self.assertEqual(result[2], "second")

    def test_regular_prose_not_a_scene_break(self):
        result = bb.parse_paragraphs(["The hero dashed forward."])
        self.assertNotIn(bb.SCENE_BREAK, result)

    def test_multi_line_paragraph_joined(self):
        result = bb.parse_paragraphs(["line one", "line two", "line three"])
        self.assertEqual(result, ["line one line two line three"])

    def test_multi_line_then_blank_then_next(self):
        result = bb.parse_paragraphs(["line one", "line two", "", "next para"])
        self.assertEqual(result[0], "line one line two")
        self.assertEqual(result[1], "next para")

    def test_custom_scene_break_pattern(self):
        result = bb.parse_paragraphs(["text", "", "===", "", "text"], r"^=+$")
        self.assertIn(bb.SCENE_BREAK, result)

    def test_scene_break_adjacent_to_paragraphs(self):
        result = bb.parse_paragraphs(["before", "- - -", "after"])
        self.assertEqual(len(result), 3)

    def test_multiple_scene_breaks(self):
        lines = ["a", "", "- - -", "", "b", "", "- - -", "", "c"]
        result = bb.parse_paragraphs(lines)
        breaks = [r for r in result if r == bb.SCENE_BREAK]
        self.assertEqual(len(breaks), 2)
