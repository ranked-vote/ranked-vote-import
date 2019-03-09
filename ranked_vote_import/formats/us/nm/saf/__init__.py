from typing import List, Iterator, NamedTuple, Dict, DefaultDict

from ranked_vote.ballot import Ballot, UNDERVOTE, OVERVOTE, Candidate, Choice, WRITE_IN
from ranked_vote_import.base_normalizer import BaseNormalizer
from ranked_vote_import.base_reader import BaseReader

import zipfile
import csv
import io


class SantaFeNormalizer(BaseNormalizer):
    def normalize(self, ballot: Ballot) -> Ballot:
        normalized_choices = list()
        seen = set()
        for choice in ballot.choices:
            if choice == UNDERVOTE:
                # Santa Fe Code of Ordinances IX 9-1.15 (B) (12): If a voter skips a numerical ranking, the skipped
                # ranking will be ignored and the next indicated ranking on that ballot will be valid.
                pass
            elif choice == OVERVOTE:
                # Santa Fe Code of Ordinances IX 9-1.15 (B) (9): If a voter gives the same ranking to more than one (1)
                # candidate, the voter's rankings shall be counted in order of preference, stopping at the point where
                # the ballot contains the same ranking for more than one (1) candidate.
                normalized_choices.append(OVERVOTE)
                break
            elif choice not in seen:
                normalized_choices.append(choice)
                seen.add(choice)
        while len(normalized_choices) < len(ballot.choices):
            normalized_choices.append(UNDERVOTE)
        return Ballot(ballot.ballot_id, normalized_choices)


class SantaFeImporter(BaseReader):
    format_name = 'us_nm_saf'
    ballots: Iterator[Ballot]

    @property
    def candidates(self):
        return self._candidates

    def _read_ballots(self):
        data_filename, = self.filenames
        contest = self._params.get('contest')
        candidates = dict()
        contest_id = None
        num_ranks = None

        with zipfile.ZipFile(data_filename) as zf:
            with zf.open('csvFiles/ContestManifest.csv', 'r') as contest_manifest_fh:
                contest_manifest_text_fh = io.TextIOWrapper(contest_manifest_fh, 'utf-8')
                for row in csv.DictReader(contest_manifest_text_fh):
                    if row['Description'] == contest:
                        num_ranks = int(row['NumOfRanks']) + 1
                        contest_id = row['Id']
                        break

            with zf.open('csvFiles/CandidateManifest.csv', 'r') as candidate_manifest_fh:
                candidate_manifest_text_fh = io.TextIOWrapper(candidate_manifest_fh, 'utf-8')
                for row in csv.DictReader(candidate_manifest_text_fh):
                    if row['ContestId'] == contest_id:
                        candidates[row['Id']] = Candidate(row['Description'])
                self._candidates = [str(c) for c in candidates.values()]

            with zf.open('csvFiles/CvrExport.csv', 'r') as ballots_fh:
                ballots_text_fh = io.TextIOWrapper(ballots_fh, 'utf-8')
                for row in csv.DictReader(ballots_text_fh):
                    ballot_ranks = dict()
                    ballot_id = row['RecordId']

                    for ballot_contest in range(100):
                        key = f'Original/Cards/0/Contests/{ballot_contest}/Id'
                        if key not in row:
                            break

                        if row[key] == contest_id:

                            for mark in range(num_ranks):
                                candidate_key = f'Original/Cards/0/Contests/{ballot_contest}/Marks/{mark}/CandidateId'
                                rank_key = f'Original/Cards/0/Contests/{ballot_contest}/Marks/{mark}/Rank'
                                candidate_id = row[candidate_key]

                                if candidate_id == '':
                                    break

                                rank = int(row[rank_key]) - 1

                                candidate = candidates[candidate_id]

                                if rank in ballot_ranks:
                                    ballot_ranks[rank] = OVERVOTE
                                else:
                                    ballot_ranks[rank] = candidate

                            yield Ballot(ballot_id, [ballot_ranks.get(i, UNDERVOTE) for i in range(num_ranks)])
                            break

            return

    def read_next_ballot(self) -> Ballot:
        return next(self.ballots)

    def read(self):
        self.ballots = self._read_ballots()
