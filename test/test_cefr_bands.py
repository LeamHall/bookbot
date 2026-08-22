"""Tests for bin/cefr_bands.py.

Run with:  python3 -m unittest
"""

import io
import unittest

from bin import cefr_bands


class TestLoadWordCounts(unittest.TestCase):

    def test_parses_word_and_count(self):
        src = io.StringIO("the  3071\nchapter  91\n")
        self.assertEqual(
            cefr_bands.load_word_counts(src),
            {"the": 3071, "chapter": 91},
        )

    def test_skips_blank_lines(self):
        src = io.StringIO("the  3\n\n  \nchapter  1\n")
        self.assertEqual(cefr_bands.load_word_counts(src), {"the": 3, "chapter": 1})

    def test_lowercases_and_sums_duplicates(self):
        src = io.StringIO("The  3\nthe  4\n")
        self.assertEqual(cefr_bands.load_word_counts(src), {"the": 7})

    def test_rejects_line_without_count(self):
        src = io.StringIO("justoneword\n")
        with self.assertRaises(ValueError):
            cefr_bands.load_word_counts(src)


class TestLoadFrequencyRanks(unittest.TestCase):

    def test_rank_is_one_based_line_order(self):
        src = io.StringIO("you 100\ni 90\nthe 80\n")
        self.assertEqual(
            cefr_bands.load_frequency_ranks(src),
            {"you": 1, "i": 2, "the": 3},
        )

    def test_bare_word_per_line_also_works(self):
        src = io.StringIO("the\nof\nand\n")
        self.assertEqual(cefr_bands.load_frequency_ranks(src), {"the": 1, "of": 2, "and": 3})

    def test_first_occurrence_wins(self):
        src = io.StringIO("the 5\nthe 4\n")
        self.assertEqual(cefr_bands.load_frequency_ranks(src), {"the": 1})


class TestCandidateStems(unittest.TestCase):

    def test_includes_the_word_itself_first(self):
        self.assertEqual(next(iter(cefr_bands.candidate_stems("walked"))), "walked")

    def test_strips_regular_past_tense(self):
        self.assertIn("walk", list(cefr_bands.candidate_stems("walked")))

    def test_restores_silent_e(self):
        self.assertIn("smile", list(cefr_bands.candidate_stems("smiled")))

    def test_handles_ing(self):
        self.assertIn("look", list(cefr_bands.candidate_stems("looking")))

    def test_handles_doubled_consonant(self):
        self.assertIn("stop", list(cefr_bands.candidate_stems("stopped")))

    def test_handles_y_to_ies(self):
        self.assertIn("pony", list(cefr_bands.candidate_stems("ponies")))

    def test_does_not_shred_short_words(self):
        # 'was' must not be reduced to 'wa'
        self.assertNotIn("wa", list(cefr_bands.candidate_stems("was")))


class TestRankOf(unittest.TestCase):

    def setUp(self):
        self.ranks = {"walk": 50, "smile": 900, "the": 1}

    def test_direct_hit(self):
        self.assertEqual(cefr_bands.rank_of("the", self.ranks), 1)

    def test_hit_via_stem(self):
        self.assertEqual(cefr_bands.rank_of("walked", self.ranks), 50)
        self.assertEqual(cefr_bands.rank_of("smiling", self.ranks), 900)

    def test_miss_returns_none(self):
        self.assertIsNone(cefr_bands.rank_of("zzzyx", self.ranks))

    def test_returns_the_lowest_rank_among_word_and_stems(self):
        # A learner who knows 'point' and '-ed' knows 'pointed', so the burden
        # of the inflected form is the burden of its commonest family member,
        # not the rank the inflected form happens to hold in the corpus.
        ranks = {"pointed": 3000, "point": 400}
        self.assertEqual(cefr_bands.rank_of("pointed", ranks), 400)

    def test_keeps_its_own_rank_when_the_form_is_commoner_than_the_stem(self):
        # 'thugs' really is more frequent than 'thug' in the reference corpus.
        ranks = {"thugs": 8642, "thug": 9251}
        self.assertEqual(cefr_bands.rank_of("thugs", ranks), 8642)


