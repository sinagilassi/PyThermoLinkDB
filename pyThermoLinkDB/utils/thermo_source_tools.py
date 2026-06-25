# import libs
import logging
from typing import Any, Dict, List, Optional, Tuple
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty,
    CustomConstant
)
from pythermodb_settings.utils import (
    generate_component_references,
    find_component_by_id,
    find_components_by_ids,
    set_component_id
)
# locals
from ..thermo import EquationSourceCore

# NOTE: set logger
logger = logging.getLogger(__name__)


# SECTION: map component property
def map_component_property(
        data: Dict[str, CustomProperty],
        components: Optional[List[Component]],
        component_key: Optional[ComponentKey] = None,
        case_sensitive: bool = True
) -> Optional[Tuple[Dict[str, float], List[float]]]:
    # NOTE: result initialization
    res_comp: Dict[str, float] = {}
    res_values: List[float] = []

    # NOTE: component ids
    component_ids: List[str] = list(data.keys())
    components_ = None
    component_refs: Optional[Dict[str, Any]] = None

    # ! find components by ids
    if components is not None:
        components_ = find_components_by_ids(
            ids=component_ids,
            components=components,
            case_sensitive=case_sensitive
        )

        # >> check
        if not components_:
            logger.warning(
                f"No components found for ids: {component_ids}. "
                f"Returning empty results."
            )
            return None

    # NOTE: no components means no id is required anymore
    if not components:
        # iterate over the data and extract values
        for id, prop in data.items():
            if prop.value is not None:
                res_comp[id] = prop.value
                res_values.append(prop.value)
            else:
                logger.warning(
                    f"Property '{id}' has no value and will be skipped.")

    # NOTE: components are provided, so we need to transform the data
    if (
        components is not None and
        components_ is not None
    ):
        # iterate over data (component ids) and find corresponding components
        for comp, (id, prop) in zip(components_, data.items()):
            # >> check if component is found
            if comp is None:
                logger.warning(
                    f"Component with id '{id}' not found in provided components. "
                    f"Skipping this entry."
                )
                continue

            # >> check if property value is None
            if prop.value is None:
                logger.warning(
                    f"Property '{id}' has no value and will be skipped.")
                continue

            # set id
            id_ = id
            value_ = prop.value

            # >> set component id if not already set
            if comp is not None and component_key is not None:
                id_ = set_component_id(comp, component_key)

            # >> add to results
            res_comp[id_] = value_
            res_values.append(value_)

    return res_comp, res_values

# SECTION: extract component equation source


def map_component_equation(
        data: Dict[str, EquationSourceCore],
        components: Optional[List[Component]],
        component_key: Optional[ComponentKey] = None,
        case_sensitive: bool = True
) -> Optional[Dict[str, EquationSourceCore]]:
    # NOTE: result initialization
    # ! id defined as component id or component reference
    res_comp: Dict[str, EquationSourceCore] = {}

    # NOTE: component ids
    component_ids: List[str] = list(data.keys())
    components_ = None

    # ! find components by ids
    if components is not None:
        components_ = find_components_by_ids(
            ids=component_ids,
            components=components,
            case_sensitive=case_sensitive
        )

        # >> check
        if not components_:
            logger.warning(
                f"No components found for ids: {component_ids}. "
                f"Returning empty results."
            )
            return None

    # NOTE: no components means no transformation is needed
    if not components:
        res_comp = data

    # NOTE: components are provided, so we need to transform the data
    if (
        components is not None and
        components_ is not None
    ):
        # iterate over data (component ids) and find corresponding components
        for comp, (id, prop) in zip(components_, data.items()):
            # >> check if component is found
            if comp is None:
                logger.warning(
                    f"Component with id '{id}' not found in provided components. "
                    f"Skipping this entry."
                )
                continue

            # set id
            id_ = id

            # >> set component id if not already set
            if comp is not None and component_key is not None:
                id_ = set_component_id(comp, component_key)

            # >> add to results
            res_comp[id_] = prop

    return res_comp
