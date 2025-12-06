# import libs
import logging
from typing import Dict, Literal, Any, Optional, List
from pythermodb_settings.models import Component
from pyThermoDB.core import TableData
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from ..models.component_models import PropResult


# NOTE: Logger
logger = logging.getLogger(__name__)


class DataSource:
    def __init__(
        self,
        component: Component,
        source: Source,
        component_key: Literal[
            'Name-State',
            'Formula-State',
            'Name',
            'Formula',
            'Name-Formula-State',
            'Formula-Name-State'
        ] = 'Name-State',
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
                name, None)

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
