from abc import ABC, abstractmethod
from ranked_vote.ballot import Ballot, Candidate
from typing import List


class BaseReader(ABC):
    def __init__(self, files: List[str]):
        self.num_ballots = 0
        self.done_reading = False
        self.files = [{
            'name': filename,
            'sha1': ''
        } for filename in files]
        self.file_handles = [open(f) for f in files]

    def close_open_files(self):
        self.done_reading = True
        for fh in self.file_handles:
            fh.close()

    @property
    @abstractmethod
    def candidates(self) -> List[Candidate]:
        pass

    def get_metadata(self) -> dict:
        assert self.done_reading
        return {
            'num_ballots': self.num_ballots,
            'candidates': [str(c) for c in self.candidates],
            'files': self.files,
        }

    @abstractmethod
    def read_next_ballot(self) -> Ballot:
        pass

    def __next__(self) -> Ballot:
        assert not self.done_reading
        try:
            ballot = self.read_next_ballot()
            self.num_ballots += 1
            return ballot
        except StopIteration:
            self.close_open_files()
            raise

    def __iter__(self):
        return self
