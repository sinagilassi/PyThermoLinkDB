# import libs
import logging
import numpy as np
from typing import List, Optional, Dict, Any, cast
from pythermodb_settings.models import Component, ComponentKey
# locals
from ..models import ModelSource
from ..thermo import mkdts, mkeqss, EquationSourcesCore


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
            model_source: ModelSource,
            thermo_data: List[str],
            thermo_equations: List[str],
            thermo_constants: List[str],
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
        thermo_data : List[str]
            List of thermodynamic data symbol to be extracted from the model source.
        thermo_equations : List[str]
            List of thermodynamic equations symbol to be extracted from the model source.
        thermo_constants : List[str]
            List of thermodynamic constants symbol to be extracted from the model source.
        component_references : Dict[str, Any]
            Dictionary containing references for each component.
        description : Optional[str]
            Optional description of the thermodynamic model source.
        """
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.model_source = model_source
        self.thermo_data = thermo_data
        self.thermo_equations = thermo_equations
        self.thermo_constants = thermo_constants
        self.component_references = component_references
        self.description = description

        # NOTE: thermo source
        self.thermo_data_source: Dict[str, Any] = {}
        self.thermo_equations_source: Dict[str, EquationSourcesCore] = {}
        self.thermo_source: Dict[str, Any] = {}

    # SECTION: build thermo data

    def _build_thermo_data(self):
        try:
            # >> check if thermo data is available
            if len(self.thermo_data) == 0:
                logger.warning(
                    "No thermodynamic data specified for extraction."
                )
                return

            # NOTE: build thermo data
            res_ = mkdts(
                components=self.components,
                model_source=self.model_source,
                component_key=cast(ComponentKey, self.component_key),
                extract_list=self.thermo_data,
            )

            # >> check if thermo data was successfully built
            if res_ is None:
                logger.warning(
                    "Failed to build thermodynamic data from the model source."
                )
                return

            # NOTE: set thermo data in the thermo source
            # iterate over results and set in thermo source
            for key, value in res_.items():
                self.thermo_data_source[key] = value

        except Exception as e:
            logger.error(
                f"An error occurred while building thermodynamic data: {e}")
            raise

    # SECTION: build thermo equations
    def _build_thermo_equations(self):
        try:
            # >> check if thermo equations is available
            if len(self.thermo_equations) == 0:
                logger.warning(
                    "No thermodynamic equations specified for extraction."
                )
                return

            # NOTE: build thermo equations
            res_: dict[str, EquationSourcesCore] | None = mkeqss(
                components=self.components,
                model_source=self.model_source,
                component_key=cast(ComponentKey, self.component_key),
                build_list=self.thermo_equations,
            )

            # >> check if thermo equations was successfully built
            if res_ is None:
                logger.warning(
                    "Failed to build thermodynamic equations from the model source."
                )
                return

            # NOTE: set thermo equations in the thermo source
            # iterate over results and set in thermo source
            for key, value in res_.items():
                self.thermo_equations_source[key] = value

        except Exception as e:
            logger.error(
                f"An error occurred while building thermodynamic equations: {e}")
            raise

    # SECTION: build

    def build(self) -> None:
        """
        Build the thermodynamic model source by extracting data and equations from the model source.
        """
        try:
            # NOTE: thermo data and equations are built in the constructor
            self._build_thermo_data()
            self._build_thermo_equations()

        except Exception as e:
            logger.error(
                f"An error occurred while building the thermodynamic model source: {e}")
            raise

    # SECTION: config attributes
    def config_attributes(self):
        """
        Configure the attributes of the thermodynamic model source.
        """
        # NOTE: currently, there are no additional attributes to configure.

        # ! data variables
        # >>> init res
        prop_value = np.array([])
        prop_value_comp = {}
        prop_src = {}

        # iterate over thermo data and set attributes
        for symbol in self.thermo_data:
            # NOTE: set attributes for each symbol
            setattr(self, f"{symbol}_src", prop_src)

        # ! equation variables
        # >>> init res
        eqn_value = np.array([])
        eqn_value_comp: Dict[str, float] = {}
        eqn_src: Dict[str, EquationSourcesCore] = {}

        # iterate over thermo equations and set attributes
        for symbol in self.thermo_equations:
            # NOTE: set attributes for each symbol
            setattr(self, f"{symbol}_src", eqn_src)
