# import libs
import logging
import numpy as np
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty
)
# locals
from ..models import CustomConstant, CustomSource
from ..models.component_models import ConstantResult

# NOTE: logger setup
logger = logging.getLogger(__name__)


class ThermoCustomSource:
    """
    Build component-wise thermodynamic data and source-level constants from a
    user-provided custom dictionary.

    ``ThermoCustomSource`` is the custom-data counterpart to
    :class:`ThermoModelSource`. It accepts a mixed ``custom_source`` payload,
    separates component-keyed entries from general constants, and exposes each
    available symbol through ``thermo_src`` with the fixed keys ``src``,
    ``comp``, ``value``, and ``eq``.

    Component-wise entries must be dictionaries keyed by the component IDs
    generated from ``components`` and ``component_key``. Component data
    populates ``src``, ``comp``, and ``value`` in its symbol entry.

    General constants may be scalar values, lists, dictionaries,
    ``CustomProperty`` instances, or ``CustomConstant`` instances. For each
    requested constant, ``src`` contains its ``ConstantResult`` and ``value``
    contains the raw value with its original shape.

    Parameters
    ----------
    components : List[Component]
        Components used to determine the expected component IDs and output
        value order.
    component_key : ComponentKey
        Identifier strategy used to map components to keys in ``custom_source``.
    custom_source : Dict[str, Any]
        Mixed source containing component-wise data and general constants.
    requested_data : List[str]
        Component-wise symbols to extract.
    requested_constants : List[str]
        Constant symbols to extract.
    component_references : Dict[str, Any]
        Precomputed component references, including ``component_ids``.
    description : Optional[str], optional
        Optional human-readable description of the source.
    """

    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            requested_data: List[str],
            requested_constants: List[str],
            component_references: Dict[str, Any],
            description: Optional[str] = None,
            **kwargs
    ):
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.requested_data = requested_data
        self.requested_constants = requested_constants
        self.component_references = component_references
        self.description = description

        # NOTE: normalized custom source
        self.thermo_data_source: Dict[str, Dict[str, CustomProperty]] = {}
        self.thermo_constants_source: Dict[str, ConstantResult] = {}

        # NOTE: canonical symbol source mapping
        self.thermo_src: Dict[str, Dict[str, Any]] = {}

        # NOTE: custom source input
        self._custom_source: Optional[CustomSource] = None

    # SECTION: properties
    @property
    def custom_source(self) -> Optional[CustomSource]:
        """
        Get the original custom source input.

        Returns
        -------
        Optional[CustomSource]
            The original custom source dictionary provided during initialization.
        """
        return self._custom_source

    @custom_source.setter
    def custom_source(self, value: CustomSource) -> None:
        """
        Set the custom source input and trigger the build process.

        Parameters
        ----------
        value : CustomSource
            The custom source dictionary to set.

        Notes
        -----
        - Setting the custom source will automatically build the thermo data and constants.
        """
        self._custom_source = value

    # SECTION: select custom source
    def select_custom_source(self) -> CustomSource:
        """
        Select the custom source to use for building thermo data and constants.

        Returns
        -------
        CustomSource
            The custom source dictionary to be used for building.
        """
        if self._custom_source is not None:
            return self._custom_source
        else:
            raise ValueError(
                "Custom source is not set. Please provide a custom source to build thermo data and constants."
            )

    # SECTION: list all thermo symbols
    def thermo(self) -> Dict[str, List[str]]:
        """
        List all custom thermo data and constants.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary containing lists of symbols for thermo data and constants.
        """
        return {
            "thermo_data": self.requested_data,
            "thermo_constants": self.requested_constants
        }

    def _initialize_thermo_src(self) -> None:
        """Initialize one fixed-shape entry for every available symbol."""
        symbols = dict.fromkeys([
            *self.requested_data,
            *self.requested_constants,
        ])
        self.thermo_src = {
            symbol: {
                "src": None,
                "comp": None,
                "value": None,
                "eq": None,
            }
            for symbol in symbols
        }

    # SECTION: source normalization helpers
    def _is_component_data(
            self,
            value: Any,
            component_ids: List[str]
    ) -> bool:
        """
        Check whether a custom source entry is component-wise data.
        """
        if not isinstance(value, dict) or len(value) == 0:
            return False

        return any(component_id in value for component_id in component_ids)

    def _get_entry_symbol(
            self,
            key: str,
            value: Any
    ) -> str:
        """
        Get the symbol attached to a custom source entry.
        """
        symbol = getattr(value, "symbol", None)
        if symbol:
            return str(symbol)

        if isinstance(value, dict):
            direct_symbol = value.get("symbol")
            if direct_symbol:
                return str(direct_symbol)

            nested_symbols = {
                getattr(nested_value, "symbol", None)
                for nested_value in value.values()
                if getattr(nested_value, "symbol", None)
            }
            if len(nested_symbols) == 1:
                return str(next(iter(nested_symbols)))

        return key

    def _to_custom_property(
            self,
            value: Any,
            symbol: str
    ) -> CustomProperty | None:
        """
        Convert supported property-like custom values to CustomProperty.
        """
        if isinstance(value, CustomProperty):
            return value

        # NOTE: if the value is a dict with a "value" key, treat it as a property-like entry
        if isinstance(value, dict) and "value" in value:
            # set
            value_unit = value.get("unit", "None")
            value_symbol = value.get("symbol", symbol)
            value_value = value.get("value")
            # >> check if None
            if value_value is None:
                logger.warning(
                    f"Custom data value for symbol '{symbol}' is None."
                )
                return None

            return CustomProperty(
                value=value_value,
                unit=value_unit,
                symbol=value_symbol
            )

        logger.warning(
            f"Custom data value for symbol '{symbol}' is not property-like."
        )
        return None

    def _build_constant_result(
            self,
            key: str,
            value: Any
    ) -> ConstantResult:
        """
        Build a ConstantResult while preserving the raw constant value shape.
        """
        symbol = self._get_entry_symbol(key=key, value=value)
        unit = getattr(value, "unit", None)

        if isinstance(value, (CustomProperty, CustomConstant)):
            return ConstantResult(
                value=value.value,
                unit=value.unit,
                symbol=value.symbol
            )

        if isinstance(value, dict):
            if "value" in value:
                return ConstantResult(
                    value=value.get("value"),
                    unit=value.get("unit", unit),
                    symbol=value.get("symbol", symbol)
                )

            nested_units = {
                getattr(nested_value, "unit", None)
                for nested_value in value.values()
                if getattr(nested_value, "unit", None)
            }
            if len(nested_units) == 1:
                unit = next(iter(nested_units))

        return ConstantResult(
            value=value,
            unit=unit,
            symbol=symbol
        )

    # SECTION: build configuration methods
    def _build_thermo_data(self) -> None:
        try:
            if len(self.requested_data) == 0:
                logger.info("No custom data filter specified; extracting all available data.")

            # >>> set up component IDs for quick reference
            component_ids = self.component_references.get('component_ids', [])

            # NOTE: select custom source
            custom_source = self.select_custom_source()

            # >>> iterate through custom source entries to find component-wise data for requested symbols
            for key, value in custom_source.items():
                if not self._is_component_data(value=value, component_ids=component_ids):
                    continue

                symbol = self._get_entry_symbol(key=key, value=value)
                if self.requested_data and symbol not in self.requested_data:
                    continue

                data_source: Dict[str, CustomProperty] = {}
                for component_id in component_ids:
                    component_value = value.get(component_id)
                    if component_value is None:
                        logger.warning(
                            f"Custom data for symbol '{symbol}' not found for component '{component_id}'."
                        )
                        continue

                    custom_property = self._to_custom_property(
                        value=component_value,
                        symbol=symbol
                    )
                    if custom_property is not None:
                        data_source[component_id] = custom_property

                self.thermo_data_source[symbol] = data_source

            for symbol in self.requested_data:
                if symbol not in self.thermo_data_source:
                    logger.warning(
                        f"Custom data source for symbol '{symbol}' not found."
                    )

        except Exception as e:
            logger.error(
                f"An error occurred while building custom thermodynamic data: {e}")
            raise

    def _build_thermo_constants(self) -> None:
        try:
            if len(self.requested_constants) == 0:
                logger.info("No custom constants filter specified; extracting all available constants.")

            # >>> set up component IDs for quick reference
            component_ids = self.component_references.get('component_ids', [])

            # NOTE: select custom source
            custom_source = self.select_custom_source()

            for key, value in custom_source.items():
                if self._is_component_data(value=value, component_ids=component_ids):
                    continue

                const_source = self._build_constant_result(
                    key=key,
                    value=value
                )
                if (
                    self.requested_constants
                    and const_source.symbol not in self.requested_constants
                ):
                    continue

                self.thermo_constants_source[const_source.symbol] = const_source

            for symbol in self.requested_constants:
                if symbol not in self.thermo_constants_source:
                    logger.warning(
                        f"Custom constant source for symbol '{symbol}' not found."
                    )

        except Exception as e:
            logger.error(
                f"An error occurred while building custom thermodynamic constants: {e}")
            raise

    # SECTION: build
    def build_all(self) -> None:
        """
        Build custom thermodynamic data and constants from the custom source.
        """
        try:
            self._build_thermo_data()
            self._build_thermo_constants()

        except Exception as e:
            logger.error(
                f"An error occurred while building the custom thermodynamic model source: {e}")
            raise

    # SECTION: populate thermo source
    def populate_thermo_src(self) -> None:
        """Discover symbols, initialize ``thermo_src``, and populate it."""
        component_ids = self.component_references.get('component_ids', [])

        self._config_available_thermo()
        self._initialize_thermo_src()
        self._populate_data(component_ids)
        self._populate_constants()

    def _config_available_thermo(self) -> None:
        """Populate empty thermo lists from the discovered custom sources."""
        if not self.requested_data:
            self.requested_data = list(self.thermo_data_source)

        if not self.requested_constants:
            self.requested_constants = list(self.thermo_constants_source)

    # NOTE: populate data entries
    def _populate_data(self, component_ids: List[str]) -> None:
        """Populate available custom component data."""
        if not self.requested_data or not self.thermo_data_source:
            return

        # ! data variables
        for symbol in self.requested_data:
            dt_value: List[float] = []
            dt_comp: Dict[str, float] = {}
            dt_src: Dict[str, CustomProperty] = {}

            data_source = self.thermo_data_source.get(symbol, {})
            for component_id in component_ids:
                custom_property = data_source.get(component_id)

                if custom_property is None:
                    logger.warning(
                        f"Custom data source for symbol '{symbol}' not found for component '{component_id}'."
                    )
                    continue

                dt_src[component_id] = custom_property
                dt_comp[component_id] = float(custom_property.value)
                dt_value.append(float(custom_property.value))

            self.thermo_src[symbol].update({
                "src": dt_src,
                "comp": dt_comp,
                "value": np.array(dt_value),
            })

    # NOTE: populate constant entries
    def _populate_constants(self) -> None:
        """Populate custom constants without replacing component data."""
        if not self.requested_constants or not self.thermo_constants_source:
            return

        # ! constants variables
        for symbol in self.requested_constants:
            if symbol in self.requested_data:
                logger.warning(
                    f"Custom constant symbol '{symbol}' is already configured "
                    "as data; preserving the existing attributes."
                )
                continue

            const_src = self.thermo_constants_source.get(symbol)

            if const_src is None:
                logger.warning(
                    f"Custom constant source for symbol '{symbol}' not found."
                )
                continue

            self.thermo_src[symbol].update({
                "src": const_src,
                "value": const_src.value,
            })
