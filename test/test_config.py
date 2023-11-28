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
            f.write("title = Agent\n")
            f.write("author : Leam Hall\n")

    def tearDown(self):
        self.test_dir.cleanup()

    """
    def test_default_config(self):
        config = bb.read_config()
        self.assertEqual(config["author"], "")
        self.assertEqual(config["book_dir"], "book")
        self.assertEqual(config["reports_dir"], "reports")
        self.assertEqual(config["chapter_dir"], "chapters")
        self.assertEqual(config["title"], "")
        self.assertNotIn("stuff", config.keys())

    def test_read_config(self):
        args = bb.parse_args()
        config = bb.read_config(args)
        self.assertEqual(config["author"], "Leam Hall")
        self.assertEqual(config["book_dir"], "book")
        self.assertEqual(config["reports_dir"], "reports")
        self.assertEqual(config["chapter_dir"], "chapters")
        self.assertEqual(config["title"], "Agent")
    """

    def test_setup_dirs_no_config(self):
        with self.assertRaises(TypeError):
            bb.setup_dirs()

    def test_setup_dirs_no_root_dir(self):
        test_config = bb.read_config()
        bb.setup_dirs(conf=test_config)
        dirs = ["book", "reports", "chapters"]
        for d in dirs:
            self.assertTrue(os.path.exists(d))
        for d in dirs:
            os.rmdir(d)

    def test_setup_dirs_pass(self):
        test_config = bb.read_config()
        bb.setup_dirs(conf=test_config, root_dir=self.test_dir.name)
        dirs = ["book", "reports", "chapters"]
        for d in dirs:
            test_dir = os.path.join(self.test_dir.name, d)
            self.assertTrue(os.path.exists(test_dir))

    def test_parse_args(self):
        """
        Note that if unittest is called with a -f option, this test will
        fail, as it picks up whatever -f file is given to unittest.
        """
        args = bb.parse_args()
        self.assertEqual(args.file, "book_config.toml")
        self.assertEqual(args.author, None)
        self.assertEqual(args.book_dir, "book")
        self.assertEqual(args.chapter_dir, "chapters")
        self.assertEqual(args.has_header, True)
        self.assertEqual(args.page_break, "\n__page_break__\n")
        self.assertEqual(args.reports_dir, "reports")
        self.assertEqual(args.title, None)
