# name    :  test/test_book.py
# version :  0.0.1
# date    :  20231014
# author  :  Leam Hall
# desc    :  Test the book object

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
        self.config = bb.DEFAULT_CONFIG
        self.test_dir = tempfile.TemporaryDirectory()
        filenames = ["01_10.txt", "01_20.txt", "02_10.txt"]
        for f in filenames:
            in_file = os.path.join(self.test_dir.name, f)
            with open(in_file, "w") as in_f:
                in_f.write("{}\n\n".format(f))
                in_f.write("Something in {}.\n\n".format(f))

    def tearDown(self):
        self.test_dir.cleanup()

    def test_write_chapter_plain(self):
        builder = bb.BookBuilder()
        expected = "Line one.\n\nLine two.\n\n"
        result = builder.write_chapter(
            self.chapters[0],
            is_numbered = False,
            has_header = False,
        )
        self.assertEqual(result, expected)

    def test_book_builder(self):
        builder = bb.BookBuilder()
        self.assertEqual(builder.config["author"], "")
        self.assertEqual(builder.chapters, [])

    def test_book_builder_build(self):
        builder = bb.BookBuilder()
        result = builder.build()
        self.assertEqual(type(result), bb.Book)
        self.assertEqual(result.author, "")
        self.assertEqual(result.text, "")

    def test_book_with_config(self):
        builder = bb.BookBuilder(config={"author": "Leam Hall"})
        book = builder.build()
        self.assertEqual(book.author, "Leam Hall")

