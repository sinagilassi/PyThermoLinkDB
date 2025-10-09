# import packages/modules
import logging
from typing import Dict, List, Optional, Literal
import pyThermoDB as ptdb
from pyThermoDB import ComponentThermoDB, CompBuilder, MixtureThermoDB
from pythermodb_settings.models import (
    Component,
    ComponentConfig,
    ComponentRule,
    ReferenceThermoDB,
    ComponentThermoDBSource,
    MixtureThermoDBSource
)
# local
from .docs import ThermoDBHub
from .models import ModelSource, ComponentModelSource, MixtureModelSource
from .utils import (
    set_component_key,
    create_rules_from_str,
    extract_labels_from_rules,
    look_up_component_rules,
    find_mixture_ids_in_rules,
    normalize_rules,
    look_up_mixture_rules
)
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
    check_labels: bool = True,
    overwrite_rules: bool = False,
    verbose: bool = False
) -> ComponentModelSource:
    '''
    Build component model source from component thermodb and rules (optional).

    Parameters
    ----------
    component_thermodb: ComponentThermoDB
        ComponentThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the component thermodb based on the provided rules, by default True
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    ComponentModelSource
        ComponentModelSource object containing data source and equation source

    Notes
    -----
    - If rules is not provided, the reference rules in the component thermodb will be used
    - If rules is provided, it will be used to map data/equations in the thermodb to the model source
    - If check_labels is True, the labels in the component thermodb will be checked based on the provided rules
    - If verbose is True, detailed information will be printed during the process
    - Reference thermodb is optional, if not provided, only the component and thermodb will be used
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
        # ! reference thermodb is optional
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
            # >> for the case of no reference (reference_thermodb), set empty rules
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
        # create dict to hold component rules both name-state and formula-state
        component_rules_dict: Dict[str, Dict[str, ComponentRule]] = {
            name_state: reference_rules,
            formula_state: reference_rules,
        }

        # SECTION: check rules
        if rules:
            # NOTE: verbose
            if verbose:
                logger.info(
                    f"Checking rules for component: {name_state} using provided rules")

            # NOTE: overwrite existing rules in the thermodb hub
            if overwrite_rules:
                # reset component_rules_dict
                component_rules_dict = {
                    name_state: {},
                    formula_state: {}
                }

                # >> log
                if verbose:
                    logger.info(
                        "Overwriting existing rules in the thermodb hub"
                    )

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
                # ! >> by default rules key
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
            # NOTE: verbose
            if verbose:
                logger.info(
                    f"No rules provided, using reference rules for component: {name_state}")

            # no rules provided, use reference rules
            # check label results
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

        # ! >> check rule
        if not rule_:
            rule_ = None
        # >> if empty, set to None
        if rule_ and len(rule_) == 0:
            rule_ = None

        # NOTE: name state as id
        # >> add
        add_thermodb_res_ = thermodb_hub.add_thermodb(
            name=name_state,
            data=thermodb,
            rules=rule_,
        )

        # >> log
        if verbose:
            if add_thermodb_res_:
                logger.info(f"Added thermodb for component: {name_state}")
            else:
                logger.warning(
                    f"Failed to add thermodb for component: {name_state}")

        # NOTE: formula state as id
        # >> add
        add_thermodb_res_ = thermodb_hub.add_thermodb(
            name=formula_state,
            data=thermodb,
            rules=rule_,
        )

        # >> log
        if verbose:
            if add_thermodb_res_:
                logger.info(f"Added thermodb for component: {formula_state}")
            else:
                logger.warning(
                    f"Failed to add thermodb for component: {formula_state}")

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
    check_labels: bool = True,
    overwrite_rules: bool = False,
    verbose: bool = False,
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
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

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
            # ! build
            component_model_source = build_component_model_source(
                component_thermodb=component_thermodb,
                rules=rules,
                check_labels=check_labels,
                overwrite_rules=overwrite_rules,
                verbose=verbose
            )

            # append
            components_model_source.append(component_model_source)

        return components_model_source
    except Exception as e:
        logger.error(f"Error in build_components_model_source: {e}")
        raise Exception(f"Error in build_components_model_source: {e}")


def build_mixture_model_source(
    mixture_thermodb: MixtureThermoDB,
    rules: Optional[
        Dict[str, Dict[str, ComponentRule]] | str
    ] = None,
    check_labels: bool = True,
    mixture_key: Literal['Name', 'Formula'] = 'Name',
    delimiter: str = '|',
    overwrite_rules: bool = False,
    verbose: bool = False,
) -> MixtureModelSource:
    '''
    Build mixture model source from mixture thermodb and rules (optional).

    Parameters
    ----------
    mixture_thermodb: MixtureThermoDB
        MixtureThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the mixture thermodb based on the provided rules, by default True
    mixture_key: Literal['Name', 'Formula'], optional
        Key to use for mixture id, either 'Name' or 'Formula', by default '
    delimiter: str, optional
        Delimiter to separate multiple components in the mixture thermodb, by default '|'
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    MixtureModelSource
        MixtureModelSource object containing data source and equation source

    Notes
    -----
    - If rules is not provided, the reference rules in the mixture thermodb will be used
    - If rules is provided, it will be used to map data/equations in the thermodb to the model source
    - If check_labels is True, the labels in the mixture thermodb will be checked based on the provided rules
    - If verbose is True, detailed information will be printed during the process
    - Reference thermodb is optional, if not provided, only the mixture and thermodb will be used
    - Mixture id is generated based on the mixture_key and delimiter, e.g. 'Water|Ethanol' for mixture_key='Name' and delimiter='|'
    - Rules can be provided as a dictionary or a file path to a YAML file
    - If rules contain mixture ids, they will be used to map data/equations in the thermodb to the model source
    - If rules do not contain mixture ids, the reference rules will be used
    - If rules contain labels, they will be used to check labels in the mixture thermodb
    - If rules do not contain labels, the labels in the reference thermodb will be used
    '''
    try:
        # SECTION: create thermodb hub
        try:
            thermodb_hub = init()
        except Exception as e:
            logger.error(f"Error in init thermodb hub: {e}")
            raise Exception(f"Error in init thermodb hub: {e}")

        # SECTION: extract mixture thermodb
        # NOTE: mixture thermodb
        components: List[Component] = mixture_thermodb.components
        # NOTE: thermodb
        thermodb: CompBuilder = mixture_thermodb.thermodb
        # NOTE: reference thermodb
        # ! reference thermodb is optional
        reference_thermodb: Optional[ReferenceThermoDB] = mixture_thermodb.reference_thermodb

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
            # >> for the case of no reference (reference_thermodb), set empty rules
            reference_rules = {}
            labels = []
            ignore_labels = []
            ignore_props = []

        # SECTION: set ids
        # >> name states
        name_states = [
            set_component_key(
                component,
                component_key='Name'
            ) for component in components
        ]
        # >> sort alphabetically
        name_states.sort()

        # >> formula states
        formula_states = [
            set_component_key(
                component,
                component_key='Formula'
            ) for component in components
        ]
        # >> sort alphabetically
        formula_states.sort()

        # ! mixture name
        mixture_name = delimiter.join(name_states)
        # ! mixture formula
        mixture_formula = delimiter.join(formula_states)

        # NOTE: component rules
        # create dict to hold component rules both name-state and formula-state
        component_rules_dict: Dict[str, Dict[str, ComponentRule]] = {}

        # >> set default to reference rules
        # ! >> by name
        component_rules_dict[mixture_name] = reference_rules
        # ! >> by formula
        component_rules_dict[mixture_formula] = reference_rules

        # SECTION: check rules
        if rules:
            # NOTE: verbose
            if verbose:
                logger.info(
                    f"Checking rules for mixture components: {''.join(name_states)} using provided rules"
                )

            # NOTE: overwrite existing rules in the thermodb hub
            if overwrite_rules:
                # reset component_rules_dict
                component_rules_dict = {
                    mixture_name: {},
                    mixture_formula: {}
                }

                # >> log
                if verbose:
                    logger.info(
                        "Overwriting existing rules in the thermodb hub"
                    )

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

            # NOTE: find mixture ids in rules
            mixture_ids_in_rules = find_mixture_ids_in_rules(
                rules=rules,
                delimiter=delimiter
            )

            # NOTE: normalize rules
            rules_normalized = {}
            # update rules if mixture ids found in rules
            if len(mixture_ids_in_rules) > 0:
                rules_normalized = normalize_rules(
                    mixture_ids=mixture_ids_in_rules,
                    rules=rules,
                    delimiter=delimiter
                )

            # NOTE: check for mixture rules if exists
            name_state_rules_ = look_up_mixture_rules(
                mixture_id=mixture_name,
                rules=rules_normalized,
            )

            if name_state_rules_:
                # >> set
                component_rules_dict[mixture_name] = name_state_rules_

            # ! >> by formula-state
            formula_state_rules_ = look_up_mixture_rules(
                mixture_id=mixture_formula,
                rules=rules_normalized,
            )

            if formula_state_rules_:
                # >> set
                component_rules_dict[mixture_formula] = formula_state_rules_

            # NOTE: check if `component_rules_dict` is still empty, then use default rules if exists
            all_empty = True
            for key in component_rules_dict:
                if len(component_rules_dict[key]) > 0:
                    all_empty = False
                    break

            if all_empty:
                # ! >> by default rules key
                default_rules_ = look_up_mixture_rules(
                    mixture_id=mixture_name,
                    rules=rules,
                    search_key=DEFAULT_RULES_KEY
                )

                if default_rules_:
                    component_rules_dict[mixture_name] = default_rules_
                    component_rules_dict[mixture_formula] = default_rules_
                else:
                    # log
                    logger.warning(
                        f"No rules found for mixture {mixture_name} or {mixture_formula} in the provided rules."
                    )

            # SECTION: extract labels
            name_state_rules_labels = extract_labels_from_rules(
                component_rules_dict[mixture_name]
            ) if component_rules_dict[mixture_name] else []

            formula_state_rules_labels = extract_labels_from_rules(
                component_rules_dict[mixture_formula]
            ) if component_rules_dict[mixture_formula] else []
            # >> combine and unique
            mixture_rules_labels = list(
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
                len(mixture_rules_labels) > 0
            ):
                # check if all labels in mixture_rules_labels are in labels
                for label in mixture_rules_labels:
                    if label not in labels:
                        # set
                        label_link = False
                        # log
                        logger.error(
                            f"Label '{label}' in rules not found in rules labels"
                        )

        else:
            # NOTE: verbose
            if verbose:
                logger.info(
                    f"No rules provided, using reference rules for mixture components: {', '.join(name_states)}")

            # no rules provided, use reference rules
            # check label results
            label_link = False

        # SECTION: add mixture thermodb to thermodb hub
        # >> set rule
        rule_ = component_rules_dict.get(
            mixture_name,
            None
        ) or component_rules_dict.get(
            mixture_formula,
            None
        )

        # ! >> check rule
        if not rule_:
            rule_ = None
        # >> if empty, set to None
        if rule_ and len(rule_) == 0:
            rule_ = None

        # NOTE: name states as id
        # >> add
        add_thermodb_res_ = thermodb_hub.add_thermodb(
            name=mixture_name,
            data=thermodb,
            rules=rule_,
        )

        # >> log
        if verbose:
            if add_thermodb_res_:
                logger.info(
                    f"Added thermodb for mixture components: {mixture_name}")
            else:
                logger.warning(
                    f"Failed to add thermodb for mixture components: {mixture_name}")

        # NOTE: formula states as id
        # >> add
        add_thermodb_res_ = thermodb_hub.add_thermodb(
            name=mixture_formula,
            data=thermodb,
            rules=rule_,
        )

        # >> log
        if verbose:
            if add_thermodb_res_:
                logger.info(
                    f"Added thermodb for mixture components: {mixture_formula}")
            else:
                logger.warning(
                    f"Failed to add thermodb for mixture components: {mixture_formula}")

        # SECTION: build mixture model source
        datasource, equationsource = thermodb_hub.build()

        # NOTE: create mixture model source
        mixture_model_source = MixtureModelSource(
            components=components,
            data_source=datasource,
            equation_source=equationsource,
            check_labels=check_labels,
            label_link=label_link,
        )

        return mixture_model_source
    except Exception as e:
        logger.error(f"Error in build_mixture_model_source: {e}")
        raise Exception(f"Error in build_mixture_model_source: {e}")


def build_mixtures_model_source(
    mixtures_thermodb: List[MixtureThermoDB],
    rules: Optional[
        Dict[str, Dict[str, ComponentRule]] | str
    ] = None,
    check_labels: bool = True,
    mixture_key: Literal['Name', 'Formula'] = 'Name',
    delimiter: str = '|',
    overwrite_rules: bool = False,
    verbose: bool = False,
) -> List[MixtureModelSource]:
    '''
    Build list of mixture model source from list of mixture thermodb and rules

    Parameters
    ----------
    mixtures_thermodb: List[MixtureThermoDB]
        List of MixtureThermoDB object containing pythermodb data (`TableData`, `TableEquation`, etc.)
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the mixture thermodb based on the provided rules, by default True
    mixture_key: Literal['Name', 'Formula'], optional
        Key to use for mixture id, either 'Name' or 'Formula', by default 'Name'
    delimiter: str, optional
        Delimiter to separate multiple components in the mixture thermodb, by default '|'
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    List[MixtureModelSource]
        List of MixtureModelSource object containing data source and equation source
    '''
    try:
        # NOTE: create model source for multiple components
        mixtures_model_source: List[MixtureModelSource] = []

        # iterate over mixtures thermodb
        for mixture_thermodb in mixtures_thermodb:
            # ! build
            mixture_model_source = build_mixture_model_source(
                mixture_thermodb=mixture_thermodb,
                rules=rules,
                check_labels=check_labels,
                mixture_key=mixture_key,
                delimiter=delimiter,
                overwrite_rules=overwrite_rules,
                verbose=verbose
            )

            # append
            mixtures_model_source.append(mixture_model_source)

        return mixtures_model_source
    except Exception as e:
        logger.error(f"Error in build_mixtures_model_source: {e}")
        raise Exception(f"Error in build_mixtures_model_source: {e}")


def build_model_source(
    source: List[ComponentModelSource] | List[MixtureModelSource]
) -> ModelSource:
    '''
    Build model source from list of component model source

    Parameters
    ----------
    source: List[ComponentModelSource] | List[MixtureModelSource]
        List of ComponentModelSource/MixtureModelSource object containing data source and equation source

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
        for component_model_source in source:
            # add to model source
            # >> data source
            model_source.data_source.update(
                component_model_source.data_source
            )
            # >> equation source
            model_source.equation_source.update(
                component_model_source.equation_source
            )

        return model_source
    except Exception as e:
        logger.error(f"Error in build_model_source: {e}")
        raise Exception(f"Error in build_model_source: {e}")


