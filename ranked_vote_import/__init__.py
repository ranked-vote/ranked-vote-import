from typing import Dict, Type

from ranked_vote_import.base_normalizer import BaseNormalizer
from ranked_vote_import.base_reader import BaseReader
from ranked_vote_import.formats.us.ca.sfo import SanFranciscoImporter, SanFranciscoNormalizer
from ranked_vote_import.formats.us.me import MaineImporter, MaineNormalizer
from ranked_vote_import.formats.us.nm.saf import SantaFeImporter, SantaFeNormalizer

FORMATS = {
    'us_ca_sfo': SanFranciscoImporter,
    'us_me': MaineImporter,
    'us_nm_saf': SantaFeImporter,
}  # type: Dict[str, Type[BaseReader]]

NORMALIZERS = {
    'us_ca_sfo': SanFranciscoNormalizer,
    'us_me': MaineNormalizer,
    'us_nm_saf': SantaFeNormalizer,
}  # type: Dict[str, Type[BaseNormalizer]]
