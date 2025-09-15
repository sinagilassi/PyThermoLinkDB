# import libs
import logging
from typing import List, Dict
from pythermodb_settings.models import Component, ComponentRule
# local


# NOTE: logger
logger = logging.getLogger(__name__)


def set_component_key(
    component: Component,
    component_key: str = "Formula-State"
) -> str:
    '''
    Set component key

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
        if component_key == "Name-State":
            return f"{component.name}-{component.state}"
        elif component_key == "Formula-State":
            return f"{component.formula}-{component.state}"
        elif component_key == "Name":
            return component.name
        elif component_key == "Formula":
            return component.formula
        elif component_key == "Name-Formula":
            return f"{component.name}-{component.formula}"
        elif component_key == "Name-Formula-State":
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
        "EQUATION":
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
            if rule_type not in ["DATA", "EQUATION"]:
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
