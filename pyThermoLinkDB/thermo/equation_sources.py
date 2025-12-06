# import libs
import logging
from typing import Dict, Literal, Any, Optional, List
from pythermodb_settings.models import Component
from pyThermoDB.core import TableEquation
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_source import EquationSource

# NOTE: Logger
logger = logging.getLogger(__name__)


class EquationSources:
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
        Initialize EquationSource with a component and source.

        Parameters
        ----------
        component : Component
            The chemical component for which HSG properties are to be calculated, it consists of the following attributes:
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

        # SECTION: retrieve equations
        self.component_equations: Optional[Dict[str, TableEquation]] = self.source.component_eq_extractor(
            component_id=self.component_id
        )

        if self.component_equations is None:
            logger.warning(
                f"Component equations not found for component ID: {self.component_id}"
            )

    def equations(self) -> List[str]:
        """
        Get the list of equation IDs available for the component.

        Returns
        -------
        List[str]
            A list of equation IDs.
        """
        if self.component_equations is None:
            return []

        return list(self.component_equations.keys())

    def eq(
        self,
        name: str
    ) -> Optional[EquationSource]:
        """
        Make an equation source for a given property.

        Parameters
        ----------
        name : str
            The ID of the equation to be used for calculations, e.g., 'VaPr', 'Cp_IG'.

        Returns
        -------
        Optional[EquationSource]
            An EquationSource object if the equation is found; otherwise, None.
        """
        try:
            if self.component_equations is None:
                logger.error("Component equations are not available.")
                return None

            # NOTE: search for equation id in source
            if self.source.is_prop_eq_available(
                component_id=self.component_id,
                prop_name=name,
            ) is False:
                logger.error(
                    f"Equation ID '{name}' not found for component '{self.component_id}'.")
                return None

            # SECTION: Create EquationSource object
            return EquationSource(
                prop_name=name,
                component=self.component,
                source=self.source,
                component_key=self.component_key,  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error creating equation: {e}")
            return None
