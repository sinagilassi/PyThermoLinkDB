"""Configured registry for extracting thermo source entries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pythermodb_settings.models import Component

from ..models import SourceConfig, ThermoSourceHubConfig


class ThermoSourceRegistry:
    """
    Extract configured source records from a thermodynamic source hub.

    ``ThermoSourceRegistry`` resolves a ``ThermoSourceHubConfig`` against a
    built source hub. Each configured symbol can select independent source
    groups for property data, equations, and constants.
    """

    def __init__(
            self,
            thermo_src: Any,
            thermo_source_hub_config: ThermoSourceHubConfig,
    ) -> None:
        self.thermo_src = thermo_src
        self.thermo_source_hub_config = thermo_source_hub_config
        self._registry: Dict[str, Dict[str, Any]] = {}

    @property
    def registry(self) -> Dict[str, Dict[str, Any]]:
        """Return the latest extracted registry, building it on first access."""
        if not self._registry:
            return self.extract_sources()
        return self._registry

    def extract_sources(
            self,
            components: Optional[List[Component]] = None,
            include_missing: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract configured source records for all configured symbols.

        Parameters
        ----------
        components : Optional[List[Component]], optional
            Optional component order for component-wise source entries.
        include_missing : bool, optional
            When ``True``, include keys with ``None`` values for configured
            fields that are not available in the selected source group.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Registry keyed by symbol. Each symbol may contain ``src`` and
            ``eq`` entries. ``src`` is used for data and constant sources.
        """
        registry: Dict[str, Dict[str, Any]] = {}

        for symbol, source_config in self.thermo_source_hub_config.items():
            registry[symbol] = self.extract_source(
                symbol=symbol,
                source_config=source_config,
                components=components,
                include_missing=include_missing,
            )

        self._registry = registry
        return registry

    def extract_source(
            self,
            symbol: str,
            source_config: Optional[SourceConfig] = None,
            components: Optional[List[Component]] = None,
            include_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract configured source records for one symbol.

        Parameters
        ----------
        symbol : str
            Thermodynamic symbol to extract.
        source_config : Optional[SourceConfig], optional
            Source selection for the symbol. Defaults to ``SourceConfig()``.
        components : Optional[List[Component]], optional
            Optional component order for component-wise source entries.
        include_missing : bool, optional
            When ``True``, include missing fields as ``None``.

        Returns
        -------
        Dict[str, Any]
            Configured records for the symbol.
        """
        config = source_config or SourceConfig()
        source_entry: Dict[str, Any] = {}

        # ! extract property source
        property_source = config.property_source
        if property_source is not None:
            src = None
            if self.thermo_src.has_mode(
                source_type=property_source,
                symbol=symbol,
                mode="data",
            ):
                src = self.thermo_src.get_comp_src(
                    source_type=property_source,
                    symbol=symbol,
                    components=components,
                )
            self._set_if_available(
                source_entry=source_entry,
                key="src",
                value=src,
                include_missing=include_missing,
            )

        # ! extract equation source
        equation_source = config.equation_source
        if equation_source is not None:
            eq = None
            if self.thermo_src.has_mode(
                source_type=equation_source,
                symbol=symbol,
                mode="equation",
            ):
                eq = self.thermo_src.get_comp_eq(
                    source_type=equation_source,
                    symbol=symbol,
                    components=components,
                )
            self._set_if_available(
                source_entry=source_entry,
                key="eq",
                value=eq,
                include_missing=include_missing,
            )

        # ! extract constant source
        constants_source = config.constants_source
        if constants_source is not None:
            src = None
            if self.thermo_src.has_mode(
                source_type=constants_source,
                symbol=symbol,
                mode="constants",
            ):
                src = self.thermo_src.get_const_src(
                    source_type=constants_source,
                    symbol=symbol,
                )
            if src is not None or "src" not in source_entry:
                self._set_if_available(
                    source_entry=source_entry,
                    key="src",
                    value=src,
                    include_missing=include_missing,
                )

        return source_entry

    def _set_if_available(
            self,
            source_entry: Dict[str, Any],
            key: str,
            value: Any,
            include_missing: bool,
    ) -> None:
        if value is not None or include_missing:
            source_entry[key] = value
