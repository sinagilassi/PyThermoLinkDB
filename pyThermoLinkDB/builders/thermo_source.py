"""Combined model/custom thermodynamic source facade."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, Optional, Sequence

from pythermodb_settings.models import Component, ComponentKey

from .source_management import (
    ThermoSourceRegistry,
    ThermoSourceResolver,
    ThermoSourceValidationResult,
    ThermoSourceValidator,
)
from .thermo_custom_source import ThermoCustomSource
from .thermo_model_source import ThermoModelSource


class ThermoSource:
    """Facade over model and custom thermodynamic sources.

    Storage, precedence resolution, and validation are delegated to focused
    helper classes exposed through ``registry``, ``resolver``, and ``validator``.
    """

    # SECTION: Initialization
    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            thermo_model_source: Optional[ThermoModelSource],
            thermo_custom_source: Optional[ThermoCustomSource],
            description: Optional[str] = None,
            model_source_key: str = "model_source",
            custom_source_key: str = "custom_source",
    ) -> None:
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.description = description

        # LINK: initialize registry
        self.registry = ThermoSourceRegistry(
            thermo_model_source=thermo_model_source,
            thermo_custom_source=thermo_custom_source,
            model_source_key=model_source_key,
            custom_source_key=custom_source_key,
        )

        # LINK: initialize resolver
        self.resolver = ThermoSourceResolver(self.registry)

        # LINK: initialize validator
        self.validator = ThermoSourceValidator(
            self.registry,
            component_ids=self._component_ids(),
        )

    # SECTION: Internal Helpers
    def _component_ids(self) -> list[str]:
        for source in (
            self.registry.thermo_model_source,
            self.registry.thermo_custom_source,
        ):
            references = getattr(source, "component_references", None)
            if references:
                return list(references.get("component_ids", []))
        return []

    # SECTION: Properties
    @property
    def thermo_model_source(self) -> Optional[ThermoModelSource]:
        return self.registry.thermo_model_source

    @property
    def thermo_custom_source(self) -> Optional[ThermoCustomSource]:
        return self.registry.thermo_custom_source

    @property
    def source(self) -> Dict[str, Any]:
        return self.registry.source

    # SECTION: Source Configuration
    def refresh(self) -> None:
        """Refresh the categorized registry from both source objects."""
        self.registry.refresh()
        self.validator.component_ids = tuple(self._component_ids())

    def _extract_attributes(self) -> None:
        """Backward-compatible alias for :meth:`refresh`."""
        self.refresh()

    # SECTION: Registry Queries
    def get_source(self, source_type: str) -> Dict[str, Any]:
        return self.registry.get_source(source_type)

    def get(
            self,
            symbol: str,
            category: str | None = None,
            source_type: str | None = None,
            attribute: str = "value",
            default: Any = None,
    ) -> Any:
        return self.registry.get(
            symbol, category, source_type, attribute, default
        )

    def has(
            self,
            symbol: str,
            category: str | None = None,
            source_type: str | None = None,
    ) -> bool:
        return self.registry.has(symbol, category, source_type)

    def list_symbols(
            self,
            category: str | None = None,
            source_type: str | None = None,
    ) -> list[str]:
        return self.registry.list_symbols(category, source_type)

    def available(self) -> Dict[str, Dict[str, list[str]]]:
        return self.registry.available()

    # SECTION: Resolution and Conflicts
    def resolve(
            self,
            symbol: str,
            category: str | None = None,
            precedence: Sequence[str] = ("custom", "model"),
            attribute: str = "value",
            default: Any = None,
    ) -> Any:
        return self.resolver.resolve(
            symbol, category, precedence, attribute, default
        )

    def find_conflicts(self) -> Dict[str, list[str]]:
        return self.resolver.find_conflicts()

    # SECTION: Component-Level Queries
    def get_component(
            self,
            symbol: str,
            component_id: str,
            source_type: str | None = None,
            attribute: str = "comp",
            default: Any = None,
    ) -> Any:
        return self.registry.get_component(
            symbol, component_id, source_type, attribute, default
        )

    def components_for(
            self,
            symbol: str,
            source_type: str | None = None,
    ) -> list[str]:
        return self.registry.components_for(symbol, source_type)

    # SECTION: Validation and Reporting
    def is_complete(
            self,
            symbol: str,
            source_type: str | None = None,
    ) -> bool:
        return self.validator.is_complete(symbol, source_type)

    def missing(
            self,
            required: Mapping[str, Sequence[str]],
    ) -> Dict[str, list[str]]:
        return self.validator.missing(required)

    def validate(
            self,
            required: Mapping[str, Sequence[str]] | None = None,
            require_complete_components: bool = True,
    ) -> ThermoSourceValidationResult:
        return self.validator.validate(required, require_complete_components)

    def summary(self) -> Dict[str, object]:
        return self.validator.summary()

    # SECTION: Source Mutation
    def set_model_source(self, source: ThermoModelSource | None) -> None:
        self.registry.set_model_source(source)
        self.validator.component_ids = tuple(self._component_ids())

    def set_custom_source(self, source: ThermoCustomSource | None) -> None:
        self.registry.set_custom_source(source)
        self.validator.component_ids = tuple(self._component_ids())

    def remove_source(self, source_type: str) -> None:
        self.registry.remove_source(source_type)
        self.validator.component_ids = tuple(self._component_ids())

    def clear(self) -> None:
        self.registry.clear()
        self.validator.component_ids = ()

    # SECTION: Serialization and Copying
    def to_dict(self) -> Dict[str, Any]:
        """Return model and custom sources under their separate source keys."""
        return self.registry.to_dict()

    def copy(self) -> ThermoSource:
        return deepcopy(self)