class TestBandOf(unittest.TestCase):

    def test_finds_containing_band(self):
        bands = [(1, 1000), (1001, 2000)]
        self.assertEqual(cefr_bands.band_of(1, bands), (1, 1000))
        self.assertEqual(cefr_bands.band_of(1500, bands), (1001, 2000))

    def test_returns_none_when_above_all_bands(self):
        self.assertIsNone(cefr_bands.band_of(99999, [(1, 1000)]))

    def test_returns_none_for_none_rank(self):
        self.assertIsNone(cefr_bands.band_of(None, [(1, 1000)]))


class TestBasicStats(unittest.TestCase):

    def test_counts_tokens_and_types(self):
        stats = cefr_bands.basic_stats({"a": 3, "b": 1})
        self.assertEqual(stats["tokens"], 4)
        self.assertEqual(stats["types"], 2)

    def test_hapax_is_types_seen_once(self):
        stats = cefr_bands.basic_stats({"a": 3, "b": 1, "c": 1})
        self.assertEqual(stats["hapax_types"], 2)

    def test_type_token_ratio(self):
        stats = cefr_bands.basic_stats({"a": 3, "b": 1})
        self.assertAlmostEqual(stats["type_token_ratio"], 0.5)

    def test_average_word_length_is_token_weighted(self):
        # 'aa' x3 and 'bbbb' x1  ->  (2*3 + 4*1) / 4 = 2.5
        stats = cefr_bands.basic_stats({"aa": 3, "bbbb": 1})
        self.assertAlmostEqual(stats["avg_word_length"], 2.5)

    def test_empty_input_does_not_divide_by_zero(self):
        stats = cefr_bands.basic_stats({})
        self.assertEqual(stats["tokens"], 0)
        self.assertEqual(stats["type_token_ratio"], 0.0)


class TestCountSyllables(unittest.TestCase):

    def test_single_vowel_group(self):
        self.assertEqual(cefr_bands.count_syllables("cat"), 1)

    def test_two_vowel_groups(self):
        self.assertEqual(cefr_bands.count_syllables("rocket"), 2)

    def test_silent_final_e_not_counted(self):
        self.assertEqual(cefr_bands.count_syllables("smile"), 1)

    def test_never_returns_zero(self):
        self.assertEqual(cefr_bands.count_syllables("hmm"), 1)


class TestCoverageReport(unittest.TestCase):

    def setUp(self):
        self.ranks = {"the": 1, "walk": 500, "obscure": 4000}
        self.bands = [(1, 1000), (1001, 5000)]

    def test_tokens_land_in_the_right_bands(self):
        counts = {"the": 90, "walked": 5, "obscure": 5}
        rep = cefr_bands.coverage_report(counts, self.ranks, self.bands)
        self.assertEqual(rep["bands"][(1, 1000)]["tokens"], 95)
        self.assertEqual(rep["bands"][(1001, 5000)]["tokens"], 5)

    def test_cumulative_percent_accumulates(self):
        counts = {"the": 90, "obscure": 10}
        rep = cefr_bands.coverage_report(counts, self.ranks, self.bands)
        self.assertAlmostEqual(rep["bands"][(1, 1000)]["cum_percent"], 90.0)
        self.assertAlmostEqual(rep["bands"][(1001, 5000)]["cum_percent"], 100.0)

    def test_unranked_words_go_off_list(self):
        counts = {"the": 90, "zzzyx": 10}
        rep = cefr_bands.coverage_report(counts, self.ranks, self.bands)
        self.assertEqual(rep["off_list"]["tokens"], 10)
        self.assertIn(("zzzyx", 10), rep["off_list"]["words"])

    def test_excluded_words_are_removed_before_percentages(self):
        counts = {"the": 90, "wilbur": 10}
        rep = cefr_bands.coverage_report(counts, self.ranks, self.bands, exclude={"wilbur"})
        self.assertEqual(rep["core_tokens"], 90)
        self.assertEqual(rep["excluded_tokens"], 10)
        self.assertAlmostEqual(rep["bands"][(1, 1000)]["percent"], 100.0)


