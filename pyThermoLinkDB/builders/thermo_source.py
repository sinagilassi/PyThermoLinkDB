"""Container for built model and custom thermodynamic sources."""

from typing import List, Optional

from pythermodb_settings.models import Component, ComponentKey

from .thermo_custom_source import ThermoCustomSource
from .thermo_model_source import ThermoModelSource


class ThermoSource:
    """Hold model and custom thermodynamic sources with component metadata."""

    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            thermo_model_source: Optional[ThermoModelSource],
            thermo_custom_source: Optional[ThermoCustomSource],
            description: Optional[str] = None,
    ) -> None:
        self.components = components
        self.component_key = component_key
        self.thermo_model_source = thermo_model_source
        self.thermo_custom_source = thermo_custom_source
        self.description = description
