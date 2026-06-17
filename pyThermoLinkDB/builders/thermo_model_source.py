# import libs
import logging
import numpy as np
from typing import List, Optional, Dict, Any, cast
from pythermodb_settings.models import Component, ComponentKey, CustomProperty
# locals
from ..models import ModelSource
from ..models.component_models import ConstantResult
from ..thermo import (
    mkdts,
    mkeqss,
    mkct,
    EquationSourceCore,
    EquationSourcesCore,
    DataSourceCore,
    ConstantsSourceCore
)


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
        model_source : ModelSource
            The source of the thermodynamic model data.
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
        self.thermo_data_source: Dict[str, DataSourceCore] = {}
        self.thermo_equations_source: Dict[str, EquationSourcesCore] = {}
        self.thermo_constants_source: ConstantsSourceCore | None = None
        self.thermo_source: Dict[str, Any] = {}

    # SECTION: build configuration methods
    # ! build thermo data

    def _build_thermo_data(self):
        try:
            # >> check if thermo data is available
            if len(self.thermo_data) == 0:
                logger.warning(
                    "No thermodynamic data specified for extraction."
                )
                return

            # NOTE: build thermo data
            res_: Dict[str, DataSourceCore] | None = mkdts(
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

    # ! build thermo equations
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

    # ! build thermo constants
    def _build_thermo_constants(self):
        try:
            # >> check if thermo constants is available
            if len(self.thermo_constants) == 0:
                logger.warning(
                    "No thermodynamic constants specified for extraction."
                )
                return

            # NOTE: check constant source
            if self.model_source.constants_source is None:
                logger.warning(
                    "Model source does not contain any constants for extraction."
                )
                return

            # NOTE: build thermo constants
            res_: ConstantsSourceCore | None = mkct(
                model_source=self.model_source,
                extract_list=self.thermo_constants,
            )

            # >> check if thermo constants was successfully built
            if res_ is None:
                logger.warning(
                    "Failed to build thermodynamic constants from the model source."
                )
                return

            # NOTE: set thermo constants in the thermo source
            self.thermo_constants_source = res_

        except Exception as e:
            logger.error(
                f"An error occurred while building thermodynamic constants: {e}")
            raise

    # SECTION: build

    def build_all(self) -> None:
        """
        Build the thermodynamic model source by extracting data and equations from the model source.
        """
        try:
            # NOTE: thermo data and equations are built in the constructor
            self._build_thermo_data()
            self._build_thermo_equations()
            self._build_thermo_constants()

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
        component_ids = self.component_references.get('component_ids', [])

        # ! data variables
        # iterate over thermo data and set attributes
        for symbol in self.thermo_data:
            # > extract property data for the symbol for all components
            dt_value: List[float] = []
            dt_comp: Dict[str, float] = {}
            dt_src: Dict[str, CustomProperty] = {}

            # iterate over components and extract data source for the symbol
            for comp_id in component_ids:
                res_dt: DataSourceCore | None = self.thermo_data_source.get(
                    comp_id, None
                )

                # >> check
                if res_dt is not None:
                    res_dt_: CustomProperty | None = res_dt.select(
                        symbol=symbol
                    )

                    # >> check
                    if res_dt_ is not None:
                        dt_src[comp_id] = res_dt_
                        dt_comp[comp_id] = float(res_dt_.value)
                        dt_value.append(float(res_dt_.value))
                    else:
                        logger.warning(
                            f"Data source for symbol '{symbol}' not found for component '{comp_id}'."
                        )
                else:
                    logger.warning(
                        f"Data source for symbol '{symbol}' not found for component '{comp_id}'."
                    )
            # ? set attributes for each symbol
            setattr(self, f"{symbol}_src", dt_src)
            setattr(self, f"{symbol}_comp", dt_comp)
            setattr(self, f"{symbol}_value", np.array(dt_value))

        # ! equation variables
        # iterate over thermo equations and set attributes
        for symbol in self.thermo_equations:
            # > extract equation data for the symbol for all components
            eqn_value: Optional[List[float]] = None
            eqn_comp: Optional[Dict[str, float]] = None
            eqn_src: Dict[str, EquationSourceCore] = {}

            # iterate over components and extract equation source for the symbol
            for comp_id in component_ids:
                eqs_comp: EquationSourcesCore | None = self.thermo_equations_source.get(
                    comp_id, None
                )
                if eqs_comp is None:
                    logger.warning(
                        f"Equation source for symbol '{symbol}' not found for component '{comp_id}'."
                    )
                    continue

                eqn_src_comp: EquationSourceCore | None = eqs_comp.select(
                    name=symbol
                )

                # >> check if equation source for the symbol was found for the component
                if eqn_src_comp is not None:
                    eqn_src[comp_id] = eqn_src_comp
                else:
                    logger.warning(
                        f"Equation source for symbol '{symbol}' not found for component '{comp_id}'."
                    )
            # ? set attributes for each symbol
            setattr(self, f"{symbol}_src", eqn_src)
            setattr(self, f"{symbol}_comp", eqn_comp)
            setattr(self, f"{symbol}_value", eqn_value)

        # ! constants variables
        # iterate over thermo constants and set attributes
        for symbol in self.thermo_constants:
            # source
            res_const_src: ConstantsSourceCore | None = self.thermo_constants_source

            # >> check if constant source is available
            if res_const_src is None:
                logger.warning(
                    f"Constant source for symbol '{symbol}' not available in the model source."
                )
                continue

            # > extract constant data for the symbol
            const_src: ConstantResult | None = res_const_src.select(
                symbol=symbol
            )

            # >> check if constant source for the symbol was found
            if const_src is not None:
                setattr(self, f"{symbol}_src", const_src)
                setattr(self, f"{symbol}_value", const_src.value)
            else:
                logger.warning(
                    f"Constant source for symbol '{symbol}' not found in the model source."
                )
                # set attributes to None if not found
                setattr(self, f"{symbol}_src", None)
                setattr(self, f"{symbol}_value", None)