class TestLoadExclusions(unittest.TestCase):

    def test_reads_one_word_per_line(self):
        src = io.StringIO("wilbur\nakil\n")
        self.assertEqual(cefr_bands.load_exclusions(src), {"wilbur", "akil"})

    def test_ignores_blank_lines_and_full_line_comments(self):
        src = io.StringIO("# people\nwilbur\n\n   \nakil\n")
        self.assertEqual(cefr_bands.load_exclusions(src), {"wilbur", "akil"})

    def test_strips_trailing_inline_comment(self):
        src = io.StringIO("tryano   # car brand, behaves like a name\n")
        self.assertEqual(cefr_bands.load_exclusions(src), {"tryano"})

    def test_lowercases(self):
        src = io.StringIO("Wilbur\n")
        self.assertEqual(cefr_bands.load_exclusions(src), {"wilbur"})

    def test_indented_comment_is_still_a_comment(self):
        src = io.StringIO("   # indented note\nwilbur\n")
        self.assertEqual(cefr_bands.load_exclusions(src), {"wilbur"})


class TestDecisionList(unittest.TestCase):

    def setUp(self):
        self.ranks = {"the": 1, "walk": 500, "porch": 4000, "saber": 6000}
        self.counts = {"the": 100, "walked": 20, "porch": 22, "saber": 3, "zzzyx": 9}

    def test_returns_only_words_at_or_beyond_the_rank_floor(self):
        rows = cefr_bands.decision_list(self.counts, self.ranks, min_rank=3001, min_count=1)
        self.assertEqual({r[0] for r in rows}, {"porch", "saber", "zzzyx"})

    def test_applies_the_count_floor(self):
        rows = cefr_bands.decision_list(self.counts, self.ranks, min_rank=3001, min_count=5)
        self.assertEqual({r[0] for r in rows}, {"porch", "zzzyx"})

    def test_sorted_by_count_descending(self):
        rows = cefr_bands.decision_list(self.counts, self.ranks, min_rank=3001, min_count=1)
        self.assertEqual([r[1] for r in rows], [22, 9, 3])

    def test_rows_carry_word_count_and_rank(self):
        rows = cefr_bands.decision_list(self.counts, self.ranks, min_rank=3001, min_count=1)
        self.assertEqual(rows[0], ("porch", 22, 4000))

    def test_off_list_words_have_rank_none(self):
        rows = cefr_bands.decision_list(self.counts, self.ranks, min_rank=3001, min_count=1)
        self.assertIsNone(dict((r[0], r[2]) for r in rows)["zzzyx"])

    def test_excluded_words_are_dropped(self):
        rows = cefr_bands.decision_list(
            self.counts, self.ranks, min_rank=3001, min_count=1, exclude={"porch"}
        )
        self.assertNotIn("porch", {r[0] for r in rows})

    def test_ties_broken_alphabetically(self):
        counts = {"beta": 5, "alpha": 5}
        ranks = {}
        rows = cefr_bands.decision_list(counts, ranks, min_rank=3001, min_count=1)
        self.assertEqual([r[0] for r in rows], ["alpha", "beta"])


class TestVocabularyDemand(unittest.TestCase):

    def test_reports_band_where_threshold_is_crossed(self):
        # 90% in band one, 100% by band two; 95% target is met in band two
        counts = {"the": 90, "obscure": 10}
        ranks = {"the": 1, "obscure": 4000}
        bands = [(1, 1000), (1001, 5000)]
        rep = cefr_bands.coverage_report(counts, ranks, bands)
        self.assertEqual(cefr_bands.vocabulary_demand(rep, 0.95), 5000)

    def test_returns_none_when_threshold_never_met(self):
        counts = {"the": 90, "zzzyx": 10}
        ranks = {"the": 1}
        rep = cefr_bands.coverage_report(counts, ranks, [(1, 1000)])
        self.assertIsNone(cefr_bands.vocabulary_demand(rep, 0.95))


if __name__ == "__main__":
    unittest.main()
