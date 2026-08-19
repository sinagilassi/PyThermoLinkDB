"""Configured registry for extracting thermo source entries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pythermodb_settings.models import Component, Mixture, MixtureKey

from ..models import SourceConfig, ThermoSourceHubConfig


class ThermoSourceRegistry:
    """
    Extract configured source records from a thermodynamic source hub.

    ``ThermoSourceRegistry`` resolves a ``ThermoSourceHubConfig`` against a
    built source hub. Each configured symbol resolves to one selected source
    object under ``src`` and records the inferred source ``mode``.
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
            mixtures: Optional[List[Mixture]] = None,
            mixture_key: Optional[MixtureKey] = None,
            include_missing: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract configured source records for all configured symbols.

        Parameters
        ----------
        components : Optional[List[Component]], optional
            Optional component order for component-wise source entries.
        mixtures : Optional[List[Mixture]], optional
            Optional mixture order for mixture-keyed matrix-data source entries.
        mixture_key : Optional[MixtureKey], optional
            Optional mixture identifier strategy for matrix-data source entries.
        include_missing : bool, optional
            When ``True``, include keys with ``None`` values for configured
            fields that are not available in the selected source group.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Registry keyed by symbol. Each symbol contains the selected
            ``src`` entry, inferred ``mode``, and selected ``source_type`` when
            available. Equation sources are also returned through ``src``.
        """
        registry: Dict[str, Dict[str, Any]] = {}

        for symbol, source_config in self.thermo_source_hub_config.items():
            registry[symbol] = self.extract_source(
                symbol=symbol,
                source_config=source_config,
                components=components,
                mixtures=mixtures,
                mixture_key=mixture_key,
                include_missing=include_missing,
            )

        self._registry = registry
        return registry

    def extract_source(
            self,
            symbol: str,
            source_config: Optional[SourceConfig] = None,
            components: Optional[List[Component]] = None,
            mixtures: Optional[List[Mixture]] = None,
            mixture_key: Optional[MixtureKey] = None,
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
        mixtures : Optional[List[Mixture]], optional
            Optional mixture order for mixture-keyed matrix-data source entries.
        mixture_key : Optional[MixtureKey], optional
            Optional mixture identifier strategy for matrix-data source entries.
        include_missing : bool, optional
            When ``True``, include missing fields as ``None``.

        Returns
        -------
        Dict[str, Any]
            Configured records for the symbol.
        """
        config = source_config or SourceConfig()
        source_entry: Dict[str, Any] = {}

        selected = self._select_source(
            symbol=symbol,
            config=config,
            components=components,
            mixtures=mixtures,
            mixture_key=mixture_key,
        )

        if selected is not None:
            source_type, mode, src = selected
            self._set_if_available(
                source_entry=source_entry,
                key="src",
                value=src,
                include_missing=include_missing,
            )
            self._set_if_available(
                source_entry=source_entry,
                key="mode",
                value=mode,
                include_missing=include_missing,
            )
            self._set_if_available(
                source_entry=source_entry,
                key="source_type",
                value=source_type,
                include_missing=include_missing,
            )
        elif include_missing:
            source_entry.update({
                "src": None,
                "mode": None,
                "source_type": self._configured_source_type(config),
            })

        return source_entry

    def _select_source(
            self,
            symbol: str,
            config: SourceConfig,
            components: Optional[List[Component]],
            mixtures: Optional[List[Mixture]],
            mixture_key: Optional[MixtureKey],
    ) -> Optional[tuple[str, str, Any]]:
        """
        Return the first configured source/mode that exists for ``symbol``.

        Mode-specific fields are used first because they disambiguate symbols
        that may exist in more than one mode. When only ``source`` is provided,
        the mode is inferred from the built source entry.
        """
        explicit_candidates = (
            ("data", config.property_source),
            ("matrix_data", config.matrix_data_source),
            ("equation", config.equation_source),
            ("constants", config.constants_source),
        )

        for mode, source_type in explicit_candidates:
            if source_type is None:
                continue
            selected = self._extract_mode_source(
                source_type=source_type,
                symbol=symbol,
                mode=mode,
                components=components,
                mixtures=mixtures,
                mixture_key=mixture_key,
            )
            if selected is not None:
                return selected

        if config.source is None:
            return None

        for mode in ("data", "matrix_data", "equation", "constants"):
            selected = self._extract_mode_source(
                source_type=config.source,
                symbol=symbol,
                mode=mode,
                components=components,
                mixtures=mixtures,
                mixture_key=mixture_key,
            )
            if selected is not None:
                return selected

        return None

    def _configured_source_type(self, config: SourceConfig) -> Optional[str]:
        """Return the first source type requested by ``config``."""
        for source_type in (
            config.property_source,
            config.matrix_data_source,
            config.equation_source,
            config.constants_source,
            config.source,
        ):
            if source_type is not None:
                return source_type
        return None

    def _extract_mode_source(
            self,
            source_type: str,
            symbol: str,
            mode: str,
            components: Optional[List[Component]],
            mixtures: Optional[List[Mixture]],
            mixture_key: Optional[MixtureKey],
    ) -> Optional[tuple[str, str, Any]]:
        """Extract a source only when the source entry exposes ``mode``."""
        if not self.thermo_src.has_mode(
            source_type=source_type,
            symbol=symbol,
            mode=mode,
        ):
            return None

        if mode == "data":
            src = self.thermo_src.get_comp_src(
                source_type=source_type,
                symbol=symbol,
                components=components,
            )
        elif mode == "matrix_data":
            src = self.thermo_src.get_matrix_data_src(
                source_type=source_type,
                symbol=symbol,
                components=components,
                mixtures=mixtures,
                mixture_key=mixture_key,
            )
        elif mode == "equation":
            src = self.thermo_src.get_comp_eq(
                source_type=source_type,
                symbol=symbol,
                components=components,
            )
        elif mode == "constants":
            src = self.thermo_src.get_const_src(
                source_type=source_type,
                symbol=symbol,
            )
        else:
            return None

        if src is None:
            return None
        return source_type, mode, src

    def _set_if_available(
            self,
            source_entry: Dict[str, Any],
            key: str,
            value: Any,
            include_missing: bool,
    ) -> None:
        if value is not None or include_missing:
            source_entry[key] = value
