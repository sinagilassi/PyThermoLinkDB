# import libs
import logging
from typing import Optional
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import set_component_id
# local
from ..thermo import Source
from .equation_sources import EquationSourcesCore
from .equation_source import EquationSourceCore
from .data_source import DataSourceCore
from .constants_source import ConstantsSourceCore

# NOTE: Logger
logger = logging.getLogger(__name__)

# SECTION: Equation Maker


def mkeqs(
    component: Component,
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
    build_all: bool = False,
    build_list: Optional[list[str]] = None,
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
    build_all : bool
        Whether to build all available equations for the component. Defaults to False.
    build_list : Optional[list[str]]
        A list of specific equation names to build. If provided, only these equations will be built. Defaults to None.

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
        Source_ = Source(
            model_source=model_source,
            component_key=component_key,
        )

        # SECTION: Create XProp object
        return EquationSourcesCore(
            component=component,
            source=Source_,
            component_key=component_key,
            build_all=build_all,
            build_list=build_list,
        )
    except Exception as e:
        logger.error(f"Error creating equation: {e}")
        return None

# NOTE: Multiple Equation Maker


def mkeqss(
    components: list[Component],
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
    build_all: bool = False,
    build_list: Optional[list[str]] = None,
) -> Optional[dict[str, EquationSourcesCore]]:
    """
    Make equation source cores for a list of components.

    Parameters
    ----------
    components : list[Component]
        The chemical components for which properties are to be calculated.
    model_source : ModelSource
        The source containing data for calculations.
    component_key : Literal
        The key to identify the components in the source data. Defaults to 'Name-State'.
    build_all : bool
        Whether to build all available equations for each component. Defaults to False.
    build_list : Optional[list[str]]
        A list of specific equation names to build. If provided, only these equations will be built. Defaults to None.

    Returns
    -------
    Optional[dict[str, EquationSourcesCore]]
        A dictionary of EquationSourcesCore objects keyed by component id; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(components, list):
            logger.error("Invalid components provided.")
            return None

        if not all(isinstance(component, Component) for component in components):
            logger.error("Invalid component found in components.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key,
        )

        # SECTION: Create EquationSourcesCore objects
        return {
            set_component_id(component, component_key): EquationSourcesCore(
                component=component,
                source=Source_,
                component_key=component_key,
                build_all=build_all,
                build_list=build_list,
            )
            for component in components
        }
    except Exception as e:
        logger.error(f"Error creating equations: {e}")
        return None

# NOTE: Single Equation Maker


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
        Source_ = Source(
            model_source=model_source,
            component_key=component_key,
        )

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
    extract_list: Optional[list[str]] = None,
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
    extract_list : Optional[list[str]]
        A list of specific property names to extract. If provided, only these properties will be extracted. Defaults to None, which means all available properties will be extracted.

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
        Source_ = Source(
            model_source=model_source,
            component_key=component_key,
        )

        # SECTION: Create DataSourceCore object
        return DataSourceCore(
            component=component,
            source=Source_,
            component_key=component_key,
            extract_list=extract_list,
        )
    except Exception as e:
        logger.error(f"Error creating data source: {e}")
        return None

# NOTE: Multiple Data Source Maker


def mkdts(
    components: list[Component],
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-State',
    extract_list: Optional[list[str]] = None,
) -> Optional[dict[str, DataSourceCore]]:
    """
    Make data source cores for a list of components.

    Parameters
    ----------
    components : list[Component]
        The chemical components for which properties are to be calculated.
    model_source : ModelSource
        The source containing data for calculations.
    component_key : Literal
        The key to identify the components in the source data. Defaults to 'Name-State'.
    extract_list : Optional[list[str]]
        A list of specific property names to extract. If provided, only these properties will be extracted. Defaults to None, which means all available properties will be extracted.

    Returns
    -------
    Optional[dict[str, DataSourceCore]]
        A dictionary of DataSourceCore objects keyed by component id; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(components, list):
            logger.error("Invalid components provided.")
            return None

        if not all(isinstance(component, Component) for component in components):
            logger.error("Invalid component found in components.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key,
        )

        # SECTION: Create DataSourceCore objects
        return {
            set_component_id(component, component_key): DataSourceCore(
                component=component,
                source=Source_,
                component_key=component_key,
                extract_list=extract_list,
            )
            for component in components
        }
    except Exception as e:
        logger.error(f"Error creating data sources: {e}")
        return None

# SECTION: Constants Source Maker


def mkct(
    model_source: ModelSource,
) -> Optional[ConstantsSourceCore]:
    """
    Make a constants source core.

    Parameters
    ----------
    model_source : ModelSource
        The source containing data for calculations.

    Returns
    -------
    Optional[ConstantsSourceCore]
        A ConstantsSourceCore object if the component constants are found; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
        )

        # SECTION: Create ConstantsSourceCore object
        return ConstantsSourceCore(
            source=Source_,
        )
    except Exception as e:
        logger.error(f"Error creating constants source: {e}")
        return None
