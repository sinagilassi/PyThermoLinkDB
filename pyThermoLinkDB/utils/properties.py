# import libs
import logging
from typing import List, Dict, Literal, Optional
from pythermodb_settings.models import Component, ComponentRule
# local
from ..config import (
    DEFAULT_RULES_KEY,
    DATA_KEY,
    EQUATIONS_KEY,
    CONSTANTS_KEY
)


# NOTE: logger
logger = logging.getLogger(__name__)


def set_component_key(
    component: Component,
    component_key: str = "Formula-State"
) -> str:
    '''
    Set component key string based on component attributes (name, formula, state), this function is case-insensitive for component_key.

    Parameters
    ----------
    component: Component
        Component object
    component_key: Literal["Name-State", "Formula-State", "Name", "Formula"], optional
        Component key type, by default "Formula-State"

    Returns
    -------
    str
        Component key string
    '''
    try:
        if component_key.lower() == "Name-State".lower():
            return f"{component.name}-{component.state}"
        elif component_key.lower() == "Formula-State".lower():
            return f"{component.formula}-{component.state}"
        elif component_key.lower() == "Name".lower():
            return component.name
        elif component_key.lower() == "Formula".lower():
            return component.formula
        elif component_key.lower() == "Name-Formula".lower():
            return f"{component.name}-{component.formula}"
        elif component_key.lower() == "Name-Formula-State".lower():
            return f"{component.name}-{component.formula}-{component.state}"
        else:
            logger.warning(
                f"Invalid component_key: {component_key}. Using 'Formula-State' instead.")
            return f"{component.formula}-{component.state}"
    except Exception as e:
        logger.error(f"Error in set_component_key: {e}")
        raise Exception(f"Error in set_component_key: {e}")


def extract_labels_from_rules(
    rules: Dict[str, ComponentRule]
) -> List[str]:
    '''
    Extract labels from rules

    Parameters
    ----------
    rules: Dict[str, ComponentRule]
        Rules dictionary

    Returns
    -------
    List[str]
        List of labels

    Notes
    -----
    The rules dictionary is defined as:

    ```python
    custom_rules = {
        "DATA":
            {
                "property1": "label1",
                "property2": "label2"
            },
        "EQUATIONS":
            {
                "property3": "label3",
                "property4": "label4"
            },
        "CONSTANTS": {
            "property5": "label5",
            "property6": "label6"
        }
    }
    ```
    '''
    labels = set()

    try:
        for rule_type, rule_dict in rules.items():
            # check rule_dict
            if rule_type not in [DATA_KEY, EQUATIONS_KEY]:
                logger.warning(
                    f"Invalid rule_type: {rule_type}. It should be 'DATA' or 'EQUATION'.")
                continue

            if isinstance(rule_dict, dict):
                for prop, label in rule_dict.items():
                    # check label
                    if isinstance(label, str) and label.strip():
                        # save label
                        labels.add(label.strip())
            else:
                logger.warning(
                    f"Invalid rule_dict for {rule_type}: {rule_dict}. It should be a dictionary.")

        return list(labels)
    except Exception as e:
        logger.error(f"Error in extract_labels_from_rules: {e}")
        raise Exception(f"Error in extract_labels_from_rules: {e}")

# NOTE: extract label from constants rules


def extract_labels_from_constants_rules(
    rules: Dict[str, ComponentRule]
) -> List[str]:
    '''
    Extract labels from constants rules

    Parameters
    ----------
    rules: Dict[str, ComponentRule]
        Rules dictionary

    Returns
    -------
    List[str]
        List of labels

    Notes
    -----
    The rules dictionary is defined as:
    custom_rules = {
        "CONSTANTS": {
            "property5": "label5",
            "property6": "label6"
        }
    }
    '''
    labels = set()

    # NOTE: validation
    # check if rules is empty
    if not rules:
        logger.warning(
            "Rules is empty. Cannot extract labels from constants rules.")
        return []

    # check if rules contains CONSTANTS_KEY
    if CONSTANTS_KEY not in rules:
        logger.warning(
            f"Rules does not contain '{CONSTANTS_KEY}' key. Cannot extract labels from constants rules.")
        return []

    try:
        for prop, label in rules.items():
            # prop should be in CONSTANTS_KEY
            if prop != CONSTANTS_KEY:
                logger.warning(
                    f"Invalid prop in constants rules: {prop}. It should be 'CONSTANTS'.")
                continue

            # iterate over label
            if isinstance(label, dict):
                for prop_, label_ in label.items():
                    # check label
                    if isinstance(label_, str) and label_.strip():
                        # save label
                        labels.add(label_.strip())
            else:
                logger.warning(
                    f"Invalid label for property '{prop}': {label}. It should be a non-empty string.")

        return list(labels)
    except Exception as e:
        logger.error(f"Error in extract_labels_from_constants_rules: {e}")
        raise Exception(f"Error in extract_labels_from_constants_rules: {e}")


