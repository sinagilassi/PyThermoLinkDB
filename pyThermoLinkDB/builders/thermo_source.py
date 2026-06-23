"""Container for built model and custom thermodynamic sources."""

from typing import List, Optional, Dict, Any

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
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.thermo_model_source = thermo_model_source
        self.thermo_custom_source = thermo_custom_source
        self.description = description

        # NOTE: thermo source
        self._thermo_source: Dict[str, Dict[str, Any]] = {
            'model_source': {},
            'custom_source': {},
        }

    # SECTION: Properties
    @property
    def thermo_source(self) -> Dict[str, Dict[str, Any]]:
        """Return thermo source dictionary."""
        return self._thermo_source

    # SECTION: Thermo source configuration
    def _configure_thermo_source(self) -> None:
        """
        Configure thermo source dictionary.
        """
        # ! model source
        if self.thermo_model_source is not None:
            self._thermo_source["model_source"] = self.thermo_model_source.thermo_src

        # ! custom source
        if self.thermo_custom_source is not None:
            self._thermo_source["custom_source"] = self.thermo_custom_source.thermo_src
