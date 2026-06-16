# import libs
import logging
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import Component, ComponentKey
# locals
from ..thermo import mkdts, mkeqss


# NOTE: logger setup
logger = logging.getLogger(__name__)


class ThermoModelSource:
    """
    Class representing a source of thermodynamic model data.
    """

    def __init__(
            self,
            components: List[Component],
            component_key: ComponentKey,
            thermo_properties: List[str],
            thermo_equations: List[str],
            component_references: Dict[str, Any],
            description: Optional[str] = None
    ):
        """
        Initialize the ThermoModelSource.

        Parameters
        ----------
        component : List[Component]
            List of components involved in the thermodynamic model.
        component_key : ComponentKey
            The key to determine which identifier to use.
            Options are:
                - 'Name-State': Use the name-state identifier.
                - 'Formula-State': Use the formula-state identifier.
                - 'Name-Formula': Use the name and formula.
                - 'Name': Use the component name.
                - 'Formula': Use the component formula.
                - 'Name-Formula-State': Use the name, formula, and state.
                - 'Formula-Name-State': Use the formula, name, and state.
        thermo_properties : List[str]
            List of thermodynamic properties to be extracted from the model source.
        thermo_equations : List[str]
            List of thermodynamic equations to be extracted from the model source.
        component_references : Dict[str, Any]
            Dictionary containing references for each component.
        description : Optional[str]
            Optional description of the thermodynamic model source.
        """
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.thermo_properties = thermo_properties
        self.thermo_equations = thermo_equations
        self.component_references = component_references
        self.description = description
