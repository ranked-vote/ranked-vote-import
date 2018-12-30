from abc import ABC, abstractmethod
from ranked_vote.ballot import Ballot


class BaseNormalizer(ABC):
    @abstractmethod
    def normalize(self, ballot: Ballot) -> Ballot:
        pass
