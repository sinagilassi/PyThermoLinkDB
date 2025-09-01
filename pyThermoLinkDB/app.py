# import packages/modules
import logging
from typing import Dict, Any, List, Literal, Optional
from pyThermoDB import ComponentThermoDB, CompBuilder
from pyThermoDB.models import Component
# local
from .docs import ThermoDBHub
from .models import ComponentModelSource, ComponentThermoDBRules, ModelSource
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
    component_key:  Literal[
        "Name-State",
        "Formula-State",
        "Name-Formula-State"
    ],
    rules: Optional[
        Dict[str, ComponentThermoDBRules] | str
    ] = None,
) -> ComponentModelSource:
    '''
    Build component model source from component thermodb and rules

    Parameters
    ----------
    component_thermodb: ComponentThermoDB
        ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    component_key: Literal["Name-State", "Formula-State", "Name-Formula-State"]
        Component key to identify the component in the thermodb hub
    rules: Optional[Dict[str, ComponentThermoDBRules] | str], optional
        Rules to map data/equations in the thermodb to the model source.

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
        # NOTE: reference configs
        reference_configs: Dict[
            str,
            Any
        ] = component_thermodb.reference_configs
        # NOTE: reference rules
        reference_rules: Dict[
            str,
            Dict[str, str]
        ] = component_thermodb.reference_rules
        # NOTE: labels
        labels: List[str] = component_thermodb.labels if component_thermodb.labels else []

        # NOTE: set name
        name_ = set_component_key(
            component,
            component_key=component_key
        )

        # SECTION: check rules
        if rules:
            # set
            check_labels = True

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

            # check rules records
            if name_ in rules_keys:
                component_rules_ = rules[name_]
            elif DEFAULT_RULES_KEY in rules_keys:
                component_rules_ = rules[DEFAULT_RULES_KEY]
            else:
                component_rules_ = None
                logger.warning(
                    f"No specific rules found for component '{name_}'. Using empty rules."
                )

            # NOTE: extract labels
            component_rules_labels = extract_labels_from_rules(
                component_rules_
            ) if component_rules_ else []

            # SECTION: check labels
            # check label results
            label_link = True

            # check labels
            if check_labels and len(labels) > 0 and len(component_rules_labels) > 0:
                # check if all labels in component_rules_labels are in labels
                for label in component_rules_labels:
                    if label not in labels:
                        # set
                        label_link = False
                        # log
                        logger.error(
                            f"Label '{label}' in rules not found in rules labels")
        else:
            # set
            check_labels = False
            label_link = False

        # SECTION: add component thermodb to thermodb hub
        # NOTE: add component thermodb to thermodb hub
        thermodb_hub.add_thermodb(
            name=name_,
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
    component_key:  Literal[
        "Name-State",
        "Formula-State",
        "Name-Formula-State"
    ],
    rules: Optional[
        Dict[str, ComponentThermoDBRules] | str
    ] = None,
) -> ModelSource:
    '''
    Build list of component model source from list of component thermodb and rules

    Parameters
    ----------
    components_thermodb: List[ComponentThermoDB]
        List of ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    component_key: Literal["Name-State", "Formula-State", "Name-Formula-State"]
        Component key to identify the component in the thermodb hub
    rules: Optional[Dict[str, ComponentThermoDBRules] | str], optional
        Rules to map data/equations in the thermodb to the model source.

    Returns
    -------
    ModelSource
        ModelSource object containing data source and equation source for multiple components
    '''
    try:
        # NOTE: create model source for multiple components
        data_source_all = {}
        equation_source_all = {}
        all_check_labels = {}
        all_label_link = {}

        # iterate over components thermodb
        for component_thermodb in components_thermodb:
            # build
            component_model_source = build_component_model_source(
                component_thermodb=component_thermodb,
                component_key=component_key,
                rules=rules,
            )

            # NOTE: extract model source
            # set
            name_ = set_component_key(
                component_model_source.component,
                component_key=component_key
            )
            data_source_all[name_] = component_model_source.data_source
            equation_source_all[name_] = component_model_source.equation_source
            all_check_labels[name_] = component_model_source.check_labels
            all_label_link[name_] = component_model_source.label_link

        # NOTE: create model source
        model_source = ModelSource(
            data_source=data_source_all,
            equation_source=equation_source_all,
            all_check_labels=all_check_labels,
            all_label_link=all_label_link,
        )

        return model_source
    except Exception as e:
        logger.error(f"Error in build_components_model_source: {e}")
        raise Exception(f"Error in build_components_model_source: {e}")
