# import libs
import logging
from typing import Literal, Optional, Tuple
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import Component
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_sources import EquationSources
from .data_source import DataSource

# NOTE: Logger
logger = logging.getLogger(__name__)

# SECTION: Equation Maker


def mkeqs(
    component: Component,
    model_source: ModelSource,
    component_key: Literal[
        'Name-State',
        'Formula-State',
        'Name',
        'Formula',
        'Name-Formula-State',
        'Formula-Name-State'
    ] = 'Name-State',
) -> Optional[EquationSources]:
    """
    Make an equation source for a given property and component.

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
    Optional[EquationSources]
        An EquationSources object if the component equations are found; otherwise, None.
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
        return EquationSources(
            component=component,
            source=Source_,
            component_key=component_key,
        )
    except Exception as e:
        logger.error(f"Error creating equation: {e}")
        return None


def mkdt(
    component: Component,
    model_source: ModelSource,
    component_key: Literal[
        'Name-State',
        'Formula-State',
        'Name',
        'Formula',
        'Name-Formula-State',
        'Formula-Name-State'
    ] = 'Name-State',
) -> Optional[DataSource]:
    """
    Make a data source for a given component.

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
    Optional[DataSource]
        A DataSource object if the component data is found; otherwise, None.
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

        # SECTION: Create DataSource object
        return DataSource(
            component=component,
            source=Source_,
            component_key=component_key,
        )
    except Exception as e:
        logger.error(f"Error creating data source: {e}")
        return None