# SECTION: look up component rules


def look_up_component_rules(
        component: Component,
        rules: Dict[str, Dict[str, ComponentRule]],
        search_key: str = "Formula-State"
) -> Dict[str, ComponentRule] | None:
    '''
    Look up component rules from rules dictionary based on component attributes (name, formula, state).

    Parameters
    ----------
    component: Component
        Component object
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary
    search_key: Literal["Name-State", "Formula-State"], optional
        Search key type, by default "Formula-State"

    Returns
    -------
    Dict[str, ComponentRule] | None
        Component rules dictionary

    Notes
    -----
    The rules dictionary is defined as:

    ```python
    rules = {
        "Formula-State": {
            "DATA":
                {
                    "property1": "label1",
                    "property2": "label2"
                },
            "EQUATIONS":
                {
                    "property3": "label3",
                    "property4": "label4"
                }
            },
        "Formula-State2": {
            ...
        }
    }
    ```
    '''
    try:
        # NOTE: component attributes
        name_state = f"{component.name}-{component.state}"
        formula_state = f"{component.formula}-{component.state}"

        # rules keys (case insensitive)
        rules_keys_lower = {key.lower(): key for key in rules.keys()}

        # reference rules
        reference_rules = None

        # NOTE: look up rules (case insensitive)
        if search_key.lower() == "Name-State".lower():
            # check
            if name_state.lower() in rules_keys_lower:
                reference_rules = rules[rules_keys_lower[name_state.lower()]]
            else:
                reference_rules = None
        elif search_key.lower() == "Formula-State".lower():
            # check
            if formula_state.lower() in rules_keys_lower:
                reference_rules = rules[rules_keys_lower[formula_state.lower()]]
            else:
                reference_rules = None
        elif search_key.lower() == DEFAULT_RULES_KEY.lower():
            # check
            if DEFAULT_RULES_KEY.lower() in rules_keys_lower:
                reference_rules = rules[rules_keys_lower[DEFAULT_RULES_KEY.lower()]]
            else:
                reference_rules = None
        else:
            logger.warning(
                f"Invalid search_key: {search_key}. It should be 'Name-State' or 'Formula-State'.")
            return None

        # return
        return reference_rules
    except Exception as e:
        logger.error(f"Error in look_up_component_rules: {e}")
        raise Exception(f"Error in look_up_component_rules: {e}")


# SECTION: look up constants rules
def look_up_constants_rules(
        constants_id: str,
        rules: Dict[str, Dict[str, ComponentRule]],
) -> Dict[str, ComponentRule] | None:
    '''
    Look up constants rules from rules dictionary based on constants id.

    Parameters
    ----------
    constants_id: str
        Constants id
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary

    Returns
    -------
    Dict[str, Dict[str, str]] | None
        Constants rules dictionary

    Notes
    -----
    The rules dictionary is defined as:

    ```python
    rules = {
        "Constants-id1": {
            "CONSTANTS":
                {
                    "property3": "label3",
                    "property4": "label4"
                }
            },
        "Constants-id2": {
            ...
        }
    }
    '''
    try:
        # rules keys (case insensitive)
        rules_keys_lower = {key.lower(): key for key in rules.keys()}

        # reference rules
        reference_rules = None

        # NOTE: look up rules (case insensitive)
        if constants_id.lower() in rules_keys_lower:
            reference_rules = rules[rules_keys_lower[constants_id.lower()]]
        # elif DEFAULT_RULES_KEY.lower() in rules_keys_lower:
        #     reference_rules = rules[rules_keys_lower[DEFAULT_RULES_KEY.lower()]]
        else:
            reference_rules = None

        # NOTE: check if reference_rules contains CONSTANTS_KEY
        if (
            reference_rules is not None and
            CONSTANTS_KEY not in reference_rules
        ):
            reference_rules = None
            # log
            logger.warning(
                f"Reference rules for constants_id '{constants_id}' does not contain 'CONSTANTS' key. Ignoring the rules."
            )

        # return
        return reference_rules
    except Exception as e:
        logger.error(f"Error in look_up_constants_rules: {e}")
        raise Exception(f"Error in look_up_constants_rules: {e}")

