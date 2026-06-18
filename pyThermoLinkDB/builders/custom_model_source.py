# import libs
import logging
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty,
    CustomProp
)
# locals

# NOTE: logger setup
logger = logging.getLogger(__name__)


class CustomModelSource:
    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            custom_source: Dict[str, Dict[str, CustomProp]],
            thermo_data: List[str],
            thermo_constants: List[str],
            component_references: Dict[str, Any],
            description: Optional[str] = None,
            **kwargs
    ):
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.custom_source = custom_source
        self.thermo_data = thermo_data
        self.thermo_constants = thermo_constants
        self.component_references = component_references
        self.description = description
