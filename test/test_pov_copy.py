import unittest
import os
import tempfile
import shutil
from bin.pov_copy import (
    parse_pov_list,
    find_chapters_for_character,
    copy_chapters,
)


class TestParsePovList(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pov_file = os.path.join(self.tmp, "pov_list.txt")
        with open(self.pov_file, "w") as f:
            f.write("01_05.txt, rachela, choi\n")
            f.write("01_10.txt, john, rachela, choi\n")
            f.write("03_30.txt, john\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_returns_dict(self):
        result = parse_pov_list(self.pov_file)
        self.assertIsInstance(result, dict)

    def test_keys_are_filenames(self):
        result = parse_pov_list(self.pov_file)
        self.assertIn("01_05.txt", result)
        self.assertIn("01_10.txt", result)

    def test_values_are_character_lists(self):
        result = parse_pov_list(self.pov_file)
        self.assertEqual(result["01_05.txt"], ["rachela", "choi"])
        self.assertEqual(result["03_30.txt"], ["john"])

    def test_single_character_line(self):
        result = parse_pov_list(self.pov_file)
        self.assertEqual(len(result["03_30.txt"]), 1)


class TestFindChaptersForCharacter(unittest.TestCase):

    def setUp(self):
        self.pov_data = {
            "01_05.txt": ["rachela", "choi"],
            "01_10.txt": ["john", "rachela", "choi"],
            "03_30.txt": ["john"],
            "03_60.txt": ["jack"],
        }

    def test_finds_chapters_with_character(self):
        result = find_chapters_for_character(self.pov_data, "rachela")
        self.assertIn("01_05.txt", result)
        self.assertIn("01_10.txt", result)

    def test_excludes_chapters_without_character(self):
        result = find_chapters_for_character(self.pov_data, "rachela")
        self.assertNotIn("03_30.txt", result)
        self.assertNotIn("03_60.txt", result)

    def test_character_not_in_any_chapter(self):
        result = find_chapters_for_character(self.pov_data, "nobody")
        self.assertEqual(result, [])

    def test_result_is_sorted(self):
        result = find_chapters_for_character(self.pov_data, "rachela")
        self.assertEqual(result, sorted(result))


class TestCopyChapters(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "chapters")
        self.dst = os.path.join(self.tmp, "output")
        os.makedirs(self.src)
        os.makedirs(self.dst)
        for name in ["01_05.txt", "01_10.txt", "03_30.txt"]:
            with open(os.path.join(self.src, name), "w") as f:
                f.write(f"content of {name}\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_copies_files_to_dest(self):
        copy_chapters(["01_05.txt", "01_10.txt"], self.src, self.dst)
        self.assertTrue(os.path.exists(os.path.join(self.dst, "01_05.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.dst, "01_10.txt")))

    def test_does_not_copy_excluded_files(self):
        copy_chapters(["01_05.txt"], self.src, self.dst)
        self.assertFalse(os.path.exists(os.path.join(self.dst, "03_30.txt")))

    def test_creates_dest_if_missing(self):
        new_dst = os.path.join(self.tmp, "new_output")
        copy_chapters(["01_05.txt"], self.src, new_dst)
        self.assertTrue(os.path.exists(os.path.join(new_dst, "01_05.txt")))

    def test_content_is_preserved(self):
        copy_chapters(["01_05.txt"], self.src, self.dst)
        with open(os.path.join(self.dst, "01_05.txt")) as f:
            self.assertEqual(f.read(), "content of 01_05.txt\n")


if __name__ == "__main__":
    unittest.main()