# NOTE: combine all rules into 'Constants' key taken from other keys if all other keys are empty


def combine_rules_into_constants_key(
    rules: Dict[str, Dict[str, ComponentRule]]
) -> Dict[str, Dict[str, ComponentRule]] | None:
    '''
    Combine all rules into 'Constants' key if all other keys are empty.

    Parameters
    ----------
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary


    Returns
    -------
    Dict[str, Dict[str, ComponentRule]] | None
        New rules dictionary with only 'Constants' key if all other keys are empty, otherwise None

    Notes
    -----
    The rules dictionary is defined as:

    ```python

    rules = {
        "ALL": {
            "DATA":
                {
                    "property1": "label1",
                    "property2": "label2"
                },
            "EQUATIONS":
                {
                    "property3": "label3",
                    "property4": "label4"
                }
            },
            "CONSTANTS": {
                "property5": "label5",
                "property6": "label6"
            }
        },
        "Constants-id1": {
            "CONSTANTS":
                {
                    "property5": "label5",
                    "property6": "label6"
                }
            },
        "Constants-id2": {
            ...
        }
    }
    ```

    ```'''
    try:
        # check if rules is empty
        if not rules:
            return None

        # check if all keys except 'Constants' are not empty
        all_empty = False

        for key in rules:
            if key == 'Constants':
                continue

            if len(rules[key]) == 0:
                all_empty = True
                break

        # ! combine all rules into 'Constants' key if all other keys are not empty
        if not all_empty:
            # create new rules dictionary with only 'Constants' key
            new_rules = {
                'Constants': {}
            }

            # rules
            rules_collection = {}

            for key in rules:
                if key == 'Constants':
                    continue

                # set
                rule_ = rules[key]

                for prop, label in rule_.items():
                    # >> only CONSTANTS_KEY
                    if prop == CONSTANTS_KEY:
                        # iterate over label
                        for prop_, label_ in rule_[prop].items():
                            # add to rules_collection
                            rules_collection[prop_] = label_

            # add to new rules (overwrite if already exists)
            new_rules['Constants'] = {
                'CONSTANTS': rules_collection
            }

            return new_rules

        # return None if not all_empty
        return None
    except Exception as e:
        logger.error(f"Error in combine_rules_into_constants_key: {e}")
        raise Exception(f"Error in combine_rules_into_constants_key: {e}")


# SECTION: look up default rules


def look_up_default_rules(
    rules: Dict[str, Dict[str, ComponentRule]]
) -> Dict[str, ComponentRule] | None:
    '''
    Look up default rules from rules dictionary based on DEFAULT_RULES_KEY.

    Parameters
    ----------
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary

    Returns
    -------
    Dict[str, ComponentRule] | None
        Default rules dictionary

    Notes
    -----
    The rules dictionary is defined as:

    ```python
    rules = {
        "ALL": {
            "DATA":
                {
                    "property1": "label1",
                    "property2": "label2"
                },
            "EQUATIONS":
                {
                    "property3": "label3",
                    "property4": "label4"
                }
            },
            "CONSTANTS": {
                "property5": "label5",
                "property6": "label6"
            }
        },
    }
    ```
    '''
    try:
        # rules keys (case insensitive)
        rules_keys_lower = {key.lower(): key for key in rules.keys()}

        # reference rules
        reference_rules = None

        # NOTE: look up default rules (case insensitive)
        if DEFAULT_RULES_KEY.lower() in rules_keys_lower:
            reference_rules = rules[rules_keys_lower[DEFAULT_RULES_KEY.lower()]]
        else:
            reference_rules = None

        # return
        return reference_rules
    except Exception as e:
        logger.error(f"Error in look_up_default_rules: {e}")
        raise Exception(f"Error in look_up_default_rules: {e}")


