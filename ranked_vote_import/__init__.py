from typing import Dict, Type
from ranked_vote_import.base_reader import BaseReader
from ranked_vote_import.base_normalizer import BaseNormalizer
from ranked_vote_import.formats.us.ca.sf import SanFranciscoImporter
from ranked_vote_import.formats.us.me import MaineImporter, MaineNormalizer

FORMATS = {
    'us_ca_sf': SanFranciscoImporter,
    'us_me': MaineImporter,
}  # type: Dict[str, Type[BaseReader]]

NORMALIZERS = {
    'us_me': MaineNormalizer
}  # type: Dict[str, Type[BaseNormalizer]]
