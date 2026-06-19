"""Non-mutating source selection and conflict inspection."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from .registry import _MISSING, ThermoSourceRegistry


class ThermoSourceResolver:
    """Select a value without combining model and custom source payloads."""

    # SECTION: Initialization
    def __init__(self, registry: ThermoSourceRegistry) -> None:
        self.registry = registry

    # SECTION: Symbol Resolution
    def resolve(
            self,
            symbol: str,
            category: str | None = None,
            precedence: Sequence[str] = ("custom", "model"),
            attribute: str = "value",
            default: Any = _MISSING,
    ) -> Any:
        # NOTE: Precedence controls selection only. The source mappings are
        # never updated, copied into one another, or merged.
        for source_type in precedence:
            if self.registry.has(symbol, category, source_type):
                return self.registry.get(
                    symbol, category, source_type, attribute, default
                )
        if default is not _MISSING:
            return default
        raise KeyError(f"Thermodynamic symbol '{symbol}' is not available.")

    # SECTION: Conflict Detection
    def find_conflicts(self) -> Dict[str, list[str]]:
        model = self.registry.get_source("model")
        custom = self.registry.get_source("custom")
        conflicts: Dict[str, list[str]] = {}
        for category in ("thermo_data", "thermo_equations", "thermo_constants"):
            overlap = set(model.get(category, {})) & set(custom.get(category, {}))
            if overlap:
                conflicts[category] = sorted(overlap)
        return conflicts
