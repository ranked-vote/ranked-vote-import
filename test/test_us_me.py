from unittest import TestCase

from ranked_vote.ballot import Ballot, Candidate, UNDERVOTE, OVERVOTE
from ranked_vote_import.formats.us.me import MaineNormalizer


class TestUSME(TestCase):
    def test_normalize_do_nothing(self):
        normalizer = MaineNormalizer()

        self.assertEqual(
            Ballot('332', [Candidate('A'), Candidate('B'), Candidate('C')]),
            normalizer.normalize(Ballot('332', [Candidate('A'), Candidate('B'), Candidate('C')]))
        )

    def test_normalize_stop_at_overvote(self):
        normalizer = MaineNormalizer()

        self.assertEqual(
            Ballot('332', [Candidate('A'), OVERVOTE, UNDERVOTE]),
            normalizer.normalize(Ballot('332', [Candidate('A'), OVERVOTE, Candidate('C')]))
        )

    def test_normalize_stop_at_double_undervote(self):
        normalizer = MaineNormalizer()

        self.assertEqual(
            Ballot('332', [Candidate('A'), Candidate('B'), Candidate('C'), UNDERVOTE, UNDERVOTE]),
            normalizer.normalize(Ballot('332', [Candidate('A'), UNDERVOTE, Candidate('B'), UNDERVOTE, Candidate('C')]))
        )

        self.assertEqual(
            Ballot('334', [Candidate('A'), UNDERVOTE, UNDERVOTE, UNDERVOTE]),
            normalizer.normalize(Ballot('334', [Candidate('A'), UNDERVOTE, UNDERVOTE, Candidate('C')]))
        )

    def test_remove_duplicate_candidate(self):
        normalizer = MaineNormalizer()

        self.assertEqual(
            Ballot('332', [Candidate('A'), Candidate('B'), Candidate('C'), UNDERVOTE, UNDERVOTE]),
            normalizer.normalize(Ballot('332', [Candidate('A'), Candidate('A'), Candidate('B'), Candidate('C'), Candidate('B')]))
        )