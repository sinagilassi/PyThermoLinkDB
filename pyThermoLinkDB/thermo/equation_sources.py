# import libs
import logging
from typing import Dict, Literal, Any, Optional, List
from pythermodb_settings.models import Component, ComponentKey
from pyThermoDB.core import TableEquation
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_source import EquationSourceCore

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
                component_key=self.component_key,  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error creating equation: {e}")
            return None
