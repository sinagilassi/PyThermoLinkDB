# import libs
import logging
from typing import List, Dict
from pythermodb_settings.models import Component, ComponentRule
# local
from ..config import DEFAULT_RULES_KEY, DATA_KEY, EQUATIONS_KEY


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
    component_rules = {
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
        "}
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
