# import packages/modules
import logging
from typing import Dict, Any, List, Literal
from pyThermoDB import ComponentThermoDB, CompBuilder
from pyThermoDB.models import Component
# local
from .docs import ThermoDBHub
from .models import ComponentModelSource, ComponentThermoDBRules
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
    rules: Dict[str, ComponentThermoDBRules] | str,
    component_key:  Literal[
        "Name-State",
        "Formula-State",
        "Name-Formula-State"
    ],
    check_labels: bool = True
) -> ComponentModelSource:
    '''
    Build component model source from component thermodb and rules

    Parameters
    ----------
    component_thermodb: ComponentThermoDB
        ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, ComponentThermoDBRules] | str
        Rules for selecting data and equations. It can be a dictionary or a file path to a YAML file.
    check_labels: bool, optional
        Whether to check labels in the component thermodb, by default True

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
        # NOTE: labels
        labels: List[str] = component_thermodb.labels if component_thermodb.labels else []

        # SECTION: check rules
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

        # SECTION: add component thermodb to thermodb hub
        # set name
        name_ = set_component_key(
            component,
            component_key=component_key
        )

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
            component_rules_) if component_rules_ else []

        # SECTION: check labels
        if check_labels and len(labels) > 0:
            # iterate over labels
            for label in labels:
                if label not in component_rules_labels:
                    logger.warning(
                        f"Label '{label}' in component thermodb not found in rules for component '{name_}'."
                    )

        # NOTE: add component thermodb to thermodb hub
        thermodb_hub.add_thermodb(
            name=name_,
            data=thermodb,
            rules=component_rules_
        )

        # SECTION: build component model source
        datasource, equationsource = thermodb_hub.build()

        # NOTE: create component model source
        component_model_source = ComponentModelSource(
            component=component,
            data_source=datasource,
            equation_source=equationsource
        )

        return component_model_source
    except Exception as e:
        logger.error(f"Error in build_component_model_source: {e}")
        raise Exception(f"Error in build_component_model_source: {e}")
