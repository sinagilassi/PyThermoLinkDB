# import libs
import logging
from typing import Dict, Literal, Any, Optional, List
from pythermodb_settings.models import Component, ComponentKey
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
