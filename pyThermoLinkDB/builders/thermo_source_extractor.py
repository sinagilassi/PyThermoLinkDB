"""Access helpers for built thermodynamic source mappings."""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, cast

import numpy as np
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import generate_component_references


# NOTE: set logger
logger = logging.getLogger(__name__)


class ThermoSourceExtractor:
    """
    Extract thermo source data from a ``ThermoSource`` mapping.
    """

    def __init__(
            self,
            thermo_source: Dict[str, Dict[str, Any]],
            component_key: ComponentKey
    ) -> None:
        # NOTE: set attributes
        self.thermo_source = thermo_source
        self.component_key = component_key

    # SECTION: reorder thermo source
    def reorder_x(
            self,
            value: Dict[str, Any],
            components: List[Component]
    ) -> Dict[str, Any]:
        """
        Return a copy of a thermo entry ordered by the requested components.

        Component-wise entries are built with values aligned to the source
        component order. This method rebuilds component IDs from ``components``
        and aligns ``src``, ``comp``, ``eq``, and vector ``value`` fields to
        that requested order without mutating the stored source.
        """
        # NOTE: no requested components means no reordering is needed
        if not components:
            return value

        # NOTE: generate requested component IDs using the source component key
        component_ids = self._component_ids(components=components)
        if not component_ids:
            return value

        # NOTE: shallow-copy the entry so the stored thermo source is unchanged
        reordered = copy.copy(value)

        # NOTE: reorder component-keyed mapping fields
        for item in ("src", "comp", "eq"):
            item_value = value.get(item)
            if isinstance(item_value, dict):
                reordered[item] = self._reorder_mapping(
                    value=item_value,
                    component_ids=component_ids
                )

        # NOTE: align vector-like values with the reordered component mapping
        comp_value = value.get("comp")
        entry_value = value.get("value")
        if isinstance(comp_value, dict):
            reordered["value"] = self._reorder_values(
                value=entry_value,
                comp=comp_value,
                component_ids=component_ids
            )

        return reordered

    # SECTION: access to thermo source
    # ! get all
    def get(
            self,
            source_name: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Dict[str, Any] | None:
        # NOTE: select source group
        source = self.thermo_source.get(source_name)
        if not isinstance(source, dict):
            logger.warning(f"Thermo source '{source_name}' not found.")
            return None

        # NOTE: select symbol entry
        value = source.get(symbol)
        if not isinstance(value, dict):
            logger.warning(
                f"Thermo symbol '{symbol}' not found in source '{source_name}'."
            )
            return None

        # NOTE: return a copied entry and reorder only when requested
        result = copy.copy(value)
        if components is not None:
            result = self.reorder_x(value=result, components=components)

        return result

    # ! get specific
    def get_item(
            self,
            source_type: str,
            symbol: str,
            item: str,
            components: List[Component] | None = None
    ) -> Any:
        # NOTE: extract the symbol entry first, then return the requested item
        value = self.get(
            source_name=source_type,
            symbol=symbol,
            components=components
        )
        if value is None:
            return None
        return value.get(item)

    # ! get component eq
    def get_comp_eq(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Any:
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="eq",
            components=components
        )

    # ! get component dt
    def get_comp_dt(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Any:
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="comp",
            components=components
        )

    # ! get constant value
    def get_const(self, source_type: str, symbol: str) -> Any:
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="value"
        )

    # SECTION: component id helpers
    def _component_ids(self, components: List[Component]) -> List[str]:
        # NOTE: use the shared settings helper to match builder component IDs
        component_references = generate_component_references(
            components=components,
            component_key=cast(ComponentKey, self.component_key)
        )
        component_ids = component_references.get("component_ids", [])
        if not isinstance(component_ids, list):
            return []
        return component_ids

    def _reorder_mapping(
            self,
            value: Dict[str, Any],
            component_ids: List[str]
    ) -> Dict[str, Any]:
        # NOTE: leave non-component mappings untouched
        if not any(component_id in value for component_id in component_ids):
            return value

        # NOTE: preserve only entries present in the requested component order
        return {
            component_id: value[component_id]
            for component_id in component_ids
            if component_id in value
        }

    def _reorder_values(
            self,
            value: Any,
            comp: Dict[str, Any],
            component_ids: List[str]
    ) -> Any:
        # NOTE: keep only components available in the component value mapping
        ordered_component_ids = [
            component_id
            for component_id in component_ids
            if component_id in comp
        ]
        if not ordered_component_ids:
            return value

        # NOTE: preserve the incoming vector container type where supported
        if isinstance(value, np.ndarray):
            return np.array([
                comp[component_id]
                for component_id in ordered_component_ids
            ])

        if isinstance(value, list):
            return [
                comp[component_id]
                for component_id in ordered_component_ids
            ]

        if isinstance(value, tuple):
            return tuple(
                comp[component_id]
                for component_id in ordered_component_ids
            )

        return value