def find_mixture_ids_in_rules(
    rules: Dict[str, Dict[str, ComponentRule]],
    delimiter: str = '|'
) -> List[str]:
    '''
    Find mixture ids in rules dictionary. By default, the mixture id should be defined as `component-name-1 | component-name-2 | ...` or `component-formula-1 | component-formula-2 | ...`.

    Parameters
    ----------
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary with mixture ids as keys

    Returns
    -------
    List[str]
        List of mixture ids
    '''
    try:
        # rules keys
        rules_keys = list(rules.keys())

        # check if rules_keys is empty
        if not rules_keys:
            return []

        # NOTE: mixture ids should contain '|'
        rules_keys = [key for key in rules_keys if delimiter in key]

        # return
        return rules_keys
    except Exception as e:
        logger.error(f"Error in find_mixture_ids_in_rules: {e}")
        raise Exception(f"Error in find_mixture_ids_in_rules: {e}")


def normalize_rules(
    mixture_ids: List[str],
    rules: Dict[str, Dict[str, ComponentRule]],
    delimiter: str = '|'
):
    '''
    Normalize rules dictionary by alphabetically sorting the rules keys (mixture ids).

    Parameters
    ----------
    mixture_ids: List[str]
        List of mixture ids
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary with mixture ids as keys
    delimiter: str, optional
        Delimiter used to separate components in mixture id, by default '|'

    Returns
    -------
    Dict[str, Dict[str, ComponentRule]]
        Normalized rules dictionary
    '''
    try:
        normalized_rules = {}

        # iterate mixture_ids
        for mixture_id in mixture_ids:
            # split mixture_id by '|'
            components = [comp.strip() for comp in mixture_id.split(delimiter)]
            # sort components alphabetically
            components_sorted = sorted(components, key=lambda x: x.lower())
            # join components back to mixture_id
            normalized_mixture_id = delimiter.join(components_sorted)
            # add to normalized_rules
            if mixture_id in rules:
                normalized_rules[normalized_mixture_id] = rules[mixture_id]

        # res
        return normalized_rules
    except Exception as e:
        logger.error(f"Error in normalize_rules: {e}")
        raise Exception(f"Error in normalize_rules: {e}")


def look_up_mixture_rules(
    mixture_id: str,
    rules: Dict[str, Dict[str, ComponentRule]],
    delimiter: str = '|',
    search_key: Optional[str] = None
) -> Dict[str, ComponentRule] | None:
    '''
    Look up mixture rules from rules dictionary based on mixture id.

    Parameters
    ----------
    mixture_id: str
        Mixture id (name or formula)
    rules: Dict[str, Dict[str, ComponentRule]]
        Rules dictionary with mixture ids as keys
    delimiter: str, optional
        Delimiter used to separate components in mixture id, by default '|'
    search_key: str, optional
        Search key type, by default None (not used)

    Returns
    -------
    Dict[str, ComponentRule] | None
        Mixture rules dictionary
    '''
    try:
        # rules keys (case insensitive)
        rules_keys_lower = {key.lower(): key for key in rules.keys()}

        # >> remove extra spaces
        mixture_id = delimiter.join(
            [comp.strip() for comp in mixture_id.split(delimiter)]
        )

        # reference rules
        reference_rules = None

        # NOTE: look up rules (case insensitive)
        if mixture_id.lower() in rules_keys_lower:
            reference_rules = rules[rules_keys_lower[mixture_id.lower()]]
        else:
            reference_rules = None

        # NOTE: not found
        if reference_rules is None and search_key is not None:
            # check for DEFAULT_RULES_KEY
            if DEFAULT_RULES_KEY.lower() in rules_keys_lower:
                reference_rules = rules[rules_keys_lower[DEFAULT_RULES_KEY.lower()]]
            else:
                reference_rules = None

        # return
        return reference_rules
    except Exception as e:
        logger.error(f"Error in look_up_mixture_rules: {e}")
        raise Exception(f"Error in look_up_mixture_rules: {e}")
