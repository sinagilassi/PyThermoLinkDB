# import packages/modules
import logging
from typing import Dict, Any, List, Literal, Optional
from pyThermoDB import ComponentThermoDB, CompBuilder
from pythermodb_settings.models import Component, ComponentConfig, ComponentRule, ReferenceThermoDB
# local
from .docs import ThermoDBHub
from .models import ComponentModelSource, ModelSource
from .utils import set_component_key, create_rules_from_str, extract_labels_from_rules
from .config import DEFAULT_RULES_KEY

# NOTE: logger
logger = logging.getLogger(__name__)


def init() -> ThermoDBHub:
    '''
    Init thermolinkdb app

    Parameters
    ----------
    None

    Returns
    -------
    ThermoDBHub
        ThermoDBHub object
    '''
    try:
        # init thermolink
        return ThermoDBHub()
    except Exception as e:
        raise Exception("Error: {}".format(e))


def build_component_model_source(
    component_thermodb: ComponentThermoDB,
    rules: Optional[
        Dict[str, Dict[str, ComponentRule]] | str
    ] = None,
    check_labels: bool = True
) -> ComponentModelSource:
    '''
    Build component model source from component thermodb and rules

    Parameters
    ----------
    component_thermodb: ComponentThermoDB
        ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the component thermodb based on the provided rules, by default True

    Returns
    -------
    ComponentModelSource
        ComponentModelSource object containing data source and equation source
    '''
    try:
        # SECTION: create thermodb hub
        try:
            thermodb_hub = init()
        except Exception as e:
            logger.error(f"Error in init thermodb hub: {e}")
            raise Exception(f"Error in init thermodb hub: {e}")

        # SECTION: extract component thermodb
        # NOTE: component thermodb
        component: Component = component_thermodb.component
        # NOTE: thermodb
        thermodb: CompBuilder = component_thermodb.thermodb
        # NOTE: reference thermodb
        reference_thermodb: ReferenceThermoDB = component_thermodb.reference_thermodb

        # ! >>> reference configs
        reference_configs: Dict[
            str,
            ComponentConfig
        ] = reference_thermodb.configs

        # ! >>> reference rules
        reference_rules: Dict[
            str,
            ComponentRule
        ] = reference_thermodb.rules

        # ! >>>  labels
        labels: List[str] = reference_thermodb.labels if reference_thermodb.labels else []

        # ! >>> ignore labels
        ignore_labels: List[str] = reference_thermodb.ignore_labels if reference_thermodb.ignore_labels else []

        # ! >>> ignore props
        ignore_props: List[str] = reference_thermodb.ignore_props if reference_thermodb.ignore_props else []

        # SECTION: set id
        # >> name state
        name_state = set_component_key(
            component,
            component_key='Name-State'
        )
        # >> formula state
        formula_state = set_component_key(
            component,
            component_key='Formula-State'
        )

        # NOTE: component id
        component_id = name_state

        # SECTION: check rules
        if rules:
            # NOTE: load rules
            if isinstance(rules, str):
                try:
                    rules = create_rules_from_str(rules)
                except Exception as e:
                    logger.error(f"Error in load rules from file: {e}")
                    raise Exception(f"Error in load rules from file: {e}")
            elif not isinstance(rules, dict):
                logger.error(
                    "Rules must be a dictionary or a file path to a YAML file.")
                raise ValueError(
                    "Rules must be a dictionary or a file path to a YAML file.")

            # NOTE: check for component rules if exists
            # rules
            rules_keys = list(rules.keys())
            # lowercase keys
            rules_keys_lower = [key.lower() for key in rules_keys]

            # ! check rules records (case insensitive)
            if name_state.lower() in rules_keys_lower:
                component_rules_ = rules[name_state]
                # >> set
                component_id = name_state
                reference_rules = component_rules_
            elif formula_state.lower() in rules_keys_lower:
                component_rules_ = rules[formula_state]
                # >> set
                component_id = formula_state
                reference_rules = component_rules_
            elif DEFAULT_RULES_KEY.lower() in rules_keys_lower:
                component_rules_ = rules[DEFAULT_RULES_KEY]
                # >> set
                reference_rules = component_rules_
            else:
                # >> set (default)
                component_rules_ = None
                logger.warning(
                    f"No specific rules found for component '{name_state} or {formula_state}'. Using empty rules."
                )

            # NOTE: extract labels
            component_rules_labels = extract_labels_from_rules(
                component_rules_
            ) if component_rules_ else []

            # SECTION: check labels
            # check label results
            label_link = True

            # NOTE: check labels
            if check_labels and len(labels) > 0 and len(component_rules_labels) > 0:
                # check if all labels in component_rules_labels are in labels
                for label in component_rules_labels:
                    if label not in labels:
                        # set
                        label_link = False
                        # log
                        logger.error(
                            f"Label '{label}' in rules not found in rules labels"
                        )
        else:
            label_link = False

        # SECTION: add component thermodb to thermodb hub
        # NOTE: add component thermodb to thermodb hub
        thermodb_hub.add_thermodb(
            name=component_id,
            data=thermodb,
            rules=reference_rules
        )

        # SECTION: build component model source
        datasource, equationsource = thermodb_hub.build()

        # NOTE: create component model source
        component_model_source = ComponentModelSource(
            component=component,
            data_source=datasource,
            equation_source=equationsource,
            check_labels=check_labels,
            label_link=label_link,
        )

        return component_model_source
    except Exception as e:
        logger.error(f"Error in build_component_model_source: {e}")
        raise Exception(f"Error in build_component_model_source: {e}")


def build_components_model_source(
    components_thermodb: List[ComponentThermoDB],
    rules: Optional[
        Dict[str, Dict[str, ComponentRule]] | str
    ] = None,
) -> List[ComponentModelSource]:
    '''
    Build list of component model source from list of component thermodb and rules

    Parameters
    ----------
    components_thermodb: List[ComponentThermoDB]
        List of ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.

    Returns
    -------
    List[ComponentModelSource]
        List of ComponentModelSource object containing data source and equation source
    '''
    try:
        # NOTE: create model source for multiple components
        components_model_source: List[ComponentModelSource] = []

        # iterate over components thermodb
        for component_thermodb in components_thermodb:
            # build
            component_model_source = build_component_model_source(
                component_thermodb=component_thermodb,
                rules=rules,
            )

            # append
            components_model_source.append(component_model_source)

        return components_model_source
    except Exception as e:
        logger.error(f"Error in build_components_model_source: {e}")
        raise Exception(f"Error in build_components_model_source: {e}")


def build_model_source(
        components_model_source: List[ComponentModelSource]
) -> ModelSource:
    '''

    Build model source from list of component model source

    Parameters
    ----------
    components_model_source: List[ComponentModelSource]
        List of ComponentModelSource object containing data source and equation source

    Returns
    -------
    ModelSource
        ModelSource object containing data source and equation source for multiple components
    '''
    try:
        # NOTE: create model source for multiple components
        model_source = ModelSource(
            data_source={},
            equation_source={},
            all_check_labels={},
            all_label_link={}
        )

        # iterate over components model source
        for component_model_source in components_model_source:
            # component key
            component_key = set_component_key(
                component_model_source.component,
                component_key='Name-State'
            )

            # add to model source
            model_source.data_source[component_key] = component_model_source.data_source
            model_source.equation_source[component_key] = component_model_source.equation_source


        return model_source
    except Exception as e:
        logger.error(f"Error in build_model_source: {e}")
        raise Exception(f"Error in build_model_source: {e}")