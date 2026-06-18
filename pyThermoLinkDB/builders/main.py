# import libs
import logging
from typing import List, Optional
from pythermodb_settings.models import Component, ComponentKey
from pythermodb_settings.utils import generate_component_references, measure_time
# locals
from .thermo_model_source import ThermoModelSource
from .thermo_custom_source import ThermoCustomSource
from ..models import ModelSource

# NOTE: logger setup
logger = logging.getLogger(__name__)

# SECTION: build thermo model source


@measure_time
def build_thermo_model_source(
        components: List[Component],
        component_key: ComponentKey,
        model_source: ModelSource,
        thermo_data: List[str],
        thermo_equations: List[str],
        thermo_constants: List[str],
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
    thermo_data : List[str]
        List of thermodynamic data symbols to be extracted from the model source.
    thermo_equations : List[str]
        List of thermodynamic equations symbols to be extracted from the model source.
    thermo_constants : List[str]
        List of thermodynamic constants symbols to be extracted from the model source.
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

        # NOTE: create ThermoModelSource instance
        thermo_model_source = ThermoModelSource(
            components=components,
            component_key=component_key,
            model_source=model_source,
            thermo_data=thermo_data,
            thermo_equations=thermo_equations,
            thermo_constants=thermo_constants,
            component_references=component_references,
            description=description
        )

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
        custom_source: dict,
        thermo_data: List[str],
        thermo_constants: List[str],
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
    custom_source : dict
        A dictionary containing custom thermodynamic data, equations, and constants.
    thermo_data : List[str]
        List of thermodynamic data symbols to be extracted from the custom source.
    thermo_constants : List[str]
        List of thermodynamic constants symbols to be extracted from the custom source.
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

        # ! build all custom thermo
        thermo_custom_source.build_all()

        # ! configure all attributes
        thermo_custom_source.config_attributes()

        return thermo_custom_source
    except Exception as e:
        logger.error(f"Error building custom thermodynamic model source: {e}")
        return None
