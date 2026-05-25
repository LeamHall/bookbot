import os
import tempfile
import unittest

import bookbot as bb


def make_section(text_lines, stype="chapter", has_header=False, number=0):
    """Helper: build a Section from a list of already-separated paragraph strings."""
    return bb.Section({
        "paragraphs": text_lines,
        "type": stype,
        "has_header": has_header,
        "number": number,
    })


class TestDocumentBuilder(unittest.TestCase):

    def test_empty_build_returns_document(self):
        doc = bb.DocumentBuilder().build()
        self.assertIsInstance(doc, bb.Document)

    def test_empty_build_author_is_empty(self):
        doc = bb.DocumentBuilder().build()
        self.assertEqual(doc.author, "")

    def test_empty_build_sections_is_empty(self):
        doc = bb.DocumentBuilder().build()
        self.assertEqual(doc.sections, [])

    def test_config_sets_author(self):
        doc = bb.DocumentBuilder(config={"author": "Leam Hall"}).build()
        self.assertEqual(doc.author, "Leam Hall")

    def test_config_sets_title(self):
        doc = bb.DocumentBuilder(config={"title": "First Contact"}).build()
        self.assertEqual(doc.title, "First Contact")

    def test_chapters_are_numbered(self):
        sections = [
            make_section(["Para one."]),
            make_section(["Para two."]),
        ]
        doc = bb.DocumentBuilder(sections=sections).build()
        self.assertEqual(doc.sections[0].number, 1)
        self.assertEqual(doc.sections[1].number, 2)

    def test_special_sections_not_numbered(self):
        sections = [make_section(["The prologue."], stype="prologue")]
        doc = bb.DocumentBuilder(sections=sections).build()
        self.assertEqual(doc.sections[0].number, 0)

    def test_chapter_label_in_novel(self):
        sections = [make_section(["Para."])]
        builder = bb.DocumentBuilder(config={"doc_type": "novel"}, sections=sections)
        doc = builder.build()
        self.assertIn("Chapter 1", doc.text)

    def test_section_label_in_report(self):
        sections = [make_section(["Para."])]
        builder = bb.DocumentBuilder(config={"doc_type": "report"}, sections=sections)
        doc = builder.build()
        self.assertIn("Section 1", doc.text)

    def test_step_label_in_sop(self):
        sections = [make_section(["Do this."])]
        builder = bb.DocumentBuilder(config={"doc_type": "sop"}, sections=sections)
        doc = builder.build()
        self.assertIn("Step 1", doc.text)

    def test_generic_no_label(self):
        sections = [make_section(["Content."])]
        builder = bb.DocumentBuilder(config={"doc_type": "generic"}, sections=sections)
        doc = builder.build()
        self.assertNotIn("Chapter", doc.text)
        self.assertNotIn("Section", doc.text)

    def test_section_break_between_chapters(self):
        sections = [make_section(["First."]), make_section(["Second."])]
        doc = bb.DocumentBuilder(sections=sections).build()
        self.assertIn("__section_break__", doc.text)

    def test_custom_section_break(self):
        sections = [make_section(["One."]), make_section(["Two."])]
        doc = bb.DocumentBuilder(
            config={"section_break": "\n---PAGE---\n"},
            sections=sections,
        ).build()
        self.assertIn("PAGE", doc.text)

    def test_section_title_included_when_present(self):
        s = bb.Section({
            "lines": ["My Header", "", "Paragraph."],
            "has_header": True,
        })
        doc = bb.DocumentBuilder(sections=[s]).build()
        self.assertIn("My Header", doc.text)

    def test_paragraph_text_in_output(self):
        sections = [make_section(["The hero walked slowly."])]
        doc = bb.DocumentBuilder(sections=sections).build()
        self.assertIn("The hero walked slowly.", doc.text)

    def test_scene_break_rendered_in_output(self):
        s = bb.Section({"paragraphs": ["Before.", bb.SCENE_BREAK, "After."]})
        doc = bb.DocumentBuilder(sections=[s]).build()
        self.assertIn("- - -", doc.text)

    def test_bookbuilder_alias_works(self):
        doc = bb.BookBuilder().build()
        self.assertIsInstance(doc, bb.Document)


