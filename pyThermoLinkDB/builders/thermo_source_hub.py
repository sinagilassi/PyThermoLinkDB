"""Container for built model and custom thermodynamic sources."""

from typing import List, Optional, Dict, Any, cast, Literal

from pythermodb_settings.models import Component, ComponentKey, CustomProperty, CustomConstant

from .thermo_custom_source import ThermoCustomSource
from .thermo_model_source import ThermoModelSource
from .thermo_source_validator import ValidationReport
from .thermo_source_extractor import ThermoSourceExtractor
from ..thermo import EquationSourceCore


class ThermoSourceHub:
    """
    Hold built model and custom thermodynamic sources behind one access layer.

    ``ThermoSourceHub`` combines optional :class:`ThermoModelSource` and
    :class:`ThermoCustomSource` instances with the component metadata used to
    build them. It exposes both sources through a canonical ``thermo_source``
    mapping with ``model_source`` and ``custom_source`` groups, and delegates
    symbol lookup, component reordering, validation summaries, and source
    completeness checks to the underlying source objects.

    Parameters
    ----------
    components : List[Component]
        Components used to build the model and custom source entries.
    component_key : ComponentKey
        Identifier strategy used for component-keyed source entries.
    thermo_model_source : Optional[ThermoModelSource]
        Built model source, or ``None`` when no model source was configured.
    thermo_custom_source : Optional[ThermoCustomSource]
        Built custom source, or ``None`` when no custom source was configured.
    description : Optional[str], optional
        Optional human-readable description of the combined source hub.

    Attributes
    ----------
    thermo_source : Dict[str, Dict[str, Any]]
        Canonical source mapping with ``model_source`` and ``custom_source``
        keys. Each source group maps symbols to entries containing ``src``,
        ``comp``, ``value``, ``eq``, and ``mode`` fields.
    """

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
        """Return the built thermo source."""
        return self._thermo_source

    # ! model source
    @property
    def thermo_model_source_hub(self) -> Dict[str, Any]:
        """Return the built thermo source, containing model source entries."""
        return self.thermo_source['model_source']

    # ! custom source
    @property
    def thermo_custom_source_hub(self) -> Dict[str, Any]:
        """return the built thermo source, containing custom source entries."""
        return self.thermo_source['custom_source']

    @property
    def thermo_source_hub_types(
        self
    ) -> Literal["model_source", "custom_source", "both"]:
        """Return the available thermo source hub types."""
        if not hasattr(self, "thermo_source_extractor"):
            self._configure_thermo_source()

        has_model_source = len(self.thermo_model_source_hub) > 0
        has_custom_source = len(self.thermo_custom_source_hub) > 0

        if has_model_source and has_custom_source:
            return "both"
        elif has_model_source:
            return "model_source"
        elif has_custom_source:
            return "custom_source"
        else:
            raise ValueError("No thermo source is available in the hub.")

    @property
    def model_source_symbols(self) -> List[str]:
        """Return available symbols from the model source group."""
        return self._ensure_thermo_source_extractor().model_symbols()

    @property
    def custom_source_symbols(self) -> List[str]:
        """Return available symbols from the custom source group."""
        return self._ensure_thermo_source_extractor().custom_symbols()

    @property
    def model_source_symbol_modes(self) -> Dict[str, List[str]]:
        """Return model-source symbols mapped to their modes."""
        return self._ensure_thermo_source_extractor().model_symbol_modes()

    @property
    def custom_source_symbol_modes(self) -> Dict[str, List[str]]:
        """Return custom-source symbols mapped to their modes."""
        return self._ensure_thermo_source_extractor().custom_symbol_modes()

    # SECTION: Thermo source configuration
    # ! to be called
    def _configure_thermo_source(self) -> None:
        """
        Configure thermo source dictionary.
        """
        # NOTE: model source
        if self.thermo_model_source is not None:
            self._thermo_source["model_source"] = self.thermo_model_source.thermo_src

        # NOTE: custom source
        if self.thermo_custom_source is not None:
            self._thermo_source["custom_source"] = self.thermo_custom_source.thermo_src

        # NOTE: thermo source extractor
        self.thermo_source_extractor = ThermoSourceExtractor(
            thermo_source=self._thermo_source,
            component_key=cast(ComponentKey, self.component_key)
        )

    def _ensure_thermo_source_extractor(self) -> ThermoSourceExtractor:
        """Configure the extractor on first access."""
        if not hasattr(self, "thermo_source_extractor"):
            self._configure_thermo_source()
        return self.thermo_source_extractor

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
    def available_symbols(self, source_type: str) -> List[str]:
        """
        Return available symbol keys from a source group.

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
        return self._ensure_thermo_source_extractor().available_symbols(
            source_type=source_type
        )

    def available_props(self, source_type: str) -> List[str]:
        """
        Return available property/symbol keys from a source group.

        This is an alias for :meth:`available_symbols` for callers that use
        ``props`` terminology for thermodynamic property symbols.
        """
        return self._ensure_thermo_source_extractor().available_props(
            source_type=source_type
        )

    # NOTE: access to thermo source symbols
    def get_model_source_symbols(self) -> List[str]:
        """Return available symbols from the model source group."""
        return self._ensure_thermo_source_extractor().model_symbols()

    def get_custom_source_symbols(self) -> List[str]:
        """Return available symbols from the custom source group."""
        return self._ensure_thermo_source_extractor().custom_symbols()

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
            ``mode`` list.
        """
        return self._ensure_thermo_source_extractor().available_symbol_modes(
            source_type=source_type
        )

    def get_model_source_symbol_modes(self) -> Dict[str, List[str]]:
        """Return model-source symbols mapped to their modes."""
        return self._ensure_thermo_source_extractor().model_symbol_modes()

    def get_custom_source_symbol_modes(self) -> Dict[str, List[str]]:
        """Return custom-source symbols mapped to their modes."""
        return self._ensure_thermo_source_extractor().custom_symbol_modes()

    def get(
            self,
            source_name: str,
            symbol: str,
            components: Optional[List[Component]] = None
    ) -> Dict[str, Any] | None:
        """
        Return the full thermo entry for a symbol from a source group.

        Parameters
        ----------
        source_name : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to extract.
        components : Optional[List[Component]], optional
            Optional component order for component-wise entries. When provided,
            ``src``, ``comp``, ``eq``, vector ``value``, and ``mode`` fields
            are returned in this component order.

        Returns
        -------
        Dict[str, Any] | None
            The source entry with ``src``, ``comp``, ``value``, ``eq``, and
            ``mode`` keys, or ``None`` when the source group or symbol is
            unavailable.
        """
        return self._ensure_thermo_source_extractor().get(
            source_name=source_name,
            symbol=symbol,
            components=components
        )

    def get_item(
            self,
            source_type: str,
            symbol: str,
            item: str,
            components: Optional[List[Component]] = None
    ) -> Any:
        """
        Return one field from a thermo symbol entry.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to extract.
        item : str
            Entry field to return, such as ``"src"``, ``"comp"``, ``"value"``,
            ``"eq"``, or ``"mode"``.
        components : Optional[List[Component]], optional
            Optional component order for component-wise entries.

        Returns
        -------
        Any
            The selected entry field, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_item(
            source_type=source_type,
            symbol=symbol,
            item=item,
            components=components
        )

    def get_comp_eq(
            self,
            source_type: str,
            symbol: str,
            components: Optional[List[Component]] = None
    ) -> Dict[str, EquationSourceCore] | None:
        """
        Return component-wise equation sources for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Equation symbol to extract.
        components : Optional[List[Component]], optional
            Optional component order for the returned equation mapping.

        Returns
        -------
        Dict[str, EquationSourceCore] | None
            Component-keyed equation mapping, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_comp_eq(
            source_type=source_type,
            symbol=symbol,
            components=components
        )

    def get_comp_src(
            self,
            source_type: str,
            symbol: str,
            components: Optional[List[Component]] = None
    ) -> Dict[str, CustomProperty] | None:
        """
        Return component-wise source objects for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to extract.
        components : Optional[List[Component]], optional
            Optional component order for the returned source mapping.

        Returns
        -------
        Dict[str, CustomProperty] | None
            Component-keyed source mapping, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_comp_src(
            source_type=source_type,
            symbol=symbol,
            components=components
        )

    def get_comp_dt(
            self,
            source_type: str,
            symbol: str,
            components: Optional[List[Component]] = None
    ) -> Dict[str, float] | None:
        """
        Return component-wise data values for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to extract.
        components : Optional[List[Component]], optional
            Optional component order for the returned component mapping.

        Returns
        -------
        Dict[str, float] | None
            Component-keyed data mapping, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_comp_dt(
            source_type=source_type,
            symbol=symbol,
            components=components
        )

    def get_comp_values(
            self,
            source_type: str,
            symbol: str,
            components: Optional[List[Component]] = None
    ) -> List[float] | None:
        """
        Return component-wise values for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Data symbol to extract.
        components : Optional[List[Component]], optional
            Optional component order for the returned component mapping.

        Returns
        -------
        List[float] | None
            Component-keyed value mapping, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_comp_values(
            source_type=source_type,
            symbol=symbol,
            components=components
        )

    def get_mode(
            self,
            source_type: str,
            symbol: str
    ) -> List[str] | None:
        """
        Return source modes for a symbol.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Thermodynamic symbol to extract.

        Returns
        -------
        List[str] | None
            Source modes such as ``["data"]`` or ``["data", "equation"]``, or
            ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_mode(
            source_type=source_type,
            symbol=symbol
        )

    def has_mode(
            self,
            source_type: str,
            symbol: str,
            mode: str
    ) -> bool:
        """
        Return whether a symbol entry includes the requested source mode.
        """
        return self._ensure_thermo_source_extractor().has_mode(
            source_type=source_type,
            symbol=symbol,
            mode=mode
        )

    def get_const(
            self,
            source_type: str,
            symbol: str
    ) -> Any:
        """
        Return a constant value from a source group.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Constant symbol to extract.

        Returns
        -------
        Any
            Constant value, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_const(
            source_type=source_type,
            symbol=symbol
        )

    def get_const_src(
            self,
            source_type: str,
            symbol: str
    ) -> Optional[CustomConstant]:
        """
        Return the constant source object from a source group.

        Parameters
        ----------
        source_type : str
            Source group name. Expected values are ``"model_source"`` or
            ``"custom_source"``.
        symbol : str
            Constant symbol to extract.

        Returns
        -------
        Optional[CustomConstant]
            Constant source object, or ``None`` when unavailable.
        """
        return self._ensure_thermo_source_extractor().get_const_src(
            source_type=source_type,
            symbol=symbol
        )
