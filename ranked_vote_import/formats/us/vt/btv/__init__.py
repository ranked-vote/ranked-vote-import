import re
import zipfile
from typing import Iterator

from ranked_vote.ballot import Ballot, Candidate, OVERVOTE, UNDERVOTE
from ranked_vote_import.base_normalizer import BaseNormalizer
from ranked_vote_import.base_reader import BaseReader


class BurlingtonNormalizer(BaseNormalizer):
    def normalize(self, ballot: Ballot) -> Ballot:
        normalized_choices = list()
        seen = set()
        for choice in ballot.choices:
            if choice == UNDERVOTE:
                pass
            elif choice == OVERVOTE:
                normalized_choices.append(OVERVOTE)
                break
            elif choice not in seen:
                normalized_choices.append(choice)
                seen.add(choice)
        while len(normalized_choices) < len(ballot.choices):
            normalized_choices.append(UNDERVOTE)
        return Ballot(ballot.ballot_id, normalized_choices)


class BurlingtonImporter(BaseReader):
    format_name = 'us_vt_btv'
    ballots: Iterator[Ballot]

    @property
    def candidates(self):
        return self._candidates.values()

    def _read_ballots(self):
        data_filename, = self.filenames
        report_path = self._params.get('report_path')

        zf = zipfile.ZipFile(data_filename)
        report = zf.open(report_path).read().decode('ascii')

        self._candidates = dict()
        lines = iter(report.split('\r\n'))
        for line in lines:
            match = re.match(r'\.CANDIDATE ([^,]+), "([^"]+)"', line)
            if match:
                cid, cname = match.groups()
                self._candidates[cid] = Candidate(cname)
            elif line.startswith('.FINAL-PILE'):
                break

        for line in lines:
            match = re.match(r'([^,]+), \d\) (.+)', line)
            if match:
                ballot_id, votes = match.groups()
                yield Ballot(ballot_id, [self._candidates.get(cid, OVERVOTE) for cid in votes.split(',')])

    def read_next_ballot(self) -> Ballot:
        return next(self.ballots)

    def read(self):
        self.ballots = self._read_ballots()
