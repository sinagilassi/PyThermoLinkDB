# import libs
import logging
from typing import List, Optional, Dict, Any
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import generate_component_references, measure_time
# locals
from .thermo_model_source import ThermoModelSource
from .thermo_custom_source import ThermoCustomSource
from .thermo_source import ThermoSource
from ..models import ModelSource, CustomSource
from ..models.source import ModelSourceConfig, CustomSourceConfig

# NOTE: logger setup
logger = logging.getLogger(__name__)


# SECTION: build thermo model source


@measure_time
def build_thermo_model_source(
        components: List[Component],
        component_key: ComponentKey,
        model_source: ModelSource,
        thermo_data: Optional[List[str]] = None,
        thermo_equations: Optional[List[str]] = None,
        thermo_constants: Optional[List[str]] = None,
        description: Optional[str] = None,
        **kwargs
) -> Optional[ThermoModelSource]:
    """
    Build a thermodynamic model source.

    Parameters
    ----------
    components : List[Component]
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
    thermo_data : List[str] | None
        List of thermodynamic data symbols to be extracted from the model source, or None to extract all available data.
    thermo_equations : List[str] | None
        List of thermodynamic equations symbols to be extracted from the model source, or None to extract all available equations.
    thermo_constants : List[str] | None
        List of thermodynamic constants symbols to be extracted from the model source, or None to extract all available constants.
    description : Optional[str]
        Optional description of the thermodynamic model source.
    **kwargs : Dict[str, Any]
        Additional keyword arguments for future extensibility.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.

    Returns
    -------
    Optional[ThermoModelSource]
        An instance of ThermoModelSource if successful, None otherwise.
    """
    try:
        # NOTE: generate component references
        component_references = generate_component_references(
            components=components,
            component_key=component_key
        )

        # NOTE: normalize
        thermo_data = [] if thermo_data is None else thermo_data
        thermo_equations = [] if thermo_equations is None else thermo_equations
        thermo_constants = [] if thermo_constants is None else thermo_constants

        # NOTE: create ThermoModelSource instance
        thermo_model_source = ThermoModelSource(
            components=components,
            component_key=component_key,
            thermo_data=thermo_data,
            thermo_equations=thermo_equations,
            thermo_constants=thermo_constants,
            component_references=component_references,
            description=description
        )

        # ! config model source with model data
        thermo_model_source.model_source = model_source

        # ! build all thermo
        thermo_model_source.build_all()

        # ! configure all attributes
        thermo_model_source.config_attributes()

        return thermo_model_source
    except Exception as e:
        logger.error(f"Error building thermodynamic model source: {e}")
        return None

# SECTION: build custom model source


@measure_time
def build_custom_model_source(
        components: List[Component],
        component_key: ComponentKey,
        custom_source: CustomSource,
        thermo_data: Optional[List[str]],
        thermo_constants: Optional[List[str]],
        description: Optional[str] = None,
        **kwargs
) -> Optional[ThermoCustomSource]:
    """
    Build a custom thermodynamic model source.

    Parameters
    ----------
    components : List[Component]
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
    custom_source : CustomSource
        A dictionary containing custom thermodynamic data, equations, and constants.
    thermo_data : List[str] | None
        List of thermodynamic data symbols to be extracted from the custom source, or None to extract all available data.
    thermo_constants : List[str] | None
        List of thermodynamic constants symbols to be extracted from the custom source, or None to extract all available constants.
    description : Optional[str]
        Optional description of the custom thermodynamic model source.
    **kwargs : Dict[str, Any]
        Additional keyword arguments for future extensibility.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.

    Returns
    -------
    Optional[ThermoCustomSource]
        An instance of ThermoCustomSource if successful, None otherwise.
    """
    try:
        # NOTE: generate component references
        component_references = generate_component_references(
            components=components,
            component_key=component_key
        )

        # NOTE: normalize
        thermo_data = [] if thermo_data is None else thermo_data
        thermo_constants = [] if thermo_constants is None else thermo_constants

        # NOTE: create ThermoCustomSource instance
        thermo_custom_source = ThermoCustomSource(
            components=components,
            component_key=component_key,
            custom_source=custom_source,
            thermo_data=thermo_data,
            thermo_constants=thermo_constants,
            component_references=component_references,
            description=description
        )

        # ! config custom model source with custom data
        thermo_custom_source.custom_source = custom_source

        # ! build all custom thermo
        thermo_custom_source.build_all()

        # ! configure all attributes
        thermo_custom_source.config_attributes()

        return thermo_custom_source
    except Exception as e:
        logger.error(f"Error building custom thermodynamic model source: {e}")
        return None


