"""Container for built model and custom thermodynamic sources."""

from typing import List, Optional, Dict, Any

from pythermodb_settings.models import Component, ComponentKey

from .thermo_custom_source import ThermoCustomSource
from .thermo_model_source import ThermoModelSource
from .thermo_source_validator import ValidationReport


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

    # SECTION: validation
    # NOTE: validation methods return None if the source is not built
    def validate_model_source(self) -> Optional[ValidationReport]:
        """Validate the built model source and return its report."""
        if self.thermo_model_source is None:
            return None
        return self.thermo_model_source.validate_thermo_src()

    # NOTE: validation methods return None if the source is not built
    def validate_custom_source(self) -> Optional[ValidationReport]:
        """Validate the built custom source and return its report."""
        if self.thermo_custom_source is None:
            return None
        return self.thermo_custom_source.validate_thermo_src()

    # NOTE: validation methods return None if the source is not built
    def validate_sources(self) -> Dict[str, Optional[ValidationReport]]:
        """Validate available model and custom sources."""
        return {
            "model_source": self.validate_model_source(),
            "custom_source": self.validate_custom_source(),
        }

    # NOTE: validation summary methods return None if the source is not built
    def model_validation_summary(self) -> Optional[Dict[str, Any]]:
        """Return the latest model-source validation summary."""
        if self.thermo_model_source is None:
            return None
        return self.thermo_model_source.validation_summary()

    # NOTE: validation summary methods return None if the source is not built
    def custom_validation_summary(self) -> Optional[Dict[str, Any]]:
        """Return the latest custom-source validation summary."""
        if self.thermo_custom_source is None:
            return None
        return self.thermo_custom_source.validation_summary()

    # NOTE: validation summary methods return None if the source is not built
    def validation_summary(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """Return validation summaries for model and custom sources."""
        return {
            "model_source": self.model_validation_summary(),
            "custom_source": self.custom_validation_summary(),
        }

    # SECTION: source validity and completeness
    # NOTE: validity and completeness methods return False if the source is not built
    def is_model_source_valid(self) -> bool:
        """Return whether the model source is valid."""
        return (
            self.thermo_model_source is not None
            and self.thermo_model_source.is_valid_build()
        )

    # NOTE: validity and completeness methods return False if the source is not built
    def is_custom_source_valid(self) -> bool:
        """Return whether the custom source is valid."""
        return (
            self.thermo_custom_source is not None
            and self.thermo_custom_source.is_valid_build()
        )

    # NOTE: validity and completeness methods return False if the source is not built
    def has_all_model_requested(self) -> bool:
        """Return whether all requested model-source symbols are available."""
        return (
            self.thermo_model_source is not None
            and self.thermo_model_source.has_all_requested()
        )

    # NOTE: validity and completeness methods return False if the source is not built
    def has_all_custom_requested(self) -> bool:
        """Return whether all requested custom-source symbols are available."""
        return (
            self.thermo_custom_source is not None
            and self.thermo_custom_source.has_all_requested()
        )

    # NOTE: validity and completeness methods return False if the source is not built
    def has_all_model_components(self) -> bool:
        """Return whether model-source data/equations cover all components."""
        return (
            self.thermo_model_source is not None
            and self.thermo_model_source.has_all_components()
        )

    # NOTE: validity and completeness methods return False if the source is not built
    def has_all_custom_components(self) -> bool:
        """Return whether custom-source data covers all components."""
        return (
            self.thermo_custom_source is not None
            and self.thermo_custom_source.has_all_components()
        )

    # SECTION: access to thermo source
    def get_all(self, source_name: str, symbol: str):
        pass

    def get_x(self, source_type: str, symbol: str, field: str):
        pass

    def get_equation(self, source_type: str, symbol: str):
        pass

    def get_constant(self, source_type: str, symbol: str):
        pass
