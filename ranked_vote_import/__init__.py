from typing import Dict, Type
from ranked_vote_import.base_reader import BaseReader
from ranked_vote_import.formats.us.ca.sf import SanFranciscoImporter


FORMATS = {
    'us_ca_sf': SanFranciscoImporter,
} # type: Dict[str, Type[BaseReader]]
