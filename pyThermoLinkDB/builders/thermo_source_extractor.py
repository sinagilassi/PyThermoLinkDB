# import libs
import logging
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import Component, ComponentKey
# locals


# NOTE: set logger
logger = logging.getLogger(__name__)


class ThermoSourceExtractor:
    """
    Extract thermo source data from ThermoSource object.
    """

    def __init__(
            self,
            thermo_source: Dict[str, Dict[str, Any]]
    ) -> None:
        # NOTE: set attributes
        self.thermo_source = thermo_source

    # SECTION: reorder thermo source
    def reorder_x(self, value: Any, components: List[Component]):
        pass

    # SECTION: access to thermo source

    def get(self, source_name: str, symbol: str):
        pass

    def get_item(self, source_type: str, symbol: str, item: str):
        pass

    def get_comp_eq(self, source_type: str, symbol: str):
        pass

    def get_comp_dt(self, source_type: str, symbol: str):
        pass

    def get_const(self, source_type: str, symbol: str):
        pass
