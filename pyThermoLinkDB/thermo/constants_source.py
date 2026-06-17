# import libs
import logging
from typing import Dict, Any, Optional, List
from pythermodb_settings.models import CustomProperty
# local
from ..thermo import Source
from ..models.component_models import ConstantResult, PropResult

# NOTE: Logger
logger = logging.getLogger(__name__)


class ConstantsSourceCore:
    """
    Core adapter for retrieving constants from a :class:`Source`.

    This helper mirrors :class:`DataSourceCore` for source-level constants. It
    exposes convenience methods to list constants, inspect symbol metadata,
    check availability, and retrieve constants either as raw source entries or
    as ``PropResult``/``CustomProperty`` when the entry follows the common
    ``value``/``unit``/``symbol`` dictionary shape.
    """

    def __init__(
            self,
            source: Source,
            extract_list: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize ConstantsSourceCore with a source.

        Parameters
        ----------
        source : Source
            The source containing data for calculations.
        extract_list : Optional[list[str]]
            A list of specific constant names to extract. If provided, only these constants will be extracted and made available through the methods. Defaults to None, which means all available constants will be extracted.
        """
        # NOTE: source
        self.source = source
        self.extract_list = extract_list

        # SECTION: retrieve constants
        # ! constants data
        self.constants_data: Dict[str, Any] = self.source.constantssource
        # ! constants symbol metadata
        self.constants_symbols_data: Dict[
            str, Any
        ] = self.source.constantssource_symbols

        if not self.constants_data:
            logger.warning("No constants data found in source.")

        # NOTE: if build_list is provided, filter component_data to only include those properties
        if (
            self.constants_data is not None and
            self.extract_list is not None and
            len(self.extract_list) > 0
        ):
            # extracted properties
            extracted_props = {}

            # iterate over build list and check availability
            for prop_name in self.extract_list:
                if not self.is_prop_available(prop_name):
                    logger.warning(
                        f"Property '{prop_name}' is not available in the source and will be skipped."
                    )
                    continue  # skip unavailable properties

                # store the property data
                extracted_props[prop_name] = self.constants_data[prop_name]

            # ! update component data to only include the extracted properties
            self.constants_data = extracted_props

        # SECTION: all constants
        self._constants: List[str] = self.all_constants()
        self._constants_symbols: List[str] = self._all_constants_symbols()

    # SECTION: Properties
    @property
    def constants(self) -> List[str]:
        """
        Get the list of constant names available in the source.

        Returns
        -------
        List[str]
            A list of constant names.
        """
        return self.all_constants()

    @property
    def props(self) -> List[str]:
        """
        Alias for ``constants`` to match the DataSourceCore listing API.
        """
        return self.constants

    @property
    def constants_symbols(self) -> List[str]:
        """
        Get the list of constant symbols available in the source.

        Returns
        -------
        List[str]
            A list of constant symbols.
        """
        return self._all_constants_symbols()

    @property
    def props_symbols(self) -> List[str]:
        """
        Alias for ``constants_symbols`` to match the DataSourceCore API.
        """
        return self.constants_symbols

    # SECTION: constants
    def all_constants(self) -> List[str]:
        """
        Get the list of constant names available in the source.

        Returns
        -------
        List[str]
            A list of constant names.
        """
        try:
            if not self.constants_data:
                logger.error("Constants data is not available.")
                return []

            return list(self.constants_data.keys())
        except Exception as e:
            logger.error(f"Error retrieving constant names: {e}")
            return []

    # SECTION: all constant symbols
    def _all_constants_symbols(self) -> List[str]:
        """
        Get the list of constant symbols available in the source.

        Returns
        -------
        List[str]
            A list of constant symbols.
        """
        try:
            if not self.constants_data:
                logger.error("Constants data is not available.")
                return []

            symbols: List[str] = []

            for constant_name, constant_value in self.constants_data.items():
                if isinstance(constant_value, dict):
                    symbol = constant_value.get("symbol", "")
                    if symbol:
                        symbols.append(symbol)
                        continue

                symbol_info = self.constants_symbols_data.get(
                    constant_name,
                    {}
                )
                if isinstance(symbol_info, dict):
                    symbol = symbol_info.get("symbol", "")
                    if symbol:
                        symbols.append(symbol)

            return symbols
        except Exception as e:
            logger.error(f"Error retrieving constant symbols: {e}")
            return []

    # SECTION: Constant availability
    def is_constant_available(self, name: str) -> bool:
        """
        Check if a specific constant is available.

        Parameters
        ----------
        name : str
            The name of the constant to check.

        Returns
        -------
        bool
            True if the constant is available, False otherwise.
        """
        try:
            return self.source.is_constant_available(
                constant_name=name
            )
        except Exception as e:
            logger.error(f"Error checking constant availability: {e}")
            return False

    def is_prop_available(self, name: str) -> bool:
        """
        Alias for ``is_constant_available`` to match the DataSourceCore API.
        """
        return self.is_constant_available(name=name)

    # NOTE: Check constants availability
    def check_constants_availability(self, names: List[str]) -> Dict[str, bool]:
        """
        Check the availability of multiple constants.

        Parameters
        ----------
        names : List[str]
            A list of constant names to check.

        Returns
        -------
        Dict[str, bool]
            A dictionary mapping constant names to their availability.
        """
        try:
            all_constants = self.all_constants()

            if not all_constants:
                logger.error("No constants available to check.")
                return {}

            return {name: name in all_constants for name in names}
        except Exception as e:
            logger.error(f"Error checking constants availability: {e}")
            return {name: False for name in names}

    def check_availability(self, names: List[str]) -> Dict[str, bool]:
        """
        Alias for ``check_constants_availability``.
        """
        return self.check_constants_availability(names=names)

    def all_available(self, names: List[str]) -> bool:
        """
        Check if all constants in a list are available.

        Parameters
        ----------
        names : List[str]
            A list of constant names to check.

        Returns
        -------
        bool
            True if all constants are available, False otherwise.
        """
        availability = self.check_constants_availability(names=names)
        return all(availability.values())

    # SECTION: get constant
    def constant(
        self,
        name: str
    ) -> Optional[Any]:
        """
        Get the raw data for a specific constant.

        Parameters
        ----------
        name : str
            The name of the constant to retrieve.

        Returns
        -------
        Optional[Any]
            The constant source entry, or None if not found.
        """
        try:
            res = self.source.constants_extractor(
                constant_name=name
            )

            if res is None:
                logger.warning(f"Constant '{name}' not found.")
                return None

            return res
        except Exception as e:
            logger.error(f"Error retrieving constant '{name}': {e}")
            return None

    def const(
        self,
        name: str
    ) -> Optional[Any]:
        """
        Alias for ``constant``.
        """
        return self.constant(name=name)

    # SECTION: get constant symbol metadata
    def symbol(
        self,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get symbol metadata for a specific constant.

        Parameters
        ----------
        name : str
            The name of the constant symbol metadata to retrieve.

        Returns
        -------
        Optional[Dict[str, Any]]
            The constant symbol metadata, or None if not found.
        """
        try:
            return self.source.constant_symbol(
                constant_name=name
            )
        except Exception as e:
            logger.error(f"Error retrieving constant symbol '{name}': {e}")
            return None

    def const_symbol(
        self,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Alias for ``symbol``.
        """
        return self.symbol(name=name)

    # SECTION: get property-like constant
    def prop(
        self,
        name: str
    ) -> Optional[PropResult]:
        """
        Get a property-like constant as a ``PropResult``.

        This method expects the constant entry to be a dictionary containing a
        ``value`` key. Plain constants are available through ``constant``.

        Parameters
        ----------
        name : str
            The name of the constant to retrieve.

        Returns
        -------
        Optional[PropResult]
            The constant value, unit and symbol, or None if the constant cannot
            be represented as a ``PropResult``.
        """
        try:
            res = self.constant(name=name)

            if res is None:
                return None

            if not isinstance(res, dict) or "value" not in res:
                logger.warning(
                    f"Constant '{name}' is not a property-like dictionary."
                )
                return None

            value = res.get("value", 0)
            unit = res.get("unit", "")
            symbol = res.get("symbol", "")

            return PropResult(
                value=float(value),
                unit=unit,
                symbol=symbol
            )
        except Exception as e:
            logger.error(
                f"Error retrieving property-like constant '{name}': {e}")
            return None

    # SECTION: select a constant
    def select_scalar(
        self,
        symbol: str
    ) -> Optional[CustomProperty]:
        """
        Select a property-like constant and return it as a ``CustomProperty``.

        Parameters
        ----------
        symbol : str
            The name of the constant to select.

        Returns
        -------
        Optional[CustomProperty]
            A CustomProperty object containing the constant's value, unit, and
            symbol, or None if the constant is not property-like.
        """
        try:
            prop_result = self.prop(symbol)
            if prop_result is None:
                return None

            return CustomProperty(
                value=prop_result.value,
                unit=prop_result.unit,
                symbol=prop_result.symbol
            )
        except Exception as e:
            logger.error(f"Error selecting constant '{symbol}': {e}")
            return None

    # SECTION: select any constant
    def select(
        self,
        symbol: str
    ) -> Optional[ConstantResult]:
        """
        Select any constant value shape and return it as a ``ConstantResult``.

        Unlike ``select``, this method does not coerce the constant value to a
        numeric ``CustomProperty``. It supports scalar, string, dictionary,
        list, and ``None`` values. If the constant entry is a metadata
        dictionary containing ``value``, ``unit``, or ``symbol`` keys, those
        fields are unpacked; otherwise the full source entry is returned as the
        value.

        Parameters
        ----------
        symbol : str
            The name of the constant to select.

        Returns
        -------
        Optional[ConstantResult]
            A ConstantResult object containing the constant's raw value, unit,
            and symbol, or None if the constant is not found.
        """
        try:
            # NOTE: check availability first to avoid unnecessary processing and provide a clear warning
            if not self.is_constant_available(name=symbol):
                logger.warning(f"Constant '{symbol}' not found.")
                return None

            # NOTE: retrieve the raw constant entry from the source
            res = self.const(symbol)

            # >> check
            if not res:
                logger.warning(f"Constant '{symbol}' not found in source.")
                return None

            selected_symbol = symbol
            symbol_info = self.constants_symbols_data.get(symbol)

            # NOTE: if the constant entry is a dictionary with symbol metadata, use that symbol; otherwise fall back to the input symbol
            if isinstance(symbol_info, dict):
                selected_symbol = symbol_info.get("symbol", symbol)

            # NOTE: constant entry
            return ConstantResult(
                value=res.get("value", res),
                unit=res.get("unit", None),
                symbol=res.get("symbol", selected_symbol)
            )

        except Exception as e:
            logger.error(f"Error selecting constant '{symbol}' wisely: {e}")
            return None
