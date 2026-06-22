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
    Build thermodynamic data, equation, and constants accessors from a
    ``ModelSource``.

    ``ThermoModelSource`` wraps a structured
    :class:`pyThermoLinkDB.models.ModelSource` and extracts the requested
    component data, component equations, and source-level constants. After
    ``build_all`` and ``config_attributes`` are called, each requested symbol is
    exposed through predictable dynamic attributes.

    For each symbol in ``requested_data``, the class creates:

    - ``{symbol}_src``: mapping of component ID to ``CustomProperty``.
    - ``{symbol}_comp``: mapping of component ID to numeric property value.
    - ``{symbol}_value``: NumPy array of values in component order.
    - ``{symbol}_eq``: ``None``.

    For each symbol in ``requested_equations``, the class creates:

    - ``{symbol}_src``: mapping of component ID to ``EquationSourceCore``.
    - ``{symbol}_comp``: currently ``None``; reserved for evaluated component
    values.
    - ``{symbol}_value``: currently ``None``; reserved for evaluated value
    arrays.
    - ``{symbol}_eq``: alias of ``{symbol}_src``.

    For each symbol in ``requested_constants``, the class creates:

    - ``{symbol}_src``: ``ConstantResult`` selected from the constants source.
    - ``{symbol}_value``: raw constant value.

    Parameters
    ----------
    components : List[Component]
        Components to extract data and equations for.
    component_key : ComponentKey
        Identifier strategy used to map components to entries in
        ``model_source``.
    model_source : ModelSource
        Structured source containing data, equation, and optional constants
        dictionaries.
    requested_data : List[str]
        Component data symbols to extract.
    requested_equations : List[str]
        Component equation symbols to build.
    requested_constants : List[str]
        Source-level constants symbols to extract.
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
            requested_equations: List[str],
            requested_constants: List[str],
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
        requested_data : List[str]
            List of thermodynamic data symbol to be extracted from the model source.
        requested_equations : List[str]
            List of thermodynamic equations symbol to be extracted from the model source.
        requested_constants : List[str]
            List of thermodynamic constants symbol to be extracted from the model source.
        component_references : Dict[str, Any]
            Dictionary containing references for each component.
        description : Optional[str]
            Optional description of the thermodynamic model source.
        """
        # NOTE: set attributes
        self.components = components
        self.component_key = component_key
        self.requested_data = requested_data
        self.requested_equations = requested_equations
        self.requested_constants = requested_constants
        self.component_references = component_references
        self.description = description

        # NOTE: thermo source
        # ! key: component ID; value: data/equation source for the component
        self.thermo_data_source: Dict[str, DataSourceCore] = {}
        self.thermo_equations_source: Dict[str, EquationSourcesCore] = {}
        # ! constants source (not component-specific)
        self.thermo_constants_source: ConstantsSourceCore | None = None

        # Symbols whose dynamic attributes were configured during the latest
        # config_attributes() pass.
        self.used_symbols: List[str] = []

        # NOTE: set model source
        self._model_source: Optional[ModelSource] = None

        # NOTE: thermo source
        self.thermo_src = {}

    # SECTION: Properties
    @property
    def model_source(self) -> Optional[ModelSource]:
        """
        Get the model source.

        Returns
        -------
        ModelSource
            The model source containing data, equations, and constants.
        """
        return self._model_source

    @model_source.setter
    def model_source(self, value: ModelSource) -> None:
        """
        Set the model source.

        Parameters
        ----------
        value : ModelSource
            The model source to set.
        """
        self._model_source = value

    # SECTION: select model source (for production)
    def select_model_source(self) -> ModelSource:
        """
        Select the model source to use for building the thermo model source.

        Returns
        -------
        ModelSource
            The selected model source.

        Raises
        ------
        ValueError
            If no model source is available.
        """
        if self.model_source is not None:
            return self.model_source
        else:
            raise ValueError("No model source available for selection.")

    # NOTE: config thermo source

    def _config_thermo_source(self) -> None:
        """
        Configure the thermo source for all requested symbols, including data, equations, and constants.

        This method initializes the thermo source for each requested symbol, creating
        a dictionary with keys for the source, component values, and evaluated values.

        Notes
        -----
        - The thermo source is a dictionary where each key is a symbol and the value is another dictionary containing the source, component values, and evaluated values for that symbol.
        - For data sources, the keys are 'src', 'comp', and 'value'.
        - For equation sources, the key is only 'eq'.
        - For constant sources, the keys are 'src' and 'value'.
        """
        # create keys (all symbols) for thermo data, equations, and constants
        symbols = [*self.requested_data, *
                   self.requested_equations, *self.requested_constants]
        # >> remove duplicates while preserving order
        symbols = list(set(symbols))

        # iterate through symbols and initialize thermo source for each symbol
        for symbol in symbols:
            self.thermo_src[symbol] = {
                "src": None,
                "comp": None,
                "value": None,
                "eq": None
            }

    # NOTE: list all generated dynamic attributes for thermo data, equations, and constants
    def dynamic_attributes(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Return all generated dynamic attributes for thermo data, equations, and constants.

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
                symbols=self.requested_data,
                suffixes=["src", "comp", "value"]
            ),
            "thermo_equations": collect(
                symbols=self.requested_equations,
                suffixes=["eq"]
            ),
            "thermo_constants": collect(
                symbols=self.requested_constants,
                suffixes=["src", "value"]
            )
        }

    # SECTION: build configuration methods
    # ! build thermo data

    def _build_thermo_data(
            self,
            model_source: ModelSource
    ):
        try:
            # >> check if thermo data is available
            if len(self.requested_data) == 0:
                logger.warning(
                    "No thermodynamic data specified for extraction."
                )

            # NOTE: build thermo data
            res_: Dict[str, DataSourceCore] | None = mkdts(
                components=self.components,
                model_source=model_source,
                component_key=cast(ComponentKey, self.component_key),
                extract_list=self.requested_data,
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
    def _build_thermo_equations(
            self,
            model_source: ModelSource
    ):
        try:
            # >> check if thermo equations is available
            if len(self.requested_equations) == 0:
                logger.warning(
                    "No thermodynamic equations specified for extraction."
                )

            # NOTE: build thermo equations
            # ? build_all is True if requested_equations is empty, meaning build all equations; otherwise, build only the specified equations
            build_all = not self.requested_equations
            build_list = self.requested_equations or None

            res_: dict[str, EquationSourcesCore] | None = mkeqss(
                components=self.components,
                model_source=model_source,
                component_key=cast(ComponentKey, self.component_key),
                # Empty means "build all"; EquationSourcesCore treats [] as
                # an explicit filter that matches no equations.
                build_all=build_all,
                build_list=build_list,
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
    def _build_thermo_constants(
            self,
            model_source: ModelSource
    ):
        try:
            # >> check if thermo constants is available
            if len(self.requested_constants) == 0:
                logger.warning(
                    "No thermodynamic constants specified for extraction."
                )

            # NOTE: check constant source
            if model_source.constants_source is None:
                logger.warning(
                    "Model source does not contain any constants for extraction."
                )
                return

            # NOTE: build thermo constants
            res_: ConstantsSourceCore | None = mkct(
                model_source=model_source,
                extract_list=self.requested_constants,
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
            # NOTE: select model source
            model_source = self.select_model_source()

            # NOTE: thermo data and equations are built in the constructor
            self._build_thermo_data(model_source)
            self._build_thermo_equations(model_source)
            self._build_thermo_constants(model_source)

        except Exception as e:
            logger.error(
                f"An error occurred while building the thermodynamic model source: {e}")
            raise

    # SECTION: list all thermo (symbols) for thermo data, equations, and constants
    def thermo(self) -> Dict[str, List[str]]:
        """
        List all thermo (symbols) for thermo data, equations, and constants.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary containing lists of symbols for thermo data, equations, and constants.
        """
        return {
            "thermo_data": self.requested_data,
            "thermo_equations": self.requested_equations,
            "thermo_constants": self.requested_constants
        }

    # NOTE: config available thermo
    def _config_available_thermo(self) -> None:
        """Populate empty thermo lists from sources built without filters."""
        # ? data source
        if not self.requested_data:
            # >>> get all property symbols from x.data.props for all components
            self.requested_data: list[str] = list(dict.fromkeys(
                prop
                for data_source in self.thermo_data_source.values()
                for prop in data_source.props
            ))

        # ? equations source
        if not self.requested_equations:
            # >>> get all equation symbols from x.equations.eqs for all components
            self.requested_equations: list[str] = list(dict.fromkeys(
                equation
                for equations_source in self.thermo_equations_source.values()
                for equation in equations_source.src
            ))

        # ? constants source
        constants_source: ConstantsSourceCore | None = self.thermo_constants_source

        if not self.requested_constants and constants_source is not None:
            # >>> get all constant symbols
            # from x.constants
            self.requested_constants: list[str] = constants_source.constants

    # SECTION: config attributes
    def config_attributes(self) -> None:
        """
        Configure the attributes of the thermodynamic model source.
        """
        component_ids = self.component_references.get('component_ids', [])
        self.used_symbols = []

        self._config_available_thermo()
        self._config_data_attributes(component_ids)
        self._config_equation_attributes(component_ids)
        self._config_constant_attributes()

    # NOTE: config data attributes
    def _config_data_attributes(
            self,
            component_ids: List[str]
    ) -> None:
        """Configure dynamic attributes for available data sources."""
        if not self.requested_data or not self.thermo_data_source:
            return

        # ! data variables
        # iterate over thermo data and set attributes
        for symbol in self.requested_data:
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
                    # >>> select data source for the symbol for the component
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

            # >> add symbol to used symbols
            if symbol not in self.used_symbols:
                self.used_symbols.append(symbol)

    # NOTE: config equation attributes
    def _config_equation_attributes(
            self,
            component_ids: List[str]
    ) -> None:
        """Configure dynamic attributes for available equation sources."""
        if not self.requested_equations or not self.thermo_equations_source:
            return

        # ! equation variables
        # iterate over thermo equations and set attributes
        for symbol in self.requested_equations:
            # > extract equation data for the symbol for all components
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
            setattr(self, f"{symbol}_eq", eqn_src)

            # >> add symbol to used symbols
            if symbol not in self.used_symbols:
                self.used_symbols.append(symbol)

    # NOTE: config constant attributes
    # ! utility
    def _component_constant_values(
            self,
            const_src: ConstantResult
    ) -> tuple[Dict[str, Any], np.ndarray] | None:
        """Return component-aligned constant values when all component IDs exist."""
        component_ids = self.component_references.get('component_ids', [])
        const_value = const_src.value

        if (
            not component_ids
            or not isinstance(const_value, dict)
            or not all(comp_id in const_value for comp_id in component_ids)
        ):
            return None

        const_comp: Dict[str, float] = {}
        const_value_list: List[float] = []

        for comp_id in component_ids:
            component_value = const_value[comp_id]
            if isinstance(component_value, CustomProperty):
                component_value = component_value.value
            elif isinstance(component_value, dict) and "value" in component_value:
                component_value = component_value["value"]

            if not isinstance(component_value, (int, float)):
                logger.warning(
                    f"Component value for '{comp_id}' in constant source is "
                    "not numeric; the constant will not be treated as component-wise."
                )
                return None

            const_comp[comp_id] = float(component_value)
            const_value_list.append(float(component_value))

        return const_comp, np.array(const_value_list)

    # NOTE: config constant attributes
    def _config_constant_attributes(self) -> None:
        """Configure constants without replacing previously configured symbols."""
        # >>> check constant source
        constants_source: ConstantsSourceCore | None = self.thermo_constants_source

        # >> check
        if (
            not self.requested_constants
            or constants_source is None
            or not constants_source.constants
        ):
            return

        # ! constants variables
        consumed_constant_symbols: List[str] = []

        # iterate over thermo constants and set attributes
        for symbol in self.requested_constants:
            # > select constant source for the symbol
            const_src: ConstantResult | None = constants_source.select(
                symbol=symbol
            )

            # Component-wise constants requested as thermo data belong only to
            # requested_data, even if no regular data source configured them.
            component_values = (
                self._component_constant_values(const_src)
                if const_src is not None
                else None
            )

            if component_values is not None and symbol in self.requested_data:
                const_comp, const_value = component_values
                setattr(self, f"{symbol}_src", const_src)
                setattr(self, f"{symbol}_comp", const_comp)
                setattr(self, f"{symbol}_value", const_value)
                consumed_constant_symbols.append(symbol)
                if symbol not in self.used_symbols:
                    self.used_symbols.append(symbol)
                logger.warning(
                    f"Data symbol '{symbol}' was configured from "
                    "component-wise values in the constant source."
                )
                continue

            # >>> check symbol conflicts with previously configured data or equations
            if symbol in self.used_symbols:
                if component_values is not None and symbol in self.requested_equations:
                    const_comp, const_value = component_values
                    setattr(self, f"{symbol}_comp", const_comp)
                    setattr(self, f"{symbol}_value", const_value)
                    consumed_constant_symbols.append(symbol)
                    logger.warning(
                        f"Equation symbol '{symbol}' received component-wise "
                        "comp and value attributes from the constant source; "
                        "its src and eq attributes were preserved."
                    )
                    continue

                if symbol in self.requested_equations:
                    consumed_constant_symbols.append(symbol)
                    logger.warning(
                        f"Constant symbol '{symbol}' is already configured as "
                        "an equation; removing it from requested_constants."
                    )
                    continue

                logger.warning(
                    f"Constant symbol '{symbol}' is already configured as data "
                    "or an equation; preserving the existing attributes."
                )
                continue

            # >> check if constant source for the symbol was found
            if const_src is not None:
                setattr(self, f"{symbol}_src", const_src)
                setattr(self, f"{symbol}_value", const_src.value)
                self.used_symbols.append(symbol)
            else:
                logger.warning(
                    f"Constant source for symbol '{symbol}' not found in the model source."
                )

        if consumed_constant_symbols:
            consumed_symbols = set(consumed_constant_symbols)
            self.requested_constants = [
                symbol
                for symbol in self.requested_constants
                if symbol not in consumed_symbols
            ]
