"""Validation and reporting for combined thermodynamic sources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Sequence

from .registry import ThermoSourceRegistry
from .resolver import ThermoSourceResolver


@dataclass(frozen=True)
class ThermoSourceValidationResult:
    """Structured result returned by :meth:`ThermoSourceValidator.validate`."""

    # SECTION: Validation State
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    missing: Dict[str, list[str]] = field(default_factory=dict)

    # SECTION: Boolean Conversion
    def __bool__(self) -> bool:
        return self.valid


class ThermoSourceValidator:
    """Check required symbols and component-level data completeness."""

    # SECTION: Initialization
    def __init__(
            self,
            registry: ThermoSourceRegistry,
            component_ids: Iterable[str] = (),
    ) -> None:
        self.registry = registry
        self.component_ids = tuple(component_ids)

    # SECTION: Required Symbol Checks
    def missing(
            self,
            required: Mapping[str, Sequence[str]],
    ) -> Dict[str, list[str]]:
        result: Dict[str, list[str]] = {}
        for category, symbols in required.items():
            normalized = self.registry.normalize_category(category)
            absent = [
                symbol for symbol in symbols
                if not self.registry.has(symbol, normalized)
            ]
            if absent:
                result[normalized] = absent
        return result

    # SECTION: Component Completeness
    def is_complete(
            self,
            symbol: str,
            source_type: str | None = None,
    ) -> bool:
        try:
            components = set(self.registry.components_for(symbol, source_type))
        except (KeyError, ValueError):
            return False
        return set(self.component_ids).issubset(components)

    # SECTION: Validation
    def validate(
            self,
            required: Mapping[str, Sequence[str]] | None = None,
            require_complete_components: bool = True,
    ) -> ThermoSourceValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        missing = self.missing(required or {})
        for category, symbols in missing.items():
            errors.append(f"Missing {category}: {', '.join(symbols)}")

        if not any(self.registry.get_source(key) for key in self.registry.source_keys):
            errors.append("No thermodynamic source is configured.")

        if require_complete_components and self.component_ids:
            for source_type in self.registry.source_keys:
                for symbol in self.registry.list_symbols("data", source_type):
                    if not self.is_complete(symbol, source_type):
                        errors.append(
                            f"Data symbol '{symbol}' is incomplete in '{source_type}'."
                        )

        # NOTE: Conflicts are warnings because the resolver can handle them
        # deterministically through its explicit precedence policy.
        conflicts = ThermoSourceResolver(self.registry).find_conflicts()
        for category, symbols in conflicts.items():
            warnings.append(f"Conflicting {category}: {', '.join(symbols)}")

        return ThermoSourceValidationResult(
            valid=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
            missing=missing,
        )

    # SECTION: Reporting
    def summary(self) -> Dict[str, object]:
        available = self.registry.available()
        return {
            "sources": {
                key: bool(self.registry.get_source(key))
                for key in self.registry.source_keys
            },
            "counts": {
                source: {
                    category: len(symbols)
                    for category, symbols in categories.items()
                }
                for source, categories in available.items()
            },
            "component_ids": list(self.component_ids),
            "conflicts": ThermoSourceResolver(self.registry).find_conflicts(),
        }
