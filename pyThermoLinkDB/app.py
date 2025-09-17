# import packages/modules
import logging
from typing import Dict, List, Optional
import pyThermoDB as ptdb
from pyThermoDB import ComponentThermoDB, CompBuilder
from pythermodb_settings.models import (
    Component,
    ComponentConfig,
    ComponentRule,
    ReferenceThermoDB,
    ComponentThermoDBSource
)
# local
from .docs import ThermoDBHub
from .models import ComponentModelSource, ModelSource
from .utils import set_component_key, create_rules_from_str, extract_labels_from_rules, look_up_component_rules
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
        reference_thermodb: Optional[ReferenceThermoDB] = component_thermodb.reference_thermodb

        # check reference thermodb
        if reference_thermodb:

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
            labels: List[str] = reference_thermodb.labels if reference_thermodb.labels else [
            ]

            # ! >>> ignore labels
            ignore_labels: List[str] = reference_thermodb.ignore_labels if reference_thermodb.ignore_labels else [
            ]

            # ! >>> ignore props
            ignore_props: List[str] = reference_thermodb.ignore_props if reference_thermodb.ignore_props else [
            ]
        else:
            # ! set empty
            reference_configs = {}
            reference_rules = {}
            labels = []
            ignore_labels = []
            ignore_props = []

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

        # NOTE: component rules
        component_rules_dict: Dict[str, Dict[str, ComponentRule]] = {
            name_state: reference_rules,
            formula_state: reference_rules,
        }

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
            # ! >> by name-state
            name_state_rules_ = look_up_component_rules(
                component=component,
                rules=rules,
                search_key="Name-State"
            )
            if name_state_rules_:
                # >> set
                component_rules_dict[name_state] = name_state_rules_

            # ! >> by formula-state
            formula_state_rules_ = look_up_component_rules(
                component=component,
                rules=rules,
                search_key="Formula-State"
            )
            if formula_state_rules_:
                # >> set
                component_rules_dict[formula_state] = formula_state_rules_

            # NOTE: check if `component_rules_dict` is still empty, then use default rules if exists
            if (
                len(component_rules_dict[name_state]) == 0 and
                len(component_rules_dict[formula_state]) == 0
            ):
                # !> by default rules key
                default_rules_ = look_up_component_rules(
                    component=component,
                    rules=rules,
                    search_key=DEFAULT_RULES_KEY
                )

                if default_rules_:
                    # >> set
                    component_rules_dict[name_state] = default_rules_
                    component_rules_dict[formula_state] = default_rules_
                else:
                    # log
                    logger.warning(
                        f"No rules found for component {name_state}/{formula_state} in the provided rules."
                    )

            # SECTION: extract labels
            name_state_rules_labels = extract_labels_from_rules(
                component_rules_dict[name_state]
            ) if component_rules_dict[name_state] else []

            formula_state_rules_labels = extract_labels_from_rules(
                component_rules_dict[formula_state]
            ) if component_rules_dict[formula_state] else []
            # >> combine and unique
            component_rules_labels = list(
                set(
                    name_state_rules_labels + formula_state_rules_labels
                )
            )

            # SECTION: check labels
            # check label results
            label_link = True

            # NOTE: check labels
            if (
                check_labels and
                len(labels) > 0 and
                len(component_rules_labels) > 0
            ):
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
        # >> set rule
        rule_ = component_rules_dict.get(
            name_state,
            None
        ) or component_rules_dict.get(
            formula_state,
            None
        )

        # >> check rule
        if not rule_:
            rule_ = None
        # >> if empty, set to None
        if rule_ and len(rule_) == 0:
            rule_ = None

        # NOTE: name state as id
        # >> add
        thermodb_hub.add_thermodb(
            name=name_state,
            data=thermodb,
            rules=rule_,
        )

        # NOTE: formula state as id
        # >> add
        thermodb_hub.add_thermodb(
            name=formula_state,
            data=thermodb,
            rules=rule_,
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
    check_labels: bool = True
) -> List[ComponentModelSource]:
    '''
    Build list of component model source from list of component thermodb and rules

    Parameters
    ----------
    components_thermodb: List[ComponentThermoDB]
        List of ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the component thermodb based on the provided rules, by default True

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
                check_labels=check_labels
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
        )

        # iterate over components model source
        for component_model_source in components_model_source:
            # add to model source
            model_source.data_source.update(component_model_source.data_source)
            model_source.equation_source.update(
                component_model_source.equation_source)

        return model_source
    except Exception as e:
        logger.error(f"Error in build_model_source: {e}")
        raise Exception(f"Error in build_model_source: {e}")


def load_and_build_model_source(
        thermodb_sources: List[ComponentThermoDBSource],
        rules: Optional[
            Dict[str, Dict[str, ComponentRule]] | str
        ] = None,
        check_labels: bool = True
) -> ModelSource:
    '''
    Load component thermodb from thermodb sources and build model source

    Parameters
    ----------
    thermodb_sources: List[ComponentThermoDBSource]
        List of ComponentThermoDBSource object containing component thermodb and source file path
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the component thermodb based on the provided rules, by default True

    Returns
    -------
    ModelSource
        ModelSource object containing data source and equation source for multiple components
    '''
    try:
        # NOTE: check inputs
        if not isinstance(thermodb_sources, list) or len(thermodb_sources) == 0:
            logger.error(
                "thermodb_sources must be a non-empty list of ComponentThermoDBSource objects.")
            raise ValueError(
                "thermodb_sources must be a non-empty list of ComponentThermoDBSource objects.")

        # iterate over thermodb sources and load thermodb
        for thermodb_source in thermodb_sources:
            if not isinstance(thermodb_source, ComponentThermoDBSource):
                logger.error(
                    "Each item in thermodb_sources must be a ComponentThermoDBSource object.")
                raise ValueError(
                    "Each item in thermodb_sources must be a ComponentThermoDBSource object.")
            if not isinstance(thermodb_source.source, str) or len(thermodb_source.source) == 0:
                logger.error(
                    "source in ComponentThermoDBSource must be a non-empty string.")
                raise ValueError(
                    "source in ComponentThermoDBSource must be a non-empty string.")
            if not isinstance(thermodb_source.component, Component):
                logger.error(
                    "component in ComponentThermoDBSource must be a Component object.")
                raise ValueError(
                    "component in ComponentThermoDBSource must be a Component object.")

        # SECTION: load thermodb and create component thermodb
        # NOTE: create list of component thermodb
        components_thermodb: List[ComponentThermoDB] = []

        # SECTION: iterate over thermodb sources
        for thermodb_source in thermodb_sources:
            # NOTE: load thermodb
            try:
                # >> file path
                thermodb_file = thermodb_source.source
                # >> load
                thermodb_ = ptdb.load_thermodb(thermodb_file=thermodb_file)
            except Exception as e:
                logger.error(
                    f"Error in load thermodb from {thermodb_source.source}: {e}")
                continue

            # set component
            component_thermodb = ComponentThermoDB(
                component=thermodb_source.component,
                thermodb=thermodb_,
                reference_thermodb=None
            )
            # append
            components_thermodb.append(component_thermodb)

        # SECTION: build components model source
        components_model_source = build_components_model_source(
            components_thermodb=components_thermodb,
            rules=rules,
            check_labels=check_labels
        )

        # SECTION: build model source
        model_source = build_model_source(
            components_model_source=components_model_source
        )

        # return
        return model_source
    except Exception as e:
        logger.error(f"Error in load_and_build_model_source: {e}")
        raise Exception(f"Error in load_and_build_model_source: {e}")
