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
        result = builder.write_chapter(self.chapters[0])
        self.assertIn("Chapter", result)

    def test_book_builder(self):
        builder = bb.BookBuilder()
        self.assertEqual(builder.config["author"], "")
        self.assertEqual(builder.chapters, [])

    def test_book_builder_build(self):
        builder = bb.BookBuilder()
        result = builder.build()
        self.assertEqual(type(result), bb.Book)
        self.assertEqual(result.author, "")
        self.assertEqual(result.text, "\n\n")

    def test_book_with_config(self):
        builder = bb.BookBuilder(config={"author": "Leam Hall"})
        book = builder.build()
        self.assertEqual(book.author, "Leam Hall")

    def test_book_text(self):
        builder = bb.BookBuilder
        book = builder(chapters=self.chapters).build()
        self.assertGreater(len(book.text), 100)

    def test_book_filename(self):
        expected = "al_saves_the_universe.txt"
        config = {
            "title": "  Al $$ Saves the () Universe",
        }
        result = bb.book_filename(config, "txt")
        self.assertEqual(result, expected)

    def test_write_book(self):
        config = {
            "title": "  Al Saves the () Universe",
            "book_dir": self.test_dir.name,
        }
        builder = bb.BookBuilder
        book = builder(chapters=self.chapters).build()
        expected_file = os.path.join(
            self.test_dir.name, "al_saves_the_universe.txt"
        )
        bb.write_book(book, config)
        self.assertTrue(os.path.exists(expected_file))
        with open(expected_file, "r") as ef:
            data = ef.read()
        self.assertIn("unu", data)
