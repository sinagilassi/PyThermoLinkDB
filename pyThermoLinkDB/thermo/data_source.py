# import libs
import logging
from typing import Dict, Any, Optional, List
from pythermodb_settings.models import Component, ComponentKey, CustomProperty
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from ..models.component_models import PropResult


# NOTE: Logger
logger = logging.getLogger(__name__)


class DataSourceCore:
    """
    Core adapter for retrieving component property data from a :class:`Source`.

    This lightweight helper binds a :class:`pythermodb_settings.models.Component`
    instance to a :class:`pyThermoLinkDB.thermo.Source` and exposes convenience
    methods to access component-level property data provided by that source.

    Responsibilities
    - Compute a stable component identifier using :func:`pythermodb_settings.utils.set_component_id`
        together with the chosen ``component_key``.
    - Query the provided ``source`` via its ``component_data_extractor`` for the
        component's raw data dictionary.
    - Provide ``props()`` to list available property names and ``prop(name)`` to
        return a ``PropResult`` containing numeric value, unit and symbol.

    Attributes
    - ``component`` (:class:`pythermodb_settings.models.Component`): The component
        model (name, formula, state, optional mole_fraction, ...).
    - ``source`` (:class:`pyThermoLinkDB.thermo.Source`): The data source used to
        extract component information. It must implement ``component_data_extractor``.
    - ``component_key`` (Literal): Format used to build the component identifier
        (e.g. ``'Name-State'``, ``'Formula'``).
    - ``component_id`` (str): The identifier computed from the component and key.
    - ``component_data`` (Optional[Dict[str, Any]]): Raw property dictionary returned
        by the source, or ``None`` if the source had no data for the component.

    Notes
    - The class intentionally keeps logic minimal — it does not perform unit
        conversions, interpolation, or deep validation beyond existence checks.
    - Missing data and lookup failures are logged via the module logger.
    """

    def __init__(
        self,
        component: Component,
        source: Source,
        component_key: ComponentKey = 'Name-State',
    ) -> None:
        """
        Initialize DataSource with a component and source.

        Parameters
        ----------
        component : Component
            The chemical component for which data is to be retrieved, it consists of the following attributes:
                - name: str
                - formula: str
                - state: str
                - mole_fraction: float, optional
        source : Source
            The source containing data for calculations.
        component_key : Literal
            The key to identify the component in the source data. Defaults to 'Name-State'.
        """
        # NOTE: component
        self.component = component
        # NOTE: source
        self.source = source
        # NOTE: component key
        self.component_key = component_key

        # SECTION: set component id
        self.component_id = set_component_id(
            component=self.component,
            component_key=self.component_key
        )

        # SECTION: retrieve data
        self.component_data: Optional[Dict[str, Any]] = self.source.component_data_extractor(  # type: ignore
            component_id=self.component_id
        )

        # >> check
        if self.component_data is None:
            logger.warning(
                f"Component data not found for component ID: {self.component_id}"
            )

        # SECTION: all properties
        self._props: List[str] = self.all_props()
        self._props_symbols: List[str] = self._all_props_symbols()

    # SECTION: Properties
    @property
    def props(self) -> List[str]:
        """
        Get the list of property names available for the component.

        Returns
        -------
        List[str]
            A list of property names.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return []

            return list(self.component_data.keys())
        except Exception as e:
            logger.error(f"Error retrieving property names: {e}")
            return []

    @property
    def props_symbols(self) -> List[str]:
        """
        Get the list of property symbols available for the component.

        Returns
        -------
        List[str]
            A list of property symbols.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return []

            symbols = []
            for prop in self.component_data.values():
                symbol = prop.get("symbol", "")
                if symbol:
                    symbols.append(symbol)

            return symbols
        except Exception as e:
            logger.error(f"Error retrieving property symbols: {e}")
            return []

    # SECTION: properties
    def all_props(self) -> List[str]:
        """
        Get the list of property names available for the component.

        Returns
        -------
        List[str]
            A list of property names.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return []

            return list(self.component_data.keys())
        except Exception as e:
            logger.error(f"Error retrieving property names: {e}")
            return []

    # SECTION: all property symbols
    def _all_props_symbols(self) -> List[str]:
        """
        Get the list of property symbols available for the component.

        Returns
        -------
        List[str]
            A list of property symbols.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return []

            symbols = []
            for prop in self.component_data.values():
                symbol = prop.get("symbol", "")
                if symbol:
                    symbols.append(symbol)

            return symbols
        except Exception as e:
            logger.error(f"Error retrieving property symbols: {e}")
            return []

    # SECTION: Property's availability
    def is_prop_available(self, name: str) -> bool:
        """
        Check if a specific property is available for the component.

        Parameters
        ----------
        name : str
            The name of the property to check.

        Returns
        -------
        bool
            True if the property is available, False otherwise.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return False

            return name in self.component_data
        except Exception as e:
            logger.error(f"Error checking property availability: {e}")
            return False

    # NOTE: Check properties availability
    def check_props_availability(self, names: List[str]) -> Dict[str, bool]:
        """
        Check the availability of multiple properties for the component.

        Parameters
        ----------
        names : List[str]
            A list of property names to check.

        Returns
        -------
        Dict[str, bool]
            A dictionary mapping property names to their availability.
        """
        try:
            # ! all props
            all_props = self.all_props()

            # >> check
            if not all_props:
                logger.error("No properties available to check.")
                return {}

            # ! check availability for each name
            availability = {name: name in all_props for name in names}

            # res
            return availability
        except Exception as e:
            logger.error(f"Error checking properties availability: {e}")
            return {name: False for name in names}

    def all_available(self, names: List[str]) -> bool:
        """
        Check if all specified properties are available for the component.

        Parameters
        ----------
        names : List[str]
            A list of property names to check.

        Returns
        -------
        bool
            True if all properties are available, False otherwise.
        """
        try:
            availability = self.check_props_availability(names)
            return all(availability.values())
        except Exception as e:
            logger.error(
                f"Error checking if all properties are available: {e}")
            return False

    # SECTION: get property
    def prop(
        self,
        name: str
    ):
        """
        Get the data for a specific property of the component.

        Parameters
        ----------
        name : str
            The name of the property to retrieve.

        Returns
        -------
        Optional[Any]
            The data for the specified property, or None if not found.
        """
        try:
            if self.component_data is None:
                logger.error("Component data is not available.")
                return None

            res: Dict[str, Any] | None = self.component_data.get(
                name,
                None
            )

            if res is None:
                logger.warning(
                    f"Property '{name}' not found for component ID: {self.component_id}"
                )
                return None

            # NOTE: extract to PropResult
            value = res.get("value", 0)
            unit = res.get("unit", "")
            symbol = res.get("symbol", "")

            return PropResult(
                value=float(value),
                unit=unit,
                symbol=symbol
            )
        except Exception as e:
            logger.error(f"Error retrieving property '{name}': {e}")
            return None

    # SECTION: select a property
    def select(
        self,
        symbol: str
    ) -> Optional[CustomProperty]:
        """
        Select a specific property of the component and return it as a CustomProperty.

        Parameters
        ----------
        symbol : str
            The symbol of the property to select.

        Returns
        -------
        Optional[CustomProperty]
            A CustomProperty object containing the property's value, unit, and symbol,
            or None if the property is not found or an error occurs.
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
            logger.error(f"Error selecting property '{symbol}': {e}")
            return None