class TestDocument(unittest.TestCase):

    def test_document_has_text_attribute(self):
        doc = bb.Document()
        self.assertEqual(doc.text, "")

    def test_document_has_sections_list(self):
        doc = bb.Document()
        self.assertIsInstance(doc.sections, list)

    def test_book_alias_is_document(self):
        doc = bb.Book()
        self.assertIsInstance(doc, bb.Document)


class TestDocumentFilename(unittest.TestCase):

    def test_spaces_become_underscores(self):
        self.assertEqual(bb.document_filename({"title": "My Great Book"}, "txt"),
                         "my_great_book.txt")

    def test_special_chars_removed(self):
        self.assertEqual(bb.document_filename({"title": "Al $$ Saves the () Universe"}, "txt"),
                         "al_saves_the_universe.txt")

    def test_lowercase(self):
        self.assertEqual(bb.document_filename({"title": "SHOUTING"}, "txt"), "shouting.txt")

    def test_extension_applied(self):
        result = bb.document_filename({"title": "Test"}, "epub")
        self.assertTrue(result.endswith(".epub"))

    def test_empty_title_returns_untitled(self):
        result = bb.document_filename({"title": ""}, "txt")
        self.assertIn("untitled", result)

    def test_book_filename_alias(self):
        result = bb.book_filename({"title": "Test Book"}, "txt")
        self.assertEqual(result, "test_book.txt")


class TestWriteDocument(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_file(self):
        doc = bb.Document()
        doc.text = "Hello world."
        config = {"title": "Test", "book_dir": self.tmp.name}
        bb.write_document(doc, config)
        expected = os.path.join(self.tmp.name, "test.txt")
        self.assertTrue(os.path.exists(expected))

    def test_file_contains_text(self):
        doc = bb.Document()
        doc.text = "The story begins."
        config = {"title": "My Story", "book_dir": self.tmp.name}
        bb.write_document(doc, config)
        path = os.path.join(self.tmp.name, "my_story.txt")
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("The story begins.", content)

    def test_write_book_alias(self):
        doc = bb.Document()
        doc.text = "Content."
        config = {"title": "Alias Test", "book_dir": self.tmp.name}
        bb.write_book(doc, config)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "alias_test.txt")))


class TestParseSections(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        for name, content in [
            ("01_10.txt", "First paragraph.\n\nSecond paragraph.\n"),
            ("01_20.txt", "Another chapter.\n"),
            ("prologue.txt", "Before the story.\n"),
        ]:
            path = os.path.join(self.tmp.name, name)
            with open(path, "w") as f:
                f.write(content)

    def tearDown(self):
        self.tmp.cleanup()

    def test_returns_two_tuple(self):
        files = bb.list_of_files(self.tmp.name)
        result = bb.parse_sections(files)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_sections_are_section_instances(self):
        files = bb.list_of_files(self.tmp.name)
        sections, _ = bb.parse_sections(files)
        for s in sections:
            self.assertIsInstance(s, bb.Section)

    def test_prologue_in_specials(self):
        files = bb.list_of_files(self.tmp.name)
        _, specials = bb.parse_sections(files)
        self.assertIsNotNone(specials.get("prologue"))
        self.assertIsInstance(specials["prologue"], bb.Section)

    def test_regular_chapters_not_in_specials(self):
        files = bb.list_of_files(self.tmp.name)
        sections, specials = bb.parse_sections(files)
        chapter_names = [s.filename for s in sections]
        self.assertIn("01_10.txt", chapter_names)

    def test_does_not_mutate_passed_specials(self):
        files = bb.list_of_files(self.tmp.name)
        original = {"prologue": None, "epilogue": None}
        before_id = id(original)
        bb.parse_sections(files, specials=original)
        self.assertEqual(id(original), before_id)

    def test_has_header_passed_to_sections(self):
        files = bb.list_of_files(self.tmp.name)
        sections, _ = bb.parse_sections(files, has_header=True)
        for s in sections:
            self.assertTrue(s._has_header)

    def test_parse_chapters_alias(self):
        files = bb.list_of_files(self.tmp.name)
        result = bb.parse_chapters(files)
        self.assertIsInstance(result, tuple)
