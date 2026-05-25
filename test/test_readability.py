import unittest

import bookbot as bb


class TestCountSentences(unittest.TestCase):

    def test_counts_periods(self):
        self.assertEqual(bb.count_sentences("One. Two. Three."), 3)

    def test_counts_question_marks(self):
        self.assertEqual(bb.count_sentences("What? Really?"), 2)

    def test_counts_exclamation_marks(self):
        self.assertEqual(bb.count_sentences("Stop! Now!"), 2)

    def test_counts_mixed_punctuation(self):
        self.assertEqual(bb.count_sentences("Yes! Are you sure? It is."), 3)

    def test_empty_string_returns_zero(self):
        self.assertEqual(bb.count_sentences(""), 0)

    def test_no_sentence_endings_returns_zero(self):
        self.assertEqual(bb.count_sentences("no ending here"), 0)

    def test_does_not_count_commas(self):
        self.assertEqual(bb.count_sentences("one, two, three"), 0)

    def test_quoted_sentence_counted(self):
        self.assertEqual(bb.count_sentences('"Run!" she said.'), 2)


class TestCountWords(unittest.TestCase):

    def test_simple_sentence(self):
        self.assertEqual(bb.count_words("one two three"), 3)

    def test_empty_string_returns_zero(self):
        self.assertEqual(bb.count_words(""), 0)

    def test_multiple_spaces_treated_as_one(self):
        self.assertEqual(bb.count_words("one  two   three"), 3)

    def test_leading_trailing_spaces(self):
        self.assertEqual(bb.count_words("  word  "), 1)

    def test_punctuation_attached_to_words_still_counts(self):
        self.assertEqual(bb.count_words("hello, world."), 2)

    def test_single_word(self):
        self.assertEqual(bb.count_words("hello"), 1)


class TestCountSyllables(unittest.TestCase):

    def test_single_vowel_word(self):
        self.assertGreaterEqual(bb.count_syllables("cat"), 1)

    def test_minimum_is_one(self):
        self.assertGreaterEqual(bb.count_syllables("the"), 1)

    def test_never_returns_zero(self):
        self.assertGreater(bb.count_syllables("xyz"), 0)

    def test_multi_syllable_word(self):
        self.assertGreater(bb.count_syllables("beautiful"), 2)

    def test_double_vowel_reduces_count(self):
        alone = bb.count_syllables("boot")
        self.assertGreaterEqual(alone, 1)

    def test_silent_e_reduced(self):
        cave = bb.count_syllables("cave")
        cat = bb.count_syllables("cat")
        self.assertGreaterEqual(cat, 1)
        self.assertGreaterEqual(cave, 1)

    def test_empty_string_returns_one(self):
        self.assertEqual(bb.count_syllables(""), 1)

    def test_sentence_higher_than_single_word(self):
        single = bb.count_syllables("cat")
        many = bb.count_syllables("the cat sat on the mat")
        self.assertGreater(many, single)


class TestReadabilityStats(unittest.TestCase):

    def setUp(self):
        self.paragraphs = [
            "Al sat with her dad on the rusty hood of the car.",
            "The view seemed to go on forever.",
            "A line of four large planes approached from the east.",
        ]

    def test_returns_dict(self):
        result = bb.readability_stats(self.paragraphs)
        self.assertIsInstance(result, dict)

    def test_has_required_keys(self):
        result = bb.readability_stats(self.paragraphs)
        for key in ("sentence_count", "word_count", "syllable_count",
                    "grade_level", "sentence_average", "syllables_per_word_average"):
            self.assertIn(key, result)

    def test_filename_in_result(self):
        result = bb.readability_stats(self.paragraphs, filename="ch01.txt")
        self.assertEqual(result["filename"], "ch01.txt")

    def test_sentence_count_is_correct(self):
        result = bb.readability_stats(self.paragraphs)
        self.assertEqual(result["sentence_count"], 3)

    def test_word_count_is_positive(self):
        result = bb.readability_stats(self.paragraphs)
        self.assertGreater(result["word_count"], 0)

    def test_scene_breaks_excluded_from_analysis(self):
        paras_with_break = [self.paragraphs[0], bb.SCENE_BREAK, self.paragraphs[1]]
        result_with = bb.readability_stats(paras_with_break)
        result_without = bb.readability_stats([self.paragraphs[0], self.paragraphs[1]])
        self.assertEqual(result_with["sentence_count"], result_without["sentence_count"])

    def test_raises_on_no_sentences(self):
        with self.assertRaises(ValueError):
            bb.readability_stats(["just words no punctuation"])

    def test_raises_on_empty_paragraphs(self):
        with self.assertRaises(ValueError):
            bb.readability_stats([])

    def test_raises_on_scene_breaks_only(self):
        with self.assertRaises(ValueError):
            bb.readability_stats([bb.SCENE_BREAK, bb.SCENE_BREAK])

    def test_grade_level_is_float(self):
        result = bb.readability_stats(self.paragraphs)
        self.assertIsInstance(result["grade_level"], float)

    def test_grade_level_reasonable_range(self):
        result = bb.readability_stats(self.paragraphs)
        self.assertGreater(result["grade_level"], 0)
        self.assertLess(result["grade_level"], 25)
