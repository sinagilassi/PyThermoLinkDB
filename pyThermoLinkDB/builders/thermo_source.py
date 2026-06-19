# import libs
import logging
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import Component, ComponentKey
# locals
from ..models.source import ModelSource, CustomSource
from .thermo_model_source import ThermoModelSource
from .thermo_custom_source import ThermoCustomSource

# NOTE: logger setup
logger = logging.getLogger(__name__)


class ThermoSource:
    """
    Class representing a thermodynamic data source, which can be either a model source or a custom source.
    """

    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            thermo_model_source: Optional[ThermoModelSource],
            thermo_custom_source: Optional[ThermoCustomSource],
            description: Optional[str] = None,
            model_source_key: str = 'model_source',
            custom_source_key: str = 'custom_source'
    ):
        # NOTE: set up attributes
        self.components = components
        self.component_key = component_key
        self.thermo_model_source = thermo_model_source
        self.thermo_custom_source = thermo_custom_source
        self.description = description

        # NOTE: source
        self._source = {
            model_source_key: {},
            custom_source_key: {}
        }

    # SECTION: Properties
    @property
    def source(self) -> Dict[str, Any]:
        return self._source

    # SECTION: Source Configuration
    # ! extract attributes from model source and custom source to populate the source dictionary
    def _extract_attributes(self):
        # NOTE: extract model source attributes
        if self.thermo_model_source:
            self._source['model_source'] = self.thermo_model_source.dynamic_attributes()
        else:
            logger.warning("No thermodynamic model source specified.")

        # NOTE: extract custom source attributes
        if self.thermo_custom_source:
            self._source['custom_source'] = self.thermo_custom_source.dynamic_attributes()
        else:
            logger.warning("No thermodynamic custom source specified.")

    # SECTION: Source Management & Utilities