def load_and_build_component_model_source(
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
        components_model_source: List[ComponentModelSource] = build_components_model_source(
            components_thermodb=components_thermodb,
            rules=rules,
            check_labels=check_labels
        )

        # SECTION: build model source
        model_source: ModelSource = build_model_source(
            source=components_model_source
        )

        # return
        return model_source
    except Exception as e:
        logger.error(f"Error in load_and_build_model_source: {e}")
        raise Exception(f"Error in load_and_build_model_source: {e}")


def load_and_build_mixture_model_source(
        thermodb_sources: List[MixtureThermoDBSource],
        rules: Optional[
            Dict[str, Dict[str, ComponentRule]] | str
        ] = None,
        check_labels: bool = True,
        mixture_key: Literal['Name', 'Formula'] = 'Name',
        delimiter: str = '|',
        overwrite_rules: bool = False,
        verbose: bool = False,
) -> ModelSource:
    '''
    Load mixture thermodb from thermodb sources and build model source

    Parameters
    ----------
    thermodb_sources: List[MixtureThermoDBSource]
        List of MixtureThermoDBSource object containing mixture thermodb and source file path
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the mixture thermodb based on the provided rules, by default True
    mixture_key: Literal['Name', 'Formula'], optional
        Key to use for mixture id, either 'Name' or 'Formula', by default 'Name'
    delimiter: str, optional
        Delimiter to separate multiple components in the mixture thermodb, by default '|'
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    ModelSource
        ModelSource object containing data source and equation source for multiple mixtures
    '''
    try:
        # NOTE: check inputs
        if not isinstance(thermodb_sources, list) or len(thermodb_sources) == 0:
            logger.error(
                "thermodb_sources must be a non-empty list of MixtureThermoDBSource objects.")
            raise ValueError(
                "thermodb_sources must be a non-empty list of MixtureThermoDBSource objects.")

        # iterate over thermodb sources and load thermodb
        for thermodb_source in thermodb_sources:
            if not isinstance(thermodb_source, MixtureThermoDBSource):
                logger.error(
                    "Each item in thermodb_sources must be a MixtureThermoDBSource object.")
                raise ValueError(
                    "Each item in thermodb_sources must be a MixtureThermoDBSource object.")
            if not isinstance(thermodb_source.source, str) or len(thermodb_source.source) == 0:
                logger.error(
                    "source in MixtureThermoDBSource must be a non-empty string.")
                raise ValueError(
                    "source in MixtureThermoDBSource must be a non-empty string.")
            if not isinstance(thermodb_source.components, list) or len(thermodb_source.components) == 0:
                logger.error(
                    "components in MixtureThermoDBSource must be a non-empty list of Component objects.")
                raise ValueError(
                    "components in MixtureThermoDBSource must be a non-empty list of Component objects.")

        # SECTION: load thermodb and create mixture thermodb
        # NOTE: create list of mixture thermodb
        mixtures_thermodb: List[MixtureThermoDB] = []

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

            # set mixture
            mixture_thermodb = MixtureThermoDB(
                components=thermodb_source.components,
                thermodb=thermodb_,
                reference_thermodb=None
            )
            # append
            mixtures_thermodb.append(mixture_thermodb)

        # SECTION: build mixtures model source
        mixtures_model_source: List[MixtureModelSource] = build_mixtures_model_source(
            mixtures_thermodb=mixtures_thermodb,
            rules=rules,
            check_labels=check_labels,
            mixture_key=mixture_key,
            delimiter=delimiter,
            overwrite_rules=overwrite_rules,
            verbose=verbose
        )

        # SECTION: build model source
        model_source: ModelSource = build_model_source(
            source=mixtures_model_source
        )

        # return
        return model_source
    except Exception as e:
        logger.error(f"Error in load_and_build_mixture_model_source: {e}")
        raise Exception(f"Error in load_and_build_mixture_model_source: {e}")


def load_and_build_model_source(
    thermodb_sources: List[ComponentThermoDBSource | MixtureThermoDBSource],
    rules: Optional[
        Dict[str, Dict[str, ComponentRule]] | str
    ] = None,
    check_labels: bool = True,
    mixture_key: Literal['Name', 'Formula'] = 'Name',
    delimiter: str = '|',
    overwrite_rules: bool = False,
    verbose: bool = False,
) -> ModelSource:
    '''
    Load thermodb from thermodb sources and build model source

    Parameters
    ----------
    thermodb_sources: List[ComponentThermoDBSource | MixtureThermoDBSource]
        List of ComponentThermoDBSource or MixtureThermoDBSource object containing thermodb and source file path
    rules: Dict[str, Dict[str, ComponentRule]] | str, optional
        Rules to map data/equations in the thermodb to the model source.
    check_labels: bool, optional
        Whether to check labels in the thermodb based on the provided rules, by default True
    mixture_key: Literal['Name', 'Formula'], optional
        Key to use for mixture id, either 'Name' or 'Formula', by default 'Name'
    delimiter: str, optional
        Delimiter to separate multiple components in the mixture thermodb, by default '|'
    overwrite_rules: bool, optional
        Whether to overwrite existing rules in the thermodb hub, by default False
    verbose: bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    ModelSource
        ModelSource object containing data source and equation source for multiple components/mixtures
    '''
    try:
        # NOTE: check inputs
        if not isinstance(thermodb_sources, list) or len(thermodb_sources) == 0:
            logger.error(
                "thermodb_sources must be a non-empty list of ComponentThermoDBSource or MixtureThermoDBSource objects.")
            raise ValueError(
                "thermodb_sources must be a non-empty list of ComponentThermoDBSource or MixtureThermoDBSource objects.")

        # SECTION: separate component and mixture thermodb sources
        component_thermodb_sources: List[ComponentThermoDBSource] = []
        mixture_thermodb_sources: List[MixtureThermoDBSource] = []

        # iterate over thermodb sources and separate
        for thermodb_source in thermodb_sources:
            if isinstance(thermodb_source, ComponentThermoDBSource):
                component_thermodb_sources.append(thermodb_source)
            elif isinstance(thermodb_source, MixtureThermoDBSource):
                mixture_thermodb_sources.append(thermodb_source)
            else:
                logger.error(
                    "Each item in thermodb_sources must be a ComponentThermoDBSource or MixtureThermoDBSource object.")
                raise ValueError(
                    "Each item in thermodb_sources must be a ComponentThermoDBSource or MixtureThermoDBSource object.")

        # SECTION: load and build component model source
        model_source_component: Optional[ModelSource] = None
        if len(component_thermodb_sources) > 0:
            model_source_component = load_and_build_component_model_source(
                thermodb_sources=component_thermodb_sources,
                rules=rules,
                check_labels=check_labels
            )
        else:
            if verbose:
                logger.info("No component thermodb sources provided.")

        # SECTION: load and build mixture model source
        model_source_mixture: Optional[ModelSource] = None
        if len(mixture_thermodb_sources) > 0:
            model_source_mixture = load_and_build_mixture_model_source(
                thermodb_sources=mixture_thermodb_sources,
                rules=rules,
                check_labels=check_labels,
                mixture_key=mixture_key,
                delimiter=delimiter,
                overwrite_rules=overwrite_rules,
                verbose=verbose
            )
        else:
            if verbose:
                logger.info("No mixture thermodb sources provided.")

        # SECTION: combine model sources
        if model_source_component and model_source_mixture:
            # combine both
            model_source: ModelSource = ModelSource(
                data_source={
                    **model_source_component.data_source,
                    **model_source_mixture.data_source
                },
                equation_source={
                    **model_source_component.equation_source,
                    **model_source_mixture.equation_source
                }
            )

        elif model_source_component:
            model_source = model_source_component
        elif model_source_mixture:
            model_source = model_source_mixture
        else:
            logger.error("No valid model source could be built.")
            raise ValueError("No valid model source could be built.")

        return model_source

    except Exception as e:
        logger.error(f"Error in load_and_build_model_source: {e}")
        raise Exception(f"Error in load_and_build_model_source: {e}")