# SECTION: main build function

@measure_time
def build_thermo_source(
        components: List[Component],
        component_key: ComponentKey,
        model_source: Optional[ModelSource],
        custom_source: Optional[CustomSource],
        model_source_config: Optional[ModelSourceConfig],
        custom_source_config: Optional[CustomSourceConfig],
        description: Optional[str] = None,
        **kwargs
) -> Optional[ThermoSource]:
    """
    Build a thermodynamic source, which can be either a model source or a custom source.

    Parameters
    ----------
    components : List[Component]
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
    model_source : Optional[ModelSource]
        The source of the thermodynamic model data, or None if not applicable.
    custom_source : Optional[CustomSource]
        A dictionary containing custom thermodynamic data, equations, and constants, or None if not applicable.
    model_source_config : Optional[ModelSourceConfig]
        Configuration for the model source, including which data, equations, and constants to extract.
    custom_source_config : Optional[CustomSourceConfig]
        Configuration for the custom source, including which data and constants to extract.
    description : Optional[str]
        Optional description of the thermodynamic source.
    **kwargs : Dict[str, Any]
        Additional keyword arguments for future extensibility.
            - mode : Literal['silent', 'log', 'attach'], optional
                Mode for time measurement logging. Default is 'silent'.
            - model_source_key : str, optional
                Key to use for the model source in the ThermoSource instance. Default is 'model_source'.
            - custom_source_key : str, optional
                Key to use for the custom source in the ThermoSource instance. Default is 'custom_source'.

    Returns
    -------
    Optional[ThermoSource]
        An instance of ThermoSource if successful, None otherwise.

    Notes
    -----
    - At least one of model_source or custom_source must be provided. If both are provided, they will be used for thermo_data, thermo_equations, and thermo_constants.
    """
    try:
        # NOTE: validate that at least one source is provided
        if model_source is None and custom_source is None:
            logger.error(
                "At least one of model_source or custom_source must be provided."
            )
            return None

        # NOTE: kwargs for source keys
        model_source_key = kwargs.get('model_source_key', 'model_source')
        custom_source_key = kwargs.get('custom_source_key', 'custom_source')

        # NOTE: build thermo model source and custom model source
        thermo_model_source = None
        thermo_custom_source = None

        # NOTE: build thermo model source if model_source is provided
        if model_source is not None:
            # ! extract model source configuration
            thermo_data = model_source_config.data if model_source_config else []
            thermo_equations = model_source_config.equations if model_source_config else []
            thermo_constants = model_source_config.constants if model_source_config else []

            # build thermo model source
            thermo_model_source: Optional[ThermoModelSource] = build_thermo_model_source(
                components=components,
                component_key=component_key,
                model_source=model_source,
                thermo_data=thermo_data,
                thermo_equations=thermo_equations,
                thermo_constants=thermo_constants,
                description=description
            )

        # NOTE: build custom model source if custom_source is provided
        if custom_source is not None:
            # ! extract custom source configuration
            thermo_data = custom_source_config.data if custom_source_config else []
            thermo_constants = custom_source_config.constants if custom_source_config else []

            # build custom model source
            thermo_custom_source: Optional[ThermoCustomSource] = build_custom_model_source(
                components=components,
                component_key=component_key,
                custom_source=custom_source,
                thermo_data=thermo_data,
                thermo_constants=thermo_constants,
                description=description
            )

        # NOTE: create ThermoSource instance
        thermo_source_instance = ThermoSource(
            components=components,
            component_key=component_key,
            thermo_model_source=thermo_model_source,
            thermo_custom_source=thermo_custom_source,
            description=description,
            model_source_key=model_source_key,
            custom_source_key=custom_source_key
        )

        # ! extract attributes from model source and custom source to populate the source dictionary
        thermo_source_instance._extract_attributes()

        return thermo_source_instance
    except Exception as e:
        logger.error(f"Error building thermodynamic source: {e}")
        return None
