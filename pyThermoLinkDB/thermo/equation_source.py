# import libs
import logging
from typing import Dict, Literal, Any, Optional, List, Callable, cast
from pythermodb_settings.models import Component, ComponentKey
from pyThermoDB.core import TableEquation
from pythermodb_settings.utils import set_component_id
from pyThermoDB.models import EquationResult
# local
from ..thermo import Source
from ..models.component_models import ComponentEquationSource


# NOTE: Logger
logger = logging.getLogger(__name__)


class EquationSourceCore:
    """
    Core adapter for retrieving and preparing equation sources for a component.

    This class couples a requested property equation (``prop_name``) with a
    specific :class:`pythermodb_settings.models.Component` and a
    :class:`pyThermoLinkDB.thermo.Source`. It locates the appropriate
    :class:`ComponentEquationSource` from the source, extracts the underlying
    :class:`pyThermoDB.core.TableEquation`, the callable equation implementation,
    and metadata such as argument names, input defaults, return units and
    symbols.

    Responsibilities
    - Build a component identifier using :func:`pythermodb_settings.utils.set_component_id`.
    - Query the provided ``source`` via its ``eq_builder`` for available
        equations matching ``prop_name`` and the component.
    - Expose convenient properties for the equation object, function,
        inputs/default-args, argument symbols/identifiers and return metadata.
    - Provide ``calc(**input_args)`` to execute the selected equation with a
        combination of stored default arguments and runtime inputs.

    Attributes
    - ``prop_name`` (str): Property/equation identifier requested (e.g. ``'VaPr'``).
    - ``component`` (:class:`pythermodb_settings.models.Component`): The component
        for which the equation is requested.
    - ``source`` (:class:`pyThermoLinkDB.thermo.Source`): The source used to
        locate equation definitions; must implement ``eq_builder`` returning a
        mapping of component IDs to :class:`ComponentEquationSource`.
    - ``component_key`` (Literal): Format used to form the component identifier.
    - ``component_id`` (str): Computed identifier for the component using
        ``set_component_id`` and ``component_key``.
    - ``component_equation`` (:class:`ComponentEquationSource`): The selected
        equation source record for the component and ``prop_name``.
    - ``_eq`` (:class:`pyThermoDB.core.TableEquation`): The equation metadata
        object (body, description, etc.).
    - ``_num`` (int): Equation number/index.
    - ``_fn`` (Callable[..., EquationResult]): Callable that performs the
        calculation and returns an :class:`pyThermoDB.models.EquationResult`.
    - ``_inputs`` (Dict[str, Any]): Named input values (defaults) for the
        equation.
    - ``_args`` (Dict[str, Any]): Stored/default arguments passed to ``_fn``.
    - ``_arg_symbols`` / ``_arg_identifiers``: Metadata for argument symbols
        and identifiers.
    - ``_returns`` / ``_return_symbols`` / ``_return_identifiers``: Metadata
        describing returned values, their units and symbols; ``_return_unit`` and
        ``_return_symbol`` store the primary return unit and symbol.

    Notes
    - The class focuses on locating and preparing equation metadata and
        dispatching the equation callable; it does not perform unit conversions
        or attempt to harmonize differing units across sources.
    - If no matching equation is found for the component and ``prop_name``, the
        equation-related attributes are initialized with empty values and
        ``calc()`` returns ``None``.
    """

    def __init__(
        self,
        prop_name: str,
        component: Component,
        source: Source,
        component_key: ComponentKey = 'Name-State',
    ) -> None:
        """
        Initialize EquationSourceCore with a property name, component, and source.

        Parameters
        ----------
        prop_name : str
            The ID of the equation to be used for calculations, e.g., 'VaPr', 'Cp_IG'.
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
        # NOTE: equation id
        self.prop_name = prop_name
        # NOTE: component
        self.component = component
        # NOTE: source
        self.source = source
        # NOTE: component key
        self.component_key = component_key

        # SECTION: settings
        self._status: bool = False

        # SECTION: set component id
        self.component_id = set_component_id(
            component=self.component,
            component_key=self.component_key
        )

        # SECTION: get equation source
        self.component_equation: Optional[
            ComponentEquationSource
        ] = self._get_equation_from_source()

        # NOTE: extract equation details
        # ! equation
        self._eq: Optional[TableEquation] = None
        # ! num
        self._num: Optional[int] = None
        # ! fn
        self._fn: Optional[Callable[..., EquationResult]] = None
        # ! inputs
        self._inputs: Dict[str, Any] = {}
        # ! args
        self._args: Dict[
            str,
            Any
        ] = {}
        # ! arg symbols
        self._arg_symbols: Dict[
            str,
            Any
        ] = {}
        # ! arg identifiers
        self._arg_identifiers: List[
            str
        ] = []
        # ! arg mappings
        self._arg_mappings: Dict[
            str,
            Any
        ] = {}
        # ! returns
        self._returns: Dict[
            str,
            Any
        ] = {}
        # ! return symbols
        self._return_symbols: Dict[
            str,
            Any
        ] = {}
        # ! return identifiers
        self._return_identifiers: List[
            str
        ] = []
        self._return_unit: Optional[str] = None
        self._return_symbol: Optional[str] = None

        # NOTE: if equation source is found, extract details
        if self.component_equation is not None:
            # >> update status
            self._status = True

            # >>> set equation details
            self._eq = self.component_equation.source
            self._num = self.component_equation.num
            self._fn = self.component_equation.fn
            self._inputs = self.component_equation.inputs or {}
            self._args = self.component_equation.args or {}
            self._arg_symbols = self.component_equation.arg_symbols or {}
            self._arg_identifiers = (
                self.component_equation.arg_identifiers or []
            )
            self._arg_mappings = self.component_equation.arg_mappings or {}
            self._returns = self.component_equation.returns or {}
            self._return_symbols = self.component_equation.return_symbols or {}
            self._return_identifiers = (
                self.component_equation.return_identifiers or []
            )

            # NOTE: units and symbols for return
            if self._returns:
                returns_inner = next(iter(self._returns.values()))
                self._return_unit = returns_inner.get('unit')
                self._return_symbol = returns_inner.get('symbol')

    # SECTION: properties
    @property
    def status(self) -> bool:
        """
        Get the status of the equation source.

        Returns
        -------
        bool
            True if the equation source is available, False otherwise.
        """
        return self._status

    @property
    def eq(self) -> Optional[TableEquation]:
        """
        Get the equation object.

        Returns
        -------
        TableEquation | None
            The equation object, or None if no equation was found.
        """
        return self._eq

    @property
    def num(self) -> Optional[int]:
        """
        Get the equation number.

        Returns
        -------
        int | None
            The equation number, or None if no equation was found.
        """
        return self._num

    @property
    def fn(self) -> Optional[Callable[..., EquationResult]]:
        """
        Get the equation function.

        Returns
        -------
        Callable[..., EquationResult] | None
            The equation function, or None if no equation was found.
        """
        return self._fn

    @property
    def inputs(self) -> Dict[str, float]:
        """
        Get the input values for the equation.

        Returns
        -------
        Dict[str, float]
            A dictionary of input names and their values.
        """
        return self._inputs

    @property
    def body(self) -> str:
        """
        Get the body of the equation as a string.

        Returns
        -------
        str
            The body of the equation.
        """
        if self._eq is None:
            return ''

        return self._eq.body

    @property
    def args(self) -> Dict[str, Any]:
        """
        Get the arguments required for the equation.

        Returns
        -------
        Dict[str, Any]
            A dictionary of argument names and their details.
        """
        return self._args

    @property
    def arg_symbols(self) -> Dict[str, Any]:
        """
        Get the symbols for the equation arguments.

        Returns
        -------
        Dict[str, Any]
            A dictionary of argument names and their symbols.
        """
        return self._arg_symbols

    @property
    def arg_identifiers(self) -> List[str]:
        """
        Get the identifiers for the equation arguments.

        Returns
        -------
        List[str]
            A list of argument identifiers.
        """
        return self._arg_identifiers

    @property
    def arg_mappings(self) -> Dict[str, Any]:
        """
        Get the argument mappings for the equation.

        Returns
        -------
        Dict[str, Any]
            A dictionary of argument names and their mappings.
        """
        return self._arg_mappings

    @property
    def returns(self) -> Dict[str, Any]:
        """
        Get the return values of the equation.

        Returns
        -------
        Dict[str, Any]
            A dictionary of return value names and their details.
        """
        return self._returns

    @property
    def return_symbol(self) -> Optional[str]:
        """
        Get the symbol for the equation return values.

        Returns
        -------
        str | None
            The symbol for the return value, or None if no equation was found.
        """
        return self._return_symbol

    @property
    def return_unit(self) -> Optional[str]:
        """
        Get the unit for the equation return values.

        Returns
        -------
        str | None
            The unit for the return value, or None if no equation was found.
        """
        return self._return_unit

    @property
    def return_identifiers(self) -> List[str]:
        """
        Get the identifiers for the equation return values.

        Returns
        -------
        List[str]
            A list of return value identifiers.
        """
        return self._return_identifiers

    @property
    def component_equation_source(self) -> Optional[ComponentEquationSource]:
        """
        Get the component equation source.

        Returns
        -------
        ComponentEquationSource | None
            The component equation source for the specified component and
            property, or None if no equation was found.
        """
        return self.component_equation

    # SECTION: get equation from source
    def _get_equation_from_source(self) -> Optional[ComponentEquationSource]:
        """
        Retrieve the component equation for the component from the source.

        Returns
        -------
        ComponentEquationSource | None
            The component equation source for the specified component and equation ID, or None if not found.

        """
        try:
            # SECTION: get equations for component
            equations: Dict[str, ComponentEquationSource] | None = self.source.eq_builder(
                components=[self.component],
                prop_name=self.prop_name,
                component_key=cast(ComponentKey, self.component_key)
            )

            if not equations:
                logger.warning(
                    f'No {self.prop_name} equation found for component ID: {self.component_id}'
                )
                return None

            # SECTION: select for component
            eq: ComponentEquationSource | None = equations.get(
                self.component_id
            )

            # >> check
            if eq is None:
                logger.warning(
                    f'No {self.prop_name} equation found for component ID: {self.component_id}'
                )
                return None

            return eq
        except Exception as e:
            logger.error(
                f'Error retrieving {self.prop_name} equation for component ID: {self.component_id} - {e}'
            )
            return None

    # SECTION: get inputs
    def get_inputs(self):
        """
        Get the input arguments for the equation as dictionary containing variable name and unit.

        Returns
        -------
        Dict[str, str]
            A dictionary of argument names and their units.
        """
        # res
        res = {}

        # iterate over inputs
        for name, details in self._arg_mappings.items():
            # get unit
            unit = details.get('unit', '')
            # symbol
            symbol = details.get('symbol', '')

            res[symbol] = unit

        return res

    # SECTION: calculate
    def calc(
        self,
        **input_args
    ) -> Optional[EquationResult]:
        """
        Calculate with args.

        Parameters
        ----------
        **input_args : Dict[str, float]
            Input arguments for the equation.

        Returns
        -------
        Optional[EquationResult]
            The calculation results, encapsulated in CalcResult as:
            - value: float
            - unit: str
            - symbol: str
        """
        try:
            if self._fn is None:
                logger.warning(
                    f"No {self.prop_name} equation available for component ID: {self.component_id}"
                )
                return None

            # SECTION: variables
            if not input_args:
                logger.error(
                    f"No input arguments provided for calculation."
                )

                # NOTE: execute without input args
                input_args = {}

            # SECTION: calculate
            result: EquationResult = self._fn(
                **input_args
            )

            return result
        except Exception as e:
            logger.error(
                f"Error calculating {e}")
            return None
