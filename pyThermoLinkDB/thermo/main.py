# import libs
import logging
from typing import Literal, Optional, Tuple
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_sources import EquationSourcesCore
from .equation_source import EquationSourceCore
from .data_source import DataSourceCore

# NOTE: Logger
logger = logging.getLogger(__name__)

# SECTION: Equation Maker


def mkeqs(
    component: Component,
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
) -> Optional[EquationSourcesCore]:
    """
    Make an equation source core for a given property and component.

    Parameters
    ----------
    component : Component
        The chemical component for which properties are to be calculated.
    model_source : ModelSource
        The source containing data for calculations.
    component_key : Literal
        The key to identify the component in the source data. Defaults to 'Name-State'.

    Returns
    -------
    Optional[EquationSourcesCore]
        An EquationSourcesCore object if the component equations are found; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(model_source=model_source)

        # SECTION: Create XProp object
        return EquationSourcesCore(
            component=component,
            source=Source_,
            component_key=component_key,
        )
    except Exception as e:
        logger.error(f"Error creating equation: {e}")
        return None


def mkeq(
    name: str,
    component: Component,
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
) -> Optional[EquationSourceCore]:
    """
    Make an equation source core for a given property and component.

    Parameters
    ----------
    name : str
        The name of the property for which equations are to be calculated.
    component : Component
        The chemical component for which properties are to be calculated.
    model_source : ModelSource
        The source containing data for calculations.
    component_key : Literal
        The key to identify the component in the source data. Defaults to 'Name-State'.

    Returns
    -------
    Optional[EquationSourceCore]
        An EquationSourceCore object if the component equations are found; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not name:
            logger.error("Property name must be provided.")
            return None

        if not isinstance(name, str):
            logger.error("Property name must be a string.")
            return None

        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(model_source=model_source)

        # NOTE: component id
        component_id: str = set_component_id(component, component_key)

        # NOTE: check if property exists in source
        check_prop = Source_.is_prop_eq_available(
            component_id=component_id,
            prop_name=name,
        )

        # >> check result
        if not check_prop:
            logger.error(
                f"Property '{name}' not found for component '{component_id}' in the source.")
            return None

        # SECTION: Create EquationSourceCore object
        return EquationSourceCore(
            prop_name=name,
            component=component,
            source=Source_,
            component_key=component_key,
        )
    except Exception as e:
        logger.error(f"Error creating equation: {e}")
        return None


# SECTION: Data Source Maker

def mkdt(
    component: Component,
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
) -> Optional[DataSourceCore]:
    """
    Make a data source core for a given component.

    Parameters
    ----------
    component : Component
        The chemical component for which properties are to be calculated.
    model_source : ModelSource
        The source containing data for calculations.
    component_key : Literal
        The key to identify the component in the source data. Defaults to 'Name-State'.

    Returns
    -------
    Optional[DataSourceCore]
        A DataSourceCore object if the component data is found; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(model_source=model_source)

        # SECTION: Create DataSourceCore object
        return DataSourceCore(
            component=component,
            source=Source_,
            component_key=component_key,
        )
    except Exception as e:
        logger.error(f"Error creating data source: {e}")
        return None
