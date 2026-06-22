"""Storage and lookup operations for combined thermodynamic sources."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Iterable

if TYPE_CHECKING:
    from ..thermo_custom_source import ThermoCustomSource
    from ..thermo_model_source import ThermoModelSource


_MISSING = object()


class ThermoSourceRegistry:
    """Assemble and query categorized thermodynamic source entries."""

    # SECTION: Category Configuration
    # NOTE: Public shorthand names are normalized to registry category keys.
    CATEGORY_ALIASES = {
        "data": "thermo_data",
        "equation": "thermo_equations",
        "equations": "thermo_equations",
        "constant": "thermo_constants",
        "constants": "thermo_constants",
        "thermo_data": "thermo_data",
        "thermo_equations": "thermo_equations",
        "thermo_constants": "thermo_constants",
    }

    # SECTION: Initialization
    def __init__(
            self,
            thermo_model_source: ThermoModelSource | None = None,
            thermo_custom_source: ThermoCustomSource | None = None,
            model_source_key: str = "model_source",
            custom_source_key: str = "custom_source",
    ) -> None:
        # NOTE: validate keys
        if not model_source_key or not custom_source_key:
            raise ValueError("Source keys must be non-empty strings.")
        if model_source_key == custom_source_key:
            raise ValueError("Model and custom source keys must be different.")

        # NOTE: set attributes
        self.model_source_key = model_source_key
        self.custom_source_key = custom_source_key
        self.thermo_model_source = thermo_model_source
        self.thermo_custom_source = thermo_custom_source

        # NOTE: initialize empty registry
        self._source: Dict[str, Dict[str, Any]] = {}

        # NOTE: build initial registry from sources
        self.refresh()

    # SECTION: Properties
    @property
    def source(self) -> Dict[str, Dict[str, Any]]:
        """Return the live combined source mapping."""
        return self._source

    @property
    def source_keys(self) -> tuple[str, str]:
        return self.model_source_key, self.custom_source_key

    # SECTION: Input Normalization
    def normalize_source_type(self, source_type: str) -> str:
        aliases = {
            "model": self.model_source_key,
            "model_source": self.model_source_key,
            self.model_source_key: self.model_source_key,
            "custom": self.custom_source_key,
            "custom_source": self.custom_source_key,
            self.custom_source_key: self.custom_source_key,
        }
        try:
            return aliases[source_type]
        except KeyError as exc:
            raise ValueError(
                f"Unknown source type '{source_type}'. Expected model/custom "
                f"or one of {self.source_keys}."
            ) from exc

    def normalize_category(self, category: str) -> str:
        try:
            return self.CATEGORY_ALIASES[category]
        except KeyError as exc:
            raise ValueError(
                f"Unknown thermodynamic category '{category}'.") from exc

    # SECTION: Registry Configuration
    @staticmethod
    def _source_entries(
            source: ThermoModelSource | ThermoCustomSource,
            equation_symbols: Iterable[str] | None = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Convert a flat ``thermo_src`` into the categorized registry view."""
        categories: Dict[str, Dict[str, Any]] = {
            "thermo_data": {},
            "thermo_equations": {},
            "thermo_constants": {},
        }
        category_config = [
            ("thermo_data", source.requested_data, ("src", "comp", "value")),
            ("thermo_constants", source.requested_constants, ("src", "value")),
        ]
        if equation_symbols is not None:
            category_config.insert(
                1,
                ("thermo_equations", equation_symbols, ("eq",)),
            )
        for category, symbols, fields in category_config:
            for symbol in symbols:
                entry = source.thermo_src.get(symbol)
                if entry is None:
                    continue
                categories[category][symbol] = {
                    f"{symbol}_{field}": entry[field]
                    for field in fields
                }
        return categories

    def refresh(self) -> None:
        """Rebuild the registry from the current source objects."""
        self._source = {
            self.model_source_key: (
                self._source_entries(
                    self.thermo_model_source,
                    equation_symbols=self.thermo_model_source.requested_equations,
                )
                if self.thermo_model_source is not None else {}
            ),
            self.custom_source_key: (
                self._source_entries(
                    self.thermo_custom_source,
                )
                if self.thermo_custom_source is not None else {}
            ),
        }

    def get_source(self, source_type: str) -> Dict[str, Any]:
        return self._source[self.normalize_source_type(source_type)]

    # SECTION: Entry Discovery
    def _categories(self, category: str | None) -> Iterable[str]:
        if category is not None:
            return (self.normalize_category(category),)
        return ("thermo_data", "thermo_equations", "thermo_constants")

    def find_entries(
            self,
            symbol: str,
            category: str | None = None,
            source_type: str | None = None,
    ) -> list[tuple[str, str, Dict[str, Any]]]:
        """Find matching ``(source key, category, attributes)`` entries."""
        source_keys = (
            (self.normalize_source_type(source_type),)
            if source_type is not None else self.source_keys
        )
        matches = []
        for source_key in source_keys:
            source = self._source[source_key]
            for category_key in self._categories(category):
                attributes = source.get(category_key, {}).get(symbol)
                if attributes is not None:
                    matches.append((source_key, category_key, attributes))
        return matches

    # SECTION: Value Lookup
    @staticmethod
    def _attribute_value(
            symbol: str,
            attributes: Dict[str, Any],
            attribute: str,
            default: Any,
    ) -> Any:
        attribute_name = (
            attribute if attribute.startswith(f"{symbol}_")
            else f"{symbol}_{attribute}"
        )
        if attribute_name in attributes:
            return attributes[attribute_name]
        if default is not _MISSING:
            return default
        raise KeyError(f"Attribute '{attribute_name}' is not available.")

    def get(
            self,
            symbol: str,
            category: str | None = None,
            source_type: str | None = None,
            attribute: str = "value",
            default: Any = _MISSING,
    ) -> Any:
        matches = self.find_entries(symbol, category, source_type)
        if not matches:
            if default is not _MISSING:
                return default
            raise KeyError(
                f"Thermodynamic symbol '{symbol}' is not available.")
        if len(matches) > 1:
            # NOTE: The registry never chooses a source implicitly. Precedence
            # is a policy decision handled by ThermoSourceResolver.
            locations = [f"{source}/{kind}" for source, kind, _ in matches]
            raise ValueError(
                f"Symbol '{symbol}' is ambiguous across {locations}; specify "
                "source_type/category or use resolve()."
            )
        return self._attribute_value(symbol, matches[0][2], attribute, default)

    def has(
            self,
            symbol: str,
            category: str | None = None,
            source_type: str | None = None,
    ) -> bool:
        return bool(self.find_entries(symbol, category, source_type))

    def list_symbols(
            self,
            category: str | None = None,
            source_type: str | None = None,
    ) -> list[str]:
        source_keys = (
            (self.normalize_source_type(source_type),)
            if source_type is not None else self.source_keys
        )
        symbols = {
            symbol
            for source_key in source_keys
            for category_key in self._categories(category)
            for symbol in self._source[source_key].get(category_key, {})
        }
        return sorted(symbols)

    def available(self) -> Dict[str, Dict[str, list[str]]]:
        return {
            source_key: {
                category: sorted(entries)
                for category, entries in source.items()
            }
            for source_key, source in self._source.items()
        }

    # SECTION: Component-Level Lookup
    def get_component(
            self,
            symbol: str,
            component_id: str,
            source_type: str | None = None,
            attribute: str = "comp",
            default: Any = _MISSING,
    ) -> Any:
        component_values = self.get(
            symbol=symbol,
            category="data",
            source_type=source_type,
            attribute=attribute,
            default=default,
        )
        if not isinstance(component_values, dict):
            if default is not _MISSING:
                return default
            raise TypeError(
                f"'{symbol}_{attribute}' is not component-indexed.")
        if component_id in component_values:
            return component_values[component_id]
        if default is not _MISSING:
            return default
        raise KeyError(
            f"Component '{component_id}' is unavailable for '{symbol}'.")

    def components_for(
            self,
            symbol: str,
            source_type: str | None = None,
    ) -> list[str]:
        values = self.get(
            symbol, category="data", source_type=source_type, attribute="comp"
        )
        return list(values) if isinstance(values, dict) else []

    # SECTION: Source Mutation
    # NOTE: Every mutation refreshes the derived registry immediately so the
    # public mapping cannot become stale.
    def set_model_source(self, source: ThermoModelSource | None) -> None:
        self.thermo_model_source = source
        self.refresh()

    def set_custom_source(self, source: ThermoCustomSource | None) -> None:
        self.thermo_custom_source = source
        self.refresh()

    def remove_source(self, source_type: str) -> None:
        source_key = self.normalize_source_type(source_type)
        if source_key == self.model_source_key:
            self.thermo_model_source = None
        else:
            self.thermo_custom_source = None
        self.refresh()

    def clear(self) -> None:
        self.thermo_model_source = None
        self.thermo_custom_source = None
        self.refresh()

    # SECTION: Serialization
    def to_dict(self, copy: bool = True) -> Dict[str, Any]:
        return deepcopy(self._source) if copy else self._source
