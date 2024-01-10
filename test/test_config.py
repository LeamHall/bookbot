# name    :  test/test_config.py
# version :  0.0.1
# date    :  20230928
# author  :  Leam Hall
# desc    :  Unittests for bookbot


import os.path
import tempfile
import unittest

import bookbot as bb


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, "book_config.toml")
        with open(self.config_file, "w") as f:
            f.write("title = 'Agent'\n")
            f.write("author = 'Leam Hall'\n")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_default_config(self):
        config = bb.read_config()
        self.assertEqual(config["author"], "")
        self.assertEqual(config["book_dir"], "book")
        self.assertEqual(config["reports_dir"], "reports")
        self.assertEqual(config["chapter_dir"], "chapters")
        self.assertEqual(config["title"], "")
        self.assertNotIn("stuff", config.keys())

    def test_read_config(self):
        _args = bb.parse_args(args=["-f", self.config_file])
        config = bb.read_config(_args)
        self.assertEqual(config["author"], "Leam Hall")
        self.assertEqual(config["book_dir"], "book")
        self.assertEqual(config["reports_dir"], "reports")
        self.assertEqual(config["chapter_dir"], "chapters")
        self.assertEqual(config["title"], "Agent")

    def test_setup_dirs_no_config(self):
        with self.assertRaises(TypeError):
            bb.setup_dirs()

    def test_setup_dirs_no_root_dir(self):
        _args = bb.parse_args(
            args=[
                "-f",
                self.config_file,
                "-b",
                "book",
                "-c",
                "chapters",
                "-r",
                "reports",
            ]
        )
        test_config = bb.read_config(_args)
        bb.setup_dirs(conf=test_config)
        dirs = ["book", "reports", "chapters"]
        for d in dirs:
            self.assertTrue(os.path.exists(d))
        for d in dirs:
            os.rmdir(d)

    def test_setup_dirs_pass(self):
        _args = bb.parse_args(
            args=[
                "-f",
                self.config_file,
                "-b",
                "book",
                "-c",
                "chapters",
                "-r",
                "reports",
            ]
        )
        test_config = bb.read_config(_args)
        bb.setup_dirs(conf=test_config, root_dir=self.test_dir.name)
        dirs = ["book", "reports", "chapters"]
        for d in dirs:
            test_dir = os.path.join(self.test_dir.name, d)
            self.assertTrue(os.path.exists(test_dir))

    def test_parse_args(self):
        _args = bb.parse_args(
            args=[
                "-f",
                self.config_file,
                "-b",
                "book",
                "-c",
                "chapters",
                "-r",
                "reports",
            ]
        )
        self.assertEqual(_args["file"], self.config_file)
        self.assertEqual(_args["author"], None)
        self.assertEqual(_args["book_dir"], "book")
        self.assertEqual(_args["chapter_dir"], "chapters")
        self.assertEqual(_args["has_header"], True)
        self.assertEqual(_args["section_break"], "\n__section_break__\n")
        self.assertEqual(_args["reports_dir"], "reports")
        self.assertEqual(_args["title"], None)
