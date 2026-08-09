# import libs
import logging
from typing import Literal, Optional
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import Component, ComponentKey, MixtureKey
from pythermodb_settings.utils import create_mixture_id, set_component_id
# local
from ..thermo import Source
from .equation_sources import EquationSourcesCore
from .equation_source import EquationSourceCore
from .data_source import DataSourceCore
from .constants_source import ConstantsSourceCore
from .matrix_data_source import MatrixDataSourceCore

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
    build_check: bool = False,
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
    build_check : bool
        Whether to check the build status of each equation source after creation. Defaults to False.

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
        res: dict[str, EquationSourcesCore] = {}

        # iterate components
        for component in components:
            # create equation source
            eq_source = EquationSourcesCore(
                component=component,
                source=Source_,
                component_key=component_key,
                build_all=build_all,
                build_list=build_list,
            )

            # set component id
            component_id: str = set_component_id(component, component_key)

            # check build status if requested
            if build_check:
                # build status
                build_status: bool = eq_source.build_status()

                # >> check result
                if not build_status:
                    # build summary
                    summary = eq_source.summary()

                    error_msg = """
                    Failed to build equation source for component '{component_id}'.
                    Build summary:
                    {summary}
                    """.format(component_id=component_id, summary=summary)

                    logger.error(error_msg)

            # add to results
            res[component_id] = eq_source

        return res
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
    check_build: bool = False,
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
    check_build : bool
        Whether to check the build status of each data source after creation. Defaults to False.

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
        res: dict[str, DataSourceCore] = {}

        # iterate components
        for component in components:
            # create data source
            data_source = DataSourceCore(
                component=component,
                source=Source_,
                component_key=component_key,
                extract_list=extract_list,
            )

            # set component id
            component_id: str = set_component_id(component, component_key)

            # check build status if requested
            if check_build:
                # build status
                build_status: bool = data_source.build_status()

                # >> check result
                if not build_status:
                    # build summary
                    summary = data_source.summary()

                    error_msg = """
                    Failed to build data source for component '{component_id}'.
                    Build summary:
                    {summary}
                    """.format(component_id=component_id, summary=summary)

                    logger.error(error_msg)

            # add to results
            res[component_id] = data_source

        return res
    except Exception as e:
        logger.error(f"Error creating data sources: {e}")
        return None

# SECTION: Constants Source Maker


def mkct(
    model_source: ModelSource,
    extract_list: Optional[list[str]] = None,
) -> Optional[ConstantsSourceCore]:
    """
    Make a constants source core.

    Parameters
    ----------
    model_source : ModelSource
        The source containing data for calculations.
    extract_list : Optional[list[str]]
        A list of specific constant names to extract. If provided, only these constants will be extracted. Defaults to None, which means all available constants will be extracted.

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
            extract_list=extract_list,
        )
    except Exception as e:
        logger.error(f"Error creating constants source: {e}")
        return None


# SECTION: Matrix data source maker
def mkmdt(
    components: list[Component],
    model_source: ModelSource,
    mixture_key: MixtureKey = 'Name',
    extract_list: Optional[list[str]] = None,
    delimiter: str = '|',
    case: Optional[Literal['lower', 'upper']] = None,
) -> Optional[MatrixDataSourceCore]:
    """
    Make a matrix data source core for a given mixture.

    Parameters
    ----------
    components : list[Component]
        Components used to generate the mixture id registered in the
        datasource.
    model_source : ModelSource
        The source containing matrix data.
    mixture_key : Literal
        The key to identify mixtures in the source data. Defaults to 'Name'.
    extract_list : Optional[list[str]]
        A list of matrix property names to extract. Defaults to None, which
        means all available matrix properties will be extracted.
    delimiter : str
        Delimiter used in mixture ids. Defaults to '|'.
    case : Optional[Literal['lower', 'upper']]
        Optional case normalization for the generated mixture id.

    Returns
    -------
    Optional[MatrixDataSourceCore]
        A MatrixDataSourceCore object if the matrix data source can be created;
        otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(components, list):
            logger.error("Invalid components provided.")
            return None

        if not components:
            logger.error("Components must be provided.")
            return None

        if not all(isinstance(component, Component) for component in components):
            logger.error("Invalid component found in components.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            mixture_key=mixture_key,
        )

        # SECTION: Create MatrixDataSourceCore object
        return MatrixDataSourceCore(
            components=components,
            source=Source_,
            mixture_key=mixture_key,
            extract_list=extract_list,
            delimiter=delimiter,
            case=case,
        )
    except Exception as e:
        logger.error(f"Error creating matrix data source: {e}")
        return None


# NOTE: Multiple Matrix Data Source Maker
def mkmdts(
    mixture_components: list[list[Component]],
    model_source: ModelSource,
    mixture_key: MixtureKey = 'Name',
    extract_list: Optional[list[str]] = None,
    check_build: bool = False,
    delimiter: str = '|',
    case: Optional[Literal['lower', 'upper']] = None,
) -> Optional[dict[str, MatrixDataSourceCore]]:
    """
    Make matrix data source cores for multiple mixtures.

    Parameters
    ----------
    mixture_components : list[list[Component]]
        List of mixtures, where each mixture is represented by a list of
        Component objects used to generate the datasource mixture id.
    model_source : ModelSource
        The source containing matrix data.
    mixture_key : Literal
        The key to identify mixtures in the source data. Defaults to 'Name'.
    extract_list : Optional[list[str]]
        A list of matrix property names to extract for each mixture. Defaults
        to None, which means all available matrix properties will be extracted.
    check_build : bool
        Whether to check the build status of each matrix data source after
        creation. Defaults to False.
    delimiter : str
        Delimiter used in mixture ids. Defaults to '|'.
    case : Optional[Literal['lower', 'upper']]
        Optional case normalization for each generated mixture id.

    Returns
    -------
    Optional[dict[str, MatrixDataSourceCore]]
        A dictionary of MatrixDataSourceCore objects keyed by generated mixture
        id; otherwise, None.
    """
    try:
        # SECTION: Validate inputs
        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(mixture_components, list):
            logger.error("Invalid mixture_components provided.")
            return None

        if not mixture_components:
            logger.error("Mixture components must be provided.")
            return None

        for components in mixture_components:
            if not isinstance(components, list) or not components:
                logger.error(
                    "Each mixture must be a non-empty list of components.")
                return None

            if not all(isinstance(component, Component) for component in components):
                logger.error("Invalid component found in mixture_components.")
                return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            mixture_key=mixture_key,
        )

        # SECTION: Create MatrixDataSourceCore objects
        res: dict[str, MatrixDataSourceCore] = {}

        # iterate mixtures
        for components in mixture_components:
            # create matrix data source
            matrix_data_source = MatrixDataSourceCore(
                components=components,
                source=Source_,
                mixture_key=mixture_key,
                extract_list=extract_list,
                delimiter=delimiter,
                case=case,
            )

            # set mixture id
            mixture_id: str = create_mixture_id(
                components=components,
                mixture_key=mixture_key,
                delimiter=delimiter,
                case=case,
            )

            # check build status if requested
            if check_build:
                # build status
                build_status: bool = matrix_data_source.build_status()

                # >> check result
                if not build_status:
                    # build summary
                    summary = matrix_data_source.summary()

                    error_msg = """
                    Failed to build matrix data source for mixture '{mixture_id}'.
                    Build summary:
                    {summary}
                    """.format(mixture_id=mixture_id, summary=summary)

                    logger.error(error_msg)

            # add to results
            res[mixture_id] = matrix_data_source

        return res
    except Exception as e:
        logger.error(f"Error creating matrix data sources: {e}")
        return None
