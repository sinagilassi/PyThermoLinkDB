"""Access helpers for built thermodynamic source mappings."""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, cast

import numpy as np
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty,
    CustomConstant,
    Mixture,
    MixtureKey,
)
from pythermodb_settings.utils import (
    generate_component_references,
    generate_mixture_references,
)
# locals
from ..thermo import EquationSourceCore


# NOTE: set logger
logger = logging.getLogger(__name__)


class ThermoSourceExtractor:
    """
    Read and reorder entries from a built thermodynamic source mapping.

    ``ThermoSourceExtractor`` is the read-only access layer used by
    :class:`pyThermoLinkDB.builders.thermo_source_hub.ThermoSourceHub`. It
    expects the canonical hub mapping produced by ``ThermoModelSource`` and
    ``ThermoCustomSource``:

    .. code-block:: python

        thermo_source = {
            "model_source": {
                "Tc": {
                    "src": {"water-l": CustomProperty(...)},
                    "comp": {"water-l": 647.1},
                    "value": numpy.array([647.1]),
                    "eq": None,
                    "mode": ["data"],
                },
            },
            "custom_source": {
                "R": {
                    "src": CustomConstant(...),
                    "comp": None,
                    "value": 8.31446261815324,
                    "eq": None,
                    "mode": ["constants"],
                },
            },
        }

    The extractor provides convenience methods for symbol discovery, whole-entry
    retrieval, field-level retrieval, component-wise data/equation access,
    matrix-data access, and constant access. When callers pass a component list,
    component-keyed mappings and vector-like values are returned in that
    requested component order without mutating the stored source mapping.

    Parameters
    ----------
    thermo_source : Dict[str, Dict[str, Any]]
        Canonical source mapping keyed first by source group, usually
        ``"model_source"`` and ``"custom_source"``, and then by thermodynamic
        symbol.
    component_key : ComponentKey
        Component identifier strategy used to regenerate component ids for
        reordering component-wise ``src``, ``comp``, ``eq``, and ``value``
        fields.
    mixture_key : MixtureKey, optional
        Mixture identifier strategy used for matrix-data lookup and reordering.
        Defaults to ``"Name"``.

    Notes
    -----
    Missing source groups, missing symbols, and unavailable fields are reported
    by returning ``None``, ``[]``, or ``{}`` depending on the method contract.
    The extractor logs warnings for missing source groups or symbols, but it
    does not validate build completeness. Validation is handled by
    ``ThermoSourceValidator`` before or after extraction.
    """

    def __init__(
            self,
            thermo_source: Dict[str, Dict[str, Any]],
            component_key: ComponentKey,
            mixture_key: MixtureKey = "Name",
    ) -> None:
        """
        Initialize the extractor with a canonical thermo source mapping.

        Parameters
        ----------
        thermo_source : Dict[str, Dict[str, Any]]
            Mapping containing source groups such as ``"model_source"`` and
            ``"custom_source"``. Each source group maps symbols to canonical
            entries with ``src``, ``comp``, ``value``, ``eq``, and ``mode``
            fields.
        component_key : ComponentKey
            Component id format used when reordering component-keyed entries.
        mixture_key : MixtureKey, optional
            Default mixture id format used when reordering matrix-data entries.
        """
        # NOTE: set attributes
        self.thermo_source = thermo_source
        self.component_key = component_key
        self.mixture_key: MixtureKey = mixture_key

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
        that requested order without mutating the stored source. Non-component
        fields such as ``mode`` are copied unchanged.
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
    def available_symbols(self, source_type: str) -> List[str]:
        """
        Return available symbol keys for a thermo source group.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.

        Returns
        -------
        List[str]
            Symbols available in the requested source group. An empty list is
            returned when the source group is missing or empty.
        """
        source: Dict[str, Any] | None = self.thermo_source.get(source_type)
        if not isinstance(source, dict):
            logger.warning(f"Thermo source '{source_type}' not found.")
            return []
        return list(source)

    def available_props(self, source_type: str) -> List[str]:
        """
        Return available property/symbol keys for a thermo source group.

        This is an alias for :meth:`available_symbols` for callers that use
        ``props`` terminology for thermodynamic property symbols.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.

        Returns
        -------
        List[str]
            Symbols available in the requested source group.
        """
        return self.available_symbols(source_type=source_type)

    def model_symbols(self) -> List[str]:
        """
        Return available symbols from the ``"model_source"`` group.

        Returns
        -------
        List[str]
            Model-source symbols in insertion order, or an empty list when the
            group is unavailable.
        """
        return self.available_symbols(source_type="model_source")

    def custom_symbols(self) -> List[str]:
        """
        Return available symbols from the ``"custom_source"`` group.

        Returns
        -------
        List[str]
            Custom-source symbols in insertion order, or an empty list when the
            group is unavailable.
        """
        return self.available_symbols(source_type="custom_source")

    def available_symbol_modes(self, source_type: str) -> Dict[str, List[str]]:
        """
        Return available symbols mapped to their source modes.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary keyed by symbol, with each value set to the symbol's
            ``mode`` list. Missing modes are returned as empty lists.
        """
        source: Dict[str, Any] | None = self.thermo_source.get(source_type)
        if not isinstance(source, dict):
            logger.warning(f"Thermo source '{source_type}' not found.")
            return {}

        symbol_modes: Dict[str, List[str]] = {}
        for symbol, entry in source.items():
            if not isinstance(entry, dict):
                symbol_modes[symbol] = []
                continue

            mode = entry.get("mode")
            if mode is None:
                symbol_modes[symbol] = []
            elif isinstance(mode, list):
                symbol_modes[symbol] = mode
            else:
                symbol_modes[symbol] = [str(mode)]

        return symbol_modes

    def model_symbol_modes(self) -> Dict[str, List[str]]:
        """
        Return model-source symbols mapped to their canonical modes.

        Returns
        -------
        Dict[str, List[str]]
            Mapping from symbol to mode list for the ``"model_source"`` group.
        """
        return self.available_symbol_modes(source_type="model_source")

    def custom_symbol_modes(self) -> Dict[str, List[str]]:
        """
        Return custom-source symbols mapped to their canonical modes.

        Returns
        -------
        Dict[str, List[str]]
            Mapping from symbol to mode list for the ``"custom_source"`` group.
        """
        return self.available_symbol_modes(source_type="custom_source")

    # ! get all
    def get(
            self,
            source_name: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Dict[str, Any] | None:
        """
        Return the full canonical thermo entry for one symbol.

        Parameters
        ----------
        source_name : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to retrieve, such as ``"Tc"``, ``"Cp_IG"``,
            ``"alpha"``, or ``"R"``.
        components : List[Component] | None, optional
            Optional component order. When provided, component-keyed ``src``,
            ``comp``, and ``eq`` fields are reordered to this component order.
            Vector-like ``value`` fields are also rebuilt from the reordered
            ``comp`` mapping when possible.

        Returns
        -------
        Dict[str, Any] | None
            A shallow copy of the canonical entry, optionally reordered. Returns
            ``None`` if the source group or symbol does not exist.

        Notes
        -----
        The stored ``thermo_source`` mapping is not mutated. Non-component
        fields, including ``mode`` and scalar constants, are copied unchanged.
        """
        # NOTE: select source group
        source: Dict[str, Any] | None = self.thermo_source.get(source_name)

        # >> check if source group is found
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
        """
        Get a specific item from a thermo source entry.

        Parameters
        ----------
        source_type : str
            The thermo source type (e.g., "model_source", "custom_source").
        symbol : str
            The symbol for which to retrieve the item such as "Tc", "Cp_IG", etc.
        item : str
            The specific item to retrieve from the thermo source entry (e.g., "value", "src", "comp", "eq", "mode").
        components : List[Component] | None, optional
            A list of components to reorder the component-wise data. If None, no reordering is performed.

        Returns
        -------
        Any
            The requested item from the thermo source entry, or None if not found.
        """
        # NOTE: extract the symbol entry first, then return the requested item
        value = self.get(
            source_name=source_type,
            symbol=symbol,
            components=components
        )
        if value is None:
            return None
        return value.get(item)

    # ! get component src
    def get_comp_src(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Dict[str, CustomProperty] | None:
        """
        Return component-keyed source objects for a data symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to retrieve.
        components : List[Component] | None, optional
            Optional component order for the returned mapping.

        Returns
        -------
        Dict[str, CustomProperty] | None
            Mapping from component id to ``CustomProperty`` source object, or
            ``None`` when unavailable.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="src",
            components=components
        )

    # ! get component eq
    def get_comp_eq(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Dict[str, EquationSourceCore] | None:
        """
        Return component-keyed equation source objects for an equation symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Equation symbol to retrieve.
        components : List[Component] | None, optional
            Optional component order for the returned mapping.

        Returns
        -------
        Dict[str, EquationSourceCore] | None
            Mapping from component id to executable equation source object, or
            ``None`` when unavailable.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="eq",
            components=components
        )

    # ! get component data (dict of values)
    def get_comp_dt(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> Dict[str, float] | None:
        """
        Return component-keyed numeric data values for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to retrieve.
        components : List[Component] | None, optional
            Optional component order for the returned mapping.

        Returns
        -------
        Dict[str, float] | None
            Mapping from component id to numeric value, or ``None`` when
            unavailable.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="comp",
            components=components
        )

    # ! get component values
    def get_comp_values(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None
    ) -> List[float] | None:
        """
        Return the vector-like value field for a component-wise symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to retrieve.
        components : List[Component] | None, optional
            Optional component order. When supplied and the entry has a
            component mapping, the returned vector is rebuilt in this order
            while preserving supported container types.

        Returns
        -------
        List[float] | numpy.ndarray | tuple | Any | None
            The entry ``value`` field. Although the annotation is
            ``List[float] | None`` for backward compatibility, current
            builders often store ``numpy.ndarray`` values.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="value",
            components=components
        )

    # ! get matrix data source
    def get_matrix_data_src(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None,
            mixtures: Optional[List[Mixture]] = None,
            mixture_key: Optional[MixtureKey] = None,
    ) -> Any:
        """
        Return matrix-data source objects for a matrix-data symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Matrix-data symbol to retrieve, for example ``"alpha"`` or
            ``"tau"``.
        components : List[Component] | None, optional
            Optional single-mixture component list. When provided, it is treated
            as one mixture and converted to a mixture id for filtering.
        mixtures : List[Mixture] | None, optional
            Optional list of mixture component lists used to select and order
            mixture-keyed matrix-data entries. Ignored when ``components`` is
            provided.
        mixture_key : MixtureKey | None, optional
            Mixture id strategy for this lookup. Defaults to the extractor's
            configured ``mixture_key``.

        Returns
        -------
        Any
            Matrix source object or mixture-keyed source mapping. Returns
            ``None`` if the symbol is unavailable or does not include
            ``"matrix_data"`` mode.
        """
        if not self.has_mode(
            source_type=source_type,
            symbol=symbol,
            mode="matrix_data",
        ):
            return None

        selected_mixture_key = cast(
            MixtureKey,
            self.mixture_key if mixture_key is None else mixture_key
        )
        matrix_src = self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="src",
            components=None
        )
        return self._reorder_mixture_mapping(
            value=matrix_src,
            components=components,
            mixtures=mixtures,
            mixture_key=selected_mixture_key,
        )

    # ! get matrix data value
    def get_matrix_data_value(
            self,
            source_type: str,
            symbol: str,
            components: List[Component] | None = None,
            mixtures: Optional[List[Mixture]] = None,
            mixture_key: Optional[MixtureKey] = None,
    ) -> Any:
        """
        Return the value field for a matrix-data symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Matrix-data symbol to retrieve.
        components : List[Component] | None, optional
            Optional single-mixture component list used to filter mixture-keyed
            values.
        mixtures : List[Mixture] | None, optional
            Optional mixture list used to filter and order mixture-keyed values.
        mixture_key : MixtureKey | None, optional
            Mixture id strategy for this lookup. Defaults to the extractor's
            configured ``mixture_key``.

        Returns
        -------
        Any
            Matrix-data value or mixture-keyed value mapping. Returns ``None``
            if the symbol is unavailable or does not include ``"matrix_data"``
            mode.

        Notes
        -----
        Model matrix data commonly stores callable/source objects in ``src``
        and leaves ``value`` as ``None``. Custom matrix data may store the raw
        matrix payload in ``value``.
        """
        if not self.has_mode(
            source_type=source_type,
            symbol=symbol,
            mode="matrix_data",
        ):
            return None

        selected_mixture_key = cast(
            MixtureKey,
            self.mixture_key if mixture_key is None else mixture_key
        )
        matrix_value = self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="value",
            components=None
        )
        return self._reorder_mixture_mapping(
            value=matrix_value,
            components=components,
            mixtures=mixtures,
            mixture_key=selected_mixture_key,
        )

    # ! get source mode
    def get_mode(self, source_type: str, symbol: str) -> List[str] | None:
        """
        Return the mode list for a symbol entry.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to inspect.

        Returns
        -------
        List[str] | None
            Mode list such as ``["data"]``, ``["equation"]``,
            ``["matrix_data"]``, or ``["constants"]``. Returns ``None`` when
            the symbol is unavailable.
        """
        mode = self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="mode"
        )
        if mode is None:
            return None
        if isinstance(mode, list):
            return mode
        return [str(mode)]

    # ! check source mode
    def has_mode(
            self,
            source_type: str,
            symbol: str,
            mode: str
    ) -> bool:
        """
        Check whether a symbol entry includes a requested mode.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to inspect.
        mode : str
            Mode to check, for example ``"data"``, ``"equation"``,
            ``"matrix_data"``, or ``"constants"``.

        Returns
        -------
        bool
            ``True`` when the symbol exists and its mode list contains
            ``mode``; otherwise ``False``.
        """
        modes = self.get_mode(
            source_type=source_type,
            symbol=symbol
        )
        return modes is not None and mode in modes

    # ! get constant value
    def get_const(self, source_type: str, symbol: str) -> Any:
        """
        Return a constant value from a source group.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Constant symbol to retrieve.

        Returns
        -------
        Any
            Constant value stored in the entry ``value`` field, or ``None``
            when unavailable.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="value"
        )

    # ! get constant source
    def get_const_src(
            self,
            source_type: str,
            symbol: str
    ) -> Optional[CustomConstant]:
        """
        Return the source object for a constant symbol.

        Parameters
        ----------
        source_type : str
            Source group name, usually ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Constant symbol to retrieve.

        Returns
        -------
        Optional[CustomConstant]
            Constant source object stored in the entry ``src`` field, or
            ``None`` when unavailable.
        """
        return self.get_item(
            source_type=source_type,
            symbol=symbol,
            item="src"
        )

    # SECTION: component id helpers
    def _component_ids(self, components: List[Component]) -> List[str]:
        """
        Build component ids using the extractor's configured component key.

        Parameters
        ----------
        components : List[Component]
            Components whose ids should be generated.

        Returns
        -------
        List[str]
            Component ids in the same order as ``components``. Returns an empty
            list when id generation does not produce a list.
        """
        # NOTE: use the shared settings helper to match builder component IDs
        component_references = generate_component_references(
            components=components,
            component_key=cast(ComponentKey, self.component_key)
        )
        component_ids = component_references.get("component_ids", [])
        if not isinstance(component_ids, list):
            return []
        return component_ids

    # SECTION: mixture id helpers
    def _mixture_ids(
            self,
            components: Optional[List[Component]] = None,
            mixtures: Optional[List[Mixture]] = None,
            mixture_key: MixtureKey = "Name",
    ) -> List[str]:
        """
        Build mixture ids for matrix-data filtering and ordering.

        Parameters
        ----------
        components : List[Component] | None, optional
            Components for one mixture. When supplied, this takes precedence
            over ``mixtures``.
        mixtures : List[Mixture] | None, optional
            Mixture component lists used when ``components`` is not supplied.
        mixture_key : MixtureKey, optional
            Mixture id strategy.

        Returns
        -------
        List[str]
            Mixture ids generated in requested order. Returns an empty list
            when no mixture information is available.
        """
        # NOTE: matrix data entries are keyed by mixture IDs, not component IDs
        selected_mixtures = mixtures if components is None else cast(
            List[Mixture],
            [components]
        )

        if not selected_mixtures:
            return []

        mixture_references = generate_mixture_references(
            mixtures=selected_mixtures,
            mixture_key=cast(MixtureKey, mixture_key)
        )
        mixture_ids = (
            mixture_references.get("mixture_ids")
            or mixture_references.get("mixture_id")
            or []
        )
        if isinstance(mixture_ids, str):
            return [mixture_ids]
        if not isinstance(mixture_ids, list):
            return []
        return mixture_ids

    def _reorder_mapping(
            self,
            value: Dict[str, Any],
            component_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Reorder a component-keyed mapping by requested component ids.

        Parameters
        ----------
        value : Dict[str, Any]
            Mapping that may be keyed by component ids.
        component_ids : List[str]
            Requested component id order.

        Returns
        -------
        Dict[str, Any]
            Reordered mapping containing only requested ids that exist in
            ``value``. If none of the requested ids are present, the original
            mapping is returned unchanged because it is likely not
            component-keyed.
        """
        # NOTE: leave non-component mappings untouched
        if not any(component_id in value for component_id in component_ids):
            return value

        # NOTE: preserve only entries present in the requested component order
        return {
            component_id: value[component_id]
            for component_id in component_ids
            if component_id in value
        }

    def _reorder_mixture_mapping(
            self,
            value: Any,
            components: Optional[List[Component]],
            mixtures: Optional[List[Mixture]],
            mixture_key: MixtureKey,
    ) -> Any:
        """
        Reorder or filter a mixture-keyed matrix-data mapping.

        Parameters
        ----------
        value : Any
            Matrix source or value. Only dictionaries are considered for
            mixture-id filtering.
        components : List[Component] | None
            Optional component list representing one mixture.
        mixtures : List[Mixture] | None
            Optional mixture list used when ``components`` is not supplied.
        mixture_key : MixtureKey
            Mixture id strategy used to generate requested mixture ids.

        Returns
        -------
        Any
            Reordered mixture-keyed dictionary when applicable. Non-dictionary
            values, unavailable mixture ids, and non-matching dictionaries are
            returned unchanged.
        """
        if not isinstance(value, dict):
            return value

        mixture_ids = self._mixture_ids(
            components=components,
            mixtures=mixtures,
            mixture_key=mixture_key,
        )
        if not mixture_ids:
            return value

        if not any(mixture_id in value for mixture_id in mixture_ids):
            return value

        return {
            mixture_id: value[mixture_id]
            for mixture_id in mixture_ids
            if mixture_id in value
        }

    def _reorder_values(
            self,
            value: Any,
            comp: Dict[str, Any],
            component_ids: List[str]
    ) -> Any:
        """
        Rebuild a vector-like value from an ordered component mapping.

        Parameters
        ----------
        value : Any
            Original ``value`` field from a thermo entry.
        comp : Dict[str, Any]
            Component-keyed numeric values.
        component_ids : List[str]
            Requested component id order.

        Returns
        -------
        Any
            Reordered values when ``value`` is a ``numpy.ndarray``, ``list``, or
            ``tuple``. Unsupported scalar or object values are returned
            unchanged.
        """
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
