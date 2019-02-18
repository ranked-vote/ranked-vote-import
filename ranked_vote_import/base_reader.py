import hashlib
from abc import ABC, abstractmethod
from os.path import join
from typing import List, Dict

from ranked_vote.ballot import Ballot, Candidate


def get_file_sha1(filename):
    with open(filename, 'rb') as fh:
        h = hashlib.sha1()
        h.update(fh.read())
        return h.hexdigest()


class BaseReader(ABC):
    _params: Dict

    def __init__(self, files: List[str], params: Dict, base_dir: str = '.'):
        self._params = params
        self.num_ballots = 0
        self.done_reading = False
        self.filenames = [join(base_dir, f) for f in files]
        self.files = [{
            'name': filename,
            'sha1': get_file_sha1(filename)
        } for filename in self.filenames]
        self.read()

    @abstractmethod
    def read(self):
        pass

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
            'format': self.format_name,
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
            self.done_reading = True
            raise

    def __iter__(self):
        return self

    @property
    @abstractmethod
    def format_name(self) -> str:
        pass
