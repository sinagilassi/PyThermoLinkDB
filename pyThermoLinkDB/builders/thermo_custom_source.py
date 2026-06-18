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
from ..models import CustomConstant
from ..models.component_models import ConstantResult

# NOTE: logger setup
logger = logging.getLogger(__name__)


class ThermoCustomSource:
    """
    Class representing a custom source of thermodynamic data and constants.
    """

    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            custom_source: Dict[str, Any],
            thermo_data: List[str],
            thermo_constants: List[str],
            component_references: Dict[str, Any],
            description: Optional[str] = None,
            **kwargs
    ):
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.custom_source = custom_source
        self.thermo_data = thermo_data
        self.thermo_constants = thermo_constants
        self.component_references = component_references
        self.description = description

        # NOTE: normalized custom source
        self.thermo_data_source: Dict[str, Dict[str, CustomProperty]] = {}
        self.thermo_constants_source: Dict[str, ConstantResult] = {}

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
            "thermo_data": self.thermo_data,
            "thermo_constants": self.thermo_constants
        }

    def dynamic_attributes(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Return all generated dynamic attributes for custom data and constants.

        Returns
        -------
        Dict[str, Dict[str, Dict[str, Any]]]
            A grouped dictionary containing generated attribute names and values.
        """
        def collect(
                symbols: List[str],
                suffixes: List[str]
        ) -> Dict[str, Dict[str, Any]]:
            attrs: Dict[str, Dict[str, Any]] = {}

            for symbol in symbols:
                symbol_attrs: Dict[str, Any] = {}

                for suffix in suffixes:
                    attr_name = f"{symbol}_{suffix}"
                    symbol_attrs[attr_name] = getattr(self, attr_name, None)

                attrs[symbol] = symbol_attrs

            return attrs

        return {
            "thermo_data": collect(
                symbols=self.thermo_data,
                suffixes=["src", "comp", "value"]
            ),
            "thermo_constants": collect(
                symbols=self.thermo_constants,
                suffixes=["src", "value"]
            )
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
            if len(self.thermo_data) == 0:
                logger.warning("No custom thermodynamic data specified.")
                return

            component_ids = self.component_references.get('component_ids', [])

            for key, value in self.custom_source.items():
                if not self._is_component_data(value=value, component_ids=component_ids):
                    continue

                symbol = self._get_entry_symbol(key=key, value=value)
                if symbol not in self.thermo_data:
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

            for symbol in self.thermo_data:
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
            if len(self.thermo_constants) == 0:
                logger.warning("No custom thermodynamic constants specified.")
                return

            component_ids = self.component_references.get('component_ids', [])

            for key, value in self.custom_source.items():
                if self._is_component_data(value=value, component_ids=component_ids):
                    continue

                const_source = self._build_constant_result(
                    key=key,
                    value=value
                )
                if const_source.symbol not in self.thermo_constants:
                    continue

                self.thermo_constants_source[const_source.symbol] = const_source

            for symbol in self.thermo_constants:
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

    # SECTION: config attributes
    def config_attributes(self) -> None:
        """
        Configure dynamic attributes of the custom thermodynamic model source.
        """
        component_ids = self.component_references.get('component_ids', [])

        # ! data variables
        for symbol in self.thermo_data:
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

            setattr(self, f"{symbol}_src", dt_src)
            setattr(self, f"{symbol}_comp", dt_comp)
            setattr(self, f"{symbol}_value", np.array(dt_value))

        # ! constants variables
        for symbol in self.thermo_constants:
            const_src = self.thermo_constants_source.get(symbol)

            if const_src is None:
                logger.warning(
                    f"Custom constant source for symbol '{symbol}' not found."
                )
                setattr(self, f"{symbol}_src", None)
                setattr(self, f"{symbol}_value", None)
                continue

            setattr(self, f"{symbol}_src", const_src)
            setattr(self, f"{symbol}_value", const_src.value)
