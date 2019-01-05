import pandas as pd
import re
from typing import List, Iterator, Dict

from ranked_vote.ballot import Ballot, UNDERVOTE, OVERVOTE, Candidate, WRITE_IN
from ranked_vote_import.base_normalizer import BaseNormalizer
from ranked_vote_import.base_reader import BaseReader


class MaineNormalizer(BaseNormalizer):
    def normalize(self, ballot: Ballot) -> Ballot:
        normalized_choices = list()
        seen = set()
        last_was_undervote = False
        for choice in ballot.choices:
            if choice == UNDERVOTE:
                if last_was_undervote:
                    normalized_choices.append(UNDERVOTE)
                    break
                last_was_undervote = True
            elif choice == OVERVOTE:
                normalized_choices.append(OVERVOTE)
                break
            elif choice not in seen:
                last_was_undervote = False
                normalized_choices.append(choice)
                seen.add(choice)
        while len(normalized_choices) < len(ballot.choices):
            normalized_choices.append(UNDERVOTE)
        return Ballot(ballot.ballot_id, normalized_choices)


class MaineImporter(BaseReader):
    format_name = 'us.me'

    def __init__(self, files: List[str]):
        super(MaineImporter, self).__init__(files)
        self.ballots = self._read_raw_ballots(files)
        self._candidates = dict()  # type: Dict[str, Candidate]

    @property
    def candidates(self):
        return list(self._candidates.values())

    @staticmethod
    def fix_string(name):
        return re.sub(r'^(?:DEM |REP )?(.+?), (.+?) ?(?: \(\d+\))?$', r'\2 \1', name)

    def read_next_ballot(self) -> Ballot:
        return next(self.ballots)

    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> (pd.DataFrame, List[str]):
        renamed = {'Cast Vote Record': 'VoteRecord'}
        n_choices = 0
        choice_columns = list()
        for c in df.columns:
            match = re.match(r'.+ (\d+)(?:st|nd|rd|th) Choice', c)
            if match:
                rank = int(match.groups()[0])
                assert rank == n_choices + 1
                n_choices = rank
                choice_col = 'choice_{}'.format(rank)
                renamed[c] = choice_col
                choice_columns.append(choice_col)
        return df.rename(columns=renamed), choice_columns

    def parse_ballot(self, choice_str):
        if choice_str == 'undervote':
            return UNDERVOTE
        elif choice_str == 'overvote':
            return OVERVOTE
        elif choice_str == 'Write-in':
            return WRITE_IN
        else:
            candidate = MaineImporter.fix_string(choice_str)
            if candidate not in self._candidates:
                self._candidates[candidate] = Candidate.get(candidate)
            return self._candidates[candidate]

    def _read_raw_ballots(self, files) -> Iterator[Ballot]:
        for filename in files:
            data = pd.read_excel(filename)
            data, choice_columns = MaineImporter.normalize_columns(data)

            for _, row in data.iterrows():
                yield Ballot(str(row['VoteRecord']), [
                    self.parse_ballot(row[c]) for c in choice_columns
                ])
