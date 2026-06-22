# import libs
import logging
from typing import Dict, Literal, Any, Optional, List, cast, Tuple
from pythermodb_settings.models import Component, ComponentKey
from pyThermoDB.core import TableEquation
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_source import EquationSourceCore
from ..utils.input_builder import (
    UnitAvailabilityFn,
    UnitConversionFn,
    validate_inputs_availability_and_units
)

# NOTE: Logger
logger = logging.getLogger(__name__)


class EquationSourcesCore:
    """
    Core adapter for retrieving all equation definitions available for a single
    component from a given Source.

    This helper locates and exposes the set of TableEquation records (by ID)
    that a Source provides for a Component, and it provides a factory method
    to construct an EquationSourceCore for a specific property/equation.

    Responsibilities
    - Build a component identifier using :func:`pythermodb_settings.utils.set_component_id`.
    - Query the provided ``source`` via its ``component_eq_extractor`` to obtain
    a mapping of equation IDs to :class:`pyThermoDB.core.TableEquation`.
    - Provide a simple API to list available equation IDs (``equations()``)
    and to construct a prepared :class:`EquationSourceCore` for a chosen ID
    (``eq(name)``).
    - Log warnings when no equations are found and surface errors when creation
    of an EquationSourceCore is not possible.

    Attributes
    - ``component`` (:class:`pythermodb_settings.models.Component`): Component for
    which equations are requested (name, formula, state, optional mole_fraction).
    - ``source`` (:class:`pyThermoLinkDB.thermo.Source`): Source instance used to retrieve component equations; expected to implement
    - ``component_eq_extractor(component_id)`` and ``is_prop_eq_available(component_id, prop_name)``.
    - ``component_key`` (Literal): Key format used to form the component ID.
    - ``component_id`` (str): Computed identifier for the component using ``set_component_id`` and ``component_key``.
    - ``component_equations`` (Optional[Dict[str, TableEquation]]): Mapping of equation IDs to :class:`pyThermoDB.core.TableEquation` returned by the
    source, or ``None`` if not available.

    Notes
    - The class is a light-weight index/adapter and does not validate or execute equations itself; creating an EquationSourceCore (via ``eq``) prepares a
    single equation for execution and may surface further errors if the underlying source data are malformed.
    - If ``component_equations`` is ``None``, ``equations()`` returns an empty list and ``eq(name)`` will log an error and return ``None``.
    """

    def __init__(
        self,
        component: Component,
        source: Source,
        component_key: ComponentKey = 'Name-State',
        build_all: bool = False,
        build_list: Optional[list[str]] = None,
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
        build_all : bool
            Whether to build all available equations for the component. Defaults to False.
        build_list : Optional[list[str]]
            A list of specific equation names to build. If provided, only these equations will be built. Defaults to None.
        """
        # NOTE: component
        self.component = component
        # NOTE: source
        self.source = source
        # NOTE: component key
        self.component_key = component_key
        # NOTE: build all
        self.build_all = build_all
        # NOTE: build list
        self.build_list = build_list

        # SECTION: set component id
        self.component_id = set_component_id(
            component=self.component,
            component_key=self.component_key
        )

        # SECTION: retrieve equations
        self.component_equations: Optional[
            Dict[str, TableEquation]
        ] = self.source.component_eq_extractor(
            component_id=self.component_id
        )

        if self.component_equations is None:
            logger.warning(
                f"Component equations not found for component ID: {self.component_id}"
            )

        # SECTION: build all equations if requested
        if (
            (self.build_all is True or self.build_list is not None) and
            self.component_equations is not None
        ):
            # ! build all sources and store in _src
            self._src = self.build()
            # ! build inputs sources for all equations and store in _inputs_src
            self._inputs_src, self._inputs_symbols_src = self.build_inputs_src()
        else:
            # ! initialize empty sources
            self._src = {}
            self._inputs_src = {}
            self._inputs_symbols_src = {}

    # SECTION: properties
    @property
    def src(self) -> Dict[str, Optional[EquationSourceCore]]:
        """
        Get the source dictionary of all equation sources.

        Returns
        -------
        Dict[str, Optional[EquationSourceCore]]
            The source dictionary.
        """
        return self._src

    @property
    def inputs_src(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Get the source dictionary of all equation inputs.

        Returns
        -------
        Dict[str, Optional[Dict[str, Any]]]
            The source dictionary of all equation inputs.
        """
        return self._inputs_src

    @property
    def inputs_symbols_src(self) -> Dict[str, Optional[List[str]]]:
        """
        Get the source dictionary of all equation input symbols.

        Returns
        -------
        Dict[str, Optional[List[str]]]
            The source dictionary of all equation input symbols.
        """
        return self._inputs_symbols_src

    # SECTION: summary of built equation sources
    # ! summary of build status for each equation in build_list
    def summary(self) -> Dict[str, bool]:
        """
        Report the build status of each requested equation.

        Returns
        -------
        Dict[str, bool]
            A mapping of each equation in ``build_list`` to whether its source
            was built successfully. Returns an empty mapping when no build
            list was requested.
        """
        if not self.build_list:
            return {}

        return {
            eq_name: self._src.get(eq_name) is not None
            for eq_name in self.build_list
        }

    # ! overall build status for the component
    def build_status(self) -> bool:
        """Return whether every equation requested in ``build_list`` was built."""
        if not self.build_list:
            return True

        return all(self.summary().values())

    # SECTION: list available equations

    def all_available_equations(self) -> List[str]:
        """
        Get the list of equation IDs available for the component before building sources.

        Returns
        -------
        List[str]
            A list of equation IDs (symbols).
        """
        if self.component_equations is None:
            return []

        return list(self.component_equations.keys())

    # NOTE: check availability of specific equations
    def check_availability(self, names: List[str]) -> Dict[str, bool]:
        """
        Check the availability of specified equation IDs for the component before building sources.

        Parameters
        ----------
        names : List[str]
            A list of equation IDs (symbols) to check for

        Returns
        -------
        Dict[str, bool]
            A dictionary mapping each specified equation ID to a boolean indicating its availability.
        """
        if self.component_equations is None:
            return {}

        return {name: name in self.component_equations.keys() for name in names}

    # NOTE: check if all specified equations are available
    def all_available(self, names: List[str]) -> bool:
        """
        Check if all specified equation IDs are available for the component before building sources.

        Parameters
        ----------
        names : List[str]
            A list of equation IDs (symbols) to check for availability.

        Returns
        -------
        bool
            True if all specified equation IDs are available; False otherwise.
        """
        if self.component_equations is None:
            return False

        return all(name in self.component_equations.keys() for name in names)

    # SECTION: make equation source for a specific property
    def eq(
        self,
        name: str
    ) -> Optional[EquationSourceCore]:
        """
        Make an equation source for a given property.

        Parameters
        ----------
        name : str
            The ID of the equation to be used for calculations, e.g., 'VaPr', 'Cp_IG'.

        Returns
        -------
        Optional[EquationSourceCore]
            An EquationSourceCore object if the equation is found; otherwise, None.
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
            return EquationSourceCore(
                prop_name=name,
                component=self.component,
                source=self.source,
                component_key=cast(ComponentKey, self.component_key)
            )
        except Exception as e:
            logger.error(f"Error creating equation: {e}")
            return None

    # SECTION: Build all equation sources
    def build(self) -> Dict[str, Optional[EquationSourceCore]]:
        """
        Make all equation sources available for the component.

        Returns
        -------
        Dict[str, Optional[EquationSourceCore]]
            A dictionary of equation IDs to EquationSourceCore objects, where the value is None if the equation could not be created.
        """
        try:
            # NOTE: build equation sources for all available equations
            eq_sources = {}

            # >> check if component equations are available
            if self.component_equations is None:
                logger.error("Component equations are not available.")
                return eq_sources

            # NOTE: if build_list is provided, filter equations to build
            if self.build_list is not None:
                component_equations_ = {
                    k: v for k, v in self.component_equations.items() if k in self.build_list
                }
            else:
                component_equations_ = self.component_equations

            # NOTE: loop through available equations and create sources
            for eq_id in component_equations_.keys():
                # set source for the equation
                eq_sources[eq_id] = self.eq(name=eq_id)

            return eq_sources
        except Exception as e:
            logger.error(f"Error creating equation sources: {e}")
            return {}

    # SECTION: Select equation source for a specific property

    def select(
        self,
        name: str
    ) -> Optional[EquationSourceCore]:
        """
        Select an equation source for a given property from the built sources.

        Parameters
        ----------
        name : str
            The ID of the equation to be selected.

        Returns
        -------
        Optional[EquationSourceCore]
            An EquationSourceCore object if the equation is found in the built sources; otherwise, None.
        """
        try:
            if not self._src:
                logger.error(
                    "Equation sources have not been built. Please build sources before selecting.")
                return None

            if name not in self._src.keys():
                logger.error(
                    f"Equation ID '{name}' not found in built sources.")
                return None

            return self._src[name]
        except Exception as e:
            logger.error(f"Error selecting equation: {e}")
            return None

    # SECTION: equation inputs source builder
    def build_inputs_src(
            self
    ) -> Tuple[Dict[str, Optional[Dict[str, Any]]], Dict[str, Optional[List[str]]]]:
        """
        Build the source of inputs for all equations available for the component.

        Returns
        -------
        Tuple[Dict[str, Optional[Dict[str, Any]]], Dict[str, Optional[List[str]]]]
            A tuple containing:
                - A dictionary of equation IDs to their corresponding input definitions, where the value is None if the inputs could not be built.
                - A dictionary of equation IDs to their corresponding list of input symbols, where the value is None if the inputs could not be built.
        """
        try:
            # NOTE: build inputs sources for all available equations
            # ! full inputs source
            inputs_src: Dict[str, Optional[Dict[str, Any]]] = {}
            # ! input symbols source
            inputs_symbols_src: Dict[str, Optional[List[str]]] = {}

            # >> check if component equations are available
            if self._src is None:
                logger.error("Equation sources have not been built.")
                return inputs_src, inputs_symbols_src

            # NOTE: loop through available equations and create sources
            for eq_id, eq_source in self._src.items():
                if eq_source is not None:
                    inputs_src[eq_id] = eq_source.inputs
                    inputs_symbols_src[eq_id] = list(eq_source.arg_identifiers)
                else:
                    inputs_src[eq_id] = None
                    inputs_symbols_src[eq_id] = None

            return inputs_src, inputs_symbols_src
        except Exception as e:
            logger.error(f"Error building inputs sources: {e}")
            return {}, {}

    # SECTION: Check inputs availability and units for a specific equation source
    def validate_inputs(
            self,
            eq_symbol: str,
            inputs: List[str],
            unit_availability_fn: UnitAvailabilityFn
    ) -> Tuple[bool, Optional[Dict[str, bool]], bool, Optional[Dict[str, bool]]]:
        """
        Validate the availability of required inputs and their units for a specific equation source.

        Parameters
        ----------
        eq_symbol : str
            The ID of the equation for which to validate inputs.
        inputs : List[str]
            A list of input values provided at runtime as strings, where each string corresponds to an input symbol expected by the equation source.
        unit_conversion_fn : UnitConversionFn
            A function that takes an input value, its current unit, and a target unit, and returns the converted value.
        unit_availability_fn : UnitAvailabilityFn
            A function that takes a unit string and returns a boolean indicating whether the unit is available in the system.

        Returns
        -------
        Tuple[bool, Optional[Dict[str, bool]], Optional[Dict[str, bool]]]
            A tuple containing:
                - A boolean indicating whether all required inputs are available and have valid units.
                - A dictionary of validated and converted input values, where keys are input symbols and values are the corresponding validated and converted input values. This is None if validation fails.
                - A boolean indicating whether all required units are available.
                - A dictionary of input symbols to their expected units, where keys are input symbols and values are the expected unit strings. This is None if validation fails.
        """
        try:
            # NOTE: check if equation source is available
            eq_source = self._src.get(eq_symbol)

            # >> check if equation source is available
            if eq_source is None:
                logger.error(
                    f"Equation source for symbol '{eq_symbol}' is not available.")
                return False, None, False, None

            # NOTE: validate inputs availability and units using the utility function
            return validate_inputs_availability_and_units(
                eq_inputs=eq_source.inputs,
                inputs=inputs,
                unit_availability_fn=unit_availability_fn
            )
        except Exception as e:
            logger.error(f"Error validating inputs: {e}")
            return False, None, False, None

    # NOTE: validate all
    def validate_all_inputs(
            self,
            inputs: List[str],
            unit_availability_fn: UnitAvailabilityFn
    ):
        """
        Validate all equation sources.

        Parameters
        ----------
        inputs : List[str]
            A list of input values provided at runtime as strings, where each string corresponds to an input symbol expected by the equation sources.
        unit_availability_fn : UnitAvailabilityFn
            A function that takes a unit string and returns a boolean indicating whether the unit is available in the system.

        Returns
        -------
        Tuple[bool, Dict[str, bool]]
            A tuple containing:
                - A boolean indicating whether all inputs for all equations are available and have valid units.
                - A dictionary mapping each equation ID to a boolean indicating whether its inputs are valid.
        """
        try:
            # NOTE: validate all equation sources
            validation_results = {}

            # iterate through all equation sources and validate their inputs
            for eq_id in self._src.keys():
                valid_inputs_, _, valid_units_, _ = self.validate_inputs(
                    eq_symbol=eq_id,
                    inputs=inputs,
                    unit_availability_fn=unit_availability_fn
                )
                validation_results[eq_id] = {
                    "inputs": valid_inputs_,
                    "units": valid_units_,
                    "overall": valid_inputs_ and valid_units_
                }

            return validation_results
        except Exception as e:
            logger.error(f"Error validating all inputs: {e}")
            return False, {}
