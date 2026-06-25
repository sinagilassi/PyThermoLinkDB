# import libs
import logging
from typing import Dict, List, Tuple, TypeVar
from pythermodb_settings.models import (
    Component,
    ComponentKey,
    CustomProperty,
)
from pythermodb_settings.utils import (
    find_component_by_id,
    set_component_id
)
# locals
from ..thermo import EquationSourceCore

# NOTE: set logger
logger = logging.getLogger(__name__)

SourceValue = TypeVar("SourceValue")


def _component_ordered_data(
        data: Dict[str, SourceValue],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True
) -> Dict[str, Tuple[str, SourceValue]]:
    """
    Match source entries to components and return them keyed by output id.

    Input keys may use any component identifier supported by
    ``find_component_by_id``. Output keys always use ``component_key``.
    """
    matched_data: Dict[str, Tuple[str, SourceValue]] = {}

    for source_id, value in data.items():
        comp = find_component_by_id(
            id=source_id,
            components=components,
            case_sensitive=case_sensitive
        )

        if comp is None:
            logger.warning(
                f"Component with id '{source_id}' not found in provided components. "
                f"Skipping this entry."
            )
            continue

        output_id = set_component_id(comp, component_key)
        if output_id in matched_data:
            logger.warning(
                f"Multiple source entries matched component '{output_id}'. "
                f"Keeping the first entry and skipping '{source_id}'."
            )
            continue

        matched_data[output_id] = (source_id, value)

    return matched_data


# SECTION: map component property
def map_prop(
        data: Dict[str, CustomProperty],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True
) -> Tuple[Dict[str, float], List[float]]:
    # NOTE: result initialization
    res_comp: Dict[str, float] = {}
    res_values: List[float] = []

    if not data:
        return res_comp, res_values

    # NOTE: data keys can use any known component id format
    matched_data = _component_ordered_data(
        data=data,
        components=components,
        component_key=component_key,
        case_sensitive=case_sensitive
    )

    # NOTE: output order follows the provided components list
    for comp in components:
        output_id = set_component_id(comp, component_key)
        matched_entry = matched_data.get(output_id)
        if matched_entry is None:
            logger.warning(
                f"Property source for component '{output_id}' not found."
            )
            continue

        source_id, prop = matched_entry
        if prop.value is None:
            logger.warning(
                f"Property '{source_id}' has no value and will be skipped."
            )
            continue

        res_comp[output_id] = prop.value
        res_values.append(prop.value)

    return res_comp, res_values

# SECTION: map component equation source


def map_eq(
        data: Dict[str, EquationSourceCore],
        components: List[Component],
        component_key: ComponentKey,
        case_sensitive: bool = True
) -> Tuple[Dict[str, EquationSourceCore], List[EquationSourceCore]]:
    # NOTE: result initialization
    # ! id defined as component id or component reference
    res_comp: Dict[str, EquationSourceCore] = {}
    res_values: List[EquationSourceCore] = []

    if not data:
        return res_comp, res_values

    # NOTE: data keys can use any known component id format
    matched_data = _component_ordered_data(
        data=data,
        components=components,
        component_key=component_key,
        case_sensitive=case_sensitive
    )

    # NOTE: output order follows the provided components list
    for comp in components:
        output_id = set_component_id(comp, component_key)
        matched_entry = matched_data.get(output_id)
        if matched_entry is None:
            logger.warning(
                f"Equation source for component '{output_id}' not found."
            )
            continue

        _, eq = matched_entry
        res_comp[output_id] = eq
        res_values.append(eq)

    return res_comp, res_values
