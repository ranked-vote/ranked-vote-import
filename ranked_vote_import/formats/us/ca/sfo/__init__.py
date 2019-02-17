from collections import defaultdict

from itertools import groupby
from typing import List, Iterator, NamedTuple, Dict, DefaultDict

from ranked_vote.ballot import Ballot, UNDERVOTE, OVERVOTE, Candidate, Choice, WRITE_IN
from ranked_vote_import.base_reader import BaseReader
from ranked_vote_import.base_normalizer import BaseNormalizer


class SanFranciscoNormalizer(BaseNormalizer):
    def normalize(self, ballot: Ballot) -> Ballot:
        normalized_choices = list()
        seen = set()
        for choice in ballot.choices:
            if choice == UNDERVOTE:
                # San Francisco Charter 13.102.a: If a voter casts a ranked-choice ballot but skips a rank, the voter's
                # vote shall be transferred to that voter's next ranked choice.
                pass
            elif choice == OVERVOTE:
                # San Francisco Charter 13.102.a: If a ranked-choice ballot gives equal rank to two or more candidates,
                # the ballot shall be declared exhausted when such multiple rankings are reached.
                normalized_choices.append(OVERVOTE)
                break
            elif choice not in seen:
                normalized_choices.append(choice)
                seen.add(choice)
        while len(normalized_choices) < len(ballot.choices):
            normalized_choices.append(UNDERVOTE)
        return Ballot(ballot.ballot_id, normalized_choices)


class MasterRecord(NamedTuple):
    record_type: str
    record_id: int
    description: str
    list_order: int
    contest_id: int
    is_writein: bool
    is_provisional: bool

    @staticmethod
    def parse(record: str) -> 'MasterRecord':
        return MasterRecord(
            record_type=record[0:10].strip(),
            record_id=int(record[10:17]),
            description=record[17:67].strip(),
            list_order=int(record[67:74]),
            contest_id=int(record[74:81]),
            is_writein=record[81:82] == '1',
            is_provisional=int(record[82:83]) == 1
        )


class BallotRecord(NamedTuple):
    contest_id: int
    pref_voter_id: int
    serial_number: int
    tally_type_id: int
    precinct_id: int
    vote_rank: int
    candidate_id: int
    over_vote: bool
    under_vote: bool

    @staticmethod
    def parse(record: str) -> 'BallotRecord':
        return BallotRecord(
            contest_id=int(record[0:7]),
            pref_voter_id=int(record[7:16]),
            serial_number=int(record[16:23]),
            tally_type_id=int(record[23:26]),
            precinct_id=int(record[26:33]),
            vote_rank=int(record[33:36]),
            candidate_id=int(record[36:43]),
            over_vote=record[43:44] == '1',
            under_vote=record[44:45] == '1'
        )


class SanFranciscoImporter(BaseReader):
    format_name = 'us.ca.sfo'

    @property
    def candidates(self):
        return [str(c) for c in self._candidates[self._contest].values()]

    def _read_ballots(self, ballots: Iterator[BallotRecord]) -> Iterator[Ballot]:
        for (ballot_id, contest_id), ballot_records in groupby(ballots, lambda x: (x.pref_voter_id, x.contest_id)):
            choices = list()  # type: List[Choice]
            if 'contest' in self._params:
                if contest_id != self._params['contest']:
                    continue
            elif self._contest:
                assert self._contest == contest_id
            else:
                self._contest = contest_id

            for ballot_record in ballot_records:
                if ballot_record.under_vote:
                    choices.append(UNDERVOTE)
                elif ballot_record.over_vote:
                    choices.append(OVERVOTE)
                else:
                    choices.append(self._candidates[ballot_record.contest_id][ballot_record.candidate_id])
            yield Ballot(str(ballot_id), choices)

    def __init__(self, files: List[str], params: Dict):
        super(SanFranciscoImporter, self).__init__(files)

        master_lookup_fh, ballot_image_fh = self.file_handles

        self._params = params
        self._candidates = defaultdict(dict)  # type: DefaultDict[int, Dict[int, Choice]]
        self._contests = dict()  # type: Dict[int, str]
        self._contest = None
        self._done_reading = False
        self.num_ballots = 0

        for mr_string in master_lookup_fh:
            master_record = MasterRecord.parse(mr_string)

            if master_record.record_type == 'Contest':
                self._contests[master_record.record_id] = master_record.description
            elif master_record.record_type == 'Candidate':
                if master_record.is_writein:
                    self._candidates[master_record.contest_id][master_record.record_id] = WRITE_IN
                else:
                    self._candidates[master_record.contest_id][master_record.record_id] = Candidate.get(
                        master_record.description)

        self.ballots = self._read_ballots(BallotRecord.parse(b) for b in ballot_image_fh)

    def read_next_ballot(self) -> Ballot:
        return next(self.ballots)
